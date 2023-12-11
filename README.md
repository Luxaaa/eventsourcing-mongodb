# Event Sourcing in Python with MongoDB
This is an extension package for the Python
[eventsourcing](https://github.com/pyeventsourcing/eventsourcing) library
that provides a persistence module for [MongoDB](https://www.mongodb.com/).

## Installation
Use pip to install the [stable distribution](https://pypi.org/project/eventsourcing_mongodb/)
from the Python Package Index. Please note, it is recommended to
install Python packages into a Python virtual environment.

    $ pip install eventsourcing-mongodb

## Getting started
Define Aggregates and Applications the usual way. Please refer to the [Eventsourcing Documentation](https://eventsourcing.readthedocs.io/en/stable/) for more detailed examples.
```python
from eventsourcing.domain import Aggregate, event
from eventsourcing.application import Application
from uuid import UUID

class Dog(Aggregate):
    @event('Registered')
    def __init__(self, name: str):
        self.name = name
        self.tricks = []

    @event('TrickAdded')
    def add_trick(self, trick: str):
        self.tricks.append(trick)
    
class DogSchool(Application):
    def register_dog(self, name: str) -> UUID:
        dog = Dog(name)
        self.save(dog)
        return dog.id

    def add_trick(self, dog_id: UUID, trick: str):
        dog = self.repository.get(dog_id)
        dog.add_trick(trick)
        self.save(dog)

    def get_dog(self, dog_id: UUID) -> dict:
        dog = self.repository.get(dog_id)
        return {'id': dog.id, 'name': dog.name, 'tricks': dog.tricks}
```

To configure your Application for using MongoDB for persistence, you need to set the environment variable `PERSISTENCE_MODULE`
to `'eventsourcing_mongodb'`.
Furthermore, you need to set the environment variables `MONGO_CONNECTION_STRING` and `MONGO_DB_NAME`. 
Please refer to the [MongoDB Documentation](https://www.mongodb.com/docs/manual/reference/connection-string/)
to learn more about connection strings. You can read more about the available variables [here](#available-environment-variables) .

```python
import os
os.environ['PERSISTENCE_MODULE'] = 'eventsourcing_mongodb'
os.environ['MONGO_CONNECTION_STRING'] = 'mongodb://localhost'
os.environ['MONGO_DB_NAME'] = 'EventSourcing'
```
Instead of setting the variables on environment level, you can also set them on application level.
```python
class DogSchool(Application):
    env = {
        'PERSISTENCE_MODULE': 'eventsourcing_mongodb',
        'MONGO_CONNECTION_STRING': 'mongodb://localhost',
        'MONGO_DB_NAME': 'EventSourcing',
        ...
    }
    ...
```

Construct and use the application in the usual way.
```python
dog_school = DogSchool()
dog_id = dog_school.register_dog('Fido')
dog_school.add_trick(dog_id, 'roll over')
dog = dog_school.get_dog(dog_id)
print(dog) # {'id': UUID('...'), 'name': 'Fido', 'tricks': ['roll over']}
```
And retrieve the data later:
```python
dog_school = DogSchool()
dog_id = UUID('...')
dog = dog_school.get_dog(dog_id)
print(dog) # {'id': UUID('...'), 'name': 'Fido', 'tricks': ['roll over']}

```

## Available Environment Variables
You can use the following variables to configure mongodb persistence:

| Variable | Type / Possible values | Required | Description |
| --- | --- | --- | --- |
| `PERSISTENCE_MODULE` | `'eventsourcing_mongodb'` | `true` | configures the application to use this module for persistence. 
| `MONGO_CONNECTION_STRING` | string | `true` | MongoDB Connection String. Please refer to the [MongoDB Documentation](https://www.mongodb.com/docs/manual/reference/connection-string/) to learn more about connection strings.
| `MONGO_DB_NAME` | string | `true` | Name of the Database the data sould be stored in
| `MONGO_COL_PREFIX` | string | `false` | Prefix for the MongoDB Collections for events, snapshots and trackings. The default is an empty String.



