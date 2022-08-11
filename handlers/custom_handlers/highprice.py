import datetime
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from typing import List, Tuple
from telegram_bot_calendar import DetailedTelegramCalendar
from database.my_db import add_in_db
from keyboards.inline.geo import geo
from loader import bot
from states.UserStateHigh import UserStateHigh
from keyboards.inline.question_photo_high import question_photo_high
from keyboards.inline.accept_info_high import accept_info_high
from keyboards.reply.again_button_high import start_again_high
from keyboards.reply.all_command import all_commands
from parser_API.parser import requests_to_api, get_hotels, get_photo


@bot.message_handler(commands=['highprice'])
def start_high(message: Message) -> None:
    """Функция для запроса города для поиска"""

    # Удаления состояния finish при переходе из других сценариев
    bot.delete_state(message.from_user.id, message.chat.id)
    # Установка состояния для города
    bot.set_state(message.from_user.id, UserStateHigh.city, message.chat.id)
    bot.send_message(message.from_user.id, ' 🏙 Укажите город для поиска отелей:')


@bot.message_handler(state=UserStateHigh.city)
def get_city_high(message: Message) -> None:
    """Функция, для запроса количества отелей"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id,
                         '🏨 Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, UserStateHigh.hotel_count, message.chat.id)

        # получение доступа к данным, заданным в состояниях
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=UserStateHigh.hotel_count)
def hotel_count_high(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
        bot.set_state(message.from_user.id, UserStateHigh.photo_count, message.chat.id)

        calendar, step = DetailedTelegramCalendar(calendar_id=3,
                                                  locale='ru',
                                                  min_date=datetime.date.today()).build()

        bot.send_message(message.chat.id, f'Выберите дату заселения:',
                     reply_markup=calendar)

    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def calendar(call: CallbackQuery):
    result, key, step = DetailedTelegramCalendar(calendar_id=3,
                                                 locale='ru',
                                                 min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f'Выберите месяц:',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'➡ Заезд: {result}',
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data["check_in"] = str(result)

        calendar, step = DetailedTelegramCalendar(calendar_id=4,
                                                  locale='ru',
                                                  min_date=datetime.date.today()).build()
        bot.send_message(call.message.chat.id, f'Выберите дату выезда:',
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
def calendar(call: CallbackQuery):
    result, key, step = DetailedTelegramCalendar(calendar_id=4,
                                                 locale='ru',
                                                 min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f'Выберите месяц: ',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'⬅ Выезд: {result}',
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data["check_out"] = str(result)

        bot.send_message(call.message.chat.id, '📸 Вывести результат поиска с фото?'
                         , reply_markup=question_photo_high())


@bot.callback_query_handler(func=lambda call: call.data == 'yes1' or call.data == 'no1')
def callback_inline_high(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes1':
            bot.send_message(call.message.chat.id, '✅ Введите количество фото для отображения')
        elif call.data == 'no1':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass

            check_in = datetime.datetime.strptime(data["check_in"], '%Y-%m-%d')
            check_out = datetime.datetime.strptime(data["check_out"], '%Y-%m-%d')
            all_days = check_out - check_in
            days = str(all_days).split()
            days = int(days[0])

            with bot.retrieve_data(call.message.chat.id) as data:
                data["days"] = days

            text = '😀 Давайте проверим введенные данные:\n' \
                   f'\nГород: {data["city_name"]}' \
                   f'\nКоличество отелей на экране: {data["hotels_count"]}' \
                   f'\nЗаезд: {data["check_in"]}' \
                   f'\nВыезд: {data["check_out"]}' \
                   f'\nДней всего: {data["days"]}'\
                   f'\n\n<b>Все верно❓</b>'

            bot.send_message(call.message.chat.id,
                             text,
                             reply_markup=accept_info_high(),
                             parse_mode='html')


@bot.message_handler(state=UserStateHigh.photo_count)
def photo_count_high(message: Message) -> None:
    """Функция, для подтверждения информации"""

    bot.set_state(message.from_user.id, UserStateHigh.finish, message.chat.id)
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = message.text

        check_in = datetime.datetime.strptime(data["check_in"], '%Y-%m-%d')
        check_out = datetime.datetime.strptime(data["check_out"], '%Y-%m-%d')
        all_days = check_out - check_in
        days = str(all_days).split()
        days = int(days[0])

        with bot.retrieve_data(message.chat.id) as data:
            data["days"] = days

        text = ' 😀 Давайте проверим введенные данные:\n' \
               f'\nГород: {data["city_name"]}' \
               f'\nКоличество отелей на экране: {data["hotels_count"]}' \
               f'\nЗаезд: {data["check_in"]}' \
               f'\nВыезд: {data["check_out"]}' \
               f'\nДней всего: {data["days"]}' \
               f'\nФото штук: {data["photo_count"]}' \
               f'\n\n<b>Все верно?</b>' \

        bot.send_message(message.from_user.id,
                         text,
                         reply_markup=accept_info_high(),
                         parse_mode='html')
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')


@bot.callback_query_handler(func=lambda call: call.data == 'show_result1' or call.data == 'again1')
def callback_func_high(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result1':
           show_hotels_high(call.message)

        elif call.data == 'again1':
            bot.send_message(call.message.chat.id, ' 🔁 Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку',
                             reply_markup=start_again_high())


def show_hotels_high(message: Message) -> None:
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    bot.send_message(message.chat.id,
                     '🔜 Отлично, начинаем поиск(это может занять некоторое время...)')
    bot.send_message(message.chat.id,
                     '❇ Подключаемся к базе данных отеля в указанном городе(1/3)...')

    with bot.retrieve_data(message.chat.id) as data:
        pass

    city_id = requests_to_api(data["city_name"])
    if city_id is not None:
        bot.send_message(message.chat.id, '✳ Получаем информацию по отелям(2/3)...')

        hotels = get_hotels(city_id=city_id,
                            search_info="PRICE_HIGHEST_FIRST",
                            count=data["hotels_count"],
                            check_in=data["check_in"],
                            check_out=data["check_out"])
        if hotels is not None:
            all_photo_list = []
            try:
                for hotel in hotels:
                    photo_list = get_photo(hotel[0], data["photo_count"])
                    if photo_list is not None:
                        all_photo_list.append(photo_list)
                    else:
                        all_photo_list.append(['фото не найдено'])
            except Exception:
                pass
            print_info_high(message, hotels, all_photo_list)

        else:
            bot.send_message(message.chat.id, '❗ К сожалению, не удалось найти информацию по отелям')
    else:
        bot.send_message(message.chat.id,
                         '❗ К сожалению, сервис с информацией по отелям временно не работает\n'
                         'Попробуйте чуть позже')


def print_info_high(message: Message, hotels: List[Tuple], all_photo_list: List[List]) -> None:
    """Функция для вывода информации по отелям в телеграмм(с заданными параметрами)"""

    with bot.retrieve_data(message.chat.id) as data:
        pass
    bot.send_message(message.chat.id, 'Результат поиска:')
    for i in range(int(data["hotels_count"])):
        total_cost = round(data["days"] *float(hotels[i][2][1:]), 5)
        text = f'🏨 Название отеля: {hotels[i][1]}' \
           f'\n📍 Адрес отеля: {hotels[i][3]}' \
           f'\n✔ Расположение от центра: {hotels[i][6]}' \
           f'\n💵 Цена за сутки: {hotels[i][2]}' \
           f'\n💰 Цена всего: {total_cost}$' \
           f'\n✨ Количество звезд отеля: {hotels[i][5]}' \
           f'\n📈 Рейтинг отеля: {hotels[i][4]}' \

        # Отправка фото
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=geo(hotels[i][7], hotels[i][8]))
        try:
            bot.send_media_group(message.chat.id,
                                 [InputMediaPhoto(media=photo)
                                  if photo != 'фото не найдено'
                                  else bot.send_message(
                                     message.chat.id,
                                     f'Для отеля {hotels[i][1]} не удалось найти фото')
                                  for photo in all_photo_list[i]])

        except Exception:
            pass

    bot.send_message(message.chat.id, 'Выберите одну из функции:', reply_markup=all_commands())
    bot.register_next_step_handler(message, add_in_database, hotels)

    del hotels


@bot.callback_query_handler(func=lambda call: call.data.startswith('geo'))
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для вывода геопозиции """

    if call.message:
        geo_data = call.data.split('/')
        print(geo_data)
        lat = float(geo_data[1])
        lon = float(geo_data[2])
        if call.data:
            bot.send_location(call.message.chat.id, latitude=lat, longitude=lon)


def add_in_database(message: Message, hotels: List[Tuple]) -> None:
    date = datetime.datetime.now()
    date = str(date)

    users_tuple = (message.from_user.id, date[:-6], 'highprice')
    add_in_db(users_info=users_tuple, hotels=hotels)


