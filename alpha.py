# ==============================================================================
# FICHIER : core/alpha.py
# ROLE : Calculateur Mathématique Pur (Utilise StrategyConfig)
# ==============================================================================
import pandas as pd
import numpy as np
from config.strategies import StrategyConfig

class AlphaEngine:
    """
    Moteur de calculs quantitatifs.
    Transforme les prix bruts en signaux exploitables (Momentum, Volatilité, ATR).
    """

    @staticmethod
    def calculate_13612W(series):
        """
        Calcule le Momentum "Keller" (13612W) pour la stratégie Canary.
        Les pondérations et fenêtres sont chargées dynamiquement depuis StrategyConfig.
        """
        # Chargement des paramètres
        params = StrategyConfig.CANARY_PARAMS
        weights = params["WEIGHTS"]
        w1 = params["MOMENTUM_WINDOW_1"]
        w2 = params["MOMENTUM_WINDOW_2"]
        w3 = params["MOMENTUM_WINDOW_3"]
        w4 = params["MOMENTUM_WINDOW_4"]

        # On s'assure d'avoir assez de données (fenêtre la plus longue)
        if len(series) < w4:
            return 0.0

        try:
            # Calcul des rendements glissants (Trading Days approx)
            # .iloc[-1] = Aujourd'hui, .iloc[-N] = Il y a N jours
            p_now = series.iloc[-1]
            
            r1 = (p_now / series.iloc[-w1]) - 1
            r3 = (p_now / series.iloc[-w2]) - 1
            r6 = (p_now / series.iloc[-w3]) - 1
            r12 = (p_now / series.iloc[-w4]) - 1
            
            # Formule pondérée dynamique
            score = (weights[0] * r1) + (weights[1] * r3) + (weights[2] * r6) + (weights[3] * r12)
            return score
            
        except Exception:
            return 0.0

    @staticmethod
    def calculate_volatility(series):
        """
        Calcule la volatilité annualisée pour le Sizing Valkyrie.
        Utilise la fenêtre définie dans la config (ex: 20 jours).
        """
        window = StrategyConfig.VALKYRIE_PARAMS["VOLATILITY_WINDOW"]

        if len(series) < window:
            return 0.0
            
        daily_ret = series.pct_change()
        # Std Dev * Racine(252) pour annualiser
        vol = daily_ret.rolling(window).std().iloc[-1] * np.sqrt(252)
        
        # Gestion des NaN ou Zéro
        if pd.isna(vol) or vol == 0:
            return 0.0
        return vol

    @staticmethod
    def calculate_atr(high, low, close, window=14):
        """
        Average True Range (Utilisé pour les Stop Loss et la mesure de bruit).
        """
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        # On prend la moyenne mobile simple du True Range
        atr = tr.rolling(window).mean().iloc[-1]
        
        if pd.isna(atr): 
            return 0.0
        return atr