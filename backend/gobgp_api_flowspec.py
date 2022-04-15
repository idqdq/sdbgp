import grpc
from grpclib import gobgp_pb2, gobgp_pb2_grpc
from typing import List
from models import FlowSpecDataClass, FlowSpecGoBGPDataClass
from grpclib.flowspec_composer import FlowSpecComposer
from grpclib.flowspec_decomposer import FlowSpecDecomposer
from config import Settings

settings = Settings()

GOBGP_HOST = settings.GOBGP_HOST
GOBGP_PORT = settings.GOBGP_PORT
GOBGP_CONN = f"{GOBGP_HOST}:{GOBGP_PORT}"

TIMEOUT_SECONDS = 1000
IPv4_FLOWSPEC=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST)
table_type=gobgp_pb2.GLOBAL

ACTION_DISCARD = 1
ACTION_ACCEPT = 2
ACTION_RATE_LIMIT = 3

def _flowspecData_to_flowspecGoBgpData(px):

    data = {}
    if '/' in px.src:
        data["src"], src_prefix_len = px.src.split('/')
        data["src_prefix_len"] = int(src_prefix_len)
    else:
        data["src"], data["src_prefix_len"] = px.src, 32

    if px.dst:
        if '/' in px.dst:
            data["dst"], dst_prefix_len = px.dst.split('/')
            data["dst_prefix_len"] = int(dst_prefix_len)
        else:
            data["dst"], data["dst_prefix_len"] = px.dst, 32
    

    data["src_ports"] = px.src_ports if px.src_ports else ''
    data["dst_ports"] = px.dst_ports if px.dst_ports else ''

    data["protocols"] = px.protocols.replace(' ', '').split(',') if px.protocols else []
    if px.action != ACTION_ACCEPT:
        data["rate_limit"] = px.rate_limit   # for the ACCEPT action the rate_limit = None
    #rate_limit = px.rate_limit if px.rate_limit else 0

    return FlowSpecGoBGPDataClass(**data)


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
    
    flowspec_nlri = b.create_nlri()
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
        px.rate_limit, _ = decomp.get_attrs() # 2nd value is an origin that we don't use in the project

        if px.rate_limit is None:
            px.action = ACTION_ACCEPT
            px.rate_limit = 0
        elif px.rate_limit == 0:
            px.action = ACTION_DISCARD
        else:
            px.action = ACTION_RATE_LIMIT
                   
        res.append(px)
    
    return res
