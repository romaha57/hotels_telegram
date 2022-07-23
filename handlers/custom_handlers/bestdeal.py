from loader import bot


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    bot.send_message(message.from_user.id, 'функция bestdeal')