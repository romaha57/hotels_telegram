from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def pop_city() -> ReplyKeyboardMarkup:
    """Кнопки для вывода 9-ти самых популярных городов"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    london = KeyboardButton(text='Лондон')
    rome = KeyboardButton(text='Рим')
    new_york = KeyboardButton(text='Нью-Йорк')
    budapesht = KeyboardButton(text='Будапешт')
    tokio = KeyboardButton(text='Токио')
    california = KeyboardButton(text='Калифорния')
    dubai = KeyboardButton(text='Дубай')
    paris = KeyboardButton(text='Париж')
    praga = KeyboardButton(text='Прага')
    keyboard.add(london, rome, new_york, budapesht, tokio, california,
                 dubai, praga, paris)

    return keyboard
