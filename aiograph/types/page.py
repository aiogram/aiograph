import re
from typing import List, Optional, Union

from attr import ib, s

from .base import TelegraphObject
from .converters import convert_content
from .node import NodeElement

__all__ = ['Page', 'PagePath']

PATH_PATTERN = re.compile('^(?P<name>\S+)-(?P<month>\d{2})-(?P<day>\d{2})(?:-(?P<number>\d))?$', re.I)


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

    def _parse_path(self):
        if not self.path:
            return

        match = PATH_PATTERN.match(self.path)
        if match:
            return match.groupdict()

    @property
    def parsed_path(self):
        path = self._parse_path()
        if path is not None:
            return PagePath(**path)


def _int_converter(number):
    if number is not None:
        return int(number)


@s
class PagePath:
    name: str = ib()
    day: int = ib(converter=_int_converter)
    month: int = ib(converter=_int_converter)
    number: Optional[int] = ib(default=0, converter=_int_converter)

    @property
    def title(self):
        return self.name.replace('-', ' ')

    def stringify(self):
        result = '-'.join(self.name.strip().split())
        result += f"-{self.month:02}-{self.day:02}"
        if self.number is not None:
            result += f"-{self.number}"
        return result
