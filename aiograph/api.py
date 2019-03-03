import asyncio
import os
import secrets
import ssl
from pathlib import Path
from typing import List, Optional, Union

import aiohttp
import certifi

from . import types
from .utils import exceptions, html

__all__ = ['Telegraph', 'Methods', 'SERVICE_URL']

SERVICE_URL = 'telegra.ph'
_PAYLOAD_EXCLUDE_LIST = ['self', 'cls']


# TODO: Allow to change default auth mode.

def _guess_filename(obj):
    """
    Get file name from object

    :param obj:
    :return:
    """
    name = getattr(obj, 'name', None)
    if name and isinstance(name, str) and name[0] != '<' and name[-1] != '>':
        return os.path.basename(name)


def _generate_payload(exclude=None, **kwargs):
    """
    Generate payload

    Usage: payload = generate_payload(**locals(), exclude=['foo'])

    :param exclude:
    :param kwargs:
    :return: dict
    """
    if exclude is None:
        exclude = []
    return {key: value for key, value in kwargs.items() if
            key not in exclude + _PAYLOAD_EXCLUDE_LIST
            and value is not None
            and not key.startswith('_')}


class Methods:
    """
    List of API methods
    """

    CREATE_ACCOUNT = 'createAccount'
    CREATE_PAGE = 'createPage'
    EDIT_ACCOUNT_INFO = 'editAccountInfo'
    EDIT_PAGE = 'editPage'
    GET_ACCOUNT_INFO = 'getAccountInfo'
    GET_PAGE = 'getPage'
    GET_PAGE_LIST = 'getPageList'
    GET_VIEWS = 'getViews'
    REVOKE_ACCESS_TOKEN = 'revokeAccessToken'


class Telegraph:
    def __init__(self,
                 token: Optional[str] = None,
                 service_url: str = SERVICE_URL,
                 connections_limit: Optional[int] = None,
                 proxy: Optional[str] = None, proxy_auth: Optional[aiohttp.BasicAuth] = None,
                 loop: asyncio.AbstractEventLoop = None,
                 json_serialize: callable = None, json_deserialize: callable = None):
        # Asyncio loop instance
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

        # JSON
        if not json_serialize or not json_deserialize:
            try:
                import ujson as json
            except ImportError:
                import json

            if json_serialize is None:
                json_serialize = json.dumps
            if json_deserialize is None:
                json_deserialize = json.loads
        self._json_serialize = json_serialize
        self._json_deserialize = json_deserialize

        # URL's
        self._service = None
        self._api_url = None
        self._service_url = None
        self.service = service_url

        # Proxy settings
        self.proxy = proxy
        self.proxy_auth = proxy_auth

        # aiohttp main session
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        if isinstance(proxy, str) and proxy.startswith('socks5://'):
            from aiosocksy.connector import ProxyClientRequest, ProxyConnector
            connector = ProxyConnector(limit=connections_limit, ssl_context=ssl_context, loop=self.loop)
            request_class = ProxyClientRequest
        else:
            connector = aiohttp.TCPConnector(limit=connections_limit, ssl=ssl_context,
                                             loop=self.loop)
            request_class = aiohttp.ClientRequest

        self.session = aiohttp.ClientSession(connector=connector, request_class=request_class,
                                             loop=self.loop, json_serialize=json_serialize)

        self._token = token

    @property
    def service(self) -> str:
        return self._service

    @service.setter
    def service(self, value: str):
        if '.' not in value or '://' in value:
            raise ValueError(f"Invalid service URL: {value}")

        value = value.rstrip('/')

        self._service = value
        self._service_url = f"http://{value}"
        self._api_url = f"https://api.{value}/"

    @property
    def api_url(self) -> str:
        return self._api_url

    @property
    def service_url(self) -> str:
        return self._service_url

    def format_api_url(self, method: str, path: Optional[str] = None) -> str:
        result = self.api_url + method
        if path:
            result += '/' + path
        return result

    def format_service_url(self, path):
        return self._service_url + path

    async def upload(self, *files, full=True) -> List[str]:
        to_be_closed = []
        form = aiohttp.FormData(quote_fields=False)
        try:
            for file in files:
                if isinstance(file, tuple):
                    if len(file) == 2:
                        filename, fileobj = file
                        content_type = None
                    elif len(file) == 3:
                        filename, fileobj, content_type = file
                    else:
                        raise ValueError('Tuple must have exactly 2 or 3 elements: filename, fileobj, content_type')
                elif isinstance(file, (str, Path)):
                    fileobj = open(file, 'rb')
                    to_be_closed.append(fileobj)
                    filename = os.path.basename(file)
                    content_type = None
                else:
                    fileobj = file
                    filename = _guess_filename(file)
                    content_type = None

                form.add_field(secrets.token_urlsafe(8), fileobj, filename=filename, content_type=content_type)

            async with self.session.post(self.format_service_url('/upload'), data=form) as response:
                result = await response.json(loads=self._json_deserialize)
        finally:
            for item in to_be_closed:
                item.close()

        if isinstance(result, dict) and 'error' in result:
            raise exceptions.NoFilesPassed()

        if full:
            return [self.format_service_url(item['src']) for item in result if 'src' in item]
        return [item['src'] for item in result if 'src' in item]

    async def request(self, method: str, *, path: Optional[str] = None, payload: Optional[dict] = None):
        url = self.format_api_url(method, path)
        async with self.session.post(url, data=payload) as response:
            json_data = await response.json(loads=self._json_deserialize)

            if not json_data.get('ok') and 'error' in json_data:
                error_text = json_data['error']
                raise exceptions.TelegraphError.detect(error_text)
        return json_data['result']

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token_or_account: Union[types.Account, str]):
        if isinstance(token_or_account, types.Account):
            if not token_or_account.access_token:
                raise TypeError('Invalid Account object. `access_token` is required!')
            self._token = token_or_account.access_token
        elif isinstance(token_or_account, str):
            self._token = token_or_account
        else:
            raise TypeError('value must be an \'str\' or \'Account\'')

    @token.deleter
    def token(self):
        self._token = None

    async def close(self):
        await self.session.close()

    def _mix_payload_token(self, payload: dict) -> dict:
        if self.token:
            payload.setdefault('access_token', self.token)

        return payload

    async def _mix_payload_author(self, payload: dict) -> dict:
        account = await self.get_account_info(
            types.AccountField.AUTHOR_NAME,
            types.AccountField.AUTHOR_URL
        )

        if account.author_name:
            payload.setdefault('author_name', account.author_name)
        if account.author_url:
            payload.setdefault('author_url', account.author_url)

        return payload

    def _prepare_content(self, content: Union[str, List[Union[str, types.NodeElement]]]) -> str:
        if content is None:
            raise exceptions.TelegraphError.detect('CONTENT_REQUIRED')
        if isinstance(content, list):
            content = html.nodes_to_json(content)
        elif isinstance(content, str):
            content = html.html_to_json(content)
        else:
            raise TypeError(f"Content must be instance of 'str' or 'List[Union[str, NodeElement]]' "
                            f"but '{type(content)}' found.")

        return self._json_serialize(content)

    async def create_account(self,
                             short_name: str,
                             author_name: str = None,
                             author_url: str = None,
                             auth: bool = True) -> types.Account:
        """
        Use this method to create a new Telegraph account.

        Most users only need one account, but this can be useful for channel administrators
        who would like to keep individual author names and profile links for each of their channels.

        On success, returns an Account object with the regular fields and an additional access_token field.

        Source: http://telegra.ph/api#createAccount

        :param short_name: (String, 1-32 characters) Required. Account name, helps users with several accounts
        remember which they are currently using. Displayed to the user above the "Edit/Publish" button on Telegra.ph,
        other users don't see this name.
        :param author_name: (String, 0-128 characters) Default author name used when creating new articles.
        :param author_url: (String, 0-512 characters) Default profile link, opened when users click
        on the author's name below the title. Can be any link, not necessarily to a Telegram profile or channel.
        :param auth: Save token and use in future requests
        :return: Account object
        """
        payload = _generate_payload(**locals())
        raw = await self.request(Methods.CREATE_ACCOUNT, payload=payload)
        account = types.Account(**raw)

        if auth:
            self.token = account.access_token

        return account

    async def edit_account_info(self,
                                access_token: Optional[str] = None,
                                short_name: Optional[str] = None,
                                author_name: Optional[str] = None,
                                author_url: Optional[str] = None) -> types.Account:
        """
        Use this method to update information about a Telegraph account.
        Pass only the parameters that you want to edit.

        On success, returns an Account object with the default fields.

        Source: http://telegra.ph/api#editAccountInfo

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param short_name: (String, 1-32 characters) New account name.
        :param author_name: (String, 0-128 characters) New default author name used when creating new articles.
        :param author_url: (String, 0-512 characters) New default profile link, opened when users
        click on the author's name below the title. Can be any link, not necessarily to a Telegram profile or channel.
        :return: Account object
        """
        payload = _generate_payload(**locals())
        self._mix_payload_token(payload)
        raw = await self.request(Methods.EDIT_ACCOUNT_INFO, payload=payload)

        return types.Account(**raw)

    async def get_account_info(self,
                               *_fields: Union[str, types.AccountField],
                               access_token: Optional[str] = None) -> types.Account:
        """
        Use this method to get information about a Telegraph account.

        Returns an Account object on success.

        Source: http://telegra.ph/api#getAccountInfo

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param _fields: (Array of String) - List of account fields to return.
        Available fields: short_name, author_name, author_url, auth_url, page_count.
        :return: Account object
        """
        fields = set()
        for field in _fields:
            if isinstance(field, types.AccountField):
                fields.add(field.name.lower())
            else:
                fields.add(field)

        if fields:
            fields = self._json_serialize(list(fields))

        payload = _generate_payload(**locals(), exclude=['field'])
        self._mix_payload_token(payload)

        raw = await self.request(Methods.GET_ACCOUNT_INFO, payload=payload)

        return types.Account(**(raw or {}))

    async def revoke_access_token(self, access_token: Optional[str] = None, auth=True) -> types.Account:
        """
        Use this method to revoke access_token and generate a new one, for example,
        if the user would like to reset all connected sessions, or you have reasons
        to believe the token was compromised.

        On success, returns an Account object with new access_token and auth_url fields.

        Source: http://telegra.ph/api#revokeAccessToken

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param auth: Save token and use in future requests
        :return: Account object
        """
        payload = _generate_payload(**locals())
        self._mix_payload_token(payload)
        raw = await self.request(Methods.REVOKE_ACCESS_TOKEN, payload=payload)
        account = types.Account(**raw)
        if auth:
            self.token = account

        return account

    async def create_page(self,
                          title: str,
                          content: Union[str, List[Union[str, types.NodeElement]]],
                          author_name: Optional[str] = None,
                          author_url: Optional[str] = None,
                          return_content: Optional[bool] = None,
                          access_token: Optional[str] = None,
                          as_user: bool = False) -> types.Page:
        """
        Use this method to create a new Telegraph page.

        On success, returns a Page object.

        Source: http://telegra.ph/api#createPage

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param title: (String, 1-256 characters) Required. Page title.
        :param author_name: (String, 0-128 characters) Author name, displayed below the article's title.
        :param author_url: (String, 0-512 characters) Profile link, opened when users click on the
        author's name below the title. Can be any link, not necessarily to a Telegram profile or channel.
        :param content: (Array of Node, up to 64 KB) Required. Content of the page.
        :param return_content: (Boolean, default = false) If true, a content field will be returned in the Page object
        :param as_user: Set author name and URL from current user.
        :return: Page object
        """
        content = self._prepare_content(content)
        payload = _generate_payload(**locals(), exclude=['as_user'])
        self._mix_payload_token(payload)
        if as_user:
            await self._mix_payload_author(payload)

        raw = await self.request(Methods.CREATE_PAGE, payload=payload)

        return types.Page(**raw)

    async def edit_page(self,
                        path: str,
                        title: str,
                        content: Union[str, List[Union[str, types.NodeElement]]],
                        author_name: Optional[str] = None,
                        author_url: Optional[str] = None,
                        return_content: Optional[bool] = None,
                        access_token: Optional[str] = None,
                        as_user: bool = False) -> types.Page:
        """
        Use this method to edit an existing Telegraph page.

        On success, returns a Page object.

        Source: http://telegra.ph/api#editPage

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param path: (String) Required. Path to the page.
        :param title: (String, 1-256 characters) Required. Page title.
        :param content: (Array of Node, up to 64 KB) Required. Content of the page.
        :param author_name: (String, 0-128 characters) Author name, displayed below the article's title.
        :param author_url: (String, 0-512 characters) Profile link, opened when users click on the author's
        name below the title. Can be any link, not necessarily to a Telegram profile or channel.
        :param return_content: (Boolean, default = false) If true, a content field will be returned in the Page object.
        :param as_user: Set author name and URL from current user.
        :return: Page object
        """
        content = self._prepare_content(content)
        payload = _generate_payload(**locals(), exclude=['path', 'as_user'])
        self._mix_payload_token(payload)
        if as_user:
            await self._mix_payload_author(payload)

        raw = await self.request(Methods.EDIT_PAGE, path=path, payload=payload)

        return types.Page(**raw)

    async def get_page(self, path: str, return_content: Optional[bool] = None) -> types.Page:
        """
        Use this method to get a Telegraph page.

        Returns a Page object on success.

        Source: http://telegra.ph/api#getPage
        :param path: (String) Required. Path to the Telegraph page.
        :param return_content: (Boolean, default = false) If true, content field will be returned in Page object.
        :return: Page object
        """
        payload = _generate_payload(**locals(), exclude=['path'])
        raw = await self.request(Methods.GET_PAGE, path=path, payload=payload)

        return types.Page(**raw)

    async def get_page_list(self,
                            offset: Optional[int] = None,
                            limit: Optional[int] = None,
                            access_token: Optional[str] = None) -> types.PageList:
        """
        Use this method to get a list of pages belonging to a Telegraph account.

        Returns a PageList object, sorted by most recently created pages first.

        Source: http://telegra.ph/api#getPageList

        :param access_token: (String) Required. Access token of the Telegraph account.
        :param offset: (Integer, default = 0) Sequential number of the first page to be returned.
        :param limit: (Integer, 0-200, default = 50) Limits the number of pages to be retrieved.
        :return: PageList object
        """
        payload = _generate_payload(**locals())
        self._mix_payload_token(payload)
        raw = await self.request(Methods.GET_PAGE_LIST, payload=payload)

        return types.PageList(**raw)

    async def get_views(self,
                        path: str,
                        year: Optional[int] = None,
                        month: Optional[int] = None,
                        day: Optional[int] = None,
                        hour: Optional[int] = None) -> int:
        """
        Use this method to get the number of views for a Telegraph article.

        Returns a PageViews object on success. By default, the total number of page views will be returned.

        Source: http://telegra.ph/api#getViews

        :param path: (String) Required. Path to the Telegraph page.
        :param year: (Integer, 2000-2100) Required if month is passed.
        If passed, the number of page views for the requested year will be returned.
        :param month: (Integer, 1-12) Required if day is passed.
        If passed, the number of page views for the requested month will be returned.
        :param day: (Integer, 1-31) Required if hour is passed.
        If passed, the number of page views for the requested day will be returned.
        :param hour: (Integer, 0-24) If passed, the number of page views for the requested hour will be returned.
        :return: Count of views
        """
        payload = _generate_payload(**locals())
        raw = await self.request(Methods.GET_VIEWS, payload=payload)

        return types.PageViews(**raw).views
