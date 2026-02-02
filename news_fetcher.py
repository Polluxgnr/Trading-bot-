# ==============================================================================
# FICHIER : data/news_fetcher.py
# ROLE : Récupérateur d'actualités (Headlines) via Yahoo Finance
# ==============================================================================
import yfinance as yf
import time

class NewsFetcher:
    def get_headlines(self, ticker):
        """
        Récupère les 3 derniers titres d'actualité pour un ticker.
        Retourne une liste de strings.
        """
        try:
            # Petit délai pour éviter le spam si on boucle trop vite
            time.sleep(0.5)
            
            t = yf.Ticker(ticker)
            news = t.news
            
            if not news:
                return []
            
            # On prend les 3 titres les plus récents
            headlines = [n.get('title', '') for n in news[:3]]
            return headlines
            
        except Exception as e:
            print(f"⚠️ [News] Erreur récup news pour {ticker}: {e}")
            return []