import requests
import json
from config_data import config


HEADARS = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def requests_to_api(city):
    """Функция, для get запроса и получение информации об указанном городе"""

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": str(city)}  # здесь указывается город
    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)

            return data["suggestions"][0]["entities"][0]["destinationId"]


    except Exception as e:
        print('Ошибка', e)


def get_hotels(city_id, count=10):
    """Функция, для получения информации по отелям в указанном(выше) городе"""

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": "25",
                   "checkIn": "2020-01-08", "checkOut": "2020-01-15", "adults1": "1",
                   "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
            hotel_id = data["data"]["body"]["searchResults"]["results"][0]["id"]
            number = 0
            while number != count:
                number += 1
                # Выводим count самых дешевых отелей и информацию по ним
                hotel_name = data["data"]["body"]["searchResults"]["results"][number]["name"]
                hotel_id = data["data"]["body"]["searchResults"]["results"][number]["id"]
                hotel_price = data["data"]["body"]["searchResults"]["results"][number]["ratePlan"]["price"]["current"]
                hotel_address = data["data"]["body"]["searchResults"]["results"][number]["address"]["streetAddress"]
                hotel_rating = data["data"]["body"]["searchResults"]["results"][number]["guestReviews"]["rating"]
                hotel_star = data["data"]["body"]["searchResults"]["results"][number]["starRating"]
                hotel_dist = data["data"]["body"]["searchResults"]["results"][number]["landmarks"][0]["distance"]
                print(hotel_name)

                # get_photo(hotel_id)

    except Exception as e:
        print('Ошибка', e)


def get_photo(hotel_id):
    """Функция для получения фото по id отеля"""

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": str(hotel_id)}
    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
            with open('photo.json', 'a') as file:
                json.dump(data, file, indent=4)

    except Exception as e:
        print('Ошибка', e)

