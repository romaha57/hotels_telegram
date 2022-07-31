from telebot.handler_backends import State, StatesGroup


class BestDealInfo(StatesGroup):
    city = State()
    price_range = State()
    dist_range = State()
    hotel_count = State()
    date = State()
    photo_count = State()
    finish = State()
