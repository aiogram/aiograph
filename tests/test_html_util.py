import pytest

from aiograph.types import NodeElement
from aiograph.utils import html

HTML = """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
nisi ut aliquip ex ea commodo consequat. 
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum 
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non 
proident, sunt in culpa qui officia deserunt mollit anim id est 
laborum.</p><img src="/file/6a5b15e7eb4d7329ca7af.jpg"/>
<li><ol>Foo</ol><ol>Bar</ol><ol>Baz</ol></li>
<a href="http://telegra.ph/">&lt;Telegra.ph&gt;</a>""".replace('\n', '')

NODES = [
    NodeElement(tag='p', children=[
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
        'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud '
        'exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. '
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu '
        'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in '
        'culpa qui officia deserunt mollit anim id est laborum.'
    ]),
    NodeElement(tag='img', attrs={
        'src': '/file/6a5b15e7eb4d7329ca7af.jpg'
    }, children=[]),
    NodeElement(tag='li', children=[
        NodeElement(tag='ol', children=['Foo']),
        NodeElement(tag='ol', children=['Bar']),
        NodeElement(tag='ol', children=['Baz'])]),
    NodeElement(tag='a', attrs={
        'href': 'http://telegra.ph/'
    }, children=[
        '<Telegra.ph>'
    ])
]

JSON = [
    {
        'tag': 'p',
        'children': [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
            'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis '
            'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. '
            'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore '
            'eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt '
            'in culpa qui officia deserunt mollit anim id est laborum.'
        ]},
    {
        'tag': 'img',
        'attrs': {
            'src': '/file/6a5b15e7eb4d7329ca7af.jpg'
        }
    },
    {
        'tag': 'li',
        'children': [
            {'tag': 'ol', 'children': ['Foo']},
            {'tag': 'ol', 'children': ['Bar']},
            {'tag': 'ol', 'children': ['Baz']}
        ]
    },
    {
        'tag': 'a',
        'attrs': {'href': 'http://telegra.ph/'},
        'children': [
            '<Telegra.ph>'
        ]
    }
]


def test_html_to_nodes():
    nodes = html.html_to_nodes(HTML)

    assert isinstance(nodes, list)
    for item in nodes:
        assert isinstance(item, NodeElement)

    assert nodes == NODES


def test_nodes_to_html():
    content = html.node_to_html(NODES)

    assert content == HTML

    with pytest.raises(TypeError):
        html.node_to_html(['test', 42])


def test_nodes_to_json():
    json = html.nodes_to_json(NODES)

    assert json == JSON


def test_html_to_json():
    content = html.html_to_json(HTML)

    assert content == JSON


def test_invalid_html():
    with pytest.raises(ValueError):
        html.html_to_nodes('<p><a href="#">test</p></a>')

    with pytest.raises(ValueError):
        html.html_to_nodes('<p>text')


def test_bad_tag():
    with pytest.raises(ValueError):
        html.html_to_nodes('<body></body>')


def test_entityref():
    nodes = html.html_to_nodes('&amp;')

    assert len(nodes) == 1
    assert nodes[0] == '&'

    content = html.node_to_html(nodes)
    assert content == '&amp;'


def test_charref():
    assert html.html_to_nodes('&#x3E;')[0] == '>'
