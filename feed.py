import yfinance as yf
import pandas as pd
import time
from config.settings import Config

class DataFeed:
    def __init__(self):
        self.tickers = Config.FULL_UNIVERSE
        self.max_retries = 3

    def fetch_market_data(self, period="2y", interval="1d"):
        print(f"📥 [DataFeed] Téléchargement de {len(self.tickers)} actifs sur {period}...")
        
        for i in range(self.max_retries):
            try:
                # On laisse yfinance gérer sa session interne (plus robuste)
                raw_data = yf.download(
                    tickers=self.tickers, 
                    period=period, 
                    interval=interval, 
                    group_by='column', 
                    auto_adjust=True, 
                    progress=False,
                    threads=False 
                )
                
                if raw_data is None or raw_data.empty:
                    raise ValueError("Le DataFrame est vide.")

                raw_data = raw_data.ffill().bfill()

                # Extraction robuste des colonnes
                if isinstance(raw_data.columns, pd.MultiIndex):
                    closes = raw_data.xs('Close', axis=1, level=0)
                    highs = raw_data.xs('High', axis=1, level=0)
                    lows = raw_data.xs('Low', axis=1, level=0)
                else:
                    closes = raw_data['Close'].to_frame(self.tickers[0])
                    highs = raw_data['High'].to_frame(self.tickers[0])
                    lows = raw_data['Low'].to_frame(self.tickers[0])

                print(f"✅ [DataFeed] Données reçues.")
                return {"close": closes, "high": highs, "low": lows}

            except Exception as e:
                print(f"⚠️ [DataFeed] Erreur (Tentative {i+1}/{self.max_retries}): {e}")
                time.sleep(5)
        
        return None

    def get_latest_prices(self):
        data = self.fetch_market_data(period="5d")
        return data["close"].iloc[-1] if data else None