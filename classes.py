from stock_evaluation_models import ddm_advance, ddm_simple, graham_number, dcf_advance, dcf_simple
import yfinance as yf
import warnings
from typing import Optional
from my_data_types import MainInfo, GrahamNumberData, DcfAdvanceData, DcfSimpleData, DdmAdvanceData, DdmSimpleData
from pandas import Series, DataFrame, isna



warnings.simplefilter(action='ignore', category=FutureWarning)
TREASURY_YLD_INDEX_TEN_YEAR: str = "^TNX"
EXPECTED_RATE_OF_RETURN: float = 0.10  # Expected Rate of Return for spm500


def get_growth_rate(stock_info: dict, income_statement: DataFrame) -> Optional[float]:
    try:
        ebitda: Series = income_statement.loc['EBITDA']
        gr_results = []
        for x in range(len(ebitda) - 1):
            gr_results.append(ebitda.iloc[x] / ebitda.iloc[x + 1] - 1)
        return sum(gr_results) / len(gr_results)
    except (KeyError, ZeroDivisionError) as e:
        return stock_info.get('earningsGrowth')


def get_dividend_growth_rate(dividends: Series) -> Optional[float]:
    if dividends.empty:
        return None
    dividends = dividends.tail(20)
    annual_growth_rates = dividends.pct_change().resample('YE').sum().dropna()
    return round(float(annual_growth_rates.mean()),2)


def get_capm(beta: Optional[float], risk_free_rate: float) -> Optional[float]:
    return None if None in {beta,risk_free_rate} else round((risk_free_rate + beta * (EXPECTED_RATE_OF_RETURN - risk_free_rate)), 4)


def get_main_info(stock_info: dict) -> MainInfo:
    return (stock_info.get(metric) for metric in ['sector', 'industry', 'country', 'shortName', 'marketCap'])


def get_graham_number_data(stock_info: dict) -> GrahamNumberData:
    earnings_per_share: Optional[float] = stock_info.get('trailingEps')
    book_value_per_share: Optional[float] = stock_info.get('bookValue')
    data = (earnings_per_share, book_value_per_share)
    return None if None in data or any(isna(x) for x in data) else data


def get_total_dividend(stock_info: dict) -> Optional[float]:
    dividend: Optional[float] = stock_info.get('dividendRate')
    cash_per_share: Optional[float] = stock_info.get('totalCashPerShare')
    return None if None in (dividend, cash_per_share) or any(isna(x) for x in (dividend, cash_per_share)) else dividend + cash_per_share


def get_ddm_simple_data(dividends: Series,stock_info: dict, risk_free_rate: float) -> DdmSimpleData:
    total_dividend = get_total_dividend(stock_info)
    dividend_growth_rate = get_dividend_growth_rate(dividends)
    beta: Optional[float] = stock_info.get('beta')
    capm = get_capm(beta, risk_free_rate)
    data = (
        total_dividend,
        dividend_growth_rate,
        capm
    )
    return None if None in data or any(isna(x) for x in data) else data


def get_ddm_advance_data(dividends: Series, stock_info: dict, income_statement: DataFrame, risk_free_rate: float) -> DdmAdvanceData:
    dividend: Optional[float] = stock_info.get('dividendRate')
    shares_outstanding: Optional[int] = stock_info.get('sharesOutstanding')
    net_income: Optional[int] = stock_info.get('netIncomeToCommon')
    beta: Optional[float] = stock_info.get('beta')
    dividend_growth_rate = get_dividend_growth_rate(dividends)
    capm = get_capm(beta, risk_free_rate)
    growth_rate = get_growth_rate(stock_info, income_statement)
    data = (
        dividend,
        shares_outstanding,
        net_income,
        dividend_growth_rate,
        capm,
        growth_rate
    )
    return None if None in data or any(isna(x) for x in data) else data


def get_wacc(total_debt, market_capital, beta, interest_expense, tax_prevision, pre_tax_income, risk_free_rate) -> float:
    weight_of_equity = market_capital / (market_capital + total_debt)
    cost_of_debt = interest_expense / total_debt
    weight_of_debt = total_debt / (market_capital + total_debt)
    tax_rate = tax_prevision / pre_tax_income
    return round((weight_of_equity * get_capm(beta, risk_free_rate)) + ((weight_of_debt * cost_of_debt) * (1 - tax_rate)), 4)


def get_dcf_simple_data(stock_info: dict,income_statement: DataFrame,) -> DcfSimpleData:
    price_of_stock = get_current_price(stock_info)
    growth_rate = get_growth_rate(stock_info, income_statement)
    data = (
        price_of_stock,
        growth_rate
    )
    return None if None in data or any(isna(x) for x in data) else data


def get_dcf_advance_data(income_statement: DataFrame, balance: DataFrame, stock_info: dict, risk_free_rate: float) -> DcfAdvanceData:
    try:
        first_key_balance = balance.keys()[0]
        first_key_income = income_statement.keys()[0]
    except IndexError:
        return None
    growth_rate = get_growth_rate(stock_info, income_statement)
    earnings_per_share: Optional[float] = stock_info.get('trailingEps')
    market_capital: Optional[float] = stock_info.get('marketCap')
    beta: Optional[float] = stock_info.get('beta')
    total_debt = balance[first_key_balance].get('Total Debt') or balance[first_key_balance].get('TotalDebt')
    interest_expense: int = income_statement[first_key_income].get('Interest Expense')
    tax_prevision: int = income_statement[first_key_income].get('Tax Provision')
    pre_tax_income: int = income_statement[first_key_income].get('Pretax Income')
    data = (growth_rate, earnings_per_share, market_capital, beta, total_debt, interest_expense, tax_prevision, pre_tax_income)
    if None in data or any(isna(x) for x in data):
        return None
    wacc = get_wacc(total_debt, market_capital, beta, interest_expense, tax_prevision, pre_tax_income, risk_free_rate)
    return earnings_per_share, wacc, growth_rate


def get_current_price(stock_info: dict) -> float:
    market_today_low: Optional[float] = stock_info.get('regularMarketDayLow')
    market_today_high: Optional[float] = stock_info.get('regularMarketDayHigh')
    return None if None in {market_today_low, market_today_high} else (market_today_low + market_today_high) / 2


class StockFinancials:
    def __init__(self, ticker: str, risk_free_rate: float):
        stock: yf.Ticker = yf.Ticker(ticker)
        balance = stock.balancesheet
        stock_info = stock.info
        income_statement = stock.income_stmt
        dividends = stock.dividends

        graham_number_data = get_graham_number_data(stock_info)
        ddm_advance_data = get_ddm_advance_data(dividends, stock_info, income_statement, risk_free_rate)
        dcf_advance_data = get_dcf_advance_data(income_statement, balance, stock_info, risk_free_rate)
        ddm_simple_data = get_ddm_simple_data(dividends, stock_info, risk_free_rate)
        dcf_simple_data = get_dcf_simple_data(stock_info, income_statement)
        current_price = get_current_price(stock_info)

        self.sector, self.industry, self.country, self.name, self.market_capital = get_main_info(stock_info)
        self.ticker = ticker
        self.graham_result = 'N/A' if graham_number_data is None else round(graham_number(*graham_number_data))
        self.ddm_advance_result = 'N/A' if None in {ddm_advance_data, current_price} else round(ddm_advance(*ddm_advance_data) / current_price, 2)
        self.dcf_advance_result = 'N/A' if None in {dcf_advance_data, current_price} else round(dcf_advance(*dcf_advance_data) / current_price, 2)
        self.ddm_simple_result = 'N/A' if None in {ddm_simple_data, current_price} else round(ddm_simple(*ddm_simple_data) / current_price, 2)
        self.dcf_simple_result = 'N/A' if None in {dcf_simple_data, current_price} else round(dcf_simple(*dcf_simple_data) / current_price, 2)
