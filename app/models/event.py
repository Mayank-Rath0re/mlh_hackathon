from peewee import CharField, ForeignKeyField, DateTimeField, TextField
from app.database import BaseModel
from app.models.user import User
from app.models.url import Url

class Event(BaseModel):
    url = ForeignKeyField(Url, backref='events')
    user = ForeignKeyField(User, backref='events', null=True)
    event_type = CharField() # e.g., "created", "clicked"
    timestamp = DateTimeField()
    details = TextField(null=True) # Storing the JSON as a text string