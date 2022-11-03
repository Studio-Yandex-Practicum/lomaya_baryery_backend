from src.core.db.models import Photo
from src.core.db.repository import AbstractRepository


class PhotoRepository(AbstractRepository):
    """Репозиторий для работы с моделью Photo."""

    pass


photo_repository = PhotoRepository(Photo)
