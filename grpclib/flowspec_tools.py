from typing import Iterable

NUMBER_PORTS = 65535


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




