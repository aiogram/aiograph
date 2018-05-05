from typing import List, Optional, Union


def pages_converter(raw_pages: List[dict]) -> List['Page']:
    """
    Convert list of raw pages to list of Page objects

    :param raw_pages:
    :return:
    """
    from .page import Page

    return [Page(**page) for page in raw_pages]


def convert_content(value: List[Union[dict, str]]) -> Optional[List[Union[str, 'NodeElement']]]:
    """
    Convert raw content to Python objects

    :param value:
    :return:
    """
    from .node import NodeElement

    if value is None:
        return

    result = []
    for item in value:
        if isinstance(item, dict):
            item = NodeElement(**item)
        result.append(item)
    return result
