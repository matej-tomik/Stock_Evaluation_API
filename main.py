from classes import StockFinancials
import os
import yfinance as yf
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import csv
from fastapi.responses import FileResponse
from pathlib import Path
import zipfile



TREASURY_YLD_INDEX_TEN_YEAR: str = "^TNX"


app = FastAPI()


@app.post("/update_file")
async def create_upload_file(file: UploadFile = File(...), ticker_column_name: str = ""):
    file_path = f"./screens/{file.filename}"
    # Save the uploaded file to the specified path
    with open(file_path, "wb") as new_file:
        new_file.write(file.file.read())
    try:
        zip_path = analyse_screen(file_path, ticker_column_name)
        return FileResponse(zip_path, filename="csv_files.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def evaluate_stock():
    pass


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


def analyse_screen(file_path: str, ticker_column_name: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'r') as f:
        headers = f.readline()
        stocks = [stock.split(',') for stock in f.readlines()]

    index: int = headers.index(ticker_column_name)

    filed_dir = Path("./failed")
    filed_dir.mkdir(exist_ok=True)
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / 'result.csv', mode='w', newline='') as result:
        with open(filed_dir / 'failed.csv', mode='w', newline='') as failed:
            csv.writer(result).writerow(["Graham number Result,DCF Advance Model Result,DDM Advance Model Result,DCF Simple Model Result,DDM Simple Model Result,Ticker symbol,Name,Market Cap, Country,Sector,Industry"])
            csv.writer(failed).writerow(["Graham number Result,DCF Advance Model Result,DDM Advance Model Result,DCF Simple Model Result,DDM Simple Model Result,Ticker symbol,Name,Market Cap, Country,Sector,Industry"])
            risk_free_rate: float = yf.Ticker(TREASURY_YLD_INDEX_TEN_YEAR).info.get('regularMarketPreviousClose', 0.04) / 100  # constant 0.04 get from sqeel ; )
            for stock in stocks:
                analysed_stock = analyse_stock(stock[index],risk_free_rate)
                file = failed
                if [*analysed_stock.values()][:5].count('N/A') <= 2:
                    file = result
                csv.writer(file).writerow([','.join([str(value) for value in [*analysed_stock.values()]])])

    zips_dir = Path("./zips")
    zips_dir.mkdir(exist_ok=True)
    zip_path = zips_dir / "files.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(results_dir / 'result.csv','result.csv')
        zipf.write(filed_dir / 'failed.csv','failed.csv')

    return zip_path


def get_screens() -> List[str]:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    screens_directory = os.path.join(current_directory, "screens")
    return [file for file in os.listdir(screens_directory) if os.path.isfile(os.path.join(screens_directory, file))]


def remove_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


@app.on_event("shutdown")
async def cleanup_temp_dir():
    for directory_path in (Path("./zips"), Path("./results"), Path("./failed")):
        remove_files_in_directory(directory_path)


@app.on_event("startup")
async def cleanup_temp_dir():
    for directory_path in (Path("./zips"), Path("./results"), Path("./failed")):
        remove_files_in_directory(directory_path)
