from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS, CUSTOM_COMMANDS, ADDITIONAL_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    base_text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    base_text = '\n'.join(base_text)
    custom_text = [f'/{command1} - {desk1}' for command1, desk1 in CUSTOM_COMMANDS]
    custom_text = '\n'.join(custom_text)
    additional_text = [f'/{command2} - {desk2}' for command2, desk2 in ADDITIONAL_COMMANDS]
    additional_text = '\n'.join(additional_text)

    bot.send_message(message.from_user.id, 'Список базовых команд: \n' + base_text +
                     '\n\nСписок команд для поиска отелей: \n' + custom_text +
                     '\n\nДополнительные команды: \n' + additional_text)
