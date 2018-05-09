from typing import List, Union

from attr import ib, s

from .base import TelegraphObject
from .converters import convert_content
from .node import NodeElement

__all__ = ['Page']


@s
class Page(TelegraphObject):
    """
    This object represents a page on Telegraph.

    Source: http://telegra.ph/api#Page
    """

    path: str = ib(default=None)
    url: str = ib(default=None)
    title: str = ib(default=None)
    description: str = ib(default=None)
    author_name: str = ib(default=None)
    author_url: str = ib(default=None)
    image_url: str = ib(default=None)
    content: List[Union[str, NodeElement]] = ib(factory=list, converter=convert_content)
    views: int = ib(default=None)
    can_edit: bool = ib(default=None)

    @property
    def html_content(self) -> str:
        """
        Get content as HTML

        :raise: ValueError if content is not available
        :return:
        """
        if not self.content:
            raise ValueError('Content is not available!')

        from ..utils.html import node_to_html
        return node_to_html(self.content)
