from telebot.handler_backends import State, StatesGroup


class LowHighPrice(StatesGroup):
    city = State()
    hotel_count = State()
    date = State()
    photo_count = State()
    finish = State()
