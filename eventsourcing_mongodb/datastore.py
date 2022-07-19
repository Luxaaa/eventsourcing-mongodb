from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection


class MongoDataStore:
    def __init__(self, connection_string: str, database_name: str):
        self._con_str = connection_string
        self._db_name = database_name
        self._create_client()

    def _create_client(self):
        self._client = MongoClient(self._con_str, uuidRepresentation='standard')

    def get_collection(self, collection_name: str) -> Collection:
        database: Database = self._client[self._db_name]
        return database[collection_name]
