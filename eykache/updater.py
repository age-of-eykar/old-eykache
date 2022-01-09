
import asyncio
import time
import os


async def start(database, config):
    while True:
        print("Updating...")
        await asyncio.sleep(config["updater"]["delay"])
