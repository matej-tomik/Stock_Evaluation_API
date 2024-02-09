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




TREASURY_YLD_INDEX_TEN_YEAR: str = "^TNX"


app = FastAPI()
r= redis.Redis(host='localhost', port=6379, db=0)


def get_current_time():
    return datetime.datetime.now().date()


def zip_file(result_path: Path, failed_path: Path) -> Path:
    zips_dir = Path("./zips")
    zips_dir.mkdir(exist_ok=True)
    zip_path = zips_dir / "files.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(result_path / 'result.csv','result.csv')
        zipf.write(failed_path / 'failed.csv','failed.csv')


def remove_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def get_risk_free_rate() -> float:
    return round(yf.Ticker(TREASURY_YLD_INDEX_TEN_YEAR).info.get('regularMarketPreviousClose', 0.04) / 100, 4)



def evaluate_stock(stock: dict):
    if all(x > 2 for x in [*stock.values()][:5]):
        stock.update({'date': get_current_time})
        ticker = str(stock.pop('ticker')).lower()
        if r.exists(ticker):
            if r.hget(ticker, 'date').decode('utf-8') == get_current_time:
                return
            else:
                for key, value in stock.items():
                    r.hset(ticker, key, value)
                return  
        for key, value in stock.items():
            r.hset(ticker, key, value)      
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


def get_evaluated_stock_list(list_of_tickers:List[str]) -> dict[str, dict]:
    risk_free_rate = get_risk_free_rate()
    evaluated_stocks = {
        "results": {},
        "failed": {}
    }
    for ticker in list_of_tickers:
        analysed_stock = analyse_stock(ticker, risk_free_rate)
        if [*analysed_stock.values()][:5].count('N/A') <= 2:
            evaluated_stocks['results'].update({analysed_stock['ticker']: analysed_stock})
            evaluate_stock(analysed_stock)
        else:
            evaluated_stocks['failed'].update({analysed_stock['ticker']: analysed_stock})
    return evaluated_stocks


def analyse_screen(file_path: str, ticker_column_name: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'r') as f:
        headers = f.readline()
        stocks = [stock.split(',') for stock in f.readlines()]

    index: int = headers.index(ticker_column_name)

    filed_path = Path("./failed")
    filed_path.mkdir(exist_ok=True)
    result_path = Path("./results")
    result_path.mkdir(exist_ok=True)
    with open(result_path / 'result.csv', mode='w', newline='') as result:
        with open(filed_path / 'failed.csv', mode='w', newline='') as failed:
            write_heade((result, failed))
            risk_free_rate = get_risk_free_rate()
            for stock in stocks:
                analysed_stock = analyse_stock(stock[index],risk_free_rate)
                file = failed
                if [*analysed_stock.values()][:5].count('N/A') <= 2:
                    file = result
                    evaluate_stock(analysed_stock)
                csv.writer(file).writerow([','.join([str(value) for value in [*analysed_stock.values()]])])

    return zip_file(result_path, filed_path)


@app.get("/file_to_analise")
async def create_upload_file(file: UploadFile = File(...), ticker_column_name: str = ""):
    file_path = f"./screens/{file.filename}"
    with open(file_path, "wb") as new_file:
        new_file.write(file.file.read())
    try:
        zip_path = analyse_screen(file_path, ticker_column_name)
        return FileResponse(zip_path, filename="csv_files.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def cleanup_temp_dir():
    for directory_path in (Path("./zips"), Path("./results"), Path("./failed")):
        remove_files_in_directory(directory_path)


@app.on_event("startup")
async def cleanup_temp_dir():
    for directory_path in (Path("./zips"), Path("./results"), Path("./failed")):
        remove_files_in_directory(directory_path)
