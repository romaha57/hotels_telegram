from telebot.types import Message
from keyboards.inline.question_photo import question_photo
from loader import bot
from states.UserState import UserState


@bot.message_handler(state=UserState.prices)
def set_prices(message: Message) -> None:
    """Функция, которая проверяет диапазон цены на корректность ввода и
    запрашивает диапазон расстояния от центра"""
    try:
        prices = message.text.split('-')
        start_price = int(prices[0].strip())
        stop_price = int(prices[1].strip())

        text = '🔛 Отлично, теперь укажите максимальную желаемую удаленность от центра' \
               '(в км, например 0.5):'

        msg = bot.send_message(message.chat.id, text)
        bot.set_state(message.from_user.id, UserState.distances, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['prices'] = (start_price, stop_price)
            data["msg_id"]["msg_id_dist"] = msg.message_id
            data["msg_id"]["msg_id_price_range2"] = message.message_id

    except TypeError:
        msg = bot.send_message(message.chat.id, 'Некорректный ввод.Попробуйте еще раз')
        with bot.retrieve_data(message.chat.id) as data:
            data["msg_id"]["msg_id_mistake4"] = msg.message_id


@bot.message_handler(state=UserState.distances)
def date(message: Message) -> None:
    """Функция, которая проверяет диапазон расстояния от центра на корректность ввода и
    устанавливает состояние на photo_count, чтобы вернуться на основной сценарий"""

    if not message.text.isalpha():

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = message.text
            data["msg_id"]["msg_id_dist2"] = message.message_id

        bot.set_state(message.chat.id, UserState.photo_count)
        msg = bot.send_message(message.chat.id, '📸 Вывести результат поиска с фото?',
                               reply_markup=question_photo())
        data["msg_id"]["msg_id_photo_question2"] = msg.message_id

    else:
        msg = bot.send_message(message.chat.id, 'Ошибка ввода, введите число')
        with bot.retrieve_data(message.chat.id) as data:
            data["msg_id"]["msg_id_mistake5"] = msg.message_id
