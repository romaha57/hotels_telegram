from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    command = State()
    city = State()
    hotel_count = State()
    prices = State()
    distances = State()
    check_in = State()
    check_out = State()
    photo_count = State()
