from typing import List

from attr import ib, s

from .base import TelegraphObject
from .converters import pages_converter
from .page import Page

__all__ = ['PageList']


@s
class PageList(TelegraphObject):
    """
    This object represents a list of Telegraph articles belonging to an account. Most recently created articles first.

    Source: http://telegra.ph/api#PageList
    """

    total_count: int = ib(default=None)
    pages: List[Page] = ib(factory=list, convert=pages_converter)
