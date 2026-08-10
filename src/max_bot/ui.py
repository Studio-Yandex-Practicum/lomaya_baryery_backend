from aiomax.buttons import CallbackButton

LOMBARIERS_BALANCE = 'Баланс ломбарьеров'
SKIP_A_TASK = 'Пропустить задание'

BALANCE_CALLBACK = 'balance'
SKIP_TASK_CALLBACK = 'skip_task'
CONFIRM_SKIP_TASK_CALLBACK = 'confirm_skip_task'
CANCEL_SKIP_TASK_CALLBACK = 'cancel_skip_task'

# В Max нет reply-клавиатур, поэтому кнопки ежедневного задания
# отправляются inline-клавиатурой вместе с сообщением задания.
DAILY_TASK_KEYBOARD = [
    [
        CallbackButton(SKIP_A_TASK, SKIP_TASK_CALLBACK),
        CallbackButton(LOMBARIERS_BALANCE, BALANCE_CALLBACK),
    ]
]

CONFIRM_SKIP_TASK_KEYBOARD = [
    [
        CallbackButton('Пропустить', CONFIRM_SKIP_TASK_CALLBACK, intent='negative'),
        CallbackButton('Отмена', CANCEL_SKIP_TASK_CALLBACK),
    ]
]
