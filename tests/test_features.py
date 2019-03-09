import pytest
from aiohttp import BasicAuth
from aiohttp_socks import SocksConnector, SocksVer

from aiograph import Telegraph, types
from aiograph.utils import exceptions


def test_prepare_content():
    telegraph = Telegraph()
    with pytest.raises(exceptions.ContentRequired):
        telegraph._prepare_content(None)
    with pytest.raises(TypeError):
        telegraph._prepare_content(42)

    content = telegraph._prepare_content('content')
    assert isinstance(content, str)

    content = telegraph._prepare_content(['content'])
    assert isinstance(content, str)


def test_token_property(telegraph: Telegraph):
    telegraph.token = 'abcdef01234567890'
    assert telegraph.token == 'abcdef01234567890'

    with pytest.raises(TypeError):
        telegraph.token = 42

    account = types.Account(short_name='test', author_name='Test',
                            access_token='abcdef01234567890')
    telegraph.token = account
    assert telegraph.token == account.access_token

    with pytest.raises(TypeError):
        account = types.Account(short_name='test', author_name='Test')
        telegraph.token = account

    del telegraph.token

    assert telegraph.token is None


def test_service(telegraph):
    assert telegraph.service == 'telegra.ph'
    assert telegraph.api_url == f"https://api.{telegraph.service}/"
    assert telegraph.service_url == f"https://{telegraph.service}"

    with pytest.raises(ValueError):
        telegraph.service = telegraph.service_url

    telegraph.service = 'example.com'


def test_exceptions_detection():
    with pytest.raises(exceptions.TelegraphError, match='UNKNOWN') as exc_info:
        exceptions.TelegraphError.detect('UNKNOWN')

    assert type(exc_info.value) is exceptions.TelegraphError

    with pytest.raises(exceptions.UnknownMethod) as exc_info:
        exceptions.UnknownMethod.detect('UNKNOWN_METHOD')

    assert type(exc_info.value) is exceptions.UnknownMethod


class CustomException(exceptions.TelegraphError, match='CUSTOM'):
    text = 'My custom error'


def test_custom_error():
    with pytest.raises(CustomException, match='My custom error'):
        exceptions.TelegraphError.detect('CUSTOM')


def test_context_token(telegraph: Telegraph):
    original_token = telegraph.token

    with telegraph.with_token('foo'):
        assert telegraph.token == 'foo'

        with telegraph.with_token('bar'):
            assert telegraph.token == 'bar'
            telegraph.token = 'baz'
            assert telegraph.token == 'bar'

        assert telegraph.token == 'foo'

    assert telegraph.token != original_token
    assert telegraph.token == 'baz'


def test_socks5_proxy():
    telegraph = Telegraph(proxy='socks5://example.com:1050', proxy_auth=BasicAuth('username', 'password'))
    connector = telegraph.session._connector

    assert isinstance(connector, SocksConnector)
    assert connector._socks_ver == SocksVer.SOCKS5
    assert connector._socks_host == 'example.com'
    assert connector._socks_port == 1050
    assert connector._socks_username == 'username'
    assert connector._socks_password == 'password'
