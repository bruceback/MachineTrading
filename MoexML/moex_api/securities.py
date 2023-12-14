import requests
from datetime import datetime
import pandas as pd
import typing as tp


def find_on_moex(query: str, page: int = 1) -> tp.Optional[pd.DataFrame]:
    """
    Делает запрос на поиск финансовых инструментов по Московской бирже
    :param query: Строковый запрос
    :param page: Номер страницы
    :return: Таблица с найденными финансовыми инструментами в формате pandas
    """
    useless_info = ["id", "regnumber", "isin", "emitent_id", "emitent_inn", "emitent_okpo", "emitent_title", "gosreg"]
    res_json = requests.get(f"https://iss.moex.com/iss/securities.json?q={query}&start={(page - 1) * 100}").json()

    try:
        data = [{k: r[i] for i, k in enumerate(res_json['securities']['columns']) if k not in useless_info} for r in
                res_json['securities']['data']]
        res_df = pd.DataFrame(data)
        res_df[["engine", "market"]] = res_df.group.str.split("_", expand=True)
        res_df.drop(columns="group")
    except KeyError:
        return
    except AttributeError:
        return

    return res_df


def get_history_on_page(security_id: str, engine: str, market: str,
                        start_date: str = None,
                        end_date: str = None,
                        page: int = 1) -> tp.Optional[pd.DataFrame]:
    """
    Запрашивает историю финансового инструмента на определенной странице
    :param security_id: Идентификатор финансового инструмента
    :param engine: Наименование торговой системы, например, stock (Фондовый рынок и рынок депозитов)
    :param market: Наименование рынка торговой системы, например, shares (Рынок акций в stock)
    :param start_date: Дата начала наблюдений. По умолчанию с самого первого наблюдения
    :param end_date: Дата конца наблюдений. По умолчанию до самого последнего наблюдения
    :param page: Номер страницы
    :return: Таблица с историей на странице
    """

    res_json = requests.get(
        f"http://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security_id}.json?start={(page - 1) * 100}"
        f"{'&from=' + start_date if start_date else ''}"
        f"{'&till=' + end_date if end_date else ''}").json()
    try:
        data = [{k: r[i] for i, k in enumerate(res_json['history']['columns'])} for r in
                res_json['history']['data']]
        if not data:
            return None
    except KeyError:
        return

    res_df = pd.DataFrame(data)
    return res_df


def get_history(security_id: str, engine: str, market: str,
                start_date: str = None,
                end_date: str = None, ) -> tp.Optional[pd.DataFrame]:
    """
    Запрашивает всю историю финансового инструмента
    :param security_id: Идентификатор финансового инструмента
    :param engine: Наименование торговой системы, например, stock (Фондовый рынок и рынок депозитов)
    :param market: Наименование рынка торговой системы, например, shares (Рынок акций в stock)
    :param start_date: Дата начала наблюдений. По умолчанию с самого первого наблюдения
    :param end_date: Дата конца наблюдений. По умолчанию до самого последнего наблюдения
    :return: Таблица со всей историей
    """
    all_history = get_history_on_page(security_id, engine, market, start_date=start_date, end_date=end_date, page=1)
    page = 2
    while True:
        history_on_page = get_history_on_page(security_id, engine, market, start_date=start_date, end_date=end_date, page=page)
        if history_on_page is None:
            break
        all_history = pd.concat([all_history, history_on_page])
        page += 1
    return all_history
    # [["BOARDID", "TRADEDATE", "WAPRICE"]]


def get_current_candles(security_id: str, engine: str, market: str,) -> tp.Optional[pd.DataFrame]:
    """
    Запрашивает свечи финансового инструмента на текущий день
    :param security_id: Идентификатор финансового инструмента
    :param engine: Наименование торговой системы, например, stock (Фондовый рынок и рынок депозитов)
    :param market: Наименование рынка торговой системы, например, shares (Рынок акций в stock)
    :return: Таблица со свечами
    """

    res_json = requests.get(
        f"http://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security_id}/candles.json?"
        f"&from={datetime.now().strftime('%Y-%m-%d')}").json()
    try:
        data = [{k: r[i] for i, k in enumerate(res_json['candles']['columns'])} for r in
                res_json['candles']['data']]
        if not data:
            return None
    except KeyError:
        return

    res_df = pd.DataFrame(data)
    return res_df


def get_current_price(security_id: str, engine: str, market: str,) -> float:
    """
    Выводит «цену» инструмента, рассчитанную как (low + high) / 2 предыдущей свечи # доступ к стакану платный :(
    :param security_id: Идентификатор финансового инструмента
    :param engine: Наименование торговой системы, например, stock (Фондовый рынок и рынок депозитов)
    :param market: Наименование рынка торговой системы, например, shares (Рынок акций в stock)
    :return: текущая цена
    """
    candles = get_current_candles(security_id, engine, market)
    last_candle = candles.iloc[-1]
    price = (last_candle["low"] + last_candle["high"]) / 2
    return price


def get_portfolio_price(portfolio: dict):
    price = 0
    for security_id, amount in portfolio.items():
        price += get_current_price(security_id, "stock", "shares") * amount
    return price
