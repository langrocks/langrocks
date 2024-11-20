import asyncio

from langrocks.client.anthropic import ComputerTool


async def main():
    computer = ComputerTool(url="localhost:50051")

    response = await computer(action="key", text="ctrl+l")
    response = await computer(action="type", text="https://www.google.com")
    response = await computer(action="key", text="Return")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
    loop.close()
