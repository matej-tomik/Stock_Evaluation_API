from math import sqrt

"""""
sources of the model computations

dcf_advance is according to https://www.gurufocus.com/term/iv_dcf/AAPL/Intrinsic-Value:-DCF-(FCF-Based)/Apple

dcf_simple  is according to https://finbox.com/NASDAQGS:AAPL/models/ddm-sg/ without calculating cash per share and 

ddm_advance is according to https://finbox.com/NASDAQGS:AAPL/models/ddm-sg/

ddm_simple is according to https://www.investopedia.com/terms/d/ddm.asp in section Examples of the DDM

graham_number it simply according to google
"""""


def dcf_advance(earnings_per_share: float, wacc: float, growth_rate: float, terminal_growth_rate: float = 0.04, year: int = 10) -> float:
    if growth_rate < 0.05:
        growth_rate = 0.05
    x = 0
    for n in range(1, year + 1):
        x += ((1 + growth_rate) ** n) / ((1 + wacc) ** n)
    y = 0
    for n in range(1, year + 1):
        y += ((1 + terminal_growth_rate) ** n) / ((1 + wacc) ** n)

    return earnings_per_share * (x + ((1 + growth_rate) ** 10) / ((1 + wacc) ** 10) * y)


def dcf_simple(price_of_stock: float, growth_rate: float) -> float:
    result = price_of_stock / (1 + growth_rate)
    for n in range(2,6):
        dividend = price_of_stock * growth_rate
        result += price_of_stock / (1 + growth_rate) ** n
    return result / 5


def ddm_advance(dividend: float, shares_outstanding: int, net_income: int, dividend_growth_rate: float, capm: float, growth_rate: float) -> float:
    cash_dividends_paid = shares_outstanding * dividend
    cash_retained = net_income - cash_dividends_paid
    required_retention_ratio = [0.2, 0.125, 0.075]  # % net income needed for future growth  20% LOW 12.5% MID 7.5% HIGH
    excess_retained = [(cash_retained - net_income * required_retention_ratio[x]) / shares_outstanding for x in range(3)]
    adjusted_dividend = [dividend + excess_retained[x] for x in range(3)]
    ddm_results = [(adjusted_dividend[x] * (1 + dividend_growth_rate) / capm) - growth_rate for x in range(3)]

    return sum(ddm_results) / len(ddm_results)


def ddm_simple(dividend: float, dividend_growth_rate: float, capm: float) -> float:
    return (dividend * (1 + dividend_growth_rate)) / (capm - dividend_growth_rate)


def graham_number(earnings_per_share: float, book_value_per_share: float) -> float:
    result = 22.5 * earnings_per_share * book_value_per_share
    return sqrt(result) if result > 0 else 'N/A'
