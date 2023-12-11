from typing import List, Sequence, Dict, Optional, Any

from eventsourcing.persistence import ApplicationRecorder, Notification

from eventsourcing_mongodb.datastore import MongoDataStore
from eventsourcing_mongodb.recorders.aggregate import MongoDBAggregateRecorder


class MongoDBApplicationRecorder(MongoDBAggregateRecorder, ApplicationRecorder):
    def __init__(self, datastore: MongoDataStore, events_collection_name: str):
        super().__init__(datastore, events_collection_name)

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

    def max_notification_id(self):
        return 0

    @classmethod
    def _build_select_notifications_query(cls, start: int, stop: Optional[int] = None,
                                          topics: Sequence[str] = ()) -> dict:
        query = {'originator_version': {'$gte': start}}
        if stop:
            query['originator_version']['$lte'] = stop
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
