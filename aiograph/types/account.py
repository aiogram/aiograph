import enum

from attr import ib, s

from .base import TelegraphObject

__all__ = ['Account', 'AccountField']


@s
class Account(TelegraphObject):
    """
    This object represents a Telegraph account.

    Source: http://telegra.ph/api#Account
    """

    short_name: str = ib(default=None)
    author_name: str = ib(default=None)
    author_url: str = ib(default=None)
    access_token: str = ib(default=None)
    auth_url: str = ib(default=None)
    page_count: int = ib(default=None)


class AccountField(enum.Enum):
    """
    Helper for account fields
    """

    SHORT_NAME = enum.auto()
    AUTHOR_NAME = enum.auto()
    AUTHOR_URL = enum.auto()
    AUTH_URL = enum.auto()
    PAGE_COUNT = enum.auto()
