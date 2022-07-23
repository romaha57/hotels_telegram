from loader import bot


@bot.message_handler(commands=['highprice'])
def highprice(message):
    bot.send_message(message.from_user.id,)