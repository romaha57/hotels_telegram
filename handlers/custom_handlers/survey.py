from loader import bot
from keyboards.reply.contact_button import requsts_contact
from states.contact_information import UserInfoState
from telebot.types import Message


@bot.message_handler(commands=['survey'])
def survey(message):
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    bot.send_message(message.from_user.id, f'Здравствуйте {message.from_user.username}, пожалуйста введите свое имя')


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
                   f'Номер телефона - {data["contact"]}'

            bot.send_message(message.from_user.id, text)

    else:
        bot.send_message(message.from_user.id, 'Для отправки контакта нажмите на кнопку ниже')

