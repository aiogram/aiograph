import asyncio

from aiograph import Telegraph

telegraph = Telegraph()

HTML = """
        <figure>
            <img src='{image}' alt='missing' />
            <figcaption>{caption}</figcaption>
        </figure>
    """


async def main():
    await telegraph.create_account("aiograph-demo")

    image = await telegraph.upload_from_url("https://www.python.org/static/community_logos/python-logo-master-v3-TM.png")

    page = await telegraph.create_page("Demo", HTML.format(image=image, caption="Python!"))

    print("Created page:", page.url)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(telegraph.close())
