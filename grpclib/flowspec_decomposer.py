from typing import List, Optional, Tuple, Iterable
from google.protobuf.any_pb2 import Any
import attribute_pb2
from attribute_pb2 import FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI, FlowSpecIPPrefix


NEXT_HOP = '0.0.0.0'
ORIGIN_INCOMPLETE = 2


class FlowSpecDecomposer:
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
        return(f'FlowSpecBuilder('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit}')

    def __str__(self):
        return(f'FlowSpecBuilder('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit}')
               
    def _get_nlri(self, prefix: str, prefix_len: int, direction: str):
        nlri = Any()
        nlri.Pack(attribute_pb2.FlowSpecIPPrefix(
            type=self._SRC_DST_IP_MAP[direction],
            prefix_len=prefix_len,
            prefix=prefix
        ))
        return nlri

    def _craft_src_dst_packet(self) -> List[Any]:
        src_dst = [self._get_nlri(self.src, self.src_prefix, 'SRC')]
        if self.dst:
            src_dst.append(self._get_nlri(self.dst, self.dst_prefix, 'DST'))
        return src_dst

    def _get_flowspec_item(self, ports: str, direction: str) -> Any:
        flowspec_items = []        

        for operand, port in self._get_ports(ports):
            flowspec_items.append(FlowSpecComponentItem(op=operand, value=port))
        flowspec_component = Any()
        flowspec_component.Pack(FlowSpecComponent(type=self._FLOWSPEC_COMPONENT_MAP[direction], items=flowspec_items))
        return flowspec_component

    def _get_ports(self, ports: str) -> Tuple[int, int]:
        # ports  = "5,77-80,82-85,87-90,92-95,97-100,22,23,24
        print(f'{ports=}')
        for i in ports.replace(' ', '').split(','):
            if '-' in i:
                start, end = i.split('-')
                yield self._OPERAND_MAP['>='], int(start)
                yield self._OPERAND_MAP['&'], int(end)
            else:
                yield self._OPERAND_MAP['=='], int(i)

    def _craft_src_dst_ports(self):
        flowspec_components = []
        if self.src_ports:
            flowspec_components.append(self._get_flowspec_item(self.src_ports, 'SRC'))
        if self.dst_ports:
            flowspec_components.append(self._get_flowspec_item(self.dst_ports, 'DST'))
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

    def create_rules(self):
        src_dst = self._craft_src_dst_packet()
        rules = []
        rules.extend(src_dst)
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
        traffic_rate = Any()
        traffic_rate.Pack(attribute_pb2.TrafficRateExtended(rate=self.rate_limit))
        community = Any()
        community.Pack(attribute_pb2.ExtendedCommunitiesAttribute(communities=[traffic_rate]))
        return [next_hop, origin, community]



"""
RFC 5575 - encoding flowspec operations 
-----------------------------------------------------
  0   1   2   3   4   5   6   7
+---+---+---+---+---+---+---+---+
| e | a |  len  | 0 |lt |gt |eq |
+---+---+---+---+---+---+---+---+

                    Numeric operator

e -   end-of-list bit.  Set in the last {op, value} pair in the
    list.

a -   AND bit.  If unset, the previous term is logically ORed
    with the current one.  If set, the operation is a logical
    AND.  It should be unset in the first operator byte of a
    sequence.  The AND operator has higher priority than OR
    for the purposes of evaluating logical expressions.

len - The length of the value field for this operand is given
    as (1 << len). 0-255:0 255-65536:1 etc

lt -  less than comparison between data and value.

gt -  greater than comparison between data and value.
-----------------------------------------------------

to convert back from stream into the string we have to use some magic based on the above statements
we don't care of bits 0,2,3 so we have a bitmask 0b10110000 = 176
(actually we do care of the 0th bit that means the value is last on the list and we don't need to put comma in the end)
thus the operations conversion would be:
   op = op AND bitmask XOR op

using python bitwise operators
   op &= bitmask ^ op

so lets assume we have some data decoded from stream:
msg=type: 5
items {
  op: 1 => 0000 0001    ==
  value: 80
}
items {
  op: 17 => 0001 0001   ==
  value: 443
}
items {
  op: 19 => 0001 0011   >=
  value: 5000
}
items {
  op: 213 => 1101 0101   end, &<=
  value: 6000
}
using that technic we can translate it to the 
destination-port: ==80 ==443 >=5000&<=6000
it looks pretty the same output from the gobgp daemon
but we don't want that ugly format 
there are many operations that probably useful for tcp flags and fragments but we don't need them yet
in my case (src_dst_ports) only > and >= operations important. they mark the beginnig of a range
all over operations is just a comma (,) between values except the last one
bear that in mind we can easily convert the data to the string
dst_ports = '80,443,5000-6000'
"""

OP_MAP_ENCODE = {
        '==': 1,
        '>': 2,
        '>=': 3,
        '<': 4,
        '<=': 5,
        '!=': 6,
        '&': 69  # rfc5575
    }

OP_MAP_DECODE = {
    1: '==',
    2: '>',
    3: '>=',
    4: '<',
    5: '<=',
    6: '!=',
    69: '&',
    70: '&==',
    75: '&<='
}


def decode_flowspec_nlri_value(items: List[FlowSpecComponentItem]):
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

