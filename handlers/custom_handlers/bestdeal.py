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

        bot.send_message(message.chat.id, text)
        bot.set_state(message.from_user.id, UserState.distances, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['prices'] = (start_price, stop_price)

    except TypeError:
        bot.send_message(message.chat.id, 'Некорректный ввод.Попробуйте еще раз')


@bot.message_handler(state=UserState.distances)
def date(message: Message) -> None:
    """Функция, которая проверяет диапазон расстояния от центра на корректность ввода и
    устанавливает состояние на photo_count, чтобы вернуться на основной сценарий"""

    if not message.text.isalpha():

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = message.text

        bot.set_state(message.chat.id, UserState.photo_count)
        bot.send_message(message.chat.id, '📸 Вывести результат поиска с фото?',
                             reply_markup=question_photo())

    else:
        bot.send_message(message.chat.id, 'Ошибка ввода, введите число')

