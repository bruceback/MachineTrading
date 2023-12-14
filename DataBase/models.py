from dataclasses import dataclass


@dataclass
class User:
    tg: str
    balance: float
    all_deposits: float

@dataclass
class TradingRecord:
    id: int
    primary_boardid: str
    amount: int
    price: float
    exec_date: int
    user_tg: str
