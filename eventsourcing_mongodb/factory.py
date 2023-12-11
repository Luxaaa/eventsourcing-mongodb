from eventsourcing.persistence import InfrastructureFactory, AggregateRecorder, ApplicationRecorder, ProcessRecorder
from eventsourcing.utils import Environment
from eventsourcing_mongodb.datastore import MongoDataStore
from eventsourcing_mongodb.recorders import MongoDBAggregateRecorder, MongoDBApplicationRecorder, MongoDBProcessRecorder


class Factory(InfrastructureFactory):
    MONGO_CONNECTION_STRING = 'MONGO_CONNECTION_STRING'
    MONGO_DB_NAME = 'MONGO_DB_NAME'
    MONGO_COL_PREFIX = 'MONGO_COL_PREFIX'

    def __init__(self, env: Environment):
        super().__init__(env)
        conn_str = self.env.get(self.MONGO_CONNECTION_STRING)
        if not conn_str:
            keys = self.env.create_keys(self.MONGO_CONNECTION_STRING)
            raise EnvironmentError(f'MongoDB connection string not found in environment with keys: {", ".join(keys)}')
        db_name = self.env.get(self.MONGO_DB_NAME)
        if not db_name:
            keys = self.env.create_keys(self.MONGO_DB_NAME)
            raise EnvironmentError(f'MongoDB database name not found in environment with keys: {", ".join(keys)}')

        self.datastore = MongoDataStore(conn_str, db_name)

    def aggregate_recorder(self, purpose: str = "events") -> AggregateRecorder:
        recorder = MongoDBAggregateRecorder(self.datastore, self._events_collection_name(purpose))
        return recorder

    def application_recorder(self) -> ApplicationRecorder:
        recorder = MongoDBApplicationRecorder(self.datastore, self._events_collection_name('events'))
        return recorder

    def process_recorder(self) -> ProcessRecorder:
        recorder = MongoDBProcessRecorder(self.datastore, self._events_collection_name('events'),
                                          trackings_collection_name=self._trackings_collection_name()
                                          )
        return recorder

    def _events_collection_name(self, purpose: str):
        return self.env.get(self.MONGO_COL_PREFIX, '') + purpose.capitalize()

    def _trackings_collection_name(self):
        return self.env.get(self.MONGO_COL_PREFIX, 'Trackings')
