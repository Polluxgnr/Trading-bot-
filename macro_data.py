# ==============================================================================
# FICHIER : data/macro_data.py
# ROLE : Surveillance Macro-Économique (VIX, Taux, Yield Curve)
# ==============================================================================
import yfinance as yf
import pandas as pd

class MacroProvider:
    def __init__(self):
        # ^VIX = Volatilité, ^TNX = Taux 10 ans, ^IRX = Taux 13 semaines (Court terme)
        self.tickers = ["^VIX", "^TNX", "^IRX"]

    def fetch_macro_indicators(self):
        """
        Récupère les indicateurs de santé économique.
        Retourne un dictionnaire avec l'état macro.
        """
        try:
            data = yf.download(self.tickers, period="5d", progress=False, group_by='ticker')
            
            # Extraction des dernières valeurs
            vix = data['^VIX']['Close'].iloc[-1]
            yield_10y = data['^TNX']['Close'].iloc[-1]
            yield_3m = data['^IRX']['Close'].iloc[-1] # Proxy taux court

            # Calcul de l'inversion de la courbe des taux (Indicateur de récession)
            # Si 10 ans < 3 mois, c'est une inversion.
            yield_curve = yield_10y - yield_3m
            
            status = "HEALTHY"
            if vix > 30: status = "PANIC"
            elif yield_curve < 0: status = "RECESSION_WARNING"

            return {
                "VIX": round(vix, 2),
                "10Y_YIELD": round(yield_10y, 2),
                "YIELD_CURVE": round(yield_curve, 2),
                "MACRO_STATUS": status
            }
        except Exception as e:
            print(f"⚠️ [Macro] Erreur : {e}")
            return None