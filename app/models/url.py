from peewee import CharField, ForeignKeyField, BooleanField, DateTimeField
from app.database import BaseModel
from app.models.user import User

class Url(BaseModel):
    user = ForeignKeyField(User, backref='urls', null=True)
    short_code = CharField(unique=True, max_length=20)
    original_url = CharField(max_length=2048)
    title = CharField(max_length=255, null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)