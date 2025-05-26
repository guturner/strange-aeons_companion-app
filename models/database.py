class Database:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name