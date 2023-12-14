from datetime import datetime
import sqlite3
from models import User
from exceptions import TradingError


def get_user(tg: str, connection: sqlite3.Connection):
    cursor = connection.cursor()
    query = 'SELECT * FROM Users WHERE tg = ?'
    user_row = cursor.execute(query, (tg,)).fetchone()
    user = User(tg=user_row[0], balance=user_row[1], all_deposits=user_row[2])
    return user


def add_user(tg: str, connection: sqlite3.Connection):
    cursor = connection.cursor()
    query = 'INSERT INTO Users (tg) VALUES (?)'
    try:
        cursor.execute(query, (tg,))
    except sqlite3.IntegrityError:
        return get_user(tg, connection)

    user = User(tg=tg, balance=0, all_deposits=0)
    connection.commit()
    return user


def deposit(tg: str, money: float, connection: sqlite3.Connection):
    cursor = connection.cursor()
    query = 'UPDATE Users SET balance = balance + ?, all_deposits = all_deposits + ? WHERE tg = ?'
    cursor.execute(query, (money, money, tg))
    user = get_user(tg, connection)
    connection.commit()
    return user


def update_balance(tg: str, money: float, connection: sqlite3.Connection):
    cursor = connection.cursor()
    query = 'UPDATE Users SET balance = balance + ? WHERE tg = ?'
    cursor.execute(query, (money, tg))
    user = get_user(tg, connection)
    connection.commit()
    return user


def get_portfolio(tg: str, connection: sqlite3.Connection):
    cursor = connection.cursor()
    query = 'SELECT primary_boardid, SUM(amount) FROM TradingHistory WHERE user_tg = ? GROUP BY primary_boardid'
    cursor.execute(query, (tg,))
    portfolio = dict(cursor.fetchall())
    return portfolio


def add_trading_record(tg: str, primary_boardid: str, amount: int, price: float, connection: sqlite3.Connection):
    cursor = connection.cursor()
    user = get_user(tg, connection)
    portfolio = get_portfolio(tg, connection)

    if amount < 0:
        if primary_boardid not in portfolio:
            raise TradingError(f"There isn't security {primary_boardid} in your portfolio!")

        if amount < -portfolio[primary_boardid]:
            raise TradingError(
                f"There is {portfolio[primary_boardid]} {primary_boardid} in your portfolio not {-amount}!")
    else:
        if user.balance < amount * price:
            raise TradingError(f"{amount * price - user.balance} bucks isn't enough for you!")

    query = 'INSERT INTO TradingHistory (primary_boardid, amount, price, exec_date, user_tg) VALUES (?, ?, ?, ?, ?)'
    exec_date = int(datetime.now().timestamp())
    cursor.execute(query, (primary_boardid, amount, price, exec_date, tg))
    user = update_balance(tg, -amount * price, connection)
    connection.commit()
    return user
