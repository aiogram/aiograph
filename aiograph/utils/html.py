from html.entities import name2codepoint
from html.parser import HTMLParser
from typing import List, Union

import attr

from ..types import NodeElement

ALLOWED_TAGS = [
    'a', 'aside', 'b', 'blockquote', 'br', 'code', 'em', 'figcaption', 'figure',
    'h3', 'h4', 'hr', 'i', 'iframe', 'img', 'li', 'ol', 'p', 'pre', 's',
    'strong', 'u', 'ul', 'video'
]
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen',
    'link', 'menuitem', 'meta', 'param', 'source', 'track', 'wbr'
}
ALLOWED_ATTRS = ['href', 'src']


def node_to_html(node: Union[str, NodeElement, list]) -> str:
    """
    Convert Nodes to HTML

    :param node:
    :return:
    """
    if isinstance(node, str):  # Text
        return node

    elif isinstance(node, list):  # List of nodes
        result = ''
        for child_node in node:
            result += node_to_html(child_node)
        return result

    elif not isinstance(node, NodeElement):
        raise TypeError(f"Node must be instance of str or NodeElement, not {type(node)}")

    # NodeElement

    # Open
    result = "<" + node.tag
    if node.attrs:
        result += ' ' + ' '.join(f"{k}=\"{v}\"" for k, v in node.attrs.items())

    if node.tag in VOID_ELEMENTS:  # Close void element
        result += '/>'
    else:
        result += '>'
        for child_node in node.children:  # Container body
            result += node_to_html(child_node)
        result += '</' + node.tag + '>'  # Close tag

    return result


def html_to_nodes(html_content: str) -> List[Union[str, NodeElement]]:
    """
    Convert HTML code to Nodes

    :param html_content:
    :return:
    """
    parser = HtmlToNodesParser()
    parser.feed(html_content)

    return parser.get_nodes()


def _node_converter_filter(attribute, value) -> bool:
    return bool(value)


def nodes_to_json(nodes: List[Union[str, NodeElement]]) -> List[Union[str, dict]]:
    """
    Convert Nodes to JSON

    :param nodes:
    :return:
    """
    result = []
    for node in nodes:
        if isinstance(node, str):
            result.append(node)
        elif isinstance(node, NodeElement):
            result.append(attr.asdict(node, filter=_node_converter_filter))
    return result


def html_to_json(content: str) -> List[Union[str, dict]]:
    """
    Convert HTML to JSON

    :param content:
    :return:
    """
    return nodes_to_json(html_to_nodes(content))


class HtmlToNodesParser(HTMLParser):
    def __init__(self):
        super(HtmlToNodesParser, self).__init__()

        self.current_nodes = []
        self.parent_nodes = []

    def error(self, message):
        raise ValueError(message)

    def add_str_node(self, s):
        if not s:
            return

        if self.current_nodes and isinstance(self.current_nodes[-1], str):
            self.current_nodes[-1] += s
        else:
            self.current_nodes.append(s)

    def handle_starttag(self, tag, attrs_list):
        if tag not in ALLOWED_TAGS:
            self.error(f"{tag} tag is not allowed")

        node = NodeElement(tag=tag)

        if attrs_list:
            for attr, value in attrs_list:
                node.attrs[attr] = value

        self.current_nodes.append(node)

        if tag not in VOID_ELEMENTS:
            self.parent_nodes.append(self.current_nodes)
            self.current_nodes = node.children = []

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return

        self.current_nodes = self.parent_nodes.pop()

        last_node = self.current_nodes[-1]

        if last_node.tag != tag:
            self.error(f"\"{tag}\" tag closed instead of \"{last_node.tag}\"")

        if not last_node.children:
            last_node.children.clear()

    def handle_data(self, data):
        self.add_str_node(data)

    def handle_entityref(self, name):
        self.add_str_node(chr(name2codepoint[name]))

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))

        self.add_str_node(c)

    def get_nodes(self):
        if self.parent_nodes:
            not_closed_tag = self.parent_nodes[-1][-1].tag
            self.error(f"\"{not_closed_tag}\" tag is not closed")

        return self.current_nodes
