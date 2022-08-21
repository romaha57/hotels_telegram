import requests
import json
from config_data import config
from typing import List, Tuple, Dict
from loguru import logger


HEADARS = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def search_info_about_hotels(data: Dict, command: str, dist: float) -> List[Tuple]:
    """Функция, которая ищет характеристики отеля и создает для каждого отеля свой кортеж,
    а затем добавляет этот кортеж в общий список отелей и возвращает его"""

    number = 0
    # создаем пустой список, который будем наполнять спарсенными отелями
    hotels = []
    for _ in data["data"]["body"]["searchResults"]["results"]:
        hotel_dist = data.get("data", {}
                              ).get("body", {}
                                    ).get("searchResults", {}
                                          ).get("results", {}
                                                )[number].get("landmarks", {}
                                                              )[0].get(
            "distance", 'расстояние от центра неизвестно')

        if command == '/bestdeal':

            # заменяем запятую на точку, чтобы перевести число в float
            hotel_dist = hotel_dist.replace(',', '.')
            if float(hotel_dist[:3]) > float(dist):
                continue

        hotel_name = data.get("data", {}
                              ).get("body", {}
                                    ).get("searchResults", {}
                                          ).get("results", {}
                                                )[number].get(
            "name", 'названия нет')

        hotel_id = data.get("data", {}
                            ).get("body", {}
                                  ).get("searchResults", {}
                                        ).get("results", {}
                                              )[number].get(
            "id", '0')

        hotel_price = data.get("data", {}
                               ).get("body", {}
                                     ).get("searchResults", {}
                                           ).get("results", {}
                                                 )[number].get("ratePlan", {}
                                                               ).get("price", {}
                                                                     ).get(
            "current", 'Цена неизвестна')

        # заменяем точку на _, чтобы при ценах в переводе в float, например 3.555,
        # он представлял как 3555

        hotel_price = hotel_price.replace('.', '_')
        if hotel_price != 'цена неизвестна':
            hotel_price = str(hotel_price).replace(',', '.')

        hotel_address = data.get("data", {}
                                 ).get("body", {}
                                       ).get("searchResults", {}
                                             ).get("results", {}
                                                   )[number].get("address", {}
                                                                 ).get(
            "streetAddress", 'Адрес отсутствует,')

        hotel_rating = data.get("data", {}
                                ).get("body", {}
                                      ).get("searchResults", {}
                                            ).get("results", {}
                                                  )[number].get("guestReviews", {}
                                                                ).get(
            "rating", 'Рейтинг отеля неизвестен')

        hotel_star = data.get("data", {}
                              ).get("body", {}
                                    ).get("searchResults", {}
                                          ).get("results", {}
                                                )[number].get(
            "starRating", 'неизвестно')
        if hotel_star == 0.0:
            hotel_star = 'неизвестно'

        hotel_lat = data.get("data", {}
                             ).get("body", {}
                                   ).get("searchResults", {}
                                         ).get("results", {}
                                               )[number].get(
            "coordinate", {}).get("lat", 'неизвестно')

        hotel_lon = data.get("data", {}
                             ).get("body", {}
                                   ).get("searchResults", {}
                                         ).get("results", {}
                                               )[number].get("coordinate", {}
                                                             ).get(
            "lon", 'неизвестно')

        # создаем кортеж характеристик для каждого отеля и добавляем в общий список отелей
        new_tuple = (
            hotel_id, hotel_name, hotel_price, hotel_address, hotel_rating,
            hotel_star, hotel_dist, hotel_lat, hotel_lon
        )
        hotels.append(new_tuple)
        number += 1

    return hotels


def requests_to_api(url: str, querystring: (str, Dict)) -> (Dict, None):
    """Функция, для подключения к API rapidapi.com"""

    try:
        req = requests.get(url=url, headers=HEADARS, params=querystring, timeout=20)
        if req.status_code == 200:
            logger.debug('Успешное подключение к API-hotels')
            data = json.loads(req.text)
            return data
        else:
            logger.warning('Произошла ошибка при подключении к API-hotels')
            return None

    # ловим ошибку превышения время ожидания
    except requests.exceptions.ReadTimeout:
        logger.warning("Превышено время ожидания для подключения к API hotels")
        return None


def get_city_id(city_name: str) -> (str, None):
    """Функция, для get запроса и получение информации по отелям в указанном городе"""

    data = requests_to_api(url="https://hotels4.p.rapidapi.com/locations/v2/search",
                           querystring={"query": city_name, "locale": "ru_RU"})

    # возвращаем id города или None, если id не найден
    if data is not None:
        logger.debug('Данные по городу получены успешно')
        try:
            return data.get("suggestions", {})[0].get("entities", {})[0].get("destinationId")
        # почему-то иногда выдает ошибку и не находит id города
        except AttributeError:
            logger.warning("Ошибка при получении city_id из данных API-hotels")
            'attribute_error'
        except IndexError:
            logger.warning("Ошибка при получении city_id из данных API-hotels")
            return 'index_error'
    else:
        logger.warning("Данные по городу не получены из-за ошибки подключения к API")
        return None


def get_hotels(city_id: str, search_info: str, count: int, check_in: str,
               check_out: str, start_price=0, stop_price=100000,
               dist=0.0, command=None) -> (List[Tuple], None):

    """Функция, для получения информации по отелям в указанном(выше) городе"""

    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(count),
                   "checkIn": check_in, "checkOut": check_out, "adults1": "1",
                   "priceMin": str(start_price), "priceMax": str(stop_price),
                   "sortOrder": search_info, "locale": "ru_RU", "currency": "USD"}

    data = requests_to_api(url="https://hotels4.p.rapidapi.com/properties/list",
                           querystring=querystring)

    if data is not None:
        logger.debug('Данные по отелям получены успешно')
        # вызываем функцию для сбора характеристик отеля
        hotels = search_info_about_hotels(data=data,
                                          command=command,
                                          dist=dist)

        # возвращаем список отелей
        return hotels

    else:
        logger.warning("Данные по отелям не получены из-за ошибки подключения к API")
        return None


def get_photo(hotel_id: int, photo_count: str):
    """Функция для получения фото по id отеля"""

    data = requests_to_api(url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos",
                           querystring={"id": hotel_id})

    if data is not None:
        logger.debug('Данные по фото отелей получены успешно')
        photo_list = []
        for photo in data["hotelImages"]:

            # Проверяем количество спарсенных фото
            if len(photo_list) == int(photo_count):
                break

            # превращаем строку в ссылку на фото и добавляем в список
            temp = photo["baseUrl"][:-11] + '.jpg'
            photo_list.append(temp)

        return photo_list
