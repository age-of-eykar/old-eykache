from aiohttp import web
import aiohttp_cors
import re


def setup(app, config, database):
    routes = Routes(config, database)
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    app.add_routes(
        [
            web.get("/colonies", routes.colonies),
            web.post("/colonies", routes.colonies),
        ]
    )
    for route in list(app.router.routes()):
        cors.add(route)


class Routes:
    def __init__(self, config, database):
        self.config = config
        self.database = database

    def start(self):
        web.run_app(self.app)

    async def colonies(self, request):
        """
        Allow to test the connection
            Test: curl http://localhost:8080/colonies

            Parameters:
                self (Routes): An instance of Routes
                request (aiohttp.web_request.Request): The web request
        """
        output = []
        try:
            data = await request.json()
            xmin, ymin, xmax, ymax = (
                int(data["xmin"]),
                int(data["ymin"]),
                int(data["xmax"]),
                int(data["ymax"]),
            )

            assert xmin < xmax
            assert ymin < ymax
            assert xmax - xmin < 2 ** 16
            assert ymax - ymin < 2 ** 16

            for pack in self.database.get_plots(xmin, ymin, xmax, ymax):
                colony_id, point_str = pack
                for point in re.findall("(-*[0-9]+ -*[0-9]+)", point_str):
                    x, y = point.split(" ")
                    output.append({"colony_id": colony_id, "x": int(x), "y": int(y)})
                    break
        except:
            pass

        return web.json_response(output)
