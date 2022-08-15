import sqlite3
from typing import Tuple, List


def create_db_hotels() -> None:
    """Функция, которая создает БД hotels и таблицу в ней users"""

    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INT,
                        date TEXT,
                        command TEXT,
                        hotels TEXT)
                    ''')


def add_in_db(users_info: Tuple, hotels: List[Tuple]) -> None:
    """Функция, которая добавляет данные в БД"""

    # Делаем из списка кортежей с информацией об отелях в одну большую строку, чтобы записать в БД
    total_hotels = ''
    for i in hotels:
        hotel = ''
        for j in i:
             hotel += str(j) + '%'
        total_hotels += hotel + '\t\t'
    users_info = list(users_info)
    users_info.append(total_hotels)

    create_db_hotels()
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""INSERT INTO users(user_id, date, command, hotels) 
                    VALUES(?, ?, ?, ?)""", users_info)


def get_info_from_database(user_id: int, limit: str) -> List:
    """Функция, которая выводит информацию по отелям из БД"""

    with sqlite3.connect('hotels.db') as connect:
        cursor = connect.cursor()

        select_request = f"""SELECT * FROM
        (SELECT * FROM users WHERE user_id = ? ORDER BY id DESC LIMIT ?) 
        ORDER BY id"""
        info = cursor.execute(select_request, (user_id, limit))

        # Возвращаем кортежи из БД для определенного id пользователя
        return info.fetchall()


def delete_from_db(id_string):
    """Функция, для удаления записи из истории(БД)"""

    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("DELETE from users WHERE id = ?", (id_string,))


def clean_table() -> int:
    """Функция, которая удаляет все записи из БД"""

    with sqlite3.connect('hotels.db') as connect:
        cursor = connect.cursor()
        cursor.execute("DELETE FROM users;",)
        count_str = cursor.rowcount

    # возвращаем количество удаленных записей
    return count_str


def create_table_favorite() -> None:
    """Функция, которая создает БД hotels и таблицу в ней favorite"""

    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS favorite (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INT,
                            hotel TEXT)
                        ''')


def add_in_favorite(user_id: int, hotel_name: str) -> None:
    """Функция, которая добавляем отель в избранное """

    create_table_favorite()
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""INSERT INTO favorite(user_id, hotel) 
                    VALUES(?, ?)""", (user_id, hotel_name))


def get_favorite(user_id: int, limit: str) -> List:
    """Функция, которая выводит информацию по данным из таблицы favorite"""

    with sqlite3.connect('hotels.db') as connect:
        cursor = connect.cursor()
        select_request = """SELECT * FROM
           (SELECT * FROM favorite WHERE user_id = ? ORDER BY id DESC LIMIT ?) 
           ORDER BY id"""
        info = cursor.execute(select_request, (user_id, limit))

        # Возвращаем кортежи из БД для определенного id пользователя
        return info.fetchall()


def delete_from_favorite(id_string):
    """Функция, для удаления записи из истории(БД)"""

    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("DELETE from favorite WHERE id = ?", (id_string,))


