import datetime
from loader import bot
from states.lowhighprice import LowHighPrice
from keyboards.inline.question_photo import question_photo


@bot.message_handler(commands=['highprice'])
def start(message):
    """Функция для запроса города для поиска"""

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, LowHighPrice.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=LowHighPrice.city)
def get_city(message):
    """Функция, для запроса количества отелей"""

    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, LowHighPrice.hotel_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=LowHighPrice.hotel_count)
def hotel_count(message):
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, LowHighPrice.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=LowHighPrice.date)
def date(message):
    """Функция, для распознования вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo())
        bot.set_state(message.from_user.id, LowHighPrice.photo_count, message.chat.id)

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


@bot.message_handler(state=LowHighPrice.photo_count)
def photo_count(message):
    """Функция, для подтверждения информации"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = message.text

        text = 'Давайте проверим введеные данные:\n' \
               f'\nГород: {data["city_name"]}' \
               f'\nКоличество отелей на экране: {data["hotels_count"]}' \
               f'\nЗаезд: {data["date"][0]}' \
               f'\nВыезд: {data["date"][1]}' \
               f'\nДней всего: {data["date"][2]}' \
               f'\nФото штук: {data["photo_count"]}',
        bot.send_message(message.from_user.id, text)
        print(data["date"])
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
    bot.set_state(message.from_user.id, LowHighPrice.finish, message.chat.id)

