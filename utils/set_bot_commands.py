from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS, CUSTOM_COMMANDS, ADDITIONAL_COMMANDS


def set_default_commands(bot):
    COMMANDS = list(DEFAULT_COMMANDS) + list(CUSTOM_COMMANDS) + list(ADDITIONAL_COMMANDS)
    COMMANDS = tuple(COMMANDS)
    bot.set_my_commands(
        [BotCommand(*i) for i in COMMANDS]
    )
