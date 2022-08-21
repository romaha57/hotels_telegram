Telegram-бот для поиска отелей с помощью сайта hotels.com и его API
Этот бот позволяет быстро подбирать отели прямо в мессенджере Telegram по различным критериям поиска. Попробуйте использовать бот: @EasyTravelsBot

Данный бот позволяет:

- подбирать отели по самой низкой или высокой цене;
- подбирать отели по заданному ценовому диапазону и расстоянию от центра города;
- выводить историю поиска, а так же удалять записи из ней
- добавлять/удалять и просматривать избранные отели
- отображать геопозицию отеля на карте
- переходить на сайт отеля для брони

Примечание о безопасности:

Бот не использует и не запрашивает никакие персональные данные.

Requirements

pyTelegramBotAPI==4.4.0

python-dotenv==0.19.2

python-telegram-bot-calendar==1.0.5

requests== 2.28.1

loguru==0.6.0

Команды бота:

/start - запуск бота

/lowprice - поиск дешевых отелей в указанном городе

/highprice - поиск дорогих отелей в указанном городе

/bestdeal - поиск отелей с указанным ценовым диапазоном и расстояние от центра города

/history - история поиска

/favorite - избранные отели

/help - справка по командам



Инструкция по работе с ботом:

1. Вводите команду /start

3. Затем выбираете одну из нужных вам команд
 
5. Далее следуете инструкциям от бота