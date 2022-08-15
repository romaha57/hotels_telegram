from keyboards.inline.clean_history import clean_history_button
from keyboards.inline.delete_history import delete_history
from loader import bot
from telebot.types import Message, CallbackQuery
from database.my_db import get_info_from_database, delete_from_db, clean_table, get_favorite, \
    delete_from_favorite
from states.UserStateHistory import UserStateHistory
from keyboards.reply.all_command import all_commands


@bot.message_handler(commands=['history', 'favorite'])
def start(message: Message) -> None:
    bot.set_state(message.from_user.id, UserStateHistory.command, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = message.text

    bot.set_state(message.from_user.id, UserStateHistory.limit, message.chat.id)
    if data["command"] == '/history':
        bot.send_message(message.chat.id, 'Сколько записей истории вывести на экран?')
    else:
        bot.send_message(message.chat.id, 'Сколько записей из избранного вывести на экран?')


@bot.message_handler(state=UserStateHistory.limit)
def show_history(message: Message) -> None:
    """Функция, для вывода информации из БД"""

    if message.text.isdigit():

        # Установка LIMIT для SELECT- запроса с БД
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["limit"] = message.text
        bot.delete_state(message.from_user.id, message.chat.id)
        if data["command"] == '/history':

            # если команда /history
            info = get_info_from_database(message.from_user.id, data["limit"])
            if info:

                # Берем информацию по отелям и делаем читабельный вид
                for element in info:
                    # Преобразовываем записи отелей из БД в отдельные элементы
                    x = element[4].split('\t\t')
                    hotels = ''
                    for el in x:
                        y = el.split('%')
                        try:
                            text = f'\n\nНазвание: {y[1]}' \
                                   f'\nЦена за сутки: {y[2]}'\
                                   f'\nАдрес отеля: {y[3]}'\
                                   f'\nРейтинг отеля: {y[4]}' \
                                   f'\nКоличество звезд: {y[5]}' \
                                   f'\nРасстояние от центра: {y[6]}'
                        except IndexError:
                            text = ''

                            # делаем одну большую строку для вывода информации
                        hotels += text

                    text = f'\n<b>Дата и время:</b> {element[2]}' \
                           f'\n\n<b>Команда:</b> {element[3]}' \
                           f'\n\n<b>Отели:</b> \n{hotels}'
                    msg = bot.send_message(message.chat.id,
                                           text,
                                           parse_mode='html',)
                    bot.send_message(message.chat.id, '♦ Для удаления записи нажмите кнопку',
                                     reply_markup=delete_history(str(element[0]),
                                                                 msg.message_id,
                                                                 command=data["command"]))

                bot.send_message(message.chat.id, '❌ Очистить историю поиска?',
                                 reply_markup=clean_history_button())

                # проверяем количество записей в истории с количеством введенных пользователем
                if len(info) < int(data["limit"]):
                    text = f'*️⃣ Найдено записей: {len(info)}\nБольше записей нет'
                    bot.send_message(message.chat.id, text, reply_markup=all_commands())

            # если ничего не вернется с запроса в БД
            else:
                bot.send_message(message.chat.id, 'В истории пока нет ни одной записи',
                                 reply_markup=all_commands())

        elif data["command"] == '/favorite':

            # получаем данные из таблицы favorite
            info = get_favorite(user_id=message.from_user.id, limit=data["limit"])

            # если данные найдены:
            if info:
                for elem in info:
                    hotel_name = elem[2]
                    msg = bot.send_message(message.chat.id, f'Название отеля: {hotel_name}')

                    bot.send_message(message.chat.id, '♦ Для удаления записи нажмите кнопку',
                                     reply_markup=delete_history(str(elem[0]),
                                                                 msg.message_id,
                                                                 command=data["command"]))

                bot.send_message(message.chat.id, f'Найдено записей: {len(info)}\n'
                                                  f'Записей больше нет',
                                 reply_markup=all_commands())

            # если таблица пустая
            else:
                bot.send_message(message.chat.id, 'В избранном пока нет ни одной записи',
                                 reply_markup=all_commands())

    else:
        bot.send_message(message.chat.id, 'Некорректный ввод. Введите число')


@bot.callback_query_handler(func=lambda call: call.data.startswith('///'))
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок для удаления записи из БД """

    if call.message:
        info = call.data.split('///')
        id_string = info[1]
        message_id = info[2]
        command = info[3]
        if call.data:
            if command == '/history':
                delete_from_db(id_string=id_string)
            else:
                delete_from_favorite(id_string=id_string)
            bot.edit_message_text('Запись удалена', call.message.chat.id, message_id=message_id)

            # удаляем сообщение с кнопкой об удалении
            bot.delete_message(call.message.chat.id, message_id=str(int(message_id) + 1))


@bot.callback_query_handler(func=lambda call: call.data == 'clean_history')
def clean_history(call: CallbackQuery) -> None:
    if call.message:
        count_str = clean_table()
        bot.send_message(call.message.chat.id, f'Удалено {count_str} записей')
        bot.send_message(call.message.chat.id, 'Больше записей в истории нет',
                         reply_markup=all_commands())


