import asyncio


async def run():
    print("QQ Bot is starting... (Placeholder)")
    # Add QQ bot logic here
    while True:
        await asyncio.sleep(1)


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("QQ Bot shutting down.")


if __name__ == "__main__":
    main()
