from loader import bot
from parser_API.parser import hotels


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    bot.send_message(message.from_user.id, 'Выполняет поиск отелей(это может занять какое-то время...)')
    for elem in hotels:
        text = f'Название отеля - {elem[0]} \n' \
               f'Цена за 1 ночь - {elem[2]} \n' \
               f'Адрес отеля - {elem[3]} \n' \
               f'Рейтинг - {elem[4]} \n' \
               f'Количество звезд - {elem[5]} \n' \
               f'Расстояние от центра города - {elem[6]}'

        bot.send_message(message.from_user.id, text=text)






