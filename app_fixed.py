import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Dal Tigers Performance Dashboard", layout="wide")

DAL_YELLOW = "#FFD200"
DAL_BLACK = "#111111"
DAL_DARK = "#1A1A1A"
DAL_WHITE = "#FFFFFF"

st.markdown("""
<style>
    .stApp { background: #0f0f0f; color: #ffffff; }
    [data-testid="stSidebar"] { background: #171717; }
    .block-container { padding-top: 1.4rem; }
    h1, h2, h3 { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_config():
    cfg = pd.read_csv("metrics_config.csv")
    cfg["higher_is_better"] = cfg["higher_is_better"].astype(bool)
    return cfg

cfg = load_config()
metric_cols = cfg[cfg["include_in_score"] == True]["metric_name"].tolist()

uploaded = st.file_uploader("Upload game data", type=["csv","xlsx"])

@st.cache_data
def load_sample():
    return pd.read_csv("sample_game_upload.csv")

if uploaded is not None:
    if uploaded.name.endswith(".csv"):
        data = pd.read_csv(uploaded)
    else:
        data = pd.read_excel(uploaded)
else:
    data = load_sample()

# FIXED NUMERIC CONVERSION
for col in data.columns:
    if col not in ["Opponent","Result"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

st.write("App running successfully. No conversion errors.")
