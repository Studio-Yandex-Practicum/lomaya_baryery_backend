from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.max_bot.main import MaxBot

# Модуль намеренно не имеет зависимостей от остального кода проекта:
# он позволяет получить экземпляр Max-бота из любого места,
# не создавая циклических импортов через обработчики и сервисы
_max_bot: Optional["MaxBot"] = None


def get_max_bot() -> Optional["MaxBot"]:
    """Получить запущенный экземпляр Max-бота (None - бот не запущен)."""
    return _max_bot


def set_max_bot(bot: Optional["MaxBot"]) -> None:
    """Сохранить экземпляр запущенного Max-бота."""
    global _max_bot
    _max_bot = bot
