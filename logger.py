# ==============================================================================
# FICHIER : utils/logger.py
# ROLE : Gestion des logs (Console Colorée + Fichier Persistant pour VM)
# ==============================================================================
import logging
import sys
from colorama import Fore, Style, init

# Initialisation des couleurs pour Windows
init(autoreset=True)

class ConsoleFormatter(logging.Formatter):
    """
    Formateur pour la Console (Joli, Coloré, Icones)
    """
    def format(self, record):
        # Choix de la couleur et de l'icône selon la gravité
        if record.levelno >= logging.ERROR:
            prefix = f"{Fore.RED}➤ 💥 "
        elif record.levelno >= logging.WARNING:
            prefix = f"{Fore.YELLOW}➤ ⚠️ "
        elif record.levelno == logging.INFO:
            prefix = f"{Fore.CYAN}➤ "
        else:
            prefix = f"{Fore.WHITE}➤ "
        
        # On modifie le message juste pour l'affichage console
        original_msg = record.msg
        record.msg = f"{prefix}{original_msg}{Style.RESET_ALL}"
        res = super().format(record)
        
        # On remet le message original pour ne pas corrompre le fichier log
        record.msg = original_msg
        return res

# 1. Création du Logger Global
log = logging.getLogger("Aegis")
log.setLevel(logging.INFO)

# Nettoyage des handlers existants (évite les doublons si reload)
if log.hasHandlers():
    log.handlers.clear()

# ------------------------------------------------------------------
# HANDLER 1 : CONSOLE (Ce que vous voyez à l'écran)
# ------------------------------------------------------------------
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ConsoleFormatter("%(message)s"))
log.addHandler(console_handler)

# ------------------------------------------------------------------
# HANDLER 2 : FICHIER (Ce qui reste sur le disque dur de la VM)
# ------------------------------------------------------------------
# Enregistre tout dans 'aegis.log' à la racine
file_handler = logging.FileHandler("aegis.log", mode='a', encoding='utf-8')

# Format plus technique pour le fichier : DATE - LEVEL - MESSAGE
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

log.addHandler(file_handler)

# Test immédiat pour vérifier que le fichier se crée
log.info("📝 Système de logging initialisé (Console + Fichier).")