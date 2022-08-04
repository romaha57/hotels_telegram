import sqlite3


def add_in_db(users_info, hotels):
    connect = sqlite3.connect('hotels.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        date TEXT,
        command TEXT,
        hotels TEXT)
    ''')

    # Делаем из списка кортежей с информацией по отелям в одну большую строку, чтобы записать в БД
    total_hotels = ''
    for i in hotels:
        hotel = ''
        for j in i:
             hotel += str(j) + ' '
        total_hotels += hotel + '\t\t'
    users_info = list(users_info)
    users_info.append(total_hotels)

    cursor.execute("""INSERT INTO users(user_id, date, command, hotels) 
                    VALUES(?, ?, ?, ?)""", users_info)

    connect.commit()
    connect.close()

