from telebot.handler_backends import State, StatesGroup


class UserStateHistory(StatesGroup):
    command = State()
    limit = State()