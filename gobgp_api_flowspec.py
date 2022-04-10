import grpc
from grpclib import gobgp_pb2, gobgp_pb2_grpc
from grpclib.attribute_pb2 import FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI, FlowSpecIPPrefix
from models import FlowSpecDataClass, FlowSpecGoBGPDataClass
from grpclib.flowspec_composer import FlowSpecComposer

GOBGP_CONN = '127.0.0.1:50051'
TIMEOUT_SECONDS = 10
IPv4_FLOWSPEC=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST)
table_type=gobgp_pb2.GLOBAL

def _normalizeData(px):
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
    rate_limit = px.rate_limit if px.rate_limit else 0

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
    
    data = _normalizeData(px)
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

    data = _normalizeData(px)
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


def ListPathFlowSpec() -> list[FlowSpecGoBGPDataClass]:
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

        px = parseFlowSpecPB(path)
        res.append(FlowSpecDataClass(**px))
    
    return res


def parseFlowSpecPB(path):
    
    nlri = FlowSpecNLRI
    nlri_data = path.destination.paths[0].nlri.value
    rules = nlri.FromString(nlri_data)
    print(f"{rules=}")   
    
    for rule in rules.rules:   
        if rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecIPPrefix':
            obj = FlowSpecIPPrefix
            msg = obj.FromString(rule.value)
            print(f"{msg=}")
        elif rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecComponent':
            obj = FlowSpecComponent
            msg = obj.FromString(rule.value)
            print(f"{msg=}")

    return ({
                "src": "1.2.3.4/32",                
                "dst": "10.20.30.0/32",
                "src_ports": "1024-65535",
                "dst_ports": "80, 443, 5000-6000",
                "protocols": "tcp, udp",
                "action": 1,
                "rate_limit": 0
            })        


    
