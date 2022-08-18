import datetime
from typing import List, Tuple
from telegram_bot_calendar import DetailedTelegramCalendar
from database.my_db import add_in_db, add_in_favorite
from keyboards.inline.accept_info import accept_info
from keyboards.inline.calendar import get_calendar
from keyboards.inline.geo_favorite import geo_favorite
from keyboards.inline.question_photo import question_photo
from keyboards.reply.all_command import all_commands
from keyboards.reply.again_button import start_again
from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from parser_API.parser import get_city_id, get_hotels, get_photo
from states.UserState import UserState


def check_key(key, dict1):
    """Функция, которая проверяет наличие ключа в словаре"""

    if dict1.get(key) is not None:
        return True


def delete_message(message):
    """Функция, которая удаляет все сообщения перед выводом результата"""

    with bot.retrieve_data(message.chat.id) as data:
        pass

    # проходимся по id-сообщений, проверяем есть ли id в словаре и удаляем при наличии
    for key, value in data["msg_id"].items():
        if check_key(key=key, dict1=data["msg_id"]) and value != 0:
            bot.delete_message(message.chat.id, message_id=value)
            # обнуляем id сообщения, чтобы не выходило ошибки при повторном вызове функции
            data["msg_id"][key] = 0


def date_to_text(date: str) -> str:
    """Функция, которая преобразовывает дату в читаемый вид текстом"""

    month_list = ['0', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    month = int(date[-5:-3])
    form_date = date[-2:] + ' ' + month_list[month] + ' ' + date[:4]

    return form_date


def send_info(message: Message) -> None:
    """Функция, которая преобразовывает дату в строку, считает разницу между двумя датами, и
    выводит текст для подтверждения введенной пользователем информации"""

    with bot.retrieve_data(message.chat.id) as data:
        pass
    check_in = datetime.datetime.strptime(str(data["check_in"][0]), '%Y-%m-%d')
    check_out = datetime.datetime.strptime(str(data["check_out"][0]), '%Y-%m-%d')

    # находим разницу между двумя датами
    all_days = check_out - check_in
    days = str(all_days).split()
    # если пользователь ввел одинаковую дату заезда и выезда, то будем считать, что плата взымается
    # как за 1 день проживания
    try:
        days = int(days[0])
    except ValueError:
        days = 1

    with bot.retrieve_data(message.chat.id) as data:
        data["days"] = days

    text = '😀 Давайте проверим введенные данные:\n' \
           f'\nГород: {data["city_name"]}' \
           f'\nКоличество отелей на экране: {data["hotels_count"]}' \
           f'\nЗаезд: {data["check_in"][1]}' \
           f'\nВыезд: {data["check_out"][1]}' \
           f'\nДней всего: {data["days"]}' \
           f'\n\n<b>Все верно❓</b>'

    msg = bot.send_message(message.chat.id,
                           text,
                           reply_markup=accept_info(),
                           parse_mode='html')

    # сохраняем id_message сообщения с подтверждением информации, чтобы потом удалить его
    with bot.retrieve_data(message.chat.id) as data:
        data["msg_id"]["msg_id_check_info"] = msg.message_id


def photo(message: Message, hotels: List[Tuple]) -> List[List]:
    """Функция, которая парсит фото и добавляет их в общий список"""

    with bot.retrieve_data(message.chat.id) as data:
        pass

    all_photo_list = []
    for hotel in hotels:

        # вызываем функцию для парсинга фото
        photo_list = get_photo(hotel[0], data["photo_count"])
        if photo_list is not None:
            all_photo_list.append(photo_list)

        else:
            # добавляем, если фото по отелю не были найдены
            all_photo_list.append(['фото не найдено'])

    return all_photo_list


def send_info_for_db(user_id: int, command: str, hotels: List[Tuple], city_name: str) -> None:

    date = str(datetime.datetime.now())
    users_info = (user_id, date[:-7], command[1:], city_name)
    add_in_db(users_info=users_info, hotels=hotels)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start(message: Message) -> None:
    """Функция, которая устанавливает и ловит состояние команды"""

    bot.set_state(message.from_user.id, UserState.command, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

        data["command"] = message.text

        # создаем вложенный словарь, чтобы хранить в нем message_id
        data["msg_id"] = {}
        data["msg_id"]["msg_id_command"] = message.message_id

    bot.set_state(message.from_user.id, UserState.city, message.chat.id)
    msg = bot.send_message(message.from_user.id, '  🏙 Укажите город для поиска отелей:')
    data["msg_id"]["msg_id_city"] = msg.message_id


@bot.message_handler(state=UserState.city)
def set_city(message: Message) -> None:
    """Функция, которая проверяет название города на корректность и запрашивает количество отелей"""

    if not message.text.isdigit():
        msg = bot.send_message(message.from_user.id,
                               '🏨 Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, UserState.hotel_count, message.chat.id)

        # получение доступа к данным, заданным в состояниях
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
            data["msg_id"]["msg_id_hotel_count1"] = msg.message_id
            data["msg_id"]["msg_id_city2"] = message.message_id
    else:
        msg = bot.send_message(message.from_user.id, 'Название города должно состоять из букв')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["msg_id"]["msg_id_mistake1"] = msg.message_id


@bot.message_handler(state=UserState.hotel_count)
def set_hotel_count(message: Message) -> None:
    """Функция, которая записывает введенное количество отелей и создает календарь для
    установки даты заезда в отель"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = int(message.text)
            data["msg_id"]["msg_id_hotel_count2"] = message.message_id

        # создаем первый календарь для даты заезда
        calendar, step = get_calendar(calendar_id=1,
                                      min_date=datetime.date.today(),
                                      current_date=datetime.date.today(),
                                      locale='ru')

        bot.set_state(message.from_user.id, UserState.check_in, message.chat.id)
        msg = bot.send_message(message.chat.id, f'🗓 Выберите дату заселения: ',
                               reply_markup=calendar)

        with bot.retrieve_data(message.chat.id) as data:
            data["msg_id"]["msg_id_calendar1"] = msg.message_id

    else:
        msg = bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')
        with bot.retrieve_data(message.chat.id) as data:
            data["msg_id"]["msg_id_mistake2"] = msg.message_id


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def calendar(call: CallbackQuery) -> None:
    """Обработчик первого календаря для даты заезда"""

    result, key, step = get_calendar(calendar_id=1,
                                     min_date=datetime.date.today(),
                                     current_date=datetime.date.today(),
                                     locale='ru',
                                     callback_data=call,
                                     is_process=True)

    if not result and key:
        bot.edit_message_text(f'🗓 Выберите дату заселения:',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        str_check_in = date_to_text(str(result))

        bot.edit_message_text(f'➡ Заезд: {str_check_in}',
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data["check_in"] = (result, str_check_in)

        # создаем второй календарь для даты выезда
        calendar = get_calendar(calendar_id=2,
                                min_date=data["check_in"][0],
                                current_date=data["check_in"][0],
                                locale='ru')

        bot.set_state(call.message.from_user.id, UserState.check_out, call.message.chat.id)
        msg = bot.send_message(call.message.chat.id, f'🗓 Выберите дату выезда: ',
                               reply_markup=calendar)

        with bot.retrieve_data(call.message.chat.id) as data:
            data["msg_id"]["msg_id_calendar2"] = msg.message_id


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def calendar(call: CallbackQuery) -> None:
    """Обработчик первого календаря для даты выезда"""

    with bot.retrieve_data(call.message.chat.id) as data:
        pass
    result, key, step = get_calendar(calendar_id=2,
                                     min_date=data["check_in"][0],
                                     current_date=data["check_in"][0],
                                     locale='ru',
                                     callback_data=call,
                                     is_process=True)
    if not result and key:
        bot.edit_message_text(f'🗓 Выберите дату выезда:',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        str_check_out = date_to_text(str(result))
        bot.edit_message_text(f'⬅ Выезд: {str_check_out}',
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data["check_out"] = (result, str_check_out)

        # если команда bestdeal, то мы устанавливаем состояние для него и
        # переходим в модуль bestdeal.py
        if data["command"] == '/bestdeal':
            bot.set_state(call.message.chat.id, UserState.prices)
            msg = bot.send_message(call.message.chat.id,
                                   '💲 Теперь укажите диапазон цен отелей(пример: 100 - 500)')
            with bot.retrieve_data(call.message.chat.id) as data:
                data["msg_id"]["msg_id_price_range"] = msg.message_id

        else:
            # если команда НЕ bestdeal, то идем дальше по сценарию
            bot.set_state(call.message.chat.id, UserState.photo_count)
            msg = bot.send_message(call.message.chat.id, '📸 Вывести результат поиска с фото?',
                                   reply_markup=question_photo())

            # сохраняем id этого сообщения, чтобы потом удалить
            with bot.retrieve_data(call.message.chat.id) as data:
                data["msg_id"]["msg_id_photo_question"] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_inline(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для запроса фото"""

    if call.message:
        if call.data == 'yes':
            msg = bot.send_message(call.message.chat.id,
                                   '✅ Введите количество фото для отображения')

            with bot.retrieve_data(call.message.chat.id) as data:
                data["msg_id"]["msg_id_photo_count"] = msg.message_id
            bot.set_state(call.from_user.id, UserState.photo_count)

        elif call.data == 'no':
            # выводим подтверждения введенной информации
            send_info(message=call.message)


@bot.message_handler(state=UserState.photo_count)
def photo_count(message: Message) -> None:
    """Функция, для установки значения photo_count"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = int(message.text)
            data["msg_id"]["msg_id_photo_count2"] = message.message_id

        # выводим подтверждения введенной информации
        send_info(message=message)

    else:
        msg = bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
        with bot.retrieve_data(message.chat.id) as data:
            data["msg_id"]["msg_id_mistake3"] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data == 'show_result' or call.data == 'again')
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для подтверждения информации"""

    if call.message:
        if call.data == 'show_result':
            show_hotels(call.message)

        # если данные введены с ошибкой
        elif call.data == 'again':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass
            delete_message(call.message)

            msg = bot.send_message(call.message.chat.id, ' 🔁 Тогда давайте введем данные заново,'
                                                         'Для этого нажмите на кнопку',
                                   reply_markup=start_again(command=data["command"]))

            data["msg_id_2"]["msg_id_again"] = msg.message_id


def show_hotels(message: Message) -> None:
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    delete_message(message)
    msg1 = bot.send_message(message.chat.id, 'Поиск отелей...')
    msg2 = bot.send_sticker(message.chat.id,
                            sticker='CAACAgIAAxkBAAEFlYVi-6yT63mW4NeAIRSLmq'
                            'ihm5YPVQACvAwAAocoMEntN5GZWCFoBCkE')

    with bot.retrieve_data(message.chat.id) as data:
        pass
    data["msg_id"]["msg_id_sticker1"] = msg1.message_id
    data["msg_id"]["msg_id_sticker2"] = msg2.message_id

    # получаем id города
    city_id = get_city_id(data["city_name"])
    if city_id is not None:
        # если id найдено, идем дальше

        # запрос для вывода информации по отелям с командой lowprice
        if data["command"] == '/lowprice':
            hotels = get_hotels(city_id=city_id,
                                search_info="PRICE",
                                count=data["hotels_count"],
                                check_in=str(data["check_in"][0]),
                                check_out=str(data["check_out"][0]))

        # запрос для вывода информации по отелям с командой highprice
        elif data["command"] == '/highprice':
            hotels = get_hotels(city_id=city_id,
                                search_info="PRICE_HIGHEST_FIRST",
                                count=data["hotels_count"],
                                check_in=str(data["check_in"][0]),
                                check_out=str(data["check_out"][0]))

        # запрос для вывода информации по отелям с командой bestdeal
        else:
            hotels = get_hotels(city_id=city_id,
                                search_info="DISTANCE_FROM_LANDMARK",
                                count=data["hotels_count"],
                                start_price=data["prices"][0],
                                stop_price=data["prices"][1],
                                dist=data["dist_range"],
                                check_in=str(data["check_in"][0]),
                                check_out=str(data["check_out"][0]),
                                command=data["command"])

        # если отели спарсены успешно
        if hotels is not None:
            # когда поиск завершен удаляем стикер поиска

            # если пользователь запросил вывод информации с фото
            if data.get("photo_count") is not None:
                all_photo_list = photo(message=message, hotels=hotels)
                get_info(message, hotels, all_photo_list)
            else:
                get_info(message, hotels)

        # если отели НЕ были получены
        else:
            # когда отели не найдены удаляем стикер поиска
            bot.delete_message(message.chat.id, message_id=msg1.message_id)
            bot.delete_message(message.chat.id, message_id=msg2.message_id)

            bot.send_message(message.chat.id,
                             '❗ К сожалению, не удалось найти информацию по отелям')
    else:

        # когда поиск завершен удаляем стикер поиска
        bot.delete_message(message.chat.id, message_id=msg1.message_id)
        bot.delete_message(message.chat.id, message_id=msg2.message_id)

        # если id города не найдено, то выводим сообщение
        bot.send_message(message.chat.id,
                         f'❗ К сожалению, '
                         f'данные по вашему городу {data["city_name"]} не были найдены'
                         f'\nПроизошла ошибка на сервере\nПопробуйте еще раз')


def get_info(message: Message, hotels: List[Tuple], all_photo_list: List[List] = None) -> None:
    """Функция для вывода информации по отелям в телеграм(с заданными параметрами)"""

    with bot.retrieve_data(message.chat.id) as data:
        pass

    # удаляем сообщение с поиском и стикер перед выдачей результата
    bot.delete_message(message.chat.id, message_id=data["msg_id"]["msg_id_sticker1"])
    bot.delete_message(message.chat.id, message_id=data["msg_id"]["msg_id_sticker2"])

    text = f'Результат поиска по команде: {data["command"][1:]}' \
           f'\nГород: {data["city_name"]}' \
           f'\nКоличество отелей: {data["hotels_count"]}' \
           f'\nЗаселение: {data["check_in"][1]}' \
           f'\nВыезд: {data["check_out"][1]}' \
           f'\nДней: {data["days"]}'

    bot.send_message(message.chat.id, text)
    for i in range(int(data["hotels_count"])):
        try:
            # подсчет общей стоимости отеля
            total_cost = round(data["days"] * float(hotels[i][2][1:]), 5)
            text = f'🏨 Название отеля: {hotels[i][1]}'\
                   f'\n📍 Адрес отеля: {hotels[i][3]}' \
                   f'\n✔ Расположение от центра: {hotels[i][6]}' \
                   f'\n💵 Цена за сутки: {hotels[i][2][1:]}{hotels[i][2][0]}' \
                   f'\n💰 Цена всего: {total_cost}$' \
                   f'\n✨ Количество звезд отеля: {hotels[i][5]}' \
                   f'\n📈 Рейтинг отеля: {hotels[i][4]}' \

            bot.send_message(message.chat.id, text,
                             reply_markup=geo_favorite(lat=hotels[i][7],
                                                       lon=hotels[i][8],
                                                       hotels=hotels[i][1],
                                                       city_name=data["city_name"]))

        # ловим исключение, которое возникнет в результате того, что отелей по заданному
        # расстоянию от центра будет меньше, указанного пользователем
        except IndexError:
            bot.send_message(message.chat.id,
                             'Отелей в заданном расстоянии от центра больше не удалось найти')

        finally:
            with bot.retrieve_data(message.chat.id) as data:
                data["hotel"] = hotels

        if all_photo_list is not None:
            bot.send_media_group(message.chat.id,
                                 [InputMediaPhoto(media=i_photo)
                                  if i_photo != 'фото не найдено'
                                  else bot.send_message(
                                     message.chat.id,
                                     f'Для отеля {hotels[i][1]} не удалось найти фото')
                                  for i_photo in all_photo_list[i]])

    # вызываем функцию для формирования информации для записи в бд
    send_info_for_db(hotels=hotels,
                     user_id=message.chat.id,
                     command=data["command"],
                     city_name=data["city_name"])

    msg = bot.send_message(message.chat.id, 'Выберите одну из функции:',
                           reply_markup=all_commands())
    data["msg_id"]["msg_id_all_func"] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data.startswith('geo'))
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для вывода геопозиции """

    if call.message:

        # преобразовываем данные, которые мы передели через callback_data
        geo_data = call.data.split('/')
        lat = float(geo_data[1])
        lon = float(geo_data[2])
        hotel_name = geo_data[3]
        if call.data:
            bot.send_message(call.message.chat.id, f'Расположение на карте для отеля: {hotel_name}')
            bot.send_location(call.message.chat.id, latitude=lat, longitude=lon)


@bot.callback_query_handler(func=lambda call: call.data.startswith('favorite'))
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для добавления в избранное"""

    if call.message:
        info = call.data.split('/')
        hotel_name = info[1]
        city_name = info[2]
        with bot.retrieve_data(call.message.chat.id) as data:
            pass
        for i in range(len(data["hotel"])):

            # проверяем название отеля из общего списка отелей на совпадение
            if data["hotel"][i][1].startswith(hotel_name):
                add_in_favorite(user_id=call.from_user.id,
                                hotel=data["hotel"][i],
                                city_name=city_name)

                bot.send_message(call.message.chat.id,
                                 f'Отель {data["hotel"][i][1]} добавлен в избранное')
