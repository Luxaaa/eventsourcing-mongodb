from eventsourcing.domain import Aggregate, event
from eventsourcing.application import Application
import os
from uuid import UUID


os.environ['PERSISTENCE_MODULE'] = 'eventsourcing_mongodb'
os.environ['MONGO_CONNECTION_STRING'] = 'mongodb://localhost'
os.environ['DOGSCHOOL_MONGO_DB_NAME'] = 'EventSourcing'

from eventsourcing_mongodb import Factory
from eventsourcing.utils import Environment

env = Environment(
    env={
        'MONGO_CONNECTION_STRING': 'mongodb://localhost',
        'MONGO_DB_NAME': 'EventSourcing'
    }
)


# factory = Factory(env)
# recorder = factory.aggregate_recorder(purpose='events')
# print(recorder.select_events(UUID('30e79507-4b5d-47d6-bac5-ce3c33b2ccf4')))


class Dog(Aggregate):
    @event('Registered')
    def __init__(self, name: str):
        self.name = name
        self.tricks = []

    @event('TrickAdded')
    def add_trick(self, trick: str):
        self.tricks.append(trick)


class DogSchool(Application):
    is_snapshotting_enabled = True
    snapshotting_intervals = {Dog: 1}

    def register_dog(self, name: str):
        dog = Dog(name)
        self.save(dog)
        return dog.id

    def add_trock(self, dog_id, trick: str):
        dog = self.repository.get(dog_id)
        dog.add_trick(trick)
        self.save(dog)

    def get_dog(self, dog_id):
        dog = self.repository.get(dog_id)
        return {'id': dog.id, 'name': dog.name, 'trocks': dog.tricks}


app = DogSchool()
d_id = app.register_dog('Töle')
app.add_trock(d_id, 'Ball fangen')
print(app.get_dog(d_id))
