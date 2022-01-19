from typing import TypeVar, Generic, Union, Optional
from pydantic import BaseModel

ReadModelType = TypeVar('ReadModelType', bound=BaseModel)


class CRUDBase(Generic[ReadModelType]):
    def __init__(self, collection, read_model: ReadModelType):
        self.collection = collection
        self.read_model = read_model

    async def create(self, data: dict, **kwargs) -> Union[int, list[int]]:
        if not kwargs:
            result = await self.collection.insert_one(data)
            return result.inserted_id
        else:
            result = await self.collection.insert_many([data].append(list(kwargs.values())))
            return result.inserted_ids

    async def read(self, **kwargs) -> Optional[ReadModelType]:
        if kwargs.items():
            key, value = list(kwargs.items())[0]

            document = await self.collection.find_one({key: value})
            if document:
                return self.read_model(**document)
            return None

    async def read_multi(self, skip: int = 0, limit: int = 100) -> list[ReadModelType]:
        documents = []
        cursor = self.collection.find({})
        cursor.skip(skip).limit(limit)
        async for document in cursor:
            documents.append(self.read_model(**document))

        if documents:
            return documents
        return None

    async def update(self, update_items: dict, **kwargs):
        if kwargs.items():
            key, value = list(kwargs.items())[0]
            await self.collection.update_one(
                {key: value},
                {'$set': update_items}
            )

    async def delete(self, **kwargs):
        if kwargs.items():
            key, value = list(kwargs.items())[0]

        await self.collection.delete_one({key: value})