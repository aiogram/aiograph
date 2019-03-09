"""
Partial test of types.
Only features and untested functions will be tested here.
"""

import pytest

from aiograph import types


def test_node():
    with pytest.raises(ValueError):
        types.NodeElement(tag='table')

    node = types.NodeElement(tag='a')

    assert node.tag == 'a'
    assert isinstance(node.attrs, dict)
    assert isinstance(node.children, list)

    node['href'] = 'http://example.com'

    assert node['href'] == 'http://example.com'
    assert node.attrs['href'] == node['href']

    node.add('Text')
    assert len(node.children) == 1
    assert node.children[0] == 'Text'

    with pytest.raises(TypeError):
        node.add(42)

    assert node.as_html() == '<a href="http://example.com">Text</a>'

    del node['href']
    with pytest.raises(KeyError):
        href = node.attrs['href']


def test_page():
    page = types.Page(path='Test-path')

    assert isinstance(page.content, list)
    assert not page.content

    with pytest.raises(ValueError):
        content = page.html_content

    page = types.Page(path='Test-path', content=[{'tag': 'p', 'children': ['Test']}])

    assert len(page.content) == 1
    assert isinstance(page.content[0], types.NodeElement)


def test_path_parser():
    page = types.Page(path='Test-page-11-05')

    path = page.parsed_path
    assert isinstance(path, types.PagePath)
    assert path.title == 'Test page'
    assert path.name == 'Test-page'
    assert path.day == 5
    assert path.month == 11
    assert path.number is None

    assert page.parsed_path.stringify() == page.path

    page = types.Page(path='Bad-path')
    assert page.parsed_path is None

    assert types.PagePath('page', 5, 11, 42).stringify() == 'page-11-05-42'

    page = types.Page(path=None, content=None)
    assert page.parsed_path is None
    assert page.content is None
