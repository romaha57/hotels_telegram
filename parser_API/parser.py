import requests
import json
from config_data import config

hotels = []
HEADARS = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def requests_to_api(city_name):
    """Функция, для get запроса и получение информации по отелям в указанном городе"""

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city_name}  # здесь указывается город
    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
            return data["suggestions"][0]["entities"][0]["destinationId"]

    except Exception:
        return None


def get_hotels(city_id, search_info, count=10, start_price=0, stop_price=100000):
    """Функция, для получения информации по отелям в указанном(выше) городе"""

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(count),
                   "checkIn": "2020-01-08", "checkOut":"2020-01-15", "adults1": "1",
                   "priceMin": str(start_price), "priceMax": str(stop_price), "sortOrder": str(search_info),
                   "locale": "en_US", "currency": "USD"}

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=10)
        if req.status_code == 200:
            data = json.loads(req.text)
        number = 0
        for elem in data["data"]["body"]["searchResults"]["results"]:
            new_tuple = tuple()
            # Выводим count самых дешевых отелей и информацию по ним
            hotel_name = data["data"]["body"]["searchResults"]["results"][number]["name"]
            hotel_id = data["data"]["body"]["searchResults"]["results"][number]["id"]
            hotel_price = data["data"]["body"]["searchResults"]["results"][number]["ratePlan"]["price"]["current"]
            try:
                hotel_address = data["data"]["body"]["searchResults"]["results"][number]["address"]["streetAddress"]
            except Exception:
                hotel_address = 'Адрес отсутсвует'
            hotel_rating = data["data"]["body"]["searchResults"]["results"][number]["guestReviews"]["rating"]
            hotel_star = data["data"]["body"]["searchResults"]["results"][number]["starRating"]
            hotel_dist = data["data"]["body"]["searchResults"]["results"][number]["landmarks"][0]["distance"]
            new_tuple = (
                hotel_name, hotel_id, hotel_price, hotel_address, hotel_rating, hotel_star, hotel_dist
            )
            hotels.append(new_tuple)
            number += 1

        return hotels

    except Exception:
        return None


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
        print(e)