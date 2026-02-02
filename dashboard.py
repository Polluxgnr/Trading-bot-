# ==============================================================================
# FICHIER : interfaces/dashboard.py
# ROLE : Command Center (Interface Web Streamlit)
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Config Page
st.set_page_config(page_title="AEGIS SENTINEL", page_icon="🛡️", layout="wide")
st.markdown("""<style>.stApp { background-color: #0E1117; color: white; }</style>""", unsafe_allow_html=True)

st.title("🛡️ AEGIS SENTINEL : COMMAND CENTER")
st.markdown("---")

# Chargement Data
FILE_PATH = "database/history.csv"

if not os.path.exists(FILE_PATH):
    st.error("⚠️ En attente de données... Lancez le bot (main.py) une première fois !")
    st.stop()

try:
    df = pd.read_csv(FILE_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"Erreur de lecture du fichier CSV : {e}")
    st.stop()

# KPIs (Indicateurs Clés)
last_equity = df['Equity'].iloc[-1]
start_equity = df['Equity'].iloc[0]
perf_abs = last_equity - start_equity
perf_pct = (perf_abs / start_equity) * 100

col1, col2, col3 = st.columns(3)
col1.metric("💰 NAV (Capital)", f"${last_equity:,.2f}", f"{perf_pct:+.2f}%")
col2.metric("📈 Gain/Perte", f"${perf_abs:+.2f}")
col3.metric("📅 Dernière Mise à jour", df['Date'].iloc[-1].strftime("%Y-%m-%d"))

# Graphique Interactif
st.subheader("Performance vs Marché")
fig = go.Figure()

# Courbe du Bot (Verte)
fig.add_trace(go.Scatter(
    x=df['Date'], 
    y=df['Equity'], 
    mode='lines+markers', 
    name='AEGIS Bot', 
    line=dict(color='#00ff00', width=3)
))

# Courbe du Benchmark SPY (Grise) - Optionnelle
if 'SPY_Price' in df.columns:
    # On normalise le SPY pour qu'il démarre au même montant que le portefeuille
    spy_start = df['SPY_Price'].iloc[0]
    spy_norm = (df['SPY_Price'] / spy_start) * start_equity
    
    fig.add_trace(go.Scatter(
        x=df['Date'], 
        y=spy_norm, 
        mode='lines', 
        name='S&P 500 (Benchmark)', 
        line=dict(color='#888888', width=2, dash='dot') # <--- L'ERREUR ÉTAIT ICI
    ))

fig.update_layout(
    paper_bgcolor='#0E1117', 
    plot_bgcolor='#1e1e1e', 
    font=dict(color='white'), 
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# Historique Brut
with st.expander("📜 Voir l'Historique des Données"):
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)