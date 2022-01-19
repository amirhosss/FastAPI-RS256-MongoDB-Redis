import asyncio

from core.config import settings
from .database import db

user_coll = db['users']

#Delete inactive users
user_coll.create_index(
    'created_at',
    expireAfterSeconds=settings.USERS_EXPIRATION_TTL,
    partialFilterExpression={'is_active': False}
)