# 🛡️ Project AEGIS: Autonomous AI-Driven Portfolio Hedge Fund

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)
![AI](https://img.shields.io/badge/AI-Mistral%20Large%202-7C3AED.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live%20Cloud%20Deployment-red.svg?style=for-the-badge)
![Finance](https://img.shields.io/badge/Finance-Alpaca%20%7C%20Yahoo-green.svg?style=for-the-badge)

**AEGIS** (mon trading bot) est un système de trading algorithmique institutionnel conçu pour la gestion autonome d'un portefeuille multi actifs (Actions Tech, ETFs, Or). Contrairement aux bots classiques basés sur des indicateurs techniques isolés, AEGIS utilise un **"AI Logic Gate"** (Mistral Large 2) pour valider chaque signal technique par une analyse de sentiment macro économique en temps réel.

---

## 🏗️ Architecture du Système (Sentinel Framework)

Le système opère sur une instance Google Cloud 24/7 et exécute un cycle de décision structuré en 4 couches de défense :

### 1. 📥 Ingestion & Data Hygiene
* **Hybrid Pipeline** : Ingestion via `yfinance` optimisée avec `curl_cffi` pour assurer la stabilité des flux de données sur les serveurs Cloud.
* **Asset Universe** : Surveillance dynamique de 32 tickers incluant les indices (`SPY`, `QQQ`), les leaders technologiques (`AAPL`, `NVDA`, `GOOGL`), et les actifs de refuge (`GLD`).

### 2. 🧠 Strategy Core: "Trend King" Logic
Le moteur décisionnel suit une logique de suivi de tendance robuste :

* **Market Regime Filter** : Analyse de la tendance primaire via la $SMA 200$ sur le SPY.
    * **Régime ATTACK** : Si $Prix > SMA200$, le bot déploie le capital sur les actifs à fort momentum.
    * **Régime DEFENSE** : Si $Prix < SMA200$, le système liquide les positions risquées pour se réfugier en Cash ou en Or.
* **Mistral Oracle** : L'IA valide l'analyse technique en traitant les news récentes pour éliminer les "faux signaux" via un moteur NLP avancé.

### 3. 🛡️ Risk Engineering & Execution
* **Anti Leverage Policy** : Allocation stricte sur le cash disponible (Notional Trading) pour éliminer tout risque de liquidation.
* **Dynamic Rebalancing** : Ajustement automatique du portefeuille pour maintenir une exposition équilibrée entre les leaders du marché.
* **Alpaca Integration** : Exécution directe des ordres via API avec gestion des erreurs et des limites de taux.

### 4. 📊 Monitoring & Visual Intelligence
* **Live Dashboard** : Interface Streamlit temps réel (Port 8501) affichant la courbe d'équité et le régime actuel.
* ![AEGIS Dashboard](assets/streamlit_screenshot.png)
* **Discord Sentinel** : Reporting quotidien automatisé incluant des snapshots graphiques et le résumé de l'analyse IA.
![Discord Report](assets/discord_screenshot.png)
---

## ⚡ Backtesting & Validation Pipeline

Plutôt que de se fier à des performances passées statiques, AEGIS utilise un pipeline de validation rigoureux pour assurer la robustesse des signaux avant l'exécution Live.

### Méthodologie de Test :
* **Vectorized Backtesting** : Simulation via `pandas` sur 2 ans de données historiques (OHLCV) pour calculer le ratio de Sharpe et le Drawdown maximum.
* **Out of Sample Testing** : Validation du modèle sur des données que le bot n'a jamais "vues" pour éviter l'overfitting.
* **Stress Testing** : Simulation de crashs de marché (ex: 2022) pour vérifier l'efficacité du basculement en mode **DEFENSE**.

> **Note sur le Live Trading** : Le système est actuellement en phase de **Forward Testing** (Paper Trading) afin de valider la corrélation entre les backtests théoriques et l'exécution réelle.

### 📊 Stratégie "Trend King" : Aperçu des Backtests (Insights)

| Scénario Testé | Comportement Observé | Impact sur le Portefeuille |
| :--- | :--- | :--- |
| **Marché Haussier** | Long-only sur leaders Tech | Maximisation du rendement pondéré |
| **Marché Volatile** | Rotation vers l'Or (GLD) & Cash | Réduction drastique du Drawdown |
| **Annonces Macro (Fed)** | Pause stratégique via l'Oracle IA | Évitement de la volatilité court-terme |

--- 

## 🛠️ Technology Stack
* **Core** : Python 3.11 (Architecture modulaire : `Brain`, `Data`, `Execution`)
* **Cloud** : Google Cloud Platform (Compute Engine Debian)
* **IA** : Mistral Large 2 (Decision Validation via NLP)
* **Visuals** : Plotly & Streamlit (Dashboarding)
* **Automation** : Bash Sentinel scripts pour l'auto-restart et la persistence

---

## 🚀 Installation & Autonomous Setup

### 1. Initialisation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 2. Déploiement du Trading Bot (24/7)

```bash
nohup ./run_bot.sh > output.log 2>&1 &

```

### 3. Déploiement du Dashboard

```bash
nohup python3 -m streamlit run interfaces/dashboard.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &

```

---

## 🗺️ Roadmap & Évolutions

* [ ] **Intégration Crypto** : Ajout du BTC/ETH via Alpaca Crypto API.
* [ ] **Multi-Model Voting** : Faire voter Mistral Large et GPT-4o pour une décision encore plus robuste.
* [ ] **Analyse de Sentiment Social** : Scraping de Reddit/X pour détecter les mouvements retail.

---

## 🛡️ Disclaimer

*Ce projet est une démonstration technique de finance quantitative. Le trading comporte des risques réels. L'utilisation de ce logiciel est sous l'entière responsabilité de l'utilisateur.*

# 🛡️ Project AEGIS: Autonomous AI-Driven Portfolio Hedge Fund

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)
![AI](https://img.shields.io/badge/AI-Mistral%20Large%202-7C3AED.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live%20Cloud%20Deployment-red.svg?style=for-the-badge)
![Finance](https://img.shields.io/badge/Finance-Alpaca%20%7C%20Yahoo-green.svg?style=for-the-badge)

**AEGIS** (my trading bot) is an institutional grade algorithmic trading system designed for the autonomous management of a multi asset portfolio (Tech Equities, ETFs, Gold). Unlike conventional bots built on isolated technical indicators, AEGIS relies on an **“AI Logic Gate”** (Mistral Large 2) to validate every technical signal through real time macroeconomic sentiment analysis.

## 🏗️ System Architecture (Sentinel Framework)

The system runs 24/7 on a Google Cloud instance and executes a structured decision cycle across four defensive layers.

### 1. 📥 Ingestion & Data Hygiene
* **Hybrid Pipeline**: Data ingestion via `yfinance`, optimized with `curl_cffi` to ensure stable data flows on cloud servers.
* **Asset Universe**: Dynamic monitoring of 32 tickers, including indices (`SPY`, `QQQ`), technology leaders (`AAPL`, `NVDA`, `GOOGL`), and safe haven assets (`GLD`).

### 2. 🧠 Strategy Core: “Trend King” Logic
The decision engine follows a robust trend following framework.
* **Market Regime Filter**: Primary trend analysis using the SMA 200 on SPY.  
  * **ATTACK Regime**: If Price > SMA200, capital is deployed into high momentum assets.  
  * **DEFENSE Regime**: If Price < SMA200, risky positions are liquidated in favor of Cash or Gold.
* **Mistral Oracle**: The AI validates technical signals by processing recent news to eliminate false positives via an advanced NLP engine.

### 3. 🛡️ Risk Engineering & Execution
* **Anti Leverage Policy**: Strict allocation based solely on available cash (notional trading) to eliminate liquidation risk.
* **Dynamic Rebalancing**: Automatic portfolio adjustments to maintain balanced exposure across market leaders.
* **Alpaca Integration**: Direct order execution via API with robust error handling and rate limit management.

### 4. 📊 Monitoring & Visual Intelligence
* **Live Dashboard**: Real time Streamlit interface (Port 8501) displaying equity curve and current regime.
* **Discord Sentinel**: Automated daily reporting with chart snapshots and AI analysis summaries.

## ⚡ Backtesting & Validation Pipeline

Rather than relying on static historical performance, AEGIS employs a rigorous validation pipeline to ensure signal robustness prior to live execution.

### Testing Methodology
* **Vectorized Backtesting**: `pandas`-based simulations over two years of historical OHLCV data to compute Sharpe ratio and maximum drawdown.
* **Out of Sample Testing**: Model validation on unseen data to prevent overfitting.
* **Stress Testing**: Simulation of market crashes (e.g., 2022) to verify the effectiveness of the **DEFENSE** regime.

> **Live Trading Note**: The system is currently in **Forward Testing** (Paper Trading) to validate the alignment between theoretical backtests and real-world execution.

### 📊 “Trend King” Strategy: Backtest Insights

| Tested Scenario | Observed Behavior | Portfolio Impact |
| :--- | :--- | :--- |
| **Bull Market** | Long only exposure to Tech leaders | Maximized weighted returns |
| **Volatile Market** | Rotation into Gold (GLD) & Cash | Drastic drawdown reduction |
| **Macro Announcements (Fed)** | Strategic pause via AI Oracle | Avoidance of short-term volatility |

## 🛠️ Technology Stack
* **Core**: Python 3.11 (Modular architecture: `Brain`, `Data`, `Execution`)
* **Cloud**: Google Cloud Platform (Compute Engine, Debian)
* **AI**: Mistral Large 2 (Decision validation via NLP)
* **Visuals**: Plotly & Streamlit (Dashboarding)
* **Automation**: Bash Sentinel scripts for auto restart and persistence

## 🚀 Installation & Autonomous Setup

### 1. Initialization
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

