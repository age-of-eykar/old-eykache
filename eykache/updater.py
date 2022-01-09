import asyncio
import time
import os


async def start(database, config):
    while True:
        cur = database.conn.cursor()
        cur.execute("SELECT * FROM colonies")
        res = cur.fetchall()
        print("results: ", res)
        await asyncio.sleep(config["updater"]["delay"])
