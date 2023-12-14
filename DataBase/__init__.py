from pathlib import Path
import sqlite3


MODULE_PATH = Path(__file__)


def get_connection():
    connection = sqlite3.connect(MODULE_PATH / "machine_trading.db")
    return connection
