from typing import List, Optional, Tuple, Union
from google.protobuf.any_pb2 import Any
from grpclib import attribute_pb2
from grpclib.attribute_pb2 import ExtendedCommunitiesAttribute, FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI, FlowSpecIPPrefix, OriginAttribute, TrafficRateExtended
from grpclib.gobgp_pb2 import ListPathResponse

class FlowSpecDecomposer:
    PROTOCOLS_MAP = {
    1: 'icmp',
    6: 'tcp',
    17: 'udp',
    47: 'gre',
    50: 'esp',
    }


    def __init__(self, path: ListPathResponse):
        self.path = path
        self.attrs = path.destination.paths[0].pattrs
        self.nlri = path.destination.paths[0].nlri.value


    def get_nlri(self) -> dict:
        """
        Args:
            N/A
        Returns:
            returns dict with values extracted from the FlowSpecNLRI:
                src: str    
                dst: str
                src_ports: str
                dst_ports: str
                protocols: str
        """
        nrli_data = {}

        rules = FlowSpecNLRI.FromString(self.nlri)
        for rule in rules.rules:   
            if rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecIPPrefix':                
                msg = FlowSpecIPPrefix.FromString(rule.value)                   

                if msg.type == 1:
                    nrli_data["dst"] = msg.prefix + '/' + str(msg.prefix_len)
                elif msg.type == 2:
                    nrli_data["src"] = msg.prefix + '/' + str(msg.prefix_len)

            elif rule.type_url == 'type.googleapis.com/gobgpapi.FlowSpecComponent':                
                msg = FlowSpecComponent.FromString(rule.value)                

                if msg.type == 3:
                    for item in msg.items:
                        if nrli_data.get("protocols"):
                            nrli_data["protocols"] += ', ' + self.PROTOCOLS_MAP[item.value]
                        else: 
                            nrli_data["protocols"] = self.PROTOCOLS_MAP[item.value]
                elif msg.type == 5:
                    nrli_data["dst_ports"] = self._decode_flowspec_nlri_value(msg.items)
                elif msg.type == 6:
                    nrli_data["src_ports"] = self._decode_flowspec_nlri_value(msg.items)
        
        return nrli_data


    def get_attrs(self) -> Tuple[int, Union[None, int]]:
        """
        Args:
            N/A
        Returns:
            returns two values:
            * Origin:  
            * Rate-limit: 
                - None: action ACCEPT
                - 0: action DISCARD
                - >= 1: action rate-limit        
        """
        origin = 0
        rate_limit = None        

        for index in range (len(self.attrs)):
            if self.attrs[index].type_url == 'type.googleapis.com/gobgpapi.OriginAttribute':
                origin = OriginAttribute.FromString(self.attrs[index].value)
            if self.attrs[index].type_url == 'type.googleapis.com/gobgpapi.ExtendedCommunitiesAttribute':
                communities = ExtendedCommunitiesAttribute.FromString(self.attrs[index].value)
                rate_limit = TrafficRateExtended.FromString(communities.communities[0].value).rate
    
        return origin, rate_limit           


    def _decode_flowspec_nlri_value(self, items: List[FlowSpecComponentItem]) -> str:        
        """RFC 5575 - encoding flowspec operations 
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
        BITMASK = 0b10110000
        convert_op = lambda x: x & BITMASK ^ x
        
        result = ''
        for item in items:
            op = convert_op(item.op)
            if item.op > 127:
                div = ''                                # last item
            else: 
                div = '-' if op==2 or op==3 else ','    # 2 or 3 means > or >= and this is a start of a range ( - sign)
            
            result += str(item.value)+div

        return result