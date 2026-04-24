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
    .metric-card {
        background: linear-gradient(135deg, #181818 0%, #242424 100%);
        border: 1px solid #333333;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,.25);
    }
    .metric-label { color: #bbbbbb; font-size: .9rem; }
    .metric-value { color: #FFD200; font-size: 2.2rem; font-weight: 800; }
    .insight-box {
        background: #181818;
        border-left: 5px solid #FFD200;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
    }
    .flag-red { border-left-color: #ff5a5f; }
    .flag-green { border-left-color: #32d583; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_config():
    cfg = pd.read_csv("metrics_config.csv")
    cfg["higher_is_better"] = cfg["higher_is_better"].astype(bool)
    return cfg

cfg = load_config()
metric_cols = cfg[cfg["include_in_score"] == True]["metric_name"].tolist()
meta_cols = ["Date", "Opponent", "Result"]

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/Dalhousie_Tigers_logo.svg/320px-Dalhousie_Tigers_logo.svg.png", width=110)
    st.title("Dal Performance")
    page = st.radio("View", ["Main Dashboard", "Category Deep Dive", "Game Breakdown", "Analyst View", "Raw Data + Export"])
    uploaded = st.file_uploader("Upload game data", type=["csv", "xlsx"])
    st.caption("Upload a game-by-game file. The app scores any columns that match the metric config and scans all numeric columns for anomalies.")

@st.cache_data
def load_sample():
    return pd.read_csv("sample_game_upload.csv")

if uploaded is not None:
    if uploaded.name.lower().endswith(".csv"):
        data = pd.read_csv(uploaded)
    else:
        data = pd.read_excel(uploaded)
else:
    data = load_sample()

# Clean date
if "Date" in data.columns:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
else:
    data["Date"] = pd.date_range("2025-10-01", periods=len(data), freq="7D")
if "Opponent" not in data.columns:
    data["Opponent"] = [f"Game {i+1}" for i in range(len(data))]
if "Result" not in data.columns:
    data["Result"] = ""

data = data.sort_values("Date").reset_index(drop=True)

available_metrics = [m for m in metric_cols if m in data.columns]
missing_metrics = [m for m in metric_cols if m not in data.columns]

# Numeric conversion
for col in data.columns:
    if col not in ["Opponent", "Result"]:
        data[col] = pd.to_numeric(data[col], errors="ignore")

def normalized_series(s, higher=True):
    s = pd.to_numeric(s, errors="coerce")
    mn, mx = s.min(), s.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series([50.0] * len(s), index=s.index)
    score = (s - mn) / (mx - mn) * 100
    if not higher:
        score = 100 - score
    return score.clip(0,100)

score_parts = pd.DataFrame(index=data.index)
for _, row in cfg.iterrows():
    m = row["metric_name"]
    if m in data.columns and bool(row["include_in_score"]):
        score_parts[m] = normalized_series(data[m], bool(row["higher_is_better"]))

scored = data.copy()
if available_metrics:
    for cat in cfg["app_category"].dropna().unique():
        cat_metrics = cfg[(cfg["app_category"] == cat) & (cfg["metric_name"].isin(score_parts.columns))]
        if len(cat_metrics) == 0:
            continue
        weights = cat_metrics.set_index("metric_name")["weight_pct"]
        weights = weights / weights.sum()
        scored[f"{cat} Score"] = sum(score_parts[m] * weights.loc[m] for m in weights.index)
    weights_all = cfg[cfg["metric_name"].isin(score_parts.columns)].set_index("metric_name")["weight_pct"]
    weights_all = weights_all / weights_all.sum()
    scored["Overall Score"] = sum(score_parts[m] * weights_all.loc[m] for m in weights_all.index)
else:
    scored["Overall Score"] = 50

score_columns = [c for c in scored.columns if c.endswith(" Score") and c != "Overall Score"]

# Driver analysis per game
weight_map = cfg.set_index("metric_name")["weight_pct"].to_dict()
dir_map = cfg.set_index("metric_name")["higher_is_better"].to_dict()
cat_map = cfg.set_index("metric_name")["app_category"].to_dict()

def game_drivers(idx, n=5):
    rows=[]
    for m in available_metrics:
        val = scored.loc[idx, m]
        ns = score_parts.loc[idx, m]
        impact = (ns - 50) * weight_map.get(m,0) / 100
        rows.append({"Metric":m,"Category":cat_map.get(m,"Other"),"Value":val,"Normalized Score":round(ns,1),"Weighted Impact":round(impact,2)})
    d=pd.DataFrame(rows).sort_values("Weighted Impact", ascending=False)
    return d.head(n), d.tail(n).sort_values("Weighted Impact")

def make_takeaway(idx):
    pos, neg = game_drivers(idx, 3)
    best = ", ".join(pos["Metric"].tolist()) if len(pos) else "no clear positive drivers"
    weak = ", ".join(neg["Metric"].tolist()) if len(neg) else "no clear negative drivers"
    return f"Positive drivers: {best}. Priority concerns: {weak}. Use this as a starting point for film review, not as a final conclusion."

def metric_card(label, value, note=""):
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
        <div style='color:#aaaaaa;font-size:.85rem'>{note}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("🏒 Dal Tigers Performance Intelligence Dashboard")
st.caption("Weighted KPI scoring model built from AUS win-correlation data, with coaching-adjusted weights and anomaly scanning.")

if missing_metrics:
    with st.expander(f"Missing {len(missing_metrics)} scoring metrics from this upload"):
        st.write(missing_metrics)

latest_idx = scored.index[-1]
latest = scored.loc[latest_idx]

if page == "Main Dashboard":
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Latest Game Score", f"{latest['Overall Score']:.0f}/100", f"vs {latest['Opponent']}")
    with c2: metric_card("Season Avg", f"{scored['Overall Score'].mean():.1f}/100", "all uploaded games")
    with c3: metric_card("Best Game", f"{scored['Overall Score'].max():.0f}/100", str(scored.loc[scored['Overall Score'].idxmax(),'Opponent']))
    with c4: metric_card("Games Loaded", f"{len(scored)}", f"{len(available_metrics)} scoring metrics active")

    st.divider()
    left,right = st.columns([1.4,1])
    with left:
        st.subheader("Overall Performance Trend")
        fig=px.line(scored, x="Date", y="Overall Score", markers=True, hover_data=["Opponent","Result"], template="plotly_dark")
        fig.update_traces(line=dict(color=DAL_YELLOW, width=4), marker=dict(size=9))
        fig.add_hline(y=scored['Overall Score'].mean(), line_dash="dash", line_color="white")
        fig.update_layout(height=420, plot_bgcolor="#111111", paper_bgcolor="#111111")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Latest Category Scores")
        cat_df=pd.DataFrame({"Category":[c.replace(" Score","") for c in score_columns],"Score":[latest[c] for c in score_columns]})
        cat_df=cat_df.sort_values("Score", ascending=True)
        fig=px.bar(cat_df, x="Score", y="Category", orientation="h", template="plotly_dark", range_x=[0,100])
        fig.update_traces(marker_color=DAL_YELLOW)
        fig.update_layout(height=420, plot_bgcolor="#111111", paper_bgcolor="#111111")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Coaching Takeaway")
    st.markdown(f"<div class='insight-box'>{make_takeaway(latest_idx)}</div>", unsafe_allow_html=True)

    pos,neg=game_drivers(latest_idx,5)
    a,b=st.columns(2)
    with a:
        st.subheader("Top Positive Drivers")
        st.dataframe(pos, use_container_width=True, hide_index=True)
    with b:
        st.subheader("Top Priority Concerns")
        st.dataframe(neg, use_container_width=True, hide_index=True)

elif page == "Category Deep Dive":
    cats=sorted(cfg["app_category"].dropna().unique())
    cat=st.selectbox("Choose category", cats)
    cat_score_col=f"{cat} Score"
    st.header(cat)
    cat_metrics=cfg[cfg["app_category"]==cat].sort_values("weight_pct", ascending=False)
    active=[m for m in cat_metrics["metric_name"] if m in data.columns]
    c1,c2,c3=st.columns(3)
    with c1: metric_card("Latest Category Score", f"{latest.get(cat_score_col, np.nan):.0f}/100" if cat_score_col in scored else "N/A")
    with c2: metric_card("Category Avg", f"{scored[cat_score_col].mean():.1f}/100" if cat_score_col in scored else "N/A")
    with c3: metric_card("Active Metrics", f"{len(active)}/{len(cat_metrics)}")
    if cat_score_col in scored:
        fig=px.line(scored, x="Date", y=cat_score_col, markers=True, hover_data=["Opponent","Result"], template="plotly_dark")
        fig.update_traces(line=dict(color=DAL_YELLOW, width=4), marker=dict(size=9))
        fig.update_layout(height=380, plot_bgcolor="#111111", paper_bgcolor="#111111")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Metric Weights in This Category")
    st.dataframe(cat_metrics[["metric_name","weight_pct","higher_is_better","r_win","dal_current_value","dal_dashboard_notes"]], use_container_width=True, hide_index=True)
    if active:
        st.subheader("Latest Game Values")
        vals=pd.DataFrame({"Metric":active,"Latest Value":[latest[m] for m in active]})
        st.dataframe(vals, use_container_width=True, hide_index=True)

elif page == "Game Breakdown":
    labels=[f"{i+1}. {scored.loc[i,'Date'].date()} vs {scored.loc[i,'Opponent']} {scored.loc[i,'Result']}" for i in scored.index]
    choice=st.selectbox("Select game", scored.index, format_func=lambda i: labels[list(scored.index).index(i)])
    game=scored.loc[choice]
    c1,c2,c3=st.columns(3)
    with c1: metric_card("Game Score", f"{game['Overall Score']:.0f}/100")
    with c2: metric_card("Opponent", str(game["Opponent"]))
    with c3: metric_card("Result", str(game["Result"]))
    st.markdown(f"<div class='insight-box'>{make_takeaway(choice)}</div>", unsafe_allow_html=True)
    cat_df=pd.DataFrame({"Category":[c.replace(" Score","") for c in score_columns],"Score":[game[c] for c in score_columns]}).sort_values("Score", ascending=False)
    fig=px.bar(cat_df, x="Category", y="Score", template="plotly_dark", range_y=[0,100])
    fig.update_traces(marker_color=DAL_YELLOW)
    fig.update_layout(height=380, plot_bgcolor="#111111", paper_bgcolor="#111111")
    st.plotly_chart(fig, use_container_width=True)
    pos,neg=game_drivers(choice,8)
    a,b=st.columns(2)
    with a:
        st.subheader("Positive Drivers")
        st.dataframe(pos, use_container_width=True, hide_index=True)
    with b:
        st.subheader("Negative Drivers")
        st.dataframe(neg, use_container_width=True, hide_index=True)

elif page == "Analyst View":
    st.header("Analyst View: Outliers, Trend Shifts, and Anomalies")
    st.caption("This page scans all numeric columns, not just the 30 scoring metrics. It does not rank performance; it flags things worth investigating.")
    numeric_cols=[c for c in data.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(data[c])]
    window=st.slider("Rolling baseline window", 3, 8, 5)
    threshold=st.slider("Flag threshold vs rolling average (%)", 10, 60, 20)
    flags=[]
    if len(scored) >= 2:
        idx=scored.index[-1]
        hist=scored.iloc[:-1]
        for col in numeric_cols:
            current=scored.loc[idx,col]
            baseline=hist[col].tail(window).mean()
            if pd.isna(current) or pd.isna(baseline) or baseline == 0:
                continue
            change=(current-baseline)/abs(baseline)*100
            if abs(change) >= threshold:
                direction="Spike" if change > 0 else "Drop"
                in_score="Yes" if col in available_metrics else "No"
                category=cat_map.get(col,"Extra/Context")
                flags.append({"Metric":col,"Category":category,"Type":direction,"Current":round(current,2),"Baseline":round(baseline,2),"Change %":round(change,1),"Scoring Metric":in_score})
    flag_df=pd.DataFrame(flags).sort_values("Change %", key=lambda s: abs(s), ascending=False) if flags else pd.DataFrame()
    if len(flag_df):
        st.subheader("Latest Game Flags")
        st.dataframe(flag_df, use_container_width=True, hide_index=True)
        top=flag_df.head(5)
        for _,r in top.iterrows():
            cls="flag-green" if r["Type"]=="Spike" else "flag-red"
            st.markdown(f"<div class='insight-box {cls}'><b>{r['Metric']}</b>: {r['Type']} of {r['Change %']}% vs rolling baseline. Category: {r['Category']}.</div>", unsafe_allow_html=True)
    else:
        st.success("No major anomalies hit the current threshold for the latest game.")

    st.subheader("Category Score Movement")
    moves=[]
    if len(scored)>=2:
        for c in score_columns:
            current=scored.loc[scored.index[-1],c]
            baseline=scored[c].iloc[:-1].tail(window).mean()
            moves.append({"Category":c.replace(" Score",""),"Current":round(current,1),"Rolling Baseline":round(baseline,1),"Change":round(current-baseline,1)})
    if moves:
        st.dataframe(pd.DataFrame(moves).sort_values("Change"), use_container_width=True, hide_index=True)

else:
    st.header("Raw Data + Export")
    st.subheader("Uploaded Data")
    st.dataframe(data, use_container_width=True)
    st.subheader("Scored Data")
    st.dataframe(scored, use_container_width=True)
    st.download_button("Download scored data", scored.to_csv(index=False).encode("utf-8"), "scored_dal_dashboard_data.csv", "text/csv")
    st.subheader("Metric Configuration")
    st.dataframe(cfg, use_container_width=True)