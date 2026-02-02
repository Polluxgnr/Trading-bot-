# ==============================================================================
# FICHIER : interfaces/discord_bot.py
# ROLE : Reporter visuel (Envoie des rapports riches sur Discord)
# ==============================================================================
import requests
import datetime
from config.settings import Config

class DiscordBot:
    def __init__(self):
        self.webhook_url = Config.DISCORD_WEBHOOK

    def send_embed(self, title, description, color, fields=None):
        """Envoie un message formaté 'Rich Embed'."""
        if not self.webhook_url or "http" not in self.webhook_url:
            print("⚠️ [Discord] Webhook non configuré. Message ignoré.")
            return

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields if fields else [],
            "footer": {
                "text": f"AEGIS SENTINEL • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "icon_url": "https://i.imgur.com/8p5X5Kx.png" # Logo optionnel
            }
        }

        try:
            payload = {"embeds": [embed]}
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"❌ [Discord] Erreur d'envoi : {e}")

    def notify_decision(self, regime, orders, ai_comment=None, metrics=None):
        """Génère le rapport final avec Métriques Pro."""
        
        # 1. Couleur selon le régime
        if regime == "ATTACK":
            color = 65280 # Vert
            icon = "⚔️"
        else:
            color = 16711680 # Rouge
            icon = "🛡️"

        fields = []

        # --- BLOC A : MÉTRIQUES DE PERFORMANCE (Nouveau) ---
        if metrics:
            stats_text = (
                f"📊 **Sharpe:** {metrics['sharpe']:.2f} | "
                f"**Sortino:** {metrics['sortino']:.2f}\n"
                f"📉 **Max DD:** {metrics['max_drawdown']:.1%} | "
                f"**Trades:** {metrics['total_trades']}"
            )
            fields.append({
                "name": "PERFORMANCE LIVE",
                "value": stats_text,
                "inline": False
            })

        # --- BLOC B : ORDRES DU JOUR ---
        total_invested = 0
        for item in orders:
            capital = item['weight'] * Config.INITIAL_CAPITAL
            total_invested += item['weight']
            
            field_value = f"**{item['weight']:.1%}** (${capital:.0f})\n*{item['note']}*"
            fields.append({
                "name": f"{item['ticker']}", 
                "value": field_value, 
                "inline": True
            })

        # Cash restant
        cash_pct = 1.0 - total_invested
        if cash_pct > 0.01:
            fields.append({
                "name": "CASH (BIL)", 
                "value": f"**{cash_pct:.1%}** (Réserve)", 
                "inline": True
            })

        # --- BLOC C : IA ---
        description = f"**Régime : {regime}**"
        if ai_comment:
            description += f"\n\n🧠 **Mistral Analysis:**\n*{ai_comment}*"

        self.send_embed(
            title=f"{icon} AEGIS STRATEGY UPDATE",
            description=description,
            color=color,
            fields=fields
        )

    def send_chart(self, image_buffer):
        """Envoie le graphique de performance."""
        if not self.webhook_url: return

        try:
            # On remet le curseur au début du fichier
            image_buffer.seek(0)
            files = {'file': ('chart.png', image_buffer, 'image/png')}
            
            payload = {"content": "📊 **RAPPORT DE PERFORMANCE VISUEL**"}
            requests.post(self.webhook_url, data=payload, files=files)
        except Exception as e:
            print(f"❌ [Discord] Erreur envoi image : {e}")