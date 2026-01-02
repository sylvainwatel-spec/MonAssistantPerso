# Lazy imports
# import yfinance as yf
# import pandas as pd
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

class FinancialService:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.base_url = "https://www.alphavantage.co/query"

    def get_api_key(self) -> str:
        settings = self.data_manager.get_settings()
        api_keys = settings.get("api_keys", {})
        return api_keys.get("alpha_vantage", "")

    def get_stock_price(self, symbol: str) -> Tuple[bool, Dict[str, Any], str]:
        """Récupère le prix actuel via yfinance."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            # fast_info is faster than history
            info = ticker.fast_info
            
            # Construct a dict compatible with previous usage or simplified
            # Previous was Alpha Vantage format {"05. price": ...}
            # We map it to keep compatibility with view
            latest_price = info.last_price
            prev_close = info.previous_close
            change_percent = ((latest_price - prev_close) / prev_close) * 100
            
            # Calculate daily high/low using history(1d) if needed, or stick to fast_info
            # fast_info has year_high, year_low, but day_high might need 1d history
            hist = ticker.history(period="1d")
            if not hist.empty:
                high = hist["High"].iloc[0]
                low = hist["Low"].iloc[0]
                volume = hist["Volume"].iloc[0]
            else:
                high = latest_price
                low = latest_price
                volume = 0

            quote = {
                "05. price": str(latest_price),
                "10. change percent": f"{change_percent:.2f}%",
                "06. volume": str(volume),
                "03. high": str(high),
                "04. low": str(low)
            }
            
            return True, quote, "Succès"
                
        except Exception as e:
            return False, None, f"Erreur yfinance : {e}"

    def get_historical_data(self, symbol: str, period: str = "1y") -> Tuple[bool, Optional[Any], float]:
        """
        Récupère l'historique et calcule la moyenne.
        Returns: (success, dataframe, average_close_price)
        """
        try:
            import yfinance as yf
            import pandas as pd
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return False, None, 0.0
                
            average_price = hist["Close"].mean()
            return True, hist, average_price
            
        except Exception as e:
            return False, None, 0.0
