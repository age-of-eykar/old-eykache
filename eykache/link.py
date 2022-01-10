import asyncio
import time
import os
from web3 import Web3

async def start(database, config):
    w3 = Web3(Web3.WebsocketProvider('wss://cronos-testnet-3.crypto.org:8546/'))
    print(w3.eth.blockNumber)

    """
    while True:
        cur = database.conn.cursor()
        cur.execute("SELECT * FROM colonies")
        res = cur.fetchall()
        print("results: ", res)
        await asyncio.sleep(config["updater"]["delay"])
        """
