from typing import List, Optional, Tuple
from google.protobuf.any_pb2 import Any
from grpclib import attribute_pb2
from grpclib.attribute_pb2 import FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI, FlowSpecIPPrefix

NEXT_HOP = '0.0.0.0'
ORIGIN_INCOMPLETE = 2


class FlowSpecComposer:
    _SRC_DST_IP_MAP = {
        'SRC': 2,
        'DST': 1
    }

    _PROTOCOLS_MAP = {
        'TCP': 6,
        'UDP': 17,
        'ICMP': 1,
        'GRE': 47,
        'ESP': 50,
    }

    _FLOWSPEC_COMPONENT_MAP = {
        'SRC': 6,
        'DST': 5,
        'PROTOCOL': 3,
    }

    _OPERAND_MAP = {
        '==': 1,
        '>': 2,
        '>=': 3,
        '<': 4,
        '<=': 5,
        '!=': 6,
        '&': 69  # rfc5575
    }
    
    
    def __init__(self,
                 src: str,
                 src_prefix_len: int,
                 dst: Optional[str] = '',
                 dst_prefix_len: Optional[int] = 32,
                 src_ports: Optional[str] = '',
                 dst_ports: Optional[str] = '',
                 protocols: Optional[List[str]] = '',
                 rate_limit: int = 0,   # 0 - discard, 1 - accept, >=2 rate_limit
                 # Also builder to get another parameters (rule_ttl, rule_id, request_type) this parameters do not use
                 **kwargs,
                 ):
        self.src = src
        self.dst = dst
        self.src_prefix = src_prefix_len
        self.dst_prefix = dst_prefix_len
        self.src_ports = src_ports
        self.dst_ports = dst_ports
        self.protocols = protocols
        self.rate_limit = rate_limit
    
    def __repr__(self):
        return(f'FlowSpecComposer('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit}')

    def __str__(self):
        return(f'FlowSpecComposer('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit}')
               
    def _wrap_flowspec_prefix(self, prefix: str, prefix_len: int, direction: str):
        nlri = Any()
        nlri.Pack(FlowSpecIPPrefix(
            type=self._SRC_DST_IP_MAP[direction],
            prefix_len=prefix_len,
            prefix=prefix
        ))
        return nlri

    def _craft_src_dst_packet(self) -> List[Any]:
        src_dst = [self._wrap_flowspec_prefix(self.src, self.src_prefix, 'SRC')]
        if self.dst:
            src_dst.append(self._wrap_flowspec_prefix(self.dst, self.dst_prefix, 'DST'))
        return src_dst

    def _wrap_flowspec_item(self, ports: str, direction: str) -> Any:
        flowspec_items = []        

        for operand, port in self._get_ports(ports):
            flowspec_items.append(FlowSpecComponentItem(op=operand, value=port))
        flowspec_component = Any()
        flowspec_component.Pack(FlowSpecComponent(type=self._FLOWSPEC_COMPONENT_MAP[direction], items=flowspec_items))
        return flowspec_component

    def _get_ports(self, ports: str) -> Tuple[int, int]:
        # ports  = "5,77-80,82-85,87-90,92-95,97-100,22,23,24        
        for item in ports.replace(' ', '').split(','):
            if '-' in item:
                start, end = item.split('-')
                yield self._OPERAND_MAP['>='], int(start)
                yield self._OPERAND_MAP['&'], int(end)
            else:
                yield self._OPERAND_MAP['=='], int(item)

    def _craft_src_dst_ports(self):
        flowspec_components = []
        if self.src_ports:
            flowspec_components.append(self._wrap_flowspec_item(self.src_ports, 'SRC'))
        if self.dst_ports:
            flowspec_components.append(self._wrap_flowspec_item(self.dst_ports, 'DST'))
        return flowspec_components

    def _craft_protocol(self):
        if not self.protocols:
            return []
        items = []
        for protocol in self.protocols:
            items.append(FlowSpecComponentItem(op=self._OPERAND_MAP['=='], value=self._PROTOCOLS_MAP[protocol.upper()]))
        flowspec_component = Any()
        flowspec_component.Pack(FlowSpecComponent(type=self._FLOWSPEC_COMPONENT_MAP['PROTOCOL'], items=items))
        return [flowspec_component]

    def create_nlri(self):
        rules = []                
        rules.extend(self._craft_src_dst_packet())
        rules.extend(self._craft_src_dst_ports())
        rules.extend(self._craft_protocol())
        flowspec_nlri = Any()
        flowspec_nlri.Pack(FlowSpecNLRI(rules=rules))
        return flowspec_nlri

    def create_attibutes(self):
        next_hop = Any()
        next_hop.Pack(attribute_pb2.NextHopAttribute(next_hop=NEXT_HOP))
        
        origin = Any()
        origin.Pack(attribute_pb2.OriginAttribute(origin=ORIGIN_INCOMPLETE))

        if self.rate_limit == None:
            return [next_hop, origin]
        traffic_rate = Any()
        traffic_rate.Pack(attribute_pb2.TrafficRateExtended(rate=self.rate_limit))
        community = Any()
        community.Pack(attribute_pb2.ExtendedCommunitiesAttribute(communities=[traffic_rate]))
        return [next_hop, origin, community]

### example ###
if __name__ == '__main__':
    import grpc
    import gobgp_pb2_grpc
    import gobgp_pb2

    GOBGP_CONN = '127.0.0.1:50051'
    TIMEOUT_SECONDS = 100
        
    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    b = FlowSpecComposer(src='8.8.8.0',
                        src_prefix_len=24,
                        src_ports='22, 80-90, 500-8000',
                        protocols=['tcp', 'udp'],
                        rate_limit=10000
                        )
                        
    flowspec_nlri = b.create_nlri()
    attributes = b.create_attibutes()

    response = stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=gobgp_pb2.GLOBAL,
            path=gobgp_pb2.Path(
                nlri=flowspec_nlri,
                pattrs=attributes,
                family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST)
            )
        ),
        TIMEOUT_SECONDS,
    )