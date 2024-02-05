from typing import Tuple,Optional

Sector = str
Industry = str
Country = str
Name = str
MarketCapital = float
Dividend = float
SharesOutstanding = int
NetIncome = int
DividendGrowthRate = float
Capm = float
GrowthRate = float
EarningsPerShare = float
Wacc = float
BookValuePerShare = float
PriceOfStock = float

MainInfo = Tuple[Optional[Sector], Optional[Industry], Optional[Country], Optional[Name], Optional[MarketCapital]]
DdmAdvanceData = Optional[Tuple[Dividend, SharesOutstanding, NetIncome, DividendGrowthRate, Capm, GrowthRate]]
DcfAdvanceData = Optional[Tuple[EarningsPerShare, Wacc, GrowthRate]]
GrahamNumberData = Optional[Tuple[EarningsPerShare, BookValuePerShare]]
DdmSimpleData = Optional[Tuple[Dividend, DividendGrowthRate, Capm]]
DcfSimpleData = Optional[Tuple[PriceOfStock, GrowthRate]]

StockResult = {
    'graham_result': 'N/A',
    'dcf_advance_result': 'N/A',
    'ddm_advance_result': 'N/A',
    'dcf_simple_result': 'N/A',
    'ddm_simple_result': 'N/A',
    'ticker': None,
    'name': None,
    'market_capital': None,
    'country': None,
    'sector': None,
    'industry': None
}

# StockResult = {
#     'graham_result': ModelResult,
#     'dcf_advance_result': ModelResult,
#     'ddm_advance_result': ModelResult,
#     'dcf_simple_result': ModelResult,
#     'ddm_simple_result': ModelResult,
#     'ticker': Optional[Ticker],
#     'name': Optional[Name],
#     'market_capital': Optional[MarketCapital],
#     'country': Optional[Country],
#     'sector': Optional[Sector],
#     'industry': Optional[Industry]
# }