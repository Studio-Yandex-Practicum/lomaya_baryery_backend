from uuid import UUID

from fastapi import Depends

from src.api.request_models.photo import PhotoCreateRequest, PhotoUpdateRequest
from src.core.db.models import Photo
from src.core.db.repository import PhotoRepository


class PhotoService:
    def __init__(self, photo_repository: PhotoRepository = Depends()) -> None:
        self.__photo_repository = photo_repository

    async def create_new_photo(self, new_photo: PhotoCreateRequest) -> Photo:
        return await self.__photo_repository.create(photo=Photo(**new_photo.dict()))

    async def get_photo(self, id: UUID) -> Photo:
        return await self.__photo_repository.get(id)

    async def update_photo(self, id: UUID, update_photo_data: PhotoUpdateRequest) -> Photo:
        return await self.__photo_repository.update(id=id, photo=Photo(**update_photo_data.dict()))

    async def get_photo_by_url(self, url: str) -> Photo:
        return await self.__photo_repository.get_by_url(url=url)
