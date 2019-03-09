from pathlib import Path

import aiohttp
import pytest
import conftest
from aiograph import Telegraph, types
from aiograph.api import SERVICE_URL
from aiograph.utils import exceptions

IMAGE_PATH = Path(__file__).parent / 'telegraph.jpg'
IMAGE_URL = 'https://www.python.org/static/img/python-logo.png'

SHORT_NAME = 'aiograph_test'
AUTHOR_NAME = 'AIOGraph Wrapper'
AUTHOR_URL = 'https://t.me/aiogram_live'

content = '<p>Page created by <a href="https://github.com/aiogram/aiograph" target="_blank">AIOGraph</a></p>' \
          '<img src="{image}"/>' \
          '<h4 id="Lorem-ipsum">Lorem ipsum</h4>' \
          '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ' \
          'ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ' \
          'laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in vol ' \
          'uptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non ' \
          'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p> ' \
          '<p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, ' \
          'totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae ' \
          'dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, ' \
          'sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam ' \
          'est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius ' \
          'modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, ' \
          'quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi ' \
          'consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil ' \
          'molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?</p> ' \
          '<p><h4 id="FooBar">FooBar</h4><ul><li>Foo</li><li>Bar</li><li>Baz</li></ul></p>'


def test_service_url(telegraph: Telegraph):
    assert telegraph.service == SERVICE_URL
    assert telegraph.service_url == f"https://{SERVICE_URL}"
    assert telegraph.api_url == f"https://api.{SERVICE_URL}/"


@pytest.mark.asyncio
async def test_create_account(telegraph: Telegraph):
    account = await telegraph.create_account(SHORT_NAME, AUTHOR_NAME)
    assert account.access_token
    assert account.short_name == SHORT_NAME
    assert account.author_name == AUTHOR_NAME
    assert account.author_url == ''

    conftest.access_token = account.access_token

    assert telegraph.token == account.access_token


def test_access_token(telegraph: Telegraph):
    assert telegraph.token == conftest.access_token


@pytest.mark.asyncio
async def test_get_account_info(telegraph: Telegraph):
    account = await telegraph.get_account_info()
    assert account.short_name == SHORT_NAME
    assert account.author_name == AUTHOR_NAME

    account = await telegraph.get_account_info(types.AccountField.SHORT_NAME)
    assert account.short_name == SHORT_NAME
    assert account.author_name is None

    account = await telegraph.get_account_info('author_name', types.AccountField.PAGE_COUNT)
    assert account.short_name is None
    assert account.author_name == AUTHOR_NAME
    assert account.page_count == 0


@pytest.mark.asyncio
async def test_edit_account_info(telegraph: Telegraph):
    old_account = await telegraph.get_account_info()

    account = await telegraph.edit_account_info(
        author_name=f"{AUTHOR_NAME} [test]",
        author_url=AUTHOR_URL
    )

    assert account.short_name == old_account.short_name
    assert account.author_name == f"{AUTHOR_NAME} [test]"
    assert account.author_url == AUTHOR_URL


@pytest.mark.asyncio
async def test_revoke_access_token(telegraph: Telegraph):
    account = await telegraph.revoke_access_token()

    assert account.access_token != conftest.access_token
    assert account.access_token == telegraph.token

    conftest.access_token = account.access_token


@pytest.mark.asyncio
async def test_upload(telegraph: Telegraph):
    photos = await telegraph.upload(IMAGE_PATH)

    assert photos
    assert isinstance(photos, list)
    assert len(photos) == 1

    photo = photos[0]
    assert isinstance(photo, str)
    assert telegraph.service in photo

    photos = await telegraph.upload(IMAGE_PATH, full=False)
    assert telegraph.service not in photos[0]

    with open(IMAGE_PATH, 'rb') as file:
        photos = await telegraph.upload(file)
        assert len(photos) == 1

    with open(IMAGE_PATH, 'rb') as file:
        photos = await telegraph.upload(('image.jpg', file))
        assert len(photos) == 1

    with open(IMAGE_PATH, 'rb') as file:
        photos = await telegraph.upload(('image.jpg', file, 'image/jpeg'))
        assert len(photos) == 1

    with open(IMAGE_PATH, 'rb') as file:
        with pytest.raises(ValueError):
            await telegraph.upload((file,))

    with pytest.raises(exceptions.NoFilesPassed):
        await telegraph.upload()


@pytest.mark.asyncio
async def test_upload_from_url(telegraph: Telegraph):
    photo = await telegraph.upload_from_url(IMAGE_URL)

    assert photo
    assert isinstance(photo, str)
    assert telegraph.service in photo

    photo = await telegraph.upload_from_url(IMAGE_URL, full=False)
    assert telegraph.service not in photo

    with pytest.raises(exceptions.NoFilesPassed):
        await telegraph.upload_from_url("http://example.com/")


@pytest.mark.asyncio
async def test_create_page(telegraph: Telegraph):
    photo = (await telegraph.upload(IMAGE_PATH, full=False))[0]
    page_content = content.format(image=photo)

    page = await telegraph.create_page('Test page', page_content, return_content=True, as_user=True)

    assert page.title == 'Test page'
    assert page.path.startswith('Test-page')
    assert page.content
    assert page.author_name
    assert page.author_name == (await telegraph.get_account_info('author_name')).author_name

    assert isinstance(page.content, list)
    assert len(page.content)
    assert page.content[0].tag == 'p'
    assert page.html_content == page_content


@pytest.mark.asyncio
async def test_edit_page(telegraph: Telegraph):
    original_page = await telegraph.create_page('Test page 2', [types.NodeElement('p', children=['Test page'])],
                                                return_content=True)

    page = await telegraph.edit_page(original_page.path, 'New page title', 'content', return_content=True, as_user=True)

    assert page.path == original_page.path
    assert page.title != original_page.title
    assert page.author_name != original_page.author_name
    assert page.content != original_page.content
    assert page.html_content == 'content'


@pytest.mark.asyncio
async def test_get_page_list(telegraph: Telegraph):
    pages = await telegraph.get_page_list()

    assert isinstance(pages, types.PageList)
    assert isinstance(pages.total_count, int)
    assert pages.total_count > 0
    assert len(pages.pages) == pages.total_count
    assert all(isinstance(page, types.Page) for page in pages.pages)


@pytest.mark.asyncio
async def test_get_page(telegraph: Telegraph):
    pages = await telegraph.get_page_list(limit=1)

    page = await telegraph.get_page(pages.pages[0].path)

    assert isinstance(page, types.Page)
    assert page.path == pages.pages[0].path


@pytest.mark.asyncio
async def test_get_views(telegraph: Telegraph):
    page = (await telegraph.get_page_list(limit=1)).pages[0]

    async with aiohttp.ClientSession() as sess:
        async with sess.get(page.url) as resp:
            await resp.text()

    views = await telegraph.get_views(page.path)

    assert isinstance(views, int)
    assert views > page.views


@pytest.mark.asyncio
async def test_detect_exception(telegraph: Telegraph):
    with pytest.raises(exceptions.PageNotFound, match='Page not found!'):
        await telegraph.get_page('random-path')
