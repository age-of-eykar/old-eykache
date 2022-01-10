#import psycopg2


class Database:
    def __init__(self, config) -> None:
        self.config = config
        """
        self.conn = psycopg2.connect(
            database=config["database"]["database"],
            user=config["database"]["user"],
            password=config["database"]["password"],
            host=config["database"]["host"],
            port=config["database"]["port"],
        )
        """

    def close(self):
        self.conn.close()
