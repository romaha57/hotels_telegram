from telebot.types import Message
from loader import bot
from keyboards.reply.all_command import all_commands


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(content_types=['text'])
def bot_echo(message: Message):
    bot.send_message(message.chat.id,
                     'Я вас не понимаю 🙂\nВыберите одну из команд по кнопкам ниже',
                     reply_markup=all_commands())
