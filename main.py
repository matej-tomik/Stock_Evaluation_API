from classes import StockFinancials
import os
import yfinance as yf
import redis
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List, Tuple
import csv
from fastapi.responses import FileResponse
from pathlib import Path
import zipfile
import datetime
from io import TextIOWrapper
from pydantic import BaseModel




TREASURY_YLD_INDEX_TEN_YEAR: str = "^TNX"


app = FastAPI()
pepek = redis.Redis(host='localhost', port=6379, db=0)


def get_current_time():
    return datetime.datetime.now().date()


def get_risk_free_rate() -> float:
    return round(yf.Ticker(TREASURY_YLD_INDEX_TEN_YEAR).info.get('regularMarketPreviousClose', 0.04) / 100, 4)


def store_stock(stock: dict):
    stock.update({'date': get_current_time})
    ticker = str(stock.pop('ticker')).lower()
    if pepek.exists(ticker) and pepek.hget(ticker, 'date').decode('utf-8') == get_current_time:
        return
    else:
        for key, value in stock.items():
            pepek.hset(ticker, key, value)
        return  



def write_heade(files :Tuple[TextIOWrapper]):
    header_row = [
        "Graham number Result",
        "DCF Advance Model Result",
        "DDM Advance Model Result",
        "DCF Simple Model Result",
        "DDM Simple Model Result",
        "Ticker symbol",
        "Name",
        "Market Cap",
        "Country",
        "Sector",
        "Industry"
    ]
    for file in files:
        csv.writer(file).writerow(header_row)


def analyse_stock(ticker: str, risk_free_rate: float) -> dict:
    if pepek.exists(ticker) and pepek.hget(ticker, 'date').decode('utf-8') == get_current_time:
        return {key.decode('utf-8'): value.decode('utf-8') for key, value in pepek.hgetall(ticker).items()}    
    security = StockFinancials(ticker, risk_free_rate)
    return{
        'graham_result':  security.graham_result,
        'dcf_advance_result': security.dcf_advance_result,
        'ddm_advance_result': security.ddm_advance_result,
        'dcf_simple_result': security.dcf_simple_result,
        'ddm_simple_result': security.ddm_simple_result,
        'ticker': security.ticker,
        'name': security.name,
        'market_capital': security.market_capital,
        'country': security.country,
        'sector': security.sector,
        'industry': security.industry
    }


class Item(BaseModel):
    ticker: str = ''


@app.get("/ticker")
async def process_ticker(item: Item):
    result = analyse_stock(item, get_risk_free_rate())
    store_stock(result)
    return result 


@app.get("/tickers")
async def evaluated_stock_list(list_of_tickers: List[Item]):
    risk_free_rate = get_risk_free_rate()
    evaluated_stocks = {
        "results": {},
        "failed": {}
    }
    for ticker in list_of_tickers:
        analysed_stock = analyse_stock(ticker, risk_free_rate)
        store_stock(analyse_stock)
        if [*analysed_stock.values()][:5].count('N/A') <= 2:
            evaluated_stocks['results'].update({analysed_stock['ticker']: analysed_stock})
        else:
            evaluated_stocks['failed'].update({analysed_stock['ticker']: analysed_stock})
    return evaluated_stocks
