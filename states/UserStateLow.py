from telebot.handler_backends import State, StatesGroup


class UserStateLow(StatesGroup):
    city = State()
    hotel_count = State()
    photo_count = State()
    finish = State()
