from typing import List, Sequence, Dict, Optional, Any

from eventsourcing.persistence import ApplicationRecorder, Notification

from eventsourcing_mongodb.datastore import MongoDataStore
from eventsourcing_mongodb.recorders.aggregate import MongoDBAggregateRecorder


class MongoDBApplicationRecorder(MongoDBAggregateRecorder, ApplicationRecorder):
    def __init__(self, datastore: MongoDataStore, events_collection_name: str,
                 count_track_collection_name='EventCountTrackers'):
        super().__init__(datastore, events_collection_name, count_track_collection_name=count_track_collection_name)

    def select_notifications(
            self,
            start: int,
            limit: int,
            stop: Optional[int] = None,
            topics: Sequence[str] = (),
    ) -> List[Notification]:
        col = self.datastore.get_collection(self.events_col_name)
        cursor = col.find(self._build_select_notifications_query(start, stop=stop, topics=topics)).sort('position', 1)
        if limit:
            cursor.limit(limit)
        documents = list(cursor)
        notifications = self._documents_to_notifications(documents)
        return notifications

    def max_notification_id(self) -> int:
        collection = self.datastore.get_collection(self.count_track_col_name)
        count_doc = collection.find_one({'_id': self.events_col_name})
        return count_doc['counter'] if count_doc else 0

    @classmethod
    def _build_select_notifications_query(cls, start: int, stop: Optional[int] = None,
                                          topics: Sequence[str] = ()) -> dict:
        query = {'_id': {'$gte': start}}
        if stop:
            query['_id']['$lte'] = stop
        if topics:
            query['topic'] = {'$in': topics}
        return query

    @classmethod
    def _documents_to_notifications(cls, documents: List[Dict[str, Any]]) -> List[Notification]:
        return [Notification(
            id=doc['_id'],
            originator_id=doc['originator_id'],
            originator_version=doc['originator_version'],
            topic=doc['topic'],
            state=doc['state']
        ) for doc in documents]
