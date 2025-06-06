from pymongo import MongoClient


class DAO:
    def __init__(self, database):
        self.__client = MongoClient(database.uri)
        self._db = self.__client[database.db_name]