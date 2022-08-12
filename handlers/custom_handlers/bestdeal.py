from telebot.types import Message
from keyboards.inline.question_photo_low import question_photo_low
from loader import bot
from states.UserStateLow import UserStateLow


@bot.message_handler(state=UserStateLow.prices)
def set_prices(message: Message) -> None:
    try:
        prices = message.text.split('-')
        start_price = int(prices[0].strip())
        stop_price = int(prices[1].strip())

        bot.send_message(message.chat.id,
                         '🔛 Отлично, теперь укажите диапазон расстояния от центра(пример: 0.5 - 5)')
        bot.set_state(message.from_user.id, UserStateLow.distances, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['prices'] = (start_price, stop_price)

    except BaseException:
        bot.send_message(message.chat.id, 'Некорректный ввод.Попробуйте еще раз')


@bot.message_handler(state=UserStateLow.distances)
def date(message: Message) -> None:
    """Функция, для запроса количества отелей """

    try:
        dists = message.text.split('-')
        start_dist = float(dists[0].strip())
        stop_dist = float(dists[1].strip())

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = (start_dist, stop_dist)

        bot.set_state(message.chat.id, UserStateLow.photo_count)
        bot.send_message(message.chat.id, '📸 Вывести результат поиска с фото?',
                         reply_markup=question_photo_low())

    except BaseException:
        bot.send_message(message.chat.id, 'Ошибка ввода.Попробуйте еще раз')

