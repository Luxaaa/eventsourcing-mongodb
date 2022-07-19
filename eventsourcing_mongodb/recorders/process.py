from typing import List, Sequence, Optional, Any

from eventsourcing.persistence import ProcessRecorder, StoredEvent, Tracking

from eventsourcing_mongodb.datastore import MongoDataStore
from eventsourcing_mongodb.recorders.application import MongoDBApplicationRecorder
from uuid import UUID
uuid = UUID('5f782575-d795-47f4-8c8f-e682242b688e')




class MongoDBProcessRecorder(MongoDBApplicationRecorder, ProcessRecorder):
    def __init__(self, datastore: MongoDataStore, events_collection_name: str = 'Events',
                 count_track_collection_name='EventCountTrackers', trackings_collection_name='Trackings'):
        super().__init__(datastore, events_collection_name=events_collection_name,
                         count_track_collection_name=count_track_collection_name)
        self.trackings_col_name = trackings_collection_name

    def max_tracking_id(self, application_name: str) -> int:
        collection = self.datastore.get_collection(self.trackings_col_name)
        query = {'application_name': application_name}
        docs = collection.find(query).sort('notification_id', -1).limit(1)
        return docs[0]['_id'] if docs else 0

    def has_tracking_id(self, application_name: str, notification_id: int) -> bool:
        collection = self.datastore.get_collection(self.trackings_col_name)
        query = {'application_name': application_name, 'notification_id': notification_id}
        return collection.count_documents(query) > 0

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> Optional[Sequence[int]]:
        ids = super().insert_events(stored_events)

        tracking: Optional[Tracking] = kwargs.get("tracking", None)
        if tracking:
            collection = self.datastore.get_collection(self.trackings_col_name)
            tracking_id = self._get_next_doc_id_and_update_counter(self.trackings_col_name, 1)
            collection.insert_one({
                '_id': tracking_id,
                'application_name': tracking.application_name,
                'notification_id': tracking.notification_id
            })
        return ids
