import asyncio


async def function_asyc():
    i = 0

    while True:
        i += 1
        if i % 50000 == 0:
            print("Hello, I'm Abhishek")
            print("GFG is Great")
            await asyncio.sleep(2)


async def function_2():
    while True:
        await asyncio.sleep(1)
        print("\n HELLO WORLD \n")


loop = asyncio.get_event_loop()
asyncio.ensure_future(function_asyc())
asyncio.ensure_future(function_2())
loop.run_forever()
