import pandas as pd


def prepare_history(history: pd.DataFrame, target_col: str = "WAPRICE") -> pd.DataFrame:
    """
    Предобработка истории торгов
    :param target_col:
    :param remained_columns:
    :param history: история торгов
    :return: обработанная история торогов
    """

    history = history[history["BOARDID"] == "TQBR"]
    history = history[["TRADEDATE", "WAPRICE"]]
    history[target_col] = history[target_col].fillna(history[target_col].rolling(17, min_periods=1).median())

    return history
