from fastapi import Depends

from src.core.db.models import MessageHistory
from src.core.db.repository import MessageHistoryRepository, ShiftRepository


class MessageHistoryService:
    def __init__(
        self,
        history_message_repository: MessageHistoryRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
    ) -> None:
        self.__history_message_repository = history_message_repository
        self.__shift_repository = shift_repository

    async def create_history_message(self, user_id, chat_id, message, status) -> None:
        shift = await self.__shift_repository.get_started_shift_id()
        history_message = MessageHistory(user_id, chat_id, message, status, shift)
        await self.__history_message_repository.create(instance=history_message)
