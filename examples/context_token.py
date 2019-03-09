import asyncio

from aiograph import Telegraph

telegraph = Telegraph('token')

print(f"1. Root: '{telegraph.token}'")
with telegraph.with_token('foo'):  # Will change token in current context
    print(f"2. Inside context manager: '{telegraph.token}'")

    with telegraph.with_token('bar'):  # Will change token in current context
        print(f"3. Inside child context manager: '{telegraph.token}'")
        telegraph.token = 'baz'  # Doesn't affect token inside current context
        print(f"4. After changing: '{telegraph.token}' (is not changed inside context manager)")

    print(f"5. Inside context manager: '{telegraph.token}'")

print(f"6. Root: '{telegraph.token}'")  # Shows changed token

asyncio.run(telegraph.close())
