AIOGraph
========

|shield-pypi| |shield-pypi-status| |shield-travis| |shield-codecov| |shield-license|

**aiograph** - asynchronous Python Telegra.ph API wrapper.

Annotations
-----------
The Telegraph class (``aiograph.Telegraph``) encapsulates all API calls in a single class.
It provides functions such as create_page, get_views and other's methods described at `Telegra.ph/api <http://telegra.ph/api>`_ page

All data types  stored In the package ``aiograph.types``.

All methods are named following the `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_ instructions
for example ``create_account`` for ``createAccount`` method and etc.
All API methods are awaitable and can be called only inside Event-loop.

Also if you want to upload the file to Telegra.ph service use ``upload`` method
from the instance of Telegraph class.

By the end of all actions you will need to close HTTP connections by calling the `close()` method (is awaitable).


Installation
------------

Using PIP
~~~~~~~~~
.. code-block:: bash

    $ pip install -U aiograph

From sources
~~~~~~~~~~~~
.. code-block:: bash

    $ git clone https://github.com/aiogram/aiograph.git
    $ cd aiograph
    $ python setup.py install


Usage examples
--------------

`Basics <https://github.com/aiogram/aiograph/blob/master/examples/basics.py>`_

.. code-block:: python3

   import asyncio

   from aiograph import Telegraph

   loop = asyncio.get_event_loop()
   telegraph = Telegraph()


   async def main():
       await telegraph.create_account('aiograph-demo')
       page = await telegraph.create_page('Demo', '<p><strong>Hello, world!</strong></p>')
       print('Created page:', page.url)


   if __name__ == '__main__':
       try:
           loop.run_until_complete(main())
       except (KeyboardInterrupt, SystemExit):
           pass
       finally:
           loop.run_until_complete(telegraph.close())  # Close the aiohttp.ClientSession


Links
-----

- News: `@aiogram_live <https://t.me/aiogram_live>`_
- Community: `@aiogram <https://t.me/aiogram>`_
- Russian community: `@aiogram_ru <https://t.me/aiogram_ru>`_
- Pip: `aiograph <https://pypi.org/project/aiograph>`_
- Source: `Github repo <https://github.com/aiogram/aiograph>`_
- Issues/Bug tracker: `Github issues tracker <https://github.com/aiogram/aiograph/issues>`_

.. |shield-pypi| image:: https://img.shields.io/pypi/v/aiograph.svg?style=flat-square
   :target: https://pypi.org/project/aiograph/
   :alt: PyPI

.. |shield-pypi-status| image:: https://img.shields.io/pypi/status/aiograph.svg?style=flat-square
   :target: https://pypi.org/project/aiograph/
   :alt: PyPi status

.. |shield-travis| image:: https://img.shields.io/travis/aiogram/aiograph.svg?branch=master&style=flat-square
   :target: https://travis-ci.org/aiogram/aiograph
   :alt: Travis-CI

.. |shield-codecov| image:: https://img.shields.io/codecov/c/github/aiogram/aiograph.svg?style=flat-square
   :target: https://codecov.io/gh/aiogram/aiograph
   :alt: Codecov

.. |shield-license| image:: https://img.shields.io/pypi/l/aiogram.svg?style=flat-square
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License
