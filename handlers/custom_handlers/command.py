import datetime
from typing import List, Tuple
from telegram_bot_calendar import DetailedTelegramCalendar
from keyboards.inline.accept_info import accept_info
from keyboards.inline.calendar import get_calendar
from keyboards.inline.geo import geo
from keyboards.inline.question_photo import question_photo
from keyboards.reply.all_command import all_commands
from keyboards.reply.again_button import start_again
from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from parser_API.parser import get_city_id, get_hotels, get_photo
from states.UserState import UserState


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
    days = int(days[0])
    with bot.retrieve_data(message.chat.id) as data:
        data["days"] = days

    text = '😀 Давайте проверим введенные данные:\n' \
           f'\nГород: {data["city_name"]}' \
           f'\nКоличество отелей на экране: {data["hotels_count"]}' \
           f'\nЗаезд: {data["check_in"][1]}' \
           f'\nВыезд: {data["check_out"][1]}' \
           f'\nДней всего: {data["days"]}' \
           f'\n\n<b>Все верно❓</b>'

    bot.send_message(message.chat.id,
                     text,
                     reply_markup=accept_info(),
                     parse_mode='html')


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


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start(message: Message) -> None:
    """Функция, которая устанавливает и ловит состояние комманды"""

    bot.set_state(message.from_user.id, UserState.command, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = message.text

    bot.set_state(message.from_user.id, UserState.city, message.chat.id)
    bot.send_message(message.from_user.id, '  🏙 Укажите город для поиска отелей:')


@bot.message_handler(state=UserState.city)
def set_city(message: Message) -> None:
    """Функция, которая проверяет название города на корректность и запрашивает количество отелей"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id,
                         '🏨 Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, UserState.hotel_count, message.chat.id)

        # получение доступа к данным, заданным в состояниях
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=UserState.hotel_count)
def set_hotel_count(message: Message) -> None:
    """Функция, которая записывает введенное количество отелей и создает календарь для
    установки даты заезда в отель"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = int(message.text)

        # создаем первый календарь для даты заезда
        calendar, step = get_calendar(calendar_id=1,
                                      min_date=datetime.date.today(),
                                      current_date=datetime.date.today(),
                                      locale='ru')

        bot.set_state(message.from_user.id, UserState.check_in, message.chat.id)
        bot.send_message(message.chat.id, f'Выберите дату заселения: ',
                         reply_markup=calendar)

    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


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
        bot.edit_message_text(f'Выберите месяц:',
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
        bot.send_message(call.message.chat.id, f'Выберите дату выезда: ',
                         reply_markup=calendar)


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
        bot.edit_message_text(f'Выберите месяц:',
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
            bot.send_message(call.message.chat.id,
                             '💲 Теперь укажите диапозон цен отелей(пример: 100 - 500)')

        else:
            # если команда НЕ bestdeal, то идем дальше по сценарию
            bot.set_state(call.message.chat.id, UserState.photo_count)
            bot.send_message(call.message.chat.id, '📸 Вывести результат поиска с фото?',
                             reply_markup=question_photo())


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_inline(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes':
            bot.send_message(call.message.chat.id, '✅ Введите количество фото для отображения')
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

        # выводим подтверждения введенной информации
        send_info(message=message)

    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')


@bot.callback_query_handler(func=lambda call: call.data == 'show_result' or call.data == 'again')
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result':
           show_hotels(call.message)

        # если данные введены с ошибкой
        elif call.data == 'again':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass
            bot.send_message(call.message.chat.id, ' 🔁 Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку',
                             reply_markup=start_again(command=data["command"]))


def show_hotels(message: Message) -> None:
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    bot.send_message(message.chat.id,
                     '🔜 Отлично, начинаем поиск(это может занять некоторое время...)')
    with bot.retrieve_data(message.chat.id) as data:
        pass

    # получаем id города
    city_id = get_city_id(data["city_name"])
    if city_id is not None:

        # если id найдено, идем дальше
        bot.send_message(message.chat.id, '✳ Получаем информацию по отелям...')

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

            # если пользователь запросил вывод информации с фото
            if data.get("photo_count") is not None:
                all_photo_list = photo(message=message, hotels=hotels)
                get_info(message, hotels, all_photo_list)
            else:
                get_info(message, hotels)

        # если отели НЕ были получены
        else:
            bot.send_message(message.chat.id,
                             '❗ К сожалению, не удалось найти информацию по отелям')
    else:

        # если id города не найдено, то выводим сообщение
        bot.send_message(message.chat.id,
                         f'❗ К сожалению, '
                         f'данные по вашему городу {data["city_name"]} не были найдены')


def get_info(message: Message, hotels: List[Tuple], all_photo_list: List[List] = None) -> None:
    """Функция для вывода информации по отелям в телеграм(с заданными параметрами)"""

    with bot.retrieve_data(message.chat.id) as data:
        pass
    bot.send_message(message.chat.id, 'Результат поиска:')
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

        # Отправка фото
            bot.send_message(message.chat.id, text,
                             reply_markup=geo(hotels[i][7], hotels[i][8]))

        # ловим исключение, которое возникнет в результате того, что отелей по заданному
        # расстоянию от центра будет меньше, указанного пользователем
        except IndexError:
            bot.send_message(message.chat.id,
                             'Отелей в заданном расстоянии от центра больше не удалось найти')

        if all_photo_list is not None:
            bot.send_media_group(message.chat.id,
                                 [InputMediaPhoto(media=i_photo)
                                  if i_photo != 'фото не найдено'
                                  else bot.send_message(
                                     message.chat.id,
                                     f'Для отеля {hotels[i][1]} не удалось найти фото')
                                  for i_photo in all_photo_list[i]])

    bot.send_message(message.chat.id, 'Выберите одну из функции:', reply_markup=all_commands())


@bot.callback_query_handler(func=lambda call: call.data.startswith('geo'))
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для вывода геопозиции """

    if call.message:
        geo_data = call.data.split('/')
        lat = float(geo_data[1])
        lon = float(geo_data[2])
        if call.data:
            bot.send_location(call.message.chat.id, latitude=lat, longitude=lon)
