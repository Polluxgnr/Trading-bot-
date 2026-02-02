# ==============================================================================
# FICHIER : core/brain.py (VERSION FINALE - TREND LOGGING)
# ==============================================================================
from data.feed import DataFeed
from data.news_fetcher import NewsFetcher
from data.macro_data import MacroProvider
from core.regime import RegimeManager
from core.portfolio import PortfolioManager
from core.state_manager import StateManager
from intelligence.mistral_client import MistralOracle
from config.settings import Config

class AegisBrain:
    def __init__(self):
        self.feed = DataFeed()
        self.news = NewsFetcher()
        self.macro = MacroProvider()
        self.regime = RegimeManager()
        self.portfolio = PortfolioManager()
        self.state_manager = StateManager()
        self.oracle = MistralOracle()

    def generate_orders(self):
        print("🧠 [Brain] Démarrage de l'analyse stratégique...")

        # 0. CHECK STATE (Sécurité Anti-Doublon)
        if self.state_manager.already_traded_today():
            return "DONE", [], None

        # 1. ACQUISITION MACRO
        print("🌍 [Brain] Scan Macro-Économique...")
        macro_data = self.macro.fetch_macro_indicators()
        if macro_data:
            print(f"   > VIX: {macro_data['VIX']} | Taux 10ans: {macro_data['10Y_YIELD']}%")
        
        # 2. ACQUISITION DATA PRIX
        data = self.feed.fetch_market_data(period="2y")
        if data is None: return "ERROR", [], None

        # 3. ANALYSE RÉGIME (TREND KING)
        status, defense_asset, details = self.regime.analyze_market_health(data)
        
        # Log spécifique Trend King
        trend_msg = details.get('SPY_TREND', 'UNKNOWN')
        dist_msg = details.get('DISTANCE', 0) * 100
        print(f"🚦 [Brain] Tendance SPY : {trend_msg} ({dist_msg:+.2f}% vs SMA200)")
        print(f"   > Régime Final : {status}")
        
        # Sauvegarde du régime
        self.state_manager.update_regime(status)

        # 4. SÉLECTION TECHNIQUE
        raw_orders = []
        if status == "ATTACK":
            raw_orders = self.portfolio.select_attack_portfolio(data)
        else:
            raw_orders = self.portfolio.select_defense_portfolio(defense_asset)

        # 5. FILTRE SENTINEL (NEWS VETO)
        final_orders = []
        if status == "ATTACK":
            print("\n🛡️ [Sentinel] Analyse de risque IA en cours...")
            for order in raw_orders:
                ticker = order['ticker']
                headlines = self.news.get_headlines(ticker)
                
                risk_status = "SAFE"
                if headlines:
                    risk_status = self.oracle.analyze_risk(ticker, headlines)
                
                if risk_status == "DANGER":
                    print(f"   ⛔ VETO IA : {ticker} supprimé (Risque News)")
                else:
                    status_icon = "✅" if headlines else "⚠️"
                    print(f"   {status_icon} IA Validé : {ticker}")
                    final_orders.append(order)
        else:
            final_orders = raw_orders

        return status, final_orders, macro_data