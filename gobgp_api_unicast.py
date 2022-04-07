from __future__ import absolute_import
from __future__ import print_function

import grpc
from google.protobuf.any_pb2 import Any

from grpclib import gobgp_pb2, gobgp_pb2_grpc, attribute_pb2
from models import PathDataClass


GOBGP_CONN = '127.0.0.1:50051'
TIMEOUT_SECONDS = 10
ORIGIN_INCOMPLETE = 2

IPv4_UNICAST=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
table_type=gobgp_pb2.GLOBAL

def AddPath(px: PathDataClass):
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=px.prefix_len,
        prefix=px.src,
    ))

    origin = Any()
    origin.Pack(attribute_pb2.OriginAttribute(origin=ORIGIN_INCOMPLETE,))  # INCOMPLETE
    
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop=px.next_hop,
    ))    
    attributes = [origin, next_hop]    

    stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=nlri,
                pattrs=attributes,
                family=IPv4_UNICAST,
            )
        ),
        TIMEOUT_SECONDS,
    )    


def DelPath(px: PathDataClass):
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=px.prefix_len,
        prefix=px.src,
    ))
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop=px.next_hop,
    ))
    stub.DeletePath(
        gobgp_pb2.DeletePathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=nlri,    
                pattrs=[next_hop],
                family=IPv4_UNICAST,
            )
        ),
        TIMEOUT_SECONDS,
    )


def ListPath() -> list:
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    paths = stub.ListPath(
        gobgp_pb2.ListPathRequest(
            table_type=table_type,
            family=IPv4_UNICAST,
        ),
        TIMEOUT_SECONDS, 
    )

    res = []
    for path in paths:
        px = path.destination.prefix
        src, prefix_len = px.split("/")
        prefix_len = int(prefix_len)
        next_hop = path.destination.paths[0].pattrs[1].value.decode()[2:]
                
        res.append(dict(src=src, prefix_len=prefix_len, next_hop=next_hop))
        
    return res
