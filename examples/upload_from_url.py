import asyncio

from aiograph import Telegraph

loop = asyncio.get_event_loop()
telegraph = Telegraph()


async def main():
    telegraph_url = await telegraph.upload_from_url('https://www.python.org/static/img/python-logo.png')
    print('Uploaded:', telegraph_url)


if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        loop.run_until_complete(telegraph.close())  # Close the aiohttp.ClientSession
