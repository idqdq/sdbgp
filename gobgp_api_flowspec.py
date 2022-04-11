import grpc
from grpclib import gobgp_pb2, gobgp_pb2_grpc
from grpclib.attribute_pb2 import FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI, FlowSpecIPPrefix
from typing import List
from models import FlowSpecAction, FlowSpecDataClass, FlowSpecGoBGPDataClass
from grpclib.flowspec_composer import FlowSpecComposer
from grpclib.flowspec_decomposer import FlowSpecDecomposer

GOBGP_CONN = '127.0.0.1:50051'
TIMEOUT_SECONDS = 1000
IPv4_FLOWSPEC=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST)
table_type=gobgp_pb2.GLOBAL

ACTION_DISCARD = '1'
ACTION_ACCEPT = '2'
ACTION_RATE_LIMIT = '3'

def _flowspecData_to_flowspecGoBgpData(px):
    if '/' in px.src:
        src, src_prefix_len = px.src.split('/')
        src_prefix_len = int(src_prefix_len)
    else:
        src, src_prefix_len = px.src, 32

    if px.dst:
        if '/' in px.dst:
            dst, dst_prefix_len = px.dst.split('/')
            dst_prefix_len = int(dst_prefix_len)
        else:
            dst, dst_prefix_len = px.dst, 32
    else:
        dst, dst_prefix_len = '', 0

    src_ports = px.src_ports if px.src_ports else ''
    dst_ports = px.dst_ports if px.dst_ports else ''

    protocols = px.protocols.replace(' ', '').split(',') if px.protocols else []
    if px.action.value == ACTION_ACCEPT:
        rate_limit = None
    #rate_limit = px.rate_limit if px.rate_limit else 0

    return FlowSpecGoBGPDataClass(src=src,
                                  src_prefix_len=src_prefix_len,
                                  dst=dst,
                                  dst_prefix_len=dst_prefix_len,
                                  src_ports=src_ports,
                                  dst_ports=dst_ports,
                                  protocols=protocols,
                                  rate_limit=rate_limit)


def _getStub(data: FlowSpecGoBGPDataClass):
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    b = FlowSpecComposer(src=data.src,
                        src_prefix_len=data.src_prefix_len,
                        src_ports=data.src_ports,
                        dst=data.dst,
                        dst_prefix_len=data.dst_prefix_len,
                        dst_ports=data.dst_ports,
                        protocols=data.protocols,
                        rate_limit=data.rate_limit)
    
    flowspec_nlri = b.create_rules()
    attributes = b.create_attibutes()

    return stub, flowspec_nlri, attributes


def AddPathFlowSpec(px: FlowSpecDataClass):
    
    data = _flowspecData_to_flowspecGoBgpData(px)
    stub, flowspec_nlri, attributes = _getStub(data)

    response = stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=flowspec_nlri,
                pattrs=attributes,
                family=IPv4_FLOWSPEC,
            )
        ),
        TIMEOUT_SECONDS,
    )


def DelPathFlowSpec(px: FlowSpecDataClass):

    data = _flowspecData_to_flowspecGoBgpData(px)
    stub, flowspec_nlri, attributes = _getStub(data)

    stub.DeletePath(
        gobgp_pb2.DeletePathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=flowspec_nlri,
                pattrs=attributes,
                family=IPv4_FLOWSPEC,                
            ),
        ),
        TIMEOUT_SECONDS,
    )


def ListPathFlowSpec() -> List[FlowSpecGoBGPDataClass]:
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    paths = stub.ListPath(
        gobgp_pb2.ListPathRequest(
            table_type=table_type,
            family=IPv4_FLOWSPEC,
        ),
        TIMEOUT_SECONDS, 
    )

    res = []
    for path in paths:     
        decomp = FlowSpecDecomposer(path)
        px = FlowSpecDataClass(**decomp.get_nlri())
        _, px.rate_limit = decomp.get_attrs()

        if px.rate_limit is None:
            px.action = ACTION_ACCEPT
            px.rate_limit = 0
        elif px.rate_limit == 0:
            px.action = ACTION_DISCARD
        else:
            px.action = ACTION_RATE_LIMIT
            
        print(px)
        res.append(px)
    
    return res

# path.destination.paths[0].nlri - NRLI
# path.destination.paths[0].pattrs[0] - Origin
# path.destination.paths[0].pattrs[1] - TrafficRate (Extended Community attr) 
# path.destination.paths[0].pattrs[1+] - NLRI

PROTOCOLS_MAP = {
    1: 'icmp',
    6: 'tcp',
    17: 'udp',
    47: 'gre',
    50: 'esp',
}

def parseFlowSpecPB(path):
    
    # path.destination.paths[0].nlri
    nlri = path.destination.paths[0].nlri.value
    pattrs = path.destination.paths[0].pattrs

    #nlri = FlowSpecNLRI
    rules = FlowSpecNLRI.FromString(nlri)
    print(f"{rules=}")   
    
    nrli_data = FlowSpecDataClass(src='')
    for rule in rules.rules:   
        if rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecIPPrefix':
            obj = FlowSpecIPPrefix
            msg = obj.FromString(rule.value)   
            print(f"{msg=}")

            if msg.type == 1:
                nrli_data.dst = msg.prefix + '/' + msg.prefix_len                
            elif msg.type == 2:
                nrli_data.src = msg.prefix + '/' + msg.prefix_len                           

        elif rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecComponent':
            obj = FlowSpecComponent
            msg = obj.FromString(rule.value)
            print(f"{msg=}")

            if msg.type == 3:
                for item in msg.items:
                    nrli_data.protocols.append(PROTOCOLS_MAP[item.value])
            elif msg.type == 5:
                nrli_data.dst_ports = decode_flowspec_nlri_value(msg.items)
            elif msg.type == 6:
                nrli_data.src_ports = decode_flowspec_nlri_value(msg.items)
            
    print(f"{nrli_data=}")
    
    return nrli_data


def decode_flowspec_nlri_value(items: List[FlowSpecComponentItem]) -> str:
    BITMASK = 0b10110000
    convert_op = lambda x: x & BITMASK ^ x
    
    result = ''
    for item in items:
        op = convert_op(item.op)
        if item.op > 127:
            div = ''                                # last item
        else: 
            div = '-' if op==2 or op==3 else ','    # 2 or 3 means > or >= and this is a start of a range
        
        result += str(item.value)+div

    return result

