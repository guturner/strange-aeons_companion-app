from pymongo import MongoClient
from typing import Mapping, Any


class DAO:
    def __init__(self, database):
        self.__client = MongoClient(database.uri)
        self._db = self.__client[database.db_name]

    def count_documents(self, collection, query: Mapping[str, Any]):
        return self._db[collection].count_documents(query)