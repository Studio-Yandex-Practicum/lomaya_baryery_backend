from telegram import ReplyKeyboardMarkup

LOMBARIERS_BALANCE = 'Баланс ломбарьеров'
SKIP_A_TASK = 'Пропустить задание'

CURRENT_SHIFT_BUTTONS = ReplyKeyboardMarkup(
    [[SKIP_A_TASK, LOMBARIERS_BALANCE]],
    resize_keyboard=True,
)
