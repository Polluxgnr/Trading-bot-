# ==============================================================================
# FICHIER : utils/metrics.py
# ROLE : Calculateur de performance (Sharpe, Sortino, Drawdown)
# ==============================================================================
import pandas as pd
import numpy as np

class PerformanceMetrics:
    @staticmethod
    def calculate(history_df):
        """
        Calcule les métriques avancées basées sur l'historique d'Equity.
        Retourne un dictionnaire.
        """
        stats = {
            "sharpe": 0.0,
            "sortino": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0
        }

        # Il faut au moins 2 jours pour avoir une variation
        if history_df.empty or len(history_df) < 2:
            return stats

        # 1. Calcul des rendements journaliers
        # On s'assure que l'Equity est bien numérique
        equity = pd.to_numeric(history_df['Equity'], errors='coerce')
        returns = equity.pct_change().dropna()

        if returns.empty or returns.std() == 0:
            return stats

        # 2. SHARPE RATIO (Rendement / Risque Global)
        # Annualisé (x racine de 252 jours de bourse)
        stats["sharpe"] = (returns.mean() / returns.std()) * np.sqrt(252)

        # 3. SORTINO RATIO (Rendement / Risque de Perte uniquement)
        negative_returns = returns[returns < 0]
        if not negative_returns.empty and negative_returns.std() != 0:
            downside_risk = negative_returns.std()
            stats["sortino"] = (returns.mean() / downside_risk) * np.sqrt(252)

        # 4. MAX DRAWDOWN (Pire baisse du sommet au creux)
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        stats["max_drawdown"] = drawdown.min()

        return stats