from pathlib import Path
import sqlite3


MODULE_PATH = Path(__file__)
# print(MODULE_PATH)


def get_connection():
    connection = sqlite3.connect(MODULE_PATH.parent / "machine_trading.db")
    return connection
