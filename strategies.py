# ==============================================================================
# FICHIER : config/strategies.py
# ROLE : Définition des règles de trading (Canary & Valkyrie)
# ==============================================================================

class StrategyConfig:
    # --- PROTOCOLE CANARY (Le Détecteur) ---
    CANARY_PARAMS = {
        "MOMENTUM_WINDOW_1": 21,   # 1 Mois
        "MOMENTUM_WINDOW_2": 63,   # 3 Mois
        "MOMENTUM_WINDOW_3": 126,  # 6 Mois
        "MOMENTUM_WINDOW_4": 252,  # 1 An
        "WEIGHTS": [12, 4, 2, 1]   # Pondération (Réactivité vs Stabilité)
    }

    # --- MOTEUR VALKYRIE (L'Attaquant) ---
    VALKYRIE_PARAMS = {
        "LOOKBACK_WINDOW": 126,      # Fenêtre de classement Sharpe
        "VOLATILITY_WINDOW": 20,     # Fenêtre de calcul du risque (Sizing)
        
        # Cibles de Volatilité (Risk Target)
        "TARGET_VOL_BULL": 0.25,     # 25% annualisé en régime ATTACK
        "TARGET_VOL_BEAR": 0.15,     # 15% annualisé en régime DEFENSE
        
        # Limites
        "MAX_POSITION_SIZE": 0.40,   # Max 40% sur une ligne
        "MAX_DRAWDOWN_CUT": 0.15     # (Optionnel) Hard stop si -15%
    }

    # --- SENTINEL (L'IA) ---
    SENTINEL_PARAMS = {
        "VETO_ENABLED": True,        # Activer le blocage par news ?
        "MAX_RISK_KEYWORDS": ["FRAUD", "SEC INVESTIGATION", "BANKRUPTCY"]
    }