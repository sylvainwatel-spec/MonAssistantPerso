import requests
import json
from typing import Dict, Any, Tuple
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
        """Récupère le prix actuel (Global Quote)."""
        api_key = self.get_api_key()
        if not api_key:
            return False, None, "Clé API Alpha Vantage manquante."

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Global Quote" in data:
                quote = data["Global Quote"]
                if not quote:
                     return False, None, f"Symbole '{symbol}' non trouvé."
                return True, quote, "Succès"
            elif "Note" in data:
                return False, None, "Limite d'API atteinte (5 requêtes/min)."
            else:
                return False, None, f"Erreur API : {data}"
                
        except Exception as e:
            return False, None, f"Erreur réseau : {e}"

    def get_company_overview(self, symbol: str) -> Tuple[bool, Dict[str, Any], str]:
        """Récupère les infos de l'entreprise."""
        api_key = self.get_api_key()
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": api_key
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            if "Symbol" in data:
                return True, data, "Succès"
            else:
                return False, None, "Données non trouvées."
        except Exception as e:
            return False, None, str(e)
