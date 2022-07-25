from loader import bot
from parser_API.parser import hotels
from parser_API.parser import requests_to_api, get_hotels



def sorted_func(elem):
    return int(elem[2][1:])


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    city_name = bot.send_message(message.from_user.id, '<b>Введите город для поиска отелей:</b>', parse_mode='html')
    bot.register_next_step_handler(city_name, count_hotels)


def count_hotels(message):
    bot.send_message(message.from_user.id, f'Собираем данные по отелям в {message.text}.\n'
                                           f'Это может занять немного времени')
    city_id = requests_to_api(message.text)
    count = bot.send_message(message.from_user.id, 'Сколько отелей вывести на экран? ')
    bot.register_next_step_handler(count, print_hotels, city_id)


def print_hotels(message, city_id):
    try:
        if isinstance(int(message.text), int):
            bot.send_message(message.from_user.id, 'Выполняет поиск отелей(это может занять какое-то время...)')
            get_hotels(city_id, 'PRICE', int(message.text))
            for elem in sorted(hotels[-int(message.text):], key=sorted_func):
                text = f'Название отеля - {elem[0]} \n' \
                       f'Цена за 1 ночь - {elem[2]} \n' \
                       f'Адрес отеля - {elem[3]} \n' \
                       f'Рейтинг - {elem[4]} \n' \
                       f'Количество звезд - {elem[5]} \n' \
                       f'Расстояние от центра города - {elem[6]}'

                bot.send_message(message.from_user.id, text=text)
            bot.send_message(message.from_user.id, 'Выберите команду для поиска:'
                                                   '\n/lowprice - покажет самые дешевые отели в выбранном городе'
                                                   '\n/highprice - покажет самые дорогие отели в выбранном городе'
                                                   '\n/bestdeal - лучшие предложения на рынке')
    except Exception:
        bot.send_message(message.from_user.id, 'Ошибка ввода. Введите число')




