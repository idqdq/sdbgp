from typing import List, Optional, Tuple, Iterable
from google.protobuf.any_pb2 import Any
import grpc
from grpclib import attribute_pb2, gobgp_pb2_grpc, gobgp_pb2
from grpclib.attribute_pb2 import FlowSpecComponent, FlowSpecComponentItem, FlowSpecNLRI


GOBGP_CONN = '127.0.0.1:50051'
NEXT_HOP = '0.0.0.0'
ORIGIN_INCOMPLETE = 2
TIMEOUT_SECONDS = 10
IPv4_FLOWSPEC=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST)

NUMBER_PORTS = 65535

class FlowSpecBuilder:
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
                 dst_prefix_len: Optional[int] = 0,
                 src_ports: Optional[str] = '',
                 dst_ports: Optional[str] = '',
                 protocols: Optional[List[str]] = '',
                 rate_limit: int = 0,
                 negate: bool = False,
                 # Also builder to get another parameters (rule_ttl, rule_id, request_type) this parameters does not use
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
        self.negate = negate

    def __repr__(self):
        return(f'FlowSpecBuilder('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit},'
               f'negate={self.negate}')

    def __str__(self):
        return(f'FlowSpecBuilder('
               f'src={self.src}, dst={self.dst}, '
               f'src_prefix={self.src_prefix}, dst_prefix={self.dst_prefix})'
               f'src_ports={self.src_ports}, dst_ports={self.dst_ports},'
               f'protocols={self.protocols}, rate_limit={self.rate_limit},'
               f'negate={self.negate}')

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
        if self.negate:
            ports = revert_negate_ports(ports)

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


def revert_negate_ports(ports: str) -> str:
    exist_ports = set()
    for port in ports.replace(' ', '').split(','):
        if '-' in port:
            start, end = port.split('-')
            [exist_ports.add(i) for i in range(int(start), int(end)+1)]
        else:
            exist_ports.add(int(port))
    negate_ports = (f"{i}" for i in range(1, NUMBER_PORTS + 1) if i not in exist_ports)
    return zip_ports(negate_ports)


def zip_ports(unzipped_ports: Iterable[str]) -> str:
    """
    Получает список строк, состоящий из чисел и диапазонов чисел:
    ['60', '50', '21', '5000-5010',  '50001', '5010', '10', '11', '3', '5001', '50002', '50003']
    Сортирует этот список по числовым значениям,
    удаляет повторяющиеся значения и везвращает строковые диапазоны где это возможно.
    ['3', '10-11', '21', '50', '60', '5000-5010', '50001-50003']
    :param unzipped_ports:
    :return:
    """
    if not unzipped_ports:
        return ','.join(unzipped_ports)
    ports = set()
    for i in unzipped_ports:
        if '-' in i:
            start, end = i.split('-')
            [ports.add(x) for x in range(int(start), int(end)+1)]
        else:
            ports.add(int(i))
    ports = list(ports)
    ports.sort()
    ports_zip = []
    last, start = ports[0], ports[0]
    for port in ports[1:]:
        if last + 1 != port and last == start:
            ports_zip.append(str(last))
            start = port
        elif last + 1 != port and last != start:
            ports_zip.append(f'{start}-{last}')
            start = port
        last = port
    if start == last:
        ports_zip.append(str(last))
    else:
        ports_zip.append(f'{start}-{last}')
    return ','.join(ports_zip)


if __name__ == '__main__':
    aaa = '22, 80-90, 500-8000'
    print(revert_negate_ports(aaa))

    channel = grpc.insecure_channel(GOBGP_CONN)
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    b = FlowSpecBuilder(src='8.8.8.0',
                        src_prefix_len=24,
                        src_ports='22, 80-90, 500-8000',
                        protocols=['tcp', 'udp'],
                        negate=True)
                        
    flowspec_nlri = b.create_rules()
    attributes = b.create_attibutes()

    response = stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=gobgp_pb2.GLOBAL,
            path=gobgp_pb2.Path(
                nlri=flowspec_nlri,
                pattrs=attributes,
                family=IPv4_FLOWSPEC,
            )
        ),
        TIMEOUT_SECONDS,
    )
    # print(response.uuid)
    # result = stub.GetBgp(gobgp_pb2.GetBgpRequest())
    # print(result)

    result = stub.GetTable(gobgp_pb2.GetTableRequest(
        family=IPv4_FLOWSPEC))
    initialize_count_rules = result.num_destination
    result = stub.GetTable(gobgp_pb2.GetTableRequest(
        family=IPv4_FLOWSPEC))
    initialize_count_rules += result.num_destination

    result = stub.MonitorTable(gobgp_pb2.MonitorTableRequest())
    print(dir(result))
    print(result.running, result.details, result.code)
    # print(dir(result))
    print(f'{initialize_count_rules=}')
    # print(result.uuid)
    # stub.DeletePath(
    #     gobgp_pb2.DeletePathRequest(
    #         table_type=gobgp_pb2.GLOBAL,
    #         path=gobgp_pb2.Path(
    #             nlri=flowspec_nlri,
    #             pattrs=attributes,
    #             family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST),
    #         ),
    #
    #     ),
    #     1000,
    # )
