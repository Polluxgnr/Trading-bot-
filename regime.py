# ==============================================================================
# FICHIER : core/regime.py (VERSION FINALE - TREND KING)
# ==============================================================================
from config.settings import Config
import pandas as pd

class RegimeManager:
    def __init__(self):
        pass

    def analyze_market_health(self, data):
        """
        Stratégie Trend King :
        - Si SPY > SMA 200 jours : ATTACK (On suit la hausse)
        - Si SPY < SMA 200 jours : DEFENSE (On se protège)
        Simple, robuste, efficace.
        """
        closes = data['close']
        
        # Par défaut
        regime = "ATTACK"
        details = {"SPY_TREND": "UNKNOWN", "DISTANCE": 0.0}
        
        # Juge de Paix : Le SPY
        if "SPY" in closes.columns:
            spy = closes["SPY"]
            
            # Il faut assez d'historique pour la moyenne mobile 200
            if len(spy) > 200:
                current_price = spy.iloc[-1]
                sma_200 = spy.rolling(200).mean().iloc[-1]
                distance = (current_price / sma_200) - 1
                
                details["DISTANCE"] = distance
                
                if current_price > sma_200:
                    regime = "ATTACK"
                    details["SPY_TREND"] = "BULLISH"
                else:
                    regime = "DEFENSE"
                    details["SPY_TREND"] = "BEARISH"
        
        # --- GESTION DE LA DÉFENSE ---
        if regime == "DEFENSE":
            defense_universe = Config.ASSETS["DEFENSE"]
            best_score = -9999
            best_asset = Config.CASH_SYMBOL
            
            for asset in defense_universe:
                if asset in closes.columns:
                    p = closes[asset]
                    # Momentum court (3 mois / 63 jours) pour être réactif sur le refuge
                    if len(p) > 63:
                        score = (p.iloc[-1] / p.iloc[-63]) - 1 
                        if score > best_score:
                            best_score = score
                            best_asset = asset
            
            return "DEFENSE", best_asset, details

        return "ATTACK", None, details