# ==============================================================================
# FICHIER : backtest_suite.py (COMPATIBLE SENTINEL)
# ==============================================================================
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from config.settings import Config
from core.regime import RegimeManager
from core.portfolio import PortfolioManager

# --- PARAMÈTRES DU TEST ---
START_DATE = "2022-01-01"  # Teste le Crash 2022 + Bull Run 2023-2024
INITIAL_CAPITAL = 10000.0
TRANS_COST = 0.0010        # 0.10% de frais par trade (Slippage inclus)

class BacktestEngine:
    def __init__(self):
        # On utilise exactement les mêmes cerveaux que le bot live
        self.regime_mgr = RegimeManager()
        self.portfolio_mgr = PortfolioManager()
        
        # Univers complet pour le téléchargement
        self.universe = Config.FULL_UNIVERSE
        
        # État du portefeuille virtuel
        self.cash = INITIAL_CAPITAL
        self.positions = {} # {ticker: quantité}
        self.history = []   # Journal de bord

    def fetch_history(self):
        print(f"📥 Téléchargement de l'historique ({len(self.universe)} actifs)...")
        # On télécharge tout d'un coup
        data = yf.download(
            self.universe, 
            start=START_DATE, 
            group_by='column', 
            auto_adjust=True, 
            progress=True
        )
        # Nettoyage
        data = data.ffill().bfill()
        
        # On structure comme le DataFeed : {'close': df, 'high': df, ...}
        return {
            "close": data['Close'],
            "high": data['High'],
            "low": data['Low'],
            "open": data['Open']
        }

    def run(self):
        # 1. Récupération des données
        full_data = self.fetch_history()
        closes = full_data['close']
        dates = closes.index
        
        print(f"⚙️ Lancement de la simulation sur {len(dates)} jours...")

        # On commence après 252 jours pour avoir assez d'historique pour les calculs (Canary 12 mois)
        start_index = 252
        
        for i in range(start_index, len(dates)):
            current_date = dates[i]
            
            # --- A. VOYAGE DANS LE TEMPS ---
            # On coupe les données pour ne voir que le passé (jusqu'à la date i)
            data_slice = {
                "close": full_data['close'].iloc[:i+1],
                "high": full_data['high'].iloc[:i+1],
                "low": full_data['low'].iloc[:i+1]
            }
            
            # Prix de clôture du jour (pour exécuter les ordres)
            current_prices = full_data['close'].iloc[i]

            # --- B. LE CERVEAU RÉFLÉCHIT ---
            # 1. Analyse Régime (Canary)
            regime, defense_asset, _ = self.regime_mgr.analyze_market_health(data_slice)
            
            # 2. Sélection Portefeuille (Valkyrie)
            target_orders = []
            if regime == "ATTACK":
                target_orders = self.portfolio_mgr.select_attack_portfolio(data_slice)
            else:
                target_orders = self.portfolio_mgr.select_defense_portfolio(defense_asset)

            # --- C. EXÉCUTION VIRTUELLE ---
            self._rebalance_portfolio(target_orders, current_prices)
            
            # --- D. COMPTABILITÉ ---
            # Valeur totale = Cash + Valeur des actions détenues
            portfolio_value = self.cash
            for ticker, qty in self.positions.items():
                if ticker in current_prices:
                    portfolio_value += qty * current_prices[ticker]
            
            # On loggue le résultat
            self.history.append({
                "Date": current_date,
                "Equity": portfolio_value,
                "Regime": regime,
                "SPY": current_prices.get("SPY", 0)
            })
            
            if i % 50 == 0:
                print(f"📅 {current_date.date()} | ${portfolio_value:,.0f} | {regime}")

        self._generate_report()

    def _rebalance_portfolio(self, orders, current_prices):
        """Applique les ordres cibles au portefeuille virtuel avec frais."""
        # Calcul de la valeur totale actuelle pour déterminer les montants cibles
        total_equity = self.cash
        for t, q in self.positions.items():
            if t in current_prices:
                total_equity += q * current_prices[t]
        
        # 1. On vend ce qui doit l'être
        # Convertir la liste d'ordres en dictionnaire {ticker: target_weight}
        target_weights = {item['ticker']: item['weight'] for item in orders}
        
        # Liste des actifs à vérifier (ceux qu'on a + ceux qu'on veut)
        all_tickers = set(self.positions.keys()) | set(target_weights.keys())
        
        for ticker in all_tickers:
            if ticker not in current_prices or pd.isna(current_prices[ticker]):
                continue
                
            price = current_prices[ticker]
            current_qty = self.positions.get(ticker, 0)
            current_val = current_qty * price
            
            target_pct = target_weights.get(ticker, 0.0)
            target_val = total_equity * target_pct
            
            diff_val = target_val - current_val
            
            # Seuil de tolérance (buffer 5%) pour éviter de trader pour des centimes
            if abs(diff_val) < total_equity * 0.05:
                continue
                
            # Calcul quantité à acheter/vendre
            qty_to_trade = diff_val / price
            cost = abs(diff_val) * TRANS_COST # Frais
            
            # Mise à jour
            self.cash -= cost # On paie les frais
            self.cash -= diff_val # On paie les actions (ou on reçoit du cash si diff_val negatif)
            self.positions[ticker] = current_qty + qty_to_trade
            
            # Nettoyage des poussières (positions quasi nulles)
            if self.positions[ticker] < 0.001:
                del self.positions[ticker]

    def _generate_report(self):
        df = pd.DataFrame(self.history)
        df.set_index('Date', inplace=True)
        
        # Benchmark SPY (Normalisé à 10k)
        start_spy = df['SPY'].iloc[0]
        df['SPY_Bench'] = (df['SPY'] / start_spy) * INITIAL_CAPITAL
        
        # Performance Finale
        final_equity = df['Equity'].iloc[-1]
        perf_bot = (final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL
        perf_spy = (df['SPY_Bench'].iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL
        
        print("\n" + "="*50)
        print("📊 RÉSULTATS DU BACKTEST")
        print("="*50)
        print(f"Capital Initial : ${INITIAL_CAPITAL:,.0f}")
        print(f"Capital Final   : ${final_equity:,.0f}")
        print(f"Performance BOT : {perf_bot:+.2%}")
        print(f"Performance SPY : {perf_spy:+.2%}")
        print("="*50)
        
        # Graphique
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Equity'], label='AEGIS SENTINEL', color='#00ff00')
        plt.plot(df.index, df['SPY_Bench'], label='S&P 500', color='gray', linestyle='--')
        
        # Colorier les zones de régime
        # (Astuce visuelle : fond rouge si Défense)
        # y_min, y_max = plt.ylim()
        # plt.fill_between(df.index, y_min, y_max, where=(df['Regime'] == 'DEFENSE'), color='red', alpha=0.1)

        plt.title(f"Backtest Historique ({START_DATE} - Aujourd'hui)")
        plt.ylabel("Valeur Portefeuille ($)")
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()

if __name__ == "__main__":
    try:
        engine = BacktestEngine()
        engine.run()
    except Exception as e:
        print(f"❌ Erreur Backtest : {e}")