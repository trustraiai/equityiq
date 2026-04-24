import yfinance as yf

def stock_tool(symbol: str) -> str:
    stock = yf.Ticker(symbol)
    info = stock.info
    
    return f"""
    Company: {info.get('longName')}
    Price: {info.get('currentPrice')}
    Market Cap: {info.get('marketCap')}
    Sector: {info.get('sector')}
    """