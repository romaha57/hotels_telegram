import sqlite3


def add_in_db(users_tuple):
    connect = sqlite3.connect('hotels.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        date TEXT,
        command TEXT,
        hotels TEXT)
    ''')
    cursor.execute("""INSERT INTO users(user_id, date, command) VALUES(?, ?, ?)""", users_tuple)
    connect.commit()
    connect.close()

