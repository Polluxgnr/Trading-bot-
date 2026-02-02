# ==============================================================================
# FICHIER : main.py (VERSION GOLDEN - PRODUCTION READY)
# ==============================================================================
import sys
from core.brain import AegisBrain
from core.execution import ExecutionManager
from interfaces.discord_bot import DiscordBot
from intelligence.mistral_client import MistralOracle
from utils.visuals import Visualizer
from utils.storage import StateManager
from utils.metrics import PerformanceMetrics
from config.settings import Config

def run_sentinel():
    print("\n" + "="*60)
    print(f"🚀 DÉMARRAGE DU SYSTÈME : {Config.PROJECT_NAME} v{Config.VERSION}")
    print("="*60 + "\n")

    # 1. INITIALISATION
    brain = AegisBrain()
    executor = ExecutionManager()
    discord = DiscordBot()
    oracle = MistralOracle()
    storage = StateManager()

    # 2. STRATÉGIE
    regime, orders, macro_data = brain.generate_orders()
    
    # Gestion Anti-Doublon / Erreurs
    if regime == "DONE":
        print("💤 Le système a déjà travaillé aujourd'hui. Arrêt propre.")
        return
    if regime == "ERROR" or (not orders and regime == "ATTACK"):
        print("❌ ERREUR CRITIQUE : Problème de données.")
        return

    # 3. EXÉCUTION
    print("\n⚔️ EXÉCUTION DES ORDRES (ALPACA)...")
    executor.execute_orders(orders)
    brain.state_manager.mark_trading_done()
    
    # 4. DATA & MÉTRIQUES
    real_equity = executor.get_equity()
    
    # Fetch SPY pour le benchmark
    live_data = brain.feed.fetch_market_data(period="5d")
    current_spy = live_data['close']['SPY'].iloc[-1] if live_data is not None else 0

    # Sauvegarde
    storage.save_snapshot(real_equity, current_spy)
    history_df = storage.get_history()

    # Calcul des Stats
    print("\n📊 CALCUL DES MÉTRIQUES...")
    stats = PerformanceMetrics.calculate(history_df)
    stats["total_trades"] = executor.get_trade_count()
    print(f"   > Sharpe: {stats['sharpe']:.2f} | Trades: {stats['total_trades']}")

    # 5. INTELLIGENCE & REPORTING
    print("\n🧠 ANALYSE IA (MISTRAL)...")
    ai_comment = oracle.get_market_commentary(regime, orders, macro_data)
    
    print("\n🎨 GÉNÉRATION GRAPHIQUE...")
    if len(history_df) >= 1:
        chart_buf = Visualizer.generate_performance_chart(
            history_df['Equity'], 
            history_df['SPY_Price']
        )
        discord.send_chart(chart_buf)

    print("\n📨 NOTIFICATION DISCORD...")
    discord.notify_decision(regime, orders, ai_comment, metrics=stats)
    
    print("\n✅ MISSION ACCOMPLIE.")

if __name__ == "__main__":
    try:
        run_sentinel()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel.")
    except Exception as e:
        print(f"\n❌ ERREUR FATALE : {e}")