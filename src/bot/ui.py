from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

LOMBARIERS_BALANCE = 'Баланс ломбарьеров'
SKIP_A_TASK = 'Пропустить задание'

DAILY_TASK_BUTTONS = ReplyKeyboardMarkup(
    [[SKIP_A_TASK, LOMBARIERS_BALANCE]],
    resize_keyboard=True,
)


CONFIRM_SKIP_TASK = 'Пропустить'
CANCEL_SKIP_TASK = 'Отмена'

CONFIRM_SKIP_TASK_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(CONFIRM_SKIP_TASK, callback_data=CONFIRM_SKIP_TASK),
            InlineKeyboardButton(CANCEL_SKIP_TASK, callback_data=CANCEL_SKIP_TASK),
        ]
    ],
)
