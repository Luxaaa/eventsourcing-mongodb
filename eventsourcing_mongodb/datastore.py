import pymongo
from pymongo.database import Database
from pymongo.collection import Collection

_mongo_client = None

class MongoDataStore:
    def __init__(self, connection_string: str, database_name: str, check_connection=False):
        self._con_str = str(connection_string).strip()
        self._db_name = str(database_name).strip()
        self._validate_args()
        self._create_client(check_connection=check_connection)

    def _validate_args(self):
        if not self._con_str:
            raise ValueError('Connection string was not provided or is empty')
        if not self._db_name:
            raise ValueError('Database name was not provided or is empty')


    def _create_client(self, check_connection=False):
        global _mongo_client
        if _mongo_client:
            self._client = _mongo_client
            return
        self._client = pymongo.MongoClient(
            self._con_str,
            serverSelectionTimeoutMS=5_000,
            uuidRepresentation='standard'  # Support UUID types in documents
        )

        _mongo_client = self._client

        if check_connection:
            self._client.server_info()

    def get_collection(self, collection_name: str) -> Collection:
        database: Database = self._client[self._db_name]
        return database[collection_name]
