import asyncio

from pathlib import Path

from aiograph import Telegraph

loop = asyncio.get_event_loop()
telegraph = Telegraph()

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

IMAGE_PATH = Path(__file__).parent.parent / 'tests' / 'telegraph.jpg'


async def main():
    await telegraph.create_account('aiograph-demo')

    photo = (await telegraph.upload(IMAGE_PATH, full=False))[0]
    page_content = content.format(image=photo)
    page = await telegraph.create_page('Demo', page_content)
    print('Created page:', page.url)


if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        loop.run_until_complete(telegraph.close())  # Close the aiohttp.ClientSession
