from loader import bot


@bot.message_handler(commands=['history'])
def history(message):
    bot.send_message(message.from_user.id, 'Подгружаем историю поиска...')