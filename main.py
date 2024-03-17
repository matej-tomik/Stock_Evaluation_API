import yfinance as yf
import redis
from fastapi import FastAPI
from typing import List, Tuple
import datetime
from stock_screen_analyser.classes import StockValuation
from pydantic import BaseModel


TREASURY_YLD_INDEX_TEN_YEAR: str = "^TNX"


app = FastAPI()
redis_database = redis.Redis(host='localhost', port=6379, db=0)


def get_current_time():
    return datetime.datetime.now().date()


def get_risk_free_rate() -> float:
    return round(yf.Ticker(TREASURY_YLD_INDEX_TEN_YEAR).info.get('regularMarketPreviousClose', 0.04) / 100, 4)


def store_stock(stock: dict):
    stock.update({'date': get_current_time})
    ticker = str(stock.pop('ticker')).lower()
    print(stock)
    if redis_database.exists(ticker) and redis_database.hget(ticker, 'date'):
        if redis_database.hget(ticker, 'date').decode('utf-8') == get_current_time:
            return
    for key, value in stock.items():
        print(ticker, key, value)
        redis_database.hset(ticker, key, value)
    return


def analyse_stock(ticker: str, risk_free_rate: float) -> Tuple[dict, bool]:
    is_in_redis: bool = False
    if redis_database.exists(ticker) and redis_database.hget(ticker, 'date'):
        print(redis_database.hget(ticker, 'date'), 'analyse stock')
        if redis_database.hget(ticker, 'date').decode('utf-8') == get_current_time:
            is_in_redis: bool = True
            return {key.decode('utf-8'): value.decode('utf-8') for key, value in redis_database.hgetall(ticker).items()}, is_in_redis
    security = StockValuation(ticker, risk_free_rate)
    security.fetch_data()
    security.evaluate()
    print(security, security.result_set)
    return ({
        'graham_num': security.graham_num,
        'graham':  security.graham,
        'dcf_advance': security.dcf_advanced,
        'ddm_advance': security.ddm_advanced,
        'dcf': security.dcf,
        'ddm': security.ddm,
        'ticker': security.ticker,
    }, True)


@app.get("/ticker/{ticker}")
async def process_ticker(item: str):
    result, is_in_redis = analyse_stock(item, get_risk_free_rate())
    if not is_in_redis:
        store_stock(result)
    return result 


class Items(BaseModel):
    items: List[str]


@app.post("/tickers")
async def evaluated_stock_list(list_of_tickers: Items):
    evaluated_stocks = {
        "results": {},
        "failed": {}
    }
    for ticker in list_of_tickers.items:
        analysed_stock, is_in_redis = analyse_stock(ticker, get_risk_free_rate())
        if not is_in_redis:
            store_stock(analysed_stock)
        if [*analysed_stock.values()][:5].count('N/A') <= 2:
            evaluated_stocks['results'].update({analysed_stock['ticker']: analysed_stock})
        else:
            evaluated_stocks['failed'].update({analysed_stock['ticker']: analysed_stock})
    return evaluated_stocks
