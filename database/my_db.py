import sqlite3
from typing import Tuple, List


def create_db_hotels() -> None:
    """Функция, которая создает БД hotels"""

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

    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()

        select_request = """SELECT * FROM
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
