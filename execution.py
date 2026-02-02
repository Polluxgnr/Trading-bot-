# ==============================================================================
# FICHIER : core/execution.py (VERSION NETTOYAGE AUTO + METRICS)
# ROLE : Exécuteur d'Ordres (Alpaca Bridge)
# ==============================================================================
import time
import math
from alpaca_trade_api.rest import REST
from config.settings import Config

class ExecutionManager:
    def __init__(self):
        # Connexion API Alpaca
        self.api = REST(
            Config.ALPACA_KEY,
            Config.ALPACA_SECRET,
            Config.ALPACA_ENDPOINT
        )
        try:
            account = self.api.get_account()
            print(f"✅ [Execution] Alpaca connecté. Cash: ${float(account.cash):.2f}")
        except Exception as e:
            print(f"❌ [Execution] Erreur connexion Alpaca: {e}")

    def is_market_open(self):
        """Vérifie si la bourse est ouverte."""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except:
            return False

    def get_equity(self):
        """Récupère la valeur totale du portefeuille (pour l'historique)."""
        try:
            account = self.api.get_account()
            return float(account.equity)
        except:
            return Config.INITIAL_CAPITAL

    def get_trade_count(self):
        """Compte le nombre total d'ordres exécutés (FILL) depuis le début."""
        try:
            # On récupère les activités de type 'FILL' (Ordres remplis)
            activities = self.api.get_activities(activity_types='FILL')
            return len(activities)
        except Exception as e:
            print(f"⚠️ Impossible de compter les trades: {e}")
            return 0

    def execute_orders(self, orders):
        """
        Transforme le plan de bataille (Target Weights) en ordres réels.
        """
        print("\n⚙️ [Execution] Démarrage du Rebalancing...")
        
        # --- ETAPE CRITIQUE : NETTOYAGE ---
        # On annule tous les ordres en attente pour libérer le Buying Power
        try:
            self.api.cancel_all_orders()
            print("🧹 [Execution] Ordres précédents annulés (Buying Power libéré).")
            time.sleep(2) # On laisse 2 sec à Alpaca pour mettre à jour le solde
        except Exception as e:
            print(f"⚠️ Erreur Annulation Ordres: {e}")

        # 1. Récupération État Actuel
        try:
            positions = self.api.list_positions()
            account = self.api.get_account()
            equity = float(account.equity)
            buying_power = float(account.buying_power)
            
            # Sécurité : Si le Buying Power est buggé (parfois chez Alpaca Paper), on utilise le Cash
            if buying_power < equity * 0.5:
                 print(f"⚠️ Buying Power faible (${buying_power}). Utilisation de l'Equity estimée.")
                 # On ne change pas 'equity', c'est notre base de calcul
        except Exception as e:
            print(f"❌ Erreur compte: {e}")
            return

        # Conversion positions actuelles en dictionnaire {Symbol: Valeur_Dollars}
        current_holdings = {p.symbol: float(p.market_value) for p in positions}
        
        # 2. Identification des Cibles (Target)
        # On convertit les % cibles en Dollars
        targets = {}
        for item in orders:
            targets[item['ticker']] = item['weight'] * equity

        # ---------------------------------------------------------
        # ÉTAPE A : VENTES (D'abord on vend pour libérer du cash)
        # ---------------------------------------------------------
        for symbol, current_val in current_holdings.items():
            # Cas 1: L'actif n'est plus dans le plan -> On vend tout
            if symbol not in targets and symbol != Config.CASH_SYMBOL:
                print(f"🔻 VENTE TOTALE : {symbol} (Sortie de stratégie)")
                self._submit_order(symbol, qty=0, notional=current_val, side='sell')
                continue
            
            # Cas 2: L'actif est là mais on doit réduire la taille
            if symbol in targets:
                target_val = targets[symbol]
                if current_val > target_val * 1.05: # Marge de 5%
                    diff = current_val - target_val
                    print(f"🔻 RÉDUCTION : {symbol} (-${diff:.2f})")
                    self._submit_order(symbol, qty=0, notional=diff, side='sell')

        time.sleep(2) # Pause post-vente

        # ---------------------------------------------------------
        # ÉTAPE B : ACHATS
        # ---------------------------------------------------------
        for symbol, target_val in targets.items():
            if symbol == Config.CASH_SYMBOL: continue 

            current_val = current_holdings.get(symbol, 0.0)
            
            # Si on est sous-investi
            if current_val < target_val * 0.95:
                diff = target_val - current_val
                
                # Vérification finale du Buying Power disponible
                try:
                    acct = self.api.get_account()
                    bp = float(acct.buying_power)
                    if diff > bp:
                        print(f"⚠️ Ajustement Achat {symbol} : ${diff:.2f} -> ${bp:.2f} (Limite Buying Power)")
                        diff = bp * 0.95 # On prend une marge de sécu
                except:
                    pass

                if diff > 10: # On n'achète pas des miettes en dessous de 10$
                    print(f"🚀 ACHAT : {symbol} (+${diff:.2f})")
                    self._submit_order(symbol, qty=0, notional=diff, side='buy')

    def _submit_order(self, symbol, qty, notional, side):
        """Helper pour envoyer l'ordre."""
        try:
            if notional < 1: return 
            
            self.api.submit_order(
                symbol=symbol,
                notional=round(notional, 2),
                side=side,
                type='market',
                time_in_force='day'
            )
            time.sleep(0.5) 
        except Exception as e:
            print(f"❌ Erreur Ordre {symbol}: {e}")