# ==============================================================================
# FICHIER : intelligence/mistral_client.py
# ROLE : L'Oracle (Connecteur API Mistral)
# ==============================================================================
import requests
from config.settings import Config
from intelligence.prompts import Prompts  # <-- Import propre des textes

class MistralOracle:
    def __init__(self):
        self.api_key = Config.MISTRAL_API_KEY
        self.model = Config.MISTRAL_MODEL
        self.endpoint = "https://api.mistral.ai/v1/chat/completions"

    def analyze_risk(self, ticker, headlines):
        """
        Analyse les titres et décide s'il y a un danger immédiat (Veto).
        """
        if not self.api_key or not headlines:
            return "SAFE"

        # On prépare le texte des news
        news_text = " | ".join(headlines)
        
        # On injecte les variables dans le template du Prompt
        prompt = Prompts.RISK_ANALYSIS.format(ticker=ticker, headlines=news_text)

        try:
            # Appel API rapide (max 10 tokens car on veut juste SAFE/DANGER)
            content = self._call_api(prompt, max_tokens=10)
            clean_resp = content.strip().upper()
            
            if "DANGER" in clean_resp:
                return "DANGER"
            return "SAFE"
        except Exception as e:
            print(f"⚠️ Erreur IA Risk : {e}")
            return "SAFE"

    def get_market_commentary(self, regime, top_picks, macro_data=None):
        """
        Génère le commentaire global de fin de journée.
        """
        if not self.api_key: return "IA non connectée."

        tickers = [x['ticker'] for x in top_picks]
        
        # On formatte le prompt
        # (Si tu as macro_data plus tard, tu pourras l'ajouter ici)
        prompt = Prompts.STRATEGY_BRIEF.format(
            regime=regime, 
            tickers=tickers
        )
        
        return self._call_api(prompt, max_tokens=150)

    def _call_api(self, prompt, max_tokens):
        """Fonction interne générique pour appeler l'API."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3, 
            "max_tokens": max_tokens
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        return f"Erreur API ({response.status_code})"