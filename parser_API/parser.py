import requests
import json
from config_data import config
from typing import List, Tuple


HEADARS = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def requests_to_api(city_name: str) -> int:
    """Функция, для get запроса и получение информации по отелям в указанном городе"""

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city_name, "locale": "ru_RU"}  # здесь указывается город
    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)

            # возвращаем id города
            return data["suggestions"][0]["entities"][0]["destinationId"]

    except Exception as e:
        print(e)


def get_hotels(city_id: int, search_info: str, count: int, start_price=0, stop_price=100000) \
        -> List[Tuple] or None:
    """Функция, для получения информации по отелям в указанном(выше) городе"""

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(count),
                   "checkIn": "2020-01-08", "checkOut":"2020-01-15", "adults1": "1",
                   "priceMin": str(start_price), "priceMax": str(stop_price),
                   "sortOrder": search_info, "locale": "ru_RU", "currency": "USD"}

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
        number = 0
        # создаем пустой список, который будем наполнять спарсенными отелями
        hotels = []
        for elem in data["data"]["body"]["searchResults"]["results"]:
            try:
                hotel_name = data["data"]["body"]["searchResults"]["results"][number]["name"]
            except Exception:

                # Обработка ошибки, если не найдем ключ и вставка значения по умолчанию
                hotel_name = 'Название отеля отсутствует'
            try:
                hotel_id = data["data"]["body"]["searchResults"]["results"][number]["id"]
            except Exception:
                hotel_id = '0'
            try:
                hotel_price = data["data"]["body"]["searchResults"]["results"][number]["ratePlan"]["price"]["current"]
                hotel_price = str(hotel_price).replace(',', '.')
            except Exception:
                hotel_price = 'Цена отсутствует'
            try:
                hotel_address = data["data"]["body"]["searchResults"]["results"][number]["address"]["streetAddress"]
            except Exception:
                hotel_address = 'Адрес отсутствует'
            try:
                hotel_rating = data["data"]["body"]["searchResults"]["results"][number]["guestReviews"]["rating"]
            except Exception:
                hotel_rating = 'Рейтинг отеля отсутствует'
            try:
                hotel_star = data["data"]["body"]["searchResults"]["results"][number]["starRating"]
            except Exception:
                hotel_star = 'Количество звезд у отеля неизвестно'
            try:
                hotel_dist = data["data"]["body"]["searchResults"]["results"][number]["landmarks"][0]["distance"]
            except Exception:
                hotel_dist = 'неизвестно'

            new_tuple = (
                hotel_id, hotel_name, hotel_price, hotel_address, hotel_rating, hotel_star, hotel_dist
            )
            hotels.append(new_tuple)
            number += 1

        # возвращаем список отелей
        return hotels

    except Exception:
        return None


def get_hotels_bestdeal(city_id: int, search_info: str, count: int, start_price: int,
                        stop_price: int, start_dist: int, stop_dist: int, bestdeal_list: List,
                        page_num='1') -> List[Tuple] or None:

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": page_num, "pageSize": "25",
                   "checkIn": "2020-01-08", "checkOut": "2020-01-15", "adults1": "1",
                   "priceMin": str(start_price), "priceMax": str(stop_price),
                   "sortOrder": search_info, "locale": "ru_RU", "currency": "USD"}

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
        number = -1
        while True:
            if len(bestdeal_list) > float(count):
                break
            for elem in data["data"]["body"]["searchResults"]["results"]:
                number += 1
                try:
                    hotel_dist = \
                        data["data"]["body"]["searchResults"]["results"][number]["landmarks"][0]["distance"]
                    hotel_dist = str(hotel_dist).replace(',', '.')

                    # Проверка на вхождение в диапозоне расстояния от центра, указанный пользователем
                    if float(hotel_dist[:3]) < start_dist or float(hotel_dist[:3]) > stop_dist:
                        continue
                except Exception:
                    hotel_dist = 'неизвестно'

                try:
                    hotel_name = data["data"]["body"]["searchResults"]["results"][number]["name"]
                except Exception:
                    hotel_name = 'Название отеля отсутствует'

                try:
                    hotel_id = data["data"]["body"]["searchResults"]["results"][number]["id"]
                except Exception:
                    hotel_id = '0'

                try:
                    hotel_price = \
                        data["data"]["body"]["searchResults"]["results"][number]["ratePlan"]["price"][
                            "current"]
                    hotel_price = str(hotel_price).replace(',', '.')
                except Exception:
                    hotel_price = 'Цена отсутствует'

                try:
                    hotel_address = \
                        data["data"]["body"]["searchResults"]["results"][number]["address"]["streetAddress"]
                except Exception:
                    hotel_address = 'Адрес отсутствует'

                try:
                    hotel_rating = \
                        data["data"]["body"]["searchResults"]["results"][number]["guestReviews"]["rating"]
                except Exception:
                    hotel_rating = 'Рейтинг отеля отсутствует'

                try:
                    hotel_star = \
                        data["data"]["body"]["searchResults"]["results"][number]["starRating"]
                except Exception:
                    hotel_star = 'Количество звезд у отеля неизвестно'

                new_tuple = (
                    hotel_id, hotel_name, hotel_price,
                    hotel_address, hotel_rating, hotel_star, hotel_dist
                    )

                if hotel_id != '0':
                    bestdeal_list.append(new_tuple)
                    continue
            else:
                # Переход на следующую страницу для парсинга
                new_page = int(page_num)
                new_page += 1
                new_page = str(new_page)
                get_hotels_bestdeal(city_id=city_id,
                                    search_info="DISTANCE_FROM_LANDMARK",
                                    count=count,
                                    start_price=start_price,
                                    stop_price=stop_price,
                                    start_dist=start_dist,
                                    stop_dist=stop_dist,
                                    bestdeal_list=bestdeal_list,
                                    page_num=new_page,)

        return bestdeal_list[:int(count)]

    except Exception as e:
        print(e)
        return None


def get_photo(hotel_id: int, photo_count: str):
    """Функция для получения фото по id отеля"""

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=20)
        if req.status_code == 200:
            data = json.loads(req.text)

            photo_list = []
            try:
                for photo in data["hotelImages"]:

                    # Проверяем колиечство спарсенных фото
                    if len(photo_list) == int(photo_count):
                        break
                    # превращаем строку в ссылку на фото и добавляем в список
                    temp = photo["baseUrl"][:-11] + '.jpg'
                    photo_list.append(temp)
                return photo_list

            except Exception:
                return None

    except Exception as e:
        print(e, 'ошибка')
