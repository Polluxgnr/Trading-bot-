# ==============================================================================
# FICHIER : utils/storage.py
# ROLE : Gestionnaire d'État (Black Box Recorder)
# ==============================================================================
import pandas as pd
import os
from datetime import datetime
from config.settings import Config

class StateManager:
    def __init__(self, filename="database/history.csv"):
        self.filename = filename
        self.ensure_db_exists()

    def ensure_db_exists(self):
        """Crée le fichier CSV s'il n'existe pas encore."""
        if not os.path.exists("database"):
            os.makedirs("database")
            
        if not os.path.exists(self.filename):
            # Création de l'en-tête initial
            df = pd.DataFrame(columns=["Date", "Equity", "SPY_Price"])
            # On ajoute une ligne de départ (J-1) pour que le graph ne soit pas vide
            # start_date = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            # df.loc[0] = [start_date, Config.INITIAL_CAPITAL, 0]
            df.to_csv(self.filename, index=False)
            print(f"💾 [Storage] Nouvelle base de données créée : {self.filename}")

    def save_snapshot(self, equity, spy_price):
        """Enregistre l'état du portefeuille à l'instant T."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            df = pd.read_csv(self.filename)
            
            # Évite les doublons si on lance le script 2 fois le même jour
            if today in df['Date'].values:
                # Mise à jour de la ligne existante
                df.loc[df['Date'] == today, ['Equity', 'SPY_Price']] = [equity, spy_price]
                action = "Mise à jour"
            else:
                # Ajout nouvelle ligne
                new_row = pd.DataFrame({"Date": [today], "Equity": [equity], "SPY_Price": [spy_price]})
                df = pd.concat([df, new_row], ignore_index=True)
                action = "Ajout"
            
            df.to_csv(self.filename, index=False)
            print(f"💾 [Storage] Snapshot sauvegardé ({action}) : ${equity:.2f} | SPY ${spy_price:.2f}")
            
        except Exception as e:
            print(f"❌ [Storage] Erreur de sauvegarde : {e}")

    def get_history(self):
        """Charge l'historique pour le graphique."""
        try:
            df = pd.read_csv(self.filename)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            return df
        except Exception:
            return pd.DataFrame() # Retourne vide en cas d'erreur