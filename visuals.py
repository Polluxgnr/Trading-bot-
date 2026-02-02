# ==============================================================================
# FICHIER : utils/visuals.py
# ROLE : Générateur de graphiques financiers pour le reporting Discord
# ==============================================================================
import matplotlib.pyplot as plt
import io
import pandas as pd

class Visualizer:
    @staticmethod
    def generate_performance_chart(portfolio_data, spy_data):
        """
        Génère un graphique PNG en mémoire (Buffer).
        portfolio_data : Series pandas des valeurs du portefeuille
        spy_data : Series pandas du Benchmark
        """
        plt.style.use('dark_background') # Look "Pro"
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Normalisation base 100 pour comparaison
        if not portfolio_data.empty and not spy_data.empty:
            norm_port = (portfolio_data / portfolio_data.iloc[0]) * 100
            norm_spy = (spy_data / spy_data.iloc[0]) * 100
            
            ax.plot(norm_port, label='AEGIS SENTINEL', color='#00ff00', linewidth=2)
            ax.plot(norm_spy, label='S&P 500', color='#888888', linestyle='--', alpha=0.7)
            
            # Calcul Performance
            perf_bot = norm_port.iloc[-1] - 100
            perf_spy = norm_spy.iloc[-1] - 100
            
            ax.set_title(f"PERFORMANCE LIVE: Bot {perf_bot:+.1f}% vs SPY {perf_spy:+.1f}%", 
                         fontsize=12, fontweight='bold', color='white')
        
        ax.legend()
        ax.grid(color='#333333', linestyle=':')
        
        # Sauvegarde en mémoire (pas de fichier sur le disque)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#1e1e1e')
        buf.seek(0)
        plt.close(fig)
        
        return buf