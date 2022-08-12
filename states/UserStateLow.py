from telebot.handler_backends import State, StatesGroup


class UserStateLow(StatesGroup):
    command = State()
    city = State()
    hotel_count = State()
    prices = State()
    distances = State()
    check_in = State()
    check_out = State()
    photo_count = State()
