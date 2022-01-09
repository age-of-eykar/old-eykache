from aiohttp import web


def setup(app, config, database):
    routes = Routes(config, database)
    app.add_routes(
        [
            web.get("/colonies", routes.colonies),
        ]
    )


class Routes:
    def __init__(self, config, database):
        self.config = config
        self.database = database

    def start(self):
        web.run_app(self.app)

    async def colonies(self, request):
        print(type(request))
        """
        Allow to test the connection
            Test: curl http://localhost:8080/colonies
        
            Parameters:
                self (Routes): An instance of Routes
                request (aiohttp.web_request.Request): The web request
        """
        return web.Response(body="It seems to be working...")