import datetime
from telebot.types import Message
from loader import bot
from states.bestdeal import BestDealInfo
from keyboards.inline.question_photo import question_photo
from keyboards.inline.accept_info import accept_info


@bot.message_handler(commands=['bestdeal'])
def start(message: Message) -> None:
    """Функция для запроса города для поиска"""

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, BestDealInfo.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=BestDealInfo.city)
def get_city(message: Message) -> None:
    """Функция, для запроса диапозона цен"""

    if message.text.isalpha():
        text = 'Теперь укажите диапозон цен отелей(пример: 100-500)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.price_range, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=BestDealInfo.price_range)
def hotel_count(message: Message) -> None:
    """Функция, для запроса диапозона расстояния от центра  """

    try:
        prices = message.text.split('-')
        start_price = int(prices[0])
        stop_price = int(prices[1])
        text = 'Отлично, теперь укажите диапозон расстояния от центра(пример: 0.5-5)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.dist_range, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['prices'] = (start_price, stop_price)

    except Exception:
        bot.send_message(message.from_user.id, 'Некорректный ввод.Попробуйте еще раз')


@bot.message_handler(state=BestDealInfo.dist_range)
def date(message: Message) -> None:
    """Функция, для запроса количества отелей """

    try:
        dists = message.text.split('-')
        start_dist = int(dists[0])
        stop_dist = int(dists[1])
        bot.send_message(message.from_user.id, 'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, BestDealInfo.hotel_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = (start_dist, stop_dist)

    except:
        bot.send_message(message.from_user.id, 'Ошибка ввода.Попробуйте еще раз')


@bot.message_handler(state=BestDealInfo.hotel_count)
def hotel_count(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=BestDealInfo.date)
def date(message: Message) -> None:
    """Функция, для распознования вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo())
        bot.set_state(message.from_user.id, BestDealInfo.photo_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date'] = (dates[0], dates[1], days.days)

    except:
        bot.send_message(message.from_user.id, 'Ошибка ввода даты.Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes':
            bot.send_message(call.message.chat.id, 'Введите количество фото для отображения')
        else:
            bot.send_message(call.message.chat.id, 'Начинаем поиск')


@bot.message_handler(state=BestDealInfo.photo_count)
def photo_count(message: Message) -> None:
    """Функция, для подтверждения информации"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = message.text

        text = 'Давайте проверим введенные данные:\n' \
               f'\nГород: {data["city_name"]}' \
               f'\nДиапозон цен: от {data["prices"][0]} до {data["prices"][1]}' \
               f'\nДиапозон расстояния от центра: от {data["dist_range"][0]} до {data["dist_range"][1]}'\
               f'\nКоличество отелей на экране: {data["hotels_count"]}' \
               f'\nЗаезд: {data["date"][0]}' \
               f'\nВыезд: {data["date"][1]}' \
               f'\nДней всего: {data["date"][2]}' \
               f'\nФото штук: {data["photo_count"]}' \
               f'\n\nВсе верно?' \

        bot.send_message(message.from_user.id, text, reply_markup=accept_info())
        print(data["date"])
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
    bot.set_state(message.from_user.id, LowHighPrice.finish, message.chat.id)