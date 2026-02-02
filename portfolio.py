# ==============================================================================
# FICHIER : core/portfolio.py
# ROLE : Sélection d'actifs et Dimensionnement des positions (Sizing)
# ==============================================================================
import pandas as pd
import numpy as np
from config.settings import Config
from core.alpha import AlphaEngine

class PortfolioManager:
    def __init__(self):
        self.alpha = AlphaEngine()

    def select_attack_portfolio(self, data):
        """
        Logique VALKYRIE (V25) :
        1. Filtre l'univers d'attaque.
        2. Calcule le Score Valkyrie (Sharpe Rolling).
        3. Sélectionne le TOP 3.
        4. Calcule la taille de position (Volatilité Cible).
        
        Retourne : Liste de dictionnaires [{'ticker': 'NVDA', 'weight': 0.35, ...}]
        """
        closes = data['close']
        candidates = []
        
        # 1. SCAN DE L'ARMÉE (Tech + Sectors)
        # On fusionne les listes pour que le bot puisse choisir Tech OU Secteurs
        scan_list = list(set(Config.ASSETS["ATTACK"] + Config.ASSETS["DEFENSE"]))
        
        # Pré-calculs vectorisés pour la vitesse
        # Rendement sur 6 mois (Sharpe Window)
        returns = closes.pct_change(Config.SHARPE_WINDOW).iloc[-1]
        
        # Volatilité court terme (20 jours) pour le Sizing
        short_vol = closes.pct_change().rolling(Config.VOLATILITY_WINDOW).std().iloc[-1] * np.sqrt(252)
        
        # Prix actuel et Max 20 jours (pour Breakout)
        current_price = closes.iloc[-1]
        rolling_max = closes.rolling(20).max().iloc[-1]

        for ticker in scan_list:
            if ticker not in closes.columns: continue
            if ticker in ["BIL", "IEF", "AGG", "EEM"]: continue # On exclut les outils de régime
            
            # --- SCORING VALKYRIE ---
            ret = returns.get(ticker, 0)
            vol = short_vol.get(ticker, 0)
            
            if pd.isna(ret) or pd.isna(vol) or vol == 0: continue
            
            # Score = Rendement / Volatilité (Sharpe simplifié)
            score = ret / vol
            
            if score > 0: # On ne veut que du positif
                candidates.append({
                    'ticker': ticker,
                    'score': score,
                    'volatility': vol,
                    'price': current_price[ticker],
                    'max_20d': rolling_max[ticker]
                })
        
        # 2. SÉLECTION (TOP 3)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        top_picks = candidates[:3] # On garde les 3 meilleurs
        
        # 3. SIZING (Dimensionnement)
        final_portfolio = []
        target_vol = Config.TARGET_VOL_BULL # 25%
        
        for asset in top_picks:
            # Formule Volatilité Cible : (Cible / Vol_Actuelle) * Capital_Slot
            # Slot = 1/3 du capital (car Top 3)
            base_slot_weight = 1.0 / 3.0
            
            vol_ratio = target_vol / asset['volatility']
            weight = base_slot_weight * vol_ratio
            
            # Boost Breakout : Si prix > 98% du plus haut 20j -> +20% taille
            is_breakout = asset['price'] >= (asset['max_20d'] * 0.98)
            if is_breakout:
                weight *= 1.2
                asset['note'] = "🔥 BREAKOUT"
            else:
                asset['note'] = "✅ STRONG TREND"
            
            # Plafond de sécurité (Max 40% par ligne)
            weight = min(weight, Config.MAX_POSITION_SIZE)
            
            asset['weight'] = round(weight, 3)
            final_portfolio.append(asset)
            
        return final_portfolio

    def select_defense_portfolio(self, safe_asset):
        """
        En mode défense, c'est simple : 100% sur l'actif refuge choisi.
        """
        return [{
            'ticker': safe_asset,
            'weight': 1.0,
            'score': 0,
            'note': "🛡️ BUNKER MODE"
        }]