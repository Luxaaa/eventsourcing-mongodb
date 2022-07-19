from unittest import TestCase
import mongomock
from eventsourcing_mongodb.datastore import MongoDataStore


@mongomock.patch(servers=(('mydb.com', 27017),))
class TestAggregateRecorder(TestCase):
    def setUp(self) -> None:
        self.datastore = MongoDataStore('mongodb://mydb.com', 'Test')
