# ==============================================================================
# FICHIER : core/state_manager.py
# ROLE : Persistance de session (Empêche le double trading et gère les crashs)
# ==============================================================================
import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, filename="database/system_state.json"):
        self.filename = filename
        self._ensure_db()

    def _ensure_db(self):
        """Vérifie que le dossier et le fichier JSON existent."""
        if not os.path.exists("database"):
            os.makedirs("database")
            
        if not os.path.exists(self.filename):
            # État par défaut si le fichier n'existe pas
            default_state = {
                "last_run": None,
                "current_regime": "UNKNOWN",
                "notes": "Initialisation système"
            }
            self._save(default_state)

    def _save(self, data):
        """Écrit les données dans le JSON."""
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def _load(self):
        """Lit les données du JSON."""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"last_run": None, "current_regime": "UNKNOWN"}

    def mark_trading_done(self):
        """
        Marque la journée actuelle comme 'traitée'.
        À appeler APRÈS l'exécution des ordres.
        """
        data = self._load()
        data["last_run"] = datetime.now().strftime("%Y-%m-%d")
        self._save(data)

    def already_traded_today(self):
        """
        Vérifie si le bot a déjà tourné aujourd'hui.
        Retourne True si oui, False sinon.
        """
        data = self._load()
        last_run = data.get("last_run")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if last_run == today:
            return True
        return False

    def update_regime(self, regime):
        """Sauvegarde le régime actuel (ATTACK/DEFENSE) pour mémoire."""
        data = self._load()
        data["current_regime"] = regime
        self._save(data)

    def get_current_regime(self):
        """Récupère le dernier régime connu."""
        data = self._load()
        return data.get("current_regime", "UNKNOWN")