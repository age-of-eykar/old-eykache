from config import TomlConfig
from db import Database
from aiohttp import web
import asyncio
import server
import updater


async def main():
    # load the config
    config = TomlConfig("config/settings.toml", "config/settings.template.toml")
    if not config.configured:
        return

    app = web.Application(client_max_size=config["server"]["request_max_size"])
    database = Database(config)
    server.setup(app, config, database)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=config["server"]["port"]).start()
    await updater.start(database, config)
    await asyncio.Event().wait()


asyncio.run(main())