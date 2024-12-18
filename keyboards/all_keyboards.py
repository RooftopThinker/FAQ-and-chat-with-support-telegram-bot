from aiogram import types


def get_phone_number():
    buttons = [[types.KeyboardButton(text='Оставить номер', request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons, one_time_keyboard=True)
    return keyboard


def check_subscription():
    buttons = [[types.InlineKeyboardButton(text='Проверить подписку', callback_data='subscription')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def approve_or_decline_subscription(user_id):
    buttons = [[types.InlineKeyboardButton(text='Принять', callback_data=f'accept_{user_id}')],
               [types.InlineKeyboardButton(text='Отклонить', callback_data=f'decline_{user_id}')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu():
    buttons = [[types.KeyboardButton(text='Получить бонус')],
               [types.KeyboardButton(text='Вопросы')],
               [types.KeyboardButton(text='Проблемы с товаром')]]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons, one_time_keyboard=True)
    return keyboard


def cancel():
    buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data='cancel')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def dispenser_or_humidifier():
    buttons = [[types.InlineKeyboardButton(text='Дозатор', callback_data='dispenser')],
               [types.InlineKeyboardButton(text='Увлажнитель', callback_data='humidifier')],
               [types.InlineKeyboardButton(text="Отмена", callback_data='cancel')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_menu():
    buttons = [[types.InlineKeyboardButton(text='Статистика', callback_data='stats')],
               [types.InlineKeyboardButton(text='Рассылка', callback_data='mailing')],
               [types.InlineKeyboardButton(text="Выгрузить пользователей", callback_data='export')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel_admin():
    buttons = [[types.InlineKeyboardButton(text="Отмена", callbxack_data='admin_cancel')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def yes_or_no():
    buttons = [[types.InlineKeyboardButton(text='Да✅', callback_data='yes')],
               [types.InlineKeyboardButton(text='Нет❌', callback_data='no')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def dispenser_problems():
    buttons = [[types.InlineKeyboardButton(text='Проблема 1', callback_data='problem_1')],
               [types.InlineKeyboardButton(text='Проблема 2', callback_data='problem_2')],
               [types.InlineKeyboardButton(text='Проблема 3', callback_data='problem_3')],
               [types.InlineKeyboardButton(text="Отмена", callback_data='cancel')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def humidifier_problems():
    buttons = [[types.InlineKeyboardButton(text='Проблема 1', callback_data='problem_1')],
               [types.InlineKeyboardButton(text='Проблема 2', callback_data='problem_2')],
               [types.InlineKeyboardButton(text='Проблема 3', callback_data='problem_3')],
               [types.InlineKeyboardButton(text='Проблема 4', callback_data='problem_4')],
               [types.InlineKeyboardButton(text='Проблема 5', callback_data='problem_5')],
               [types.InlineKeyboardButton(text="Отмена", callback_data='cancel')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def review_approved():
    buttons = [[types.InlineKeyboardButton(text='Отзыв одобрен✅', callback_data='_')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def review_declined():
    buttons = [[types.InlineKeyboardButton(text='Отзыв отклонён❌', callback_data='_')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def problem_solved():
    buttons = [[types.InlineKeyboardButton(text='Не надо, проблема решена', callback_data='problemsolved')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

