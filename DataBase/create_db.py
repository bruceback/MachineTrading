import sqlite3
from DataBase import MODULE_PATH


connection = sqlite3.connect(MODULE_PATH.parent / 'machine_trading.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        tg TEXT PRIMARY KEY,
        balance REAL DEFAULT 0,
        all_deposits REAL DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS TradingHistory (
        id INTEGER PRIMARY KEY,
        primary_boardid TEXT NOT NULL,
        amount INT NOT NULL,
        price REAL NOT NULL,
        exec_date INT NOT NULL,
        user_tg INTEGER NOT NULL,
            FOREIGN KEY (user_tg)
            REFERENCES Users (tg) 
               ON UPDATE CASCADE
               ON DELETE CASCADE
    )
''')

connection.commit()
connection.close()
