from attr import ib, s

from .base import TelegraphObject

__all__ = ['PageViews']


@s
class PageViews(TelegraphObject):
    """
    This object represents the number of page views for a Telegraph article.

    Source: http://telegra.ph/api#PageViews
    """
    views: int = ib()
