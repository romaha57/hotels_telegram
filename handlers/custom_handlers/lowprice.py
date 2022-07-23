from loader import bot


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    bot.send_message(message.from_user.id, 'Выполняет поиск отелей(это может занять какое-то время...)')
    bot.send_message(message.from_user.id, 'Результат поиска дешевых отелей: ')


    # text = f'Название отеля: {}' \
    #        f'Адрес: {}' \
    #        f'Цена за 1 ночь: ' \
    #        f'Количество звезд отеля: {}' \
    #        f'Рейтинг отеля: {}' \
    #        f'Расстояние до центра: {}'

