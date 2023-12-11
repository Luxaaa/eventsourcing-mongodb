from typing import List, Sequence, Optional, Any

from eventsourcing.persistence import ProcessRecorder, StoredEvent, Tracking

from eventsourcing_mongodb.datastore import MongoDataStore
from eventsourcing_mongodb.recorders.application import MongoDBApplicationRecorder
from uuid import UUID
uuid = UUID('5f782575-d795-47f4-8c8f-e682242b688e')




class MongoDBProcessRecorder(MongoDBApplicationRecorder, ProcessRecorder):
    def __init__(self, datastore: MongoDataStore, events_collection_name: str = 'Events',
                    trackings_collection_name='Trackings'):
        super().__init__(datastore, events_collection_name=events_collection_name)
        self.trackings_col_name = trackings_collection_name

    def max_tracking_id(self, application_name: str) -> int:
        raise NotImplemented

    def has_tracking_id(self, application_name: str, notification_id: int) -> bool:
        raise NotImplemented

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> Optional[Sequence[int]]:
        raise NotImplemented
