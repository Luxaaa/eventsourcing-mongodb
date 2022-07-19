from unittest import TestCase
import unittest.mock as mock
import mongomock
from eventsourcing_mongodb.datastore import MongoDataStore
import pymongo


@mongomock.patch(servers=(('mydb.com', 27017),))
class TestDataStore(TestCase):
    def test_init(self):
        datastore = MongoDataStore('mongodb://mydb.com', 'Test', check_connection=True)
        self.assertIsInstance(datastore, MongoDataStore)
        datastore = MongoDataStore('mongodb://mydb.com', 42)
        self.assertIsInstance(datastore, MongoDataStore)

        with self.assertRaises(ValueError):
            MongoDataStore(None, None)
        with self.assertRaises(ValueError):
            MongoDataStore('', '')
        with self.assertRaises(ValueError):
            MongoDataStore('mongodb://mydb.com', '')
        with self.assertRaises(ValueError):
            MongoDataStore('mongodb://mydb.com', '    ')
        with self.assertRaises(Exception):
            MongoDataStore('mongodb://nonexistingdb.com', 'Test')
        with self.assertRaises(Exception):
            MongoDataStore('adsfi9ajsdfj', 'Test')

    def test_get_collection(self):
        datastore = MongoDataStore('mongodb://mydb.com', 'Test')
        col = datastore.get_collection('TestCollection')
        self.assertEqual(col.database.name, 'Test')
        self.assertEqual(col.name, 'TestCollection')
