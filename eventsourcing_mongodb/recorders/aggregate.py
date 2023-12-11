from eventsourcing.persistence import AggregateRecorder, StoredEvent
from eventsourcing_mongodb.datastore import MongoDataStore
import pymongo
from uuid import UUID, uuid4
from typing import List, Optional, Sequence, Dict, Any


class MongoDBAggregateRecorder(AggregateRecorder):
    def __init__(self, datastore: MongoDataStore, events_collection_name: str):
        self.datastore = datastore
        self.events_col_name = events_collection_name

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> Optional[Sequence[Any]]:
        documents = self._stored_events_to_documents(stored_events)
        collection = self.datastore.get_collection(self.events_col_name)  # database collection
        # remove older snaoshots
        if self.events_col_name.endswith('Snapshots'):
            originator_ids = [doc['originator_id'] for doc in documents]
            collection.delete_many({'originator_id': {'$in': originator_ids}})
        collection.insert_many(documents)
        return [doc['_id'] for doc in documents]

    def select_events(
            self,
            originator_id: UUID,
            gt: Optional[int] = None,
            lte: Optional[int] = None,
            desc: bool = False,
            limit: Optional[int] = None,
    ) -> List[StoredEvent]:
        query = self._select_events_query(originator_id, gt, lte)
        collection = self.datastore.get_collection(self.events_col_name)
        cursor = collection.find(query)
        cursor = cursor.sort('originator_version', pymongo.DESCENDING if desc else pymongo.ASCENDING)
        if limit:
            cursor = cursor.limit(limit)
        documents = list(cursor)
        return self._documents_to_stored_events(documents)

    def _stored_events_to_documents(self, stored_events: List[StoredEvent]) -> List[Dict[str, Any]]:
        """ converts a list of stored events into dicts which can be inserted into mongodb. """
        return [{
            '_id': uuid4(),
            'originator_id': e.originator_id,
            'originator_version': e.originator_version,
            'topic': e.topic,
            'state': e.state
        } for idx, e in enumerate(stored_events)]

    @classmethod
    def _documents_to_stored_events(cls, documents: List[Dict[str, Any]]) -> List[StoredEvent]:
        return [StoredEvent(
            originator_id=doc['originator_id'],
            originator_version=doc['originator_version'],
            topic=doc['topic'],
            state=doc['state']
        ) for doc in documents]

    @classmethod
    def _select_events_query(cls, originator_id: UUID, gt: Optional[int] = None, lte: Optional[int] = None) -> dict:
        query = {'originator_id': {'$eq': originator_id}}
        if gt:
            query['originator_version'] = {'$gt': gt}
        if lte:
            if query.get('originator_version') is not None:
                query['originator_version']['$lte'] = lte
            else:
                query['originator_version'] = {'$lte': lte}
        return query
