from datetime import datetime
from typing import Union, Optional
from bson import ObjectId

import models, schemas
from core.security import get_password, verify_password
from utils.redis import redis
from db import collections

from .base import CRUDBase


class CRUDUser(CRUDBase[models.User]):
    async def create(self, data: schemas.UserCreate, **kwargs) -> Union[int, list[int]]:
        user_in_DB = models.UserInDB(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=get_password(data.password),
            created_at=datetime.utcnow(),
            is_active=False,
            is_superuser=False
        )
        del data.password
        return await super().create(user_in_DB.dict(), **kwargs)

    async def read(self, **kwargs) -> Optional[models.User]:
        if kwargs.items():
            key, value = list(kwargs.items())[0]

            document = await self.collection.find_one({key: value})
            if document:
                _id = document.pop('_id')
                return self.read_model(public_id=str(_id), **document)
            return None

    async def read_by_id(self, public_id: str) -> Optional[models.User]:
        user = await self.collection.find_one({'_id': ObjectId(public_id)})
        if user:
            _id = user.pop('_id')
            return self.read_model(public_id=str(_id), **user)
        return None

    async def update(self, update_items: dict, public_id: str):
        if update_items.get('password'):
            hashed_password = get_password(update_items['password'])
            del update_items['password']
            update_items['hashed_password'] = hashed_password
        return await super().update(update_items, _id=ObjectId(public_id))

    async def delete_by_id(self, public_id: str):
        await redis.delete(f'{public_id}_counter')
        
        return await super().delete(_id=ObjectId(public_id))
    
    async def authenticate(self, email: str, password: str) -> Optional[models.User]:
        user = await self.read(email=email)
        if not user:
            return None
        elif not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(collections.user_coll, models.User)