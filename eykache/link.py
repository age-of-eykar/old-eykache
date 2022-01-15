import time
import logging
import json
from . import utils
from web3 import Web3
from .scanner import DatabasedState, EventScanner, ChainFinished
from tqdm import tqdm
from web3.middleware import geth_poa_middleware  # only needed for PoA networks like BSC
from websockets import connect
import asyncio


async def start(database, config):
    web3 = Web3(Web3.WebsocketProvider(config["blockchain"]["node_wss"]))
    contract_content = open(utils.get_path("Eykar.json"), "r").read()
    logging.basicConfig(level=logging.INFO)
    web3.middleware_onion.clear()
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    abi = json.loads(contract_content)["abi"]
    Eykar = web3.eth.contract(abi=abi)

    # Restore/create our persistent state
    state = DatabasedState(database)
    state.restore()

    # chain_id: int, web3: Web3, abi: dict, state: EventScannerState, events: List, filters: {}, max_chunk_scan_size: int=10000
    scanner = EventScanner(
        web3=web3,
        contract=Eykar,
        state=state,
        events=[Eykar.events.PlotChange],
        filters={"address": config["blockchain"]["contract_address"]},
        max_request_retries=5,
        # How many maximum blocks at the time we request from JSON-RPC
        # and we are unlikely to exceed the response size limit of the JSON-RPC server
        request_retry_seconds=6.0,
        max_chunk_scan_size=10000,
    )

    # Assume we might have scanned the blocks all the way to the last Ethereum block
    # that mined a few seconds before the previous scan run ended.
    # Because there might have been a minor Etherueum chain reorganisations
    # since the last scan ended, we need to discard
    # the last few blocks from the previous scan results.
    chain_reorg_safety_blocks = 10
    scanner.delete_potentially_forked_block_data(
        state.get_last_scanned_block() - chain_reorg_safety_blocks
    )

    # Scan from [last block scanned] - [latest ethereum block]
    # Note that our chain reorg safety blocks cannot go negative
    start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, 0)
    end_block = scanner.get_suggested_scan_end_block()
    blocks_to_scan = end_block - start_block

    print(f"Scanning events from blocks {start_block} - {end_block}")

    # Render a progress bar in the console
    start = time.time()
    with tqdm(total=blocks_to_scan) as progress_bar:

        def _update_progress(
            start, end, current, current_block_timestamp, chunk_size, events_count
        ):
            if current_block_timestamp:
                formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
            else:
                formatted_time = "no block time available"
            progress_bar.set_description(
                f"Block: {current} ({formatted_time}), Batch size: {chunk_size}, Processed/batch: {events_count}"
            )
            progress_bar.update(chunk_size)

        # handle old events
        try:
            await scanner.scan(
                start_block, end_block, progress_callback=_update_progress
            )
        except ChainFinished:
            pass

    state.save()
    duration = time.time() - start
    print(f"Scan last {duration} seconds")

    # listen to new events
    while True:
        await get_event(config, state)
        await asyncio.sleep(0)


async def get_event(config, state):
    async with connect(config["blockchain"]["node_wss"]) as ws:
        await ws.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        "logs",
                        {
                            "address": [config["blockchain"]["contract_address"]],
                        },
                    ],
                }
            )
        )
        await ws.recv()
        while True:
            try:
                message = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                log = message["params"]["result"]
                location = log["topics"][1]
                x = int.from_bytes(bytes.fromhex(location[2:18]), "big", signed=True)
                y = int.from_bytes(bytes.fromhex(location[18:]), "big", signed=True)
                colony_id = int.from_bytes(
                    bytes.fromhex(log["data"][2:66]), "big", signed=False
                )
                event = (
                    log["logIndex"],
                    log["transactionHash"],
                    log["blockNumber"],
                    {"location": (x, y), "colony_id": colony_id},
                )
                state.process_event(event)
                pass
            except Exception:
                pass
