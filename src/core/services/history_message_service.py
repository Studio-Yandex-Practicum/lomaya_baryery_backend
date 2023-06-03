from fastapi import Depends

from src.core.db.models import MessageHistory
from src.core.db.repository import MessageHistoryRepository


class MessageHistoryService:
    def __init__(
        self,
        history_message_repository: MessageHistoryRepository = Depends(),
    ) -> None:
        self.__history_message_repository = history_message_repository

    async def create_object_history_message(self, user_id, message_id, message, event, shift_id=None) -> MessageHistory:
        history_message = MessageHistory(
            user_id=user_id, message_id=message_id, message=message, event=event, shift_id=shift_id
        )
        return history_message

    async def create_bulk_history_message(self, objects: list[MessageHistory]) -> None:
        await self.__history_message_repository.update_all(objects)
