from typing import List, Union

from attr import ib, s

from .base import TelegraphObject
from .converters import convert_content

__all__ = ['NodeElement']


@s
class Node(TelegraphObject):
    """
    This abstract object represents a DOM Node.
    It can be a String which represents a DOM text node or a NodeElement object.

    Source: http://telegra.ph/api#Node
    """
    pass


@s
class NodeElement(Node):
    """
    This object represents a DOM element node.

    Source: http://telegra.ph/api#NodeElement
    """

    tag: str = ib()
    attrs: dict = ib(factory=dict)
    children: List[Union['NodeElement', str]] = ib(factory=list, converter=convert_content)

    @tag.validator
    def _validate_tag(self, attribute, value):
        from ..utils import html
        if value not in html.ALLOWED_TAGS:
            raise ValueError(f"This tag name is not allowed '{value}'!")

    def add(self, content: Union[str, 'NodeElement']):
        if not isinstance(content, (str, NodeElement)):
            raise TypeError(f"content must be instance of str or Node not {type(content)}")

        self.children.append(content)
        return self

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __getitem__(self, item):
        return self.attrs[item]

    def __delitem__(self, key):
        del self.attrs[key]

    def as_html(self) -> str:
        from ..utils.html import node_to_html
        return node_to_html(self)
