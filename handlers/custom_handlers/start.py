import parser_API.parser
from loader import bot
from keyboards.reply.contact_button import requsts_contact
from states.contact_information import UserInfoState
from telebot.types import Message
from parser_API.parser import requests_to_api, get_hotels
from handlers.custom_handlers import lowprice


@bot.message_handler(commands=['start'])
def start_func(message):
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    text = """\nВас приветствует EasyTravelBot для поиска отеля в любой точке мира 🌍
    \nДля начала нужно будет пройти небольшую регистрацию, которая позволит нам подбирать выгодные предложения именно для вас.\n
    \nДоступные функции:
    /lowprice - покажет самые дешевые отели в выбранном городе
    /highprice - покажет самые дорогие отели в выбранном городе
    /bestdeal - лучшие предложения на рынке
    /history - история поиска
        """
    bot.send_message(message.from_user.id, f'Здравствуйте, {message.from_user.username}😃 ' + text)
    bot.send_message(message.from_user.id, 'Введите ваше имя: ')


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Отлично, теперь нужно ввести фамилию')
        bot.set_state(message.from_user.id, UserInfoState.surname, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text.title()

    else:
        bot.send_message(message.from_user.id, 'Имя может содержать только буквы. Попробуйте еще раз')


@bot.message_handler(state=UserInfoState.surname)
def get_surname(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Отлично, теперь нужно ввести ваш возраст')
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['surname'] = message.text.title()

    else:
        bot.send_message(message.from_user.id, 'Фамилия может содержать только буквы. Попробуйте еще раз')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Отлично, теперь нужно ввести страну проживания')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = message.text

    else:
        bot.send_message(message.from_user.id, 'Возраст может содержать только цифры. Попробуйте еще раз')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Отлично, теперь нужно ввести город')
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text.title()


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Отлично, теперь нужно подтвердить ваш контактный телефон.'
                                           'Для этого нажмите на кнопку ниже', reply_markup=requsts_contact())
    bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text.title()


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
def get_phone_number(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact'] = message.contact.phone_number

            text = f'Спасибо за предоставленную информацию\n' \
                   f'Ваши данные: \n' \
                   f'Имя - {data["name"]}\n' \
                   f'Фамилия - {data["surname"]}\n' \
                   f'Возраст - {data["age"]}\n' \
                   f'Страна проживания - {data["country"]}\n' \
                   f'Город - {data["city"]}\n' \
                   f'Номер телефона - {data["contact"]}\n\n' \
                   f'Отлично, регистрация прошла успешна'

            bot.send_message(message.from_user.id, text)
            msg = bot.send_message(message.from_user.id, '<b>Введите город для поиска отелей:</b>', parse_mode='html')
            bot.register_next_step_handler(msg, start_req)

    else:
        bot.send_message(message.from_user.id, 'Для отправки контакта нажмите на кнопку ниже')


@bot.message_handler(content_types=['text'])
def start_req(message):

    """Функция для запуска парсинга общей информации по отелям в указанном городе"""
    if message.text.isalpha:
        bot.send_message(message.from_user.id, f'Собираем данные по отелям в {message.text}.\n'
                                               f'Это может занять немного времени')
        city_id = requests_to_api(message.text)
        msg = bot.send_message(message.from_user.id, 'Сколько отелей вывести на экран? ')
        bot.register_next_step_handler(msg, count_hotels, city_id)


    else:
        bot.send_message(message.from_user.id, 'Название должно состоять из букв')


@bot.message_handler(content_types=['text'])
def count_hotels(message, city_id):
    """Функция, которая принимает количество выводимых отелей"""
    get_hotels(city_id, int(message.text))
    bot.send_message(message.from_user.id, 'Выберите команду для поиска:'
                                               '\n/lowprice - покажет самые дешевые отели в выбранном городе'
                                               '\n/highprice - покажет самые дорогие отели в выбранном городе'
                                               '\n/bestdeal - лучшие предложения на рынке')





















