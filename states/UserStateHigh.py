from telebot.handler_backends import State, StatesGroup


class UserStateHigh(StatesGroup):
    city = State()
    hotel_count = State()
    date = State()
    photo_count = State()
    finish = State()