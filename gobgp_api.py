from __future__ import absolute_import
from __future__ import print_function

import grpc
from google.protobuf.any_pb2 import Any

import gobgp_pb2
import gobgp_pb2_grpc
import attribute_pb2

_TIMEOUT_SECONDS = 10
_GOBGP_CONN = '10.2.1.96:50051'

family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
table_type=gobgp_pb2.GLOBAL

def AddPath(prefix: str, prefix_len: int, nh: str):
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=prefix_len,
        prefix=prefix,
    ))

    origin = Any()
    origin.Pack(attribute_pb2.OriginAttribute(origin=2,))  # INCOMPLETE
    
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop=nh,
    ))    
    attributes = [origin, next_hop]    

    stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=nlri,
                pattrs=attributes,
                family=family,
            )
        ),
        _TIMEOUT_SECONDS,
    )    


def DelPath(prefix: str, prefix_len: int, nh: str):
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=prefix_len,
        prefix=prefix,
    ))
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop=nh,
    ))
    stub.DeletePath(
        gobgp_pb2.DeletePathRequest(
            table_type=table_type,
            path=gobgp_pb2.Path(
                nlri=nlri,    
                pattrs=[next_hop],
                family=family,
            )
        ),
        _TIMEOUT_SECONDS,
    )


def ListPath() -> list:
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    prefixes = stub.ListPath(
        gobgp_pb2.ListPathRequest(
            table_type=table_type,
            family=family,
        ),
        _TIMEOUT_SECONDS, 
    )

    res = []
    for prefix in prefixes:
        px = prefix.destination.prefix
        nh = prefix.destination.paths[0].pattrs[1].value.decode()
        print(f"{px=}, {nh=}")
        res.append(px)
        
    
    return res
