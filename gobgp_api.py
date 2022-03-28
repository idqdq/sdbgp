from __future__ import absolute_import
from __future__ import print_function

import grpc
from google.protobuf.any_pb2 import Any

import gobgp_pb2
import gobgp_pb2_grpc
import attribute_pb2
from models import PathDataClass

_TIMEOUT_SECONDS = 10
_GOBGP_CONN = '10.2.1.96:50051'

family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
table_type=gobgp_pb2.GLOBAL

def AddPath(px: PathDataClass):
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=px.mask_cidr,
        prefix=px.ip,
    ))

    origin = Any()
    origin.Pack(attribute_pb2.OriginAttribute(origin=2,))  # INCOMPLETE
    
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
                family=family,
            )
        ),
        _TIMEOUT_SECONDS,
    )    


def DelPath(px: PathDataClass):
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=px.mask_cidr,
        prefix=px.ip,
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
                family=family,
            )
        ),
        _TIMEOUT_SECONDS,
    )


def ListPath() -> list:
    channel = grpc.insecure_channel(_GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    paths = stub.ListPath(
        gobgp_pb2.ListPathRequest(
            table_type=table_type,
            family=family,
        ),
        _TIMEOUT_SECONDS, 
    )

    res = []
    for path in paths:
        px = path.destination.prefix
        ip, mask_cidr = px.split("/")
        mask_cidr = int(mask_cidr)
        next_hop = path.destination.paths[0].pattrs[1].value.decode()[2:]
                
        res.append(dict(ip=ip, mask_cidr=mask_cidr, next_hop=next_hop))
        
    return res
