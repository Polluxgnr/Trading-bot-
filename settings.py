# ==============================================================================
# FICHIER : config/settings.py (VERSION MASTERCLASS : AEGIS SENTINEL)
# ==============================================================================
import os

class Config:
    PROJECT_NAME = "Trading bot"
    VERSION = "Vf"

    # --- 1. API KEYS (SECURED) ---
    # Utilisation de variables d'environnement pour la sécurité.
    # Créez un fichier .env à la racine du projet pour stocker ces valeurs.
    ALPACA_KEY = os.getenv("ALPACA_KEY", "YOUR_ALPACA_KEY_HERE")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET", "YOUR_ALPACA_SECRET_HERE")
    ALPACA_ENDPOINT = os.getenv("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets")
    
    DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "YOUR_DISCORD_WEBHOOK_HERE")
    
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "YOUR_MISTRAL_KEY_HERE")
    MISTRAL_MODEL = "mistral-tiny"

    # --- 2. GESTION CAPITAL & RISQUE ---
    INITIAL_CAPITAL = 1000.0
    CASH_SYMBOL = "BIL"      # Actif sans risque (T-Bills)
    SLIPPAGE = 0.001          # 0.1% de frais estimés

    # Position Sizing (Adaptive Volatility V25)
    TARGET_VOL_BULL = 0.25   # Cible 25% de volatilité en marché haussier
    TARGET_VOL_BEAR = 0.15   # Cible 15% de volatilité en marché baissier
    MAX_POSITION_SIZE = 0.40 # Pas plus de 40% sur une seule action

    # --- 3. LOGIQUE STRATÉGIQUE (CANARY + VALKYRIE) ---
    # Canary Protocol (Détecteurs de Crash)
    CANARIES = ["EEM", "AGG"] 
    
    # Valkyrie Engine (Paramètres optimisés)
    SHARPE_WINDOW = 126      # 6 Mois pour le classement (Stabilité)
    VOLATILITY_WINDOW = 20   # 1 Mois pour le calibrage de la taille
    MOMENTUM_WINDOW = 126    # Base pour les fenêtres multiples

    # Seuils
    VIX_FEAR_THRESHOLD = 20  # Au-dessus de 20, on passe en mode défensif
    RSI_BUY = 10              # Pour les stratégies de Swing (Mean Reversion)
    RSI_SELL = 80

    # --- 4. UNIVERS D'INVESTISSEMENT (TOTAL WAR) ---
    ASSETS = {
        # Les Détecteurs
        "CANARY": ["EEM", "AGG"],
        
        # Le Bunker (Refuge en cas de crash)
        "DEFENSE": ["IEF", "BIL", "GLD", "UUP"],
        
        # L'Armée (Tech & Growth) - Liste V25 optimisée
        "ATTACK": [
            "NVDA", "MSFT", "META", "AMZN", "GOOGL", "AAPL", "TSLA", "AVGO",
            "AMD", "PLTR", "MSTR", "COIN", "SMCI", "NET", "CRWD", "UBER", 
            "DKNG", "APP", "DDOG", "CELH", "NOW", "ARM", "RDDT"
        ],
        
        # Indices (Pour le Swing Trading et Benchmark)
        "INDICES": ["SPY", "QQQ", "^VIX"]
    }

    # Liste complète pour le téléchargement de données
    FULL_UNIVERSE = list(set(
        ASSETS["CANARY"] + ASSETS["DEFENSE"] + ASSETS["ATTACK"] + ASSETS["INDICES"]
    ))