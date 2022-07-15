import requests
import telebot


bot = telebot.TeleBot('5531804645:AAFSBOA5d30A0tOdeEN0_adQdgz5PzC20aA')


@bot.message_handler(content_types=['text'])
def get_start_message(message):
    """Функция для запуска бота и его приветствия"""

    if message.text.lower() == '/start':
        bot.send_message(message.from_user.id, 'Приветствую тебя')
    elif message.text.lower() == '/hello-world':
        bot.send_message(message.from_user.id, 'Hello, World!')
    elif message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, 'Привет тебе еще раз)')
    elif message.text == '/помощь':
        bot.send_message(message.from_user.id, 'Сейчас помогу')
    else:
        bot.send_message(message.from_user.id, 'Пока моего функционала недостаточно')


bot.polling(none_stop=True, interval=0)


