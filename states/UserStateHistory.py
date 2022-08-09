from telebot.handler_backends import State, StatesGroup


class UserStateHistory(StatesGroup):
    limit = State()
    finish = State()