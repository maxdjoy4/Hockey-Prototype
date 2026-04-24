from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "metrics_config.csv"
SAMPLE_PATH = BASE_DIR / "sample_game_upload.csv"

APP_TITLE = "Dal Tigers Performance Intelligence Dashboard"
APP_SUBTITLE = (
    "Weighted KPI scoring model built from AUS win-correlation data, with "
    "coaching-adjusted weights and anomaly scanning."
)

DAL_YELLOW = "#FFD200"
DAL_YELLOW_SOFT = "#FFE46B"
DAL_BLACK = "#050505"
DAL_CHARCOAL = "#101010"
DAL_PANEL = "#171717"
DAL_PANEL_ALT = "#1E1E1E"
DAL_BORDER = "#353535"
DAL_WHITE = "#FFFFFF"
DAL_TEXT_MUTED = "#BDBDBD"
DAL_SUCCESS = "#3FD488"
DAL_DANGER = "#FF6B6B"

st.set_page_config(page_title="Dal Tigers Performance Dashboard", layout="wide")


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --dal-yellow: {DAL_YELLOW};
                --dal-yellow-soft: {DAL_YELLOW_SOFT};
                --dal-black: {DAL_BLACK};
                --dal-charcoal: {DAL_CHARCOAL};
                --dal-panel: {DAL_PANEL};
                --dal-panel-alt: {DAL_PANEL_ALT};
                --dal-border: {DAL_BORDER};
                --dal-white: {DAL_WHITE};
                --dal-muted: {DAL_TEXT_MUTED};
                --dal-success: {DAL_SUCCESS};
                --dal-danger: {DAL_DANGER};
            }}

            .stApp {{
                background:
                    radial-gradient(circle at top right, rgba(255, 210, 0, 0.18), transparent 24%),
                    radial-gradient(circle at top left, rgba(255, 255, 255, 0.05), transparent 18%),
                    linear-gradient(180deg, #0b0b0b 0%, #111111 100%);
                color: var(--dal-white);
            }}

            .block-container {{
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1420px;
            }}

            [data-testid="stSidebar"] {{
                background:
                    linear-gradient(180deg, rgba(255, 210, 0, 0.08) 0%, rgba(255, 210, 0, 0.02) 12%, #101010 12%, #101010 100%);
                border-right: 1px solid rgba(255, 210, 0, 0.16);
            }}

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {{
                color: var(--dal-white);
            }}

            h1, h2, h3, h4 {{
                color: var(--dal-white);
                letter-spacing: 0.01em;
            }}

            .hero-shell {{
                background:
                    linear-gradient(135deg, rgba(255, 210, 0, 0.18), rgba(255, 255, 255, 0.05)),
                    linear-gradient(180deg, #141414 0%, #0f0f0f 100%);
                border: 1px solid rgba(255, 210, 0, 0.22);
                border-radius: 28px;
                padding: 1.6rem 1.7rem;
                box-shadow: 0 24px 48px rgba(0, 0, 0, 0.26);
                margin-bottom: 1rem;
            }}

            .hero-kicker {{
                display: inline-block;
                padding: 0.34rem 0.7rem;
                border-radius: 999px;
                background: rgba(255, 210, 0, 0.12);
                border: 1px solid rgba(255, 210, 0, 0.32);
                color: var(--dal-yellow);
                font-size: 0.82rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.9rem;
            }}

            .hero-title {{
                font-size: clamp(1.9rem, 3vw, 3.15rem);
                line-height: 1.06;
                font-weight: 800;
                margin: 0;
            }}

            .hero-title span {{
                color: var(--dal-yellow);
            }}

            .hero-copy {{
                color: var(--dal-muted);
                font-size: 1rem;
                max-width: 860px;
                margin: 0.7rem 0 1rem 0;
            }}

            .hero-chip-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1rem;
            }}

            .hero-chip {{
                padding: 0.46rem 0.78rem;
                border-radius: 999px;
                border: 1px solid rgba(255, 255, 255, 0.09);
                background: rgba(255, 255, 255, 0.04);
                color: var(--dal-white);
                font-size: 0.88rem;
            }}

            .metric-card {{
                position: relative;
                overflow: hidden;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
                border: 1px solid rgba(255, 210, 0, 0.15);
                border-radius: 22px;
                padding: 1rem 1.05rem;
                min-height: 152px;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 18px 36px rgba(0,0,0,.22);
            }}

            .metric-card::after {{
                content: "";
                position: absolute;
                right: -30px;
                top: -30px;
                width: 110px;
                height: 110px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(255,210,0,0.22) 0%, rgba(255,210,0,0.02) 68%, transparent 72%);
            }}

            .metric-label {{
                color: var(--dal-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.74rem;
                font-weight: 700;
                margin-bottom: 0.55rem;
            }}

            .metric-value {{
                color: var(--dal-white);
                font-size: clamp(1.8rem, 2.3vw, 2.5rem);
                line-height: 1;
                font-weight: 800;
                margin-bottom: 0.4rem;
            }}

            .metric-note {{
                color: var(--dal-muted);
                font-size: 0.88rem;
            }}

            .metric-card .accent {{
                color: var(--dal-yellow);
            }}

            .section-shell {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 24px;
                padding: 1rem 1rem 0.35rem 1rem;
                margin-top: 0.4rem;
            }}

            .section-title {{
                font-size: 1.08rem;
                font-weight: 700;
                margin: 0 0 0.2rem 0;
            }}

            .section-copy {{
                color: var(--dal-muted);
                font-size: 0.92rem;
                margin-bottom: 0.8rem;
            }}

            .insight-box {{
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.03));
                border: 1px solid rgba(255, 210, 0, 0.18);
                border-left: 5px solid var(--dal-yellow);
                border-radius: 18px;
                padding: 1rem 1rem;
                margin: 0.35rem 0 0.8rem 0;
                box-shadow: 0 12px 26px rgba(0,0,0,0.16);
            }}

            .flag-red {{
                border-left-color: var(--dal-danger);
            }}

            .flag-green {{
                border-left-color: var(--dal-success);
            }}

            .sidebar-brand {{
                border-radius: 22px;
                padding: 1rem;
                background: linear-gradient(160deg, rgba(255,210,0,0.18), rgba(255,255,255,0.04));
                border: 1px solid rgba(255,210,0,0.16);
                margin-bottom: 1rem;
            }}

            .sidebar-brand h2 {{
                margin: 0 0 0.2rem 0;
                font-size: 1.15rem;
            }}

            .sidebar-brand p {{
                margin: 0;
                color: var(--dal-muted);
                font-size: 0.87rem;
            }}

            .status-pill {{
                display: inline-block;
                border-radius: 999px;
                padding: 0.35rem 0.65rem;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                color: var(--dal-white);
                font-size: 0.82rem;
                margin: 0.15rem 0.15rem 0 0;
            }}

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            .stDateInput > div > div,
            .stNumberInput > div > div {{
                background: rgba(255, 255, 255, 0.04);
                border-color: rgba(255, 255, 255, 0.12);
            }}

            .stButton > button,
            .stDownloadButton > button {{
                border-radius: 999px;
                border: 1px solid rgba(255, 210, 0, 0.26);
                background: linear-gradient(180deg, rgba(255,210,0,0.22), rgba(255,210,0,0.12));
                color: var(--dal-white);
                font-weight: 700;
            }}

            .stDataFrame, div[data-testid="stTable"] {{
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid rgba(255,255,255,0.08);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


@st.cache_data
def load_config() -> pd.DataFrame:
    cfg = pd.read_csv(CONFIG_PATH)
    cfg["higher_is_better"] = cfg["higher_is_better"].map(parse_bool)
    cfg["include_in_score"] = cfg["include_in_score"].map(parse_bool)
    return cfg


@st.cache_data
def load_sample() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_PATH)


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.copy()
    protected_columns = {"Date", "Opponent", "Result"}
    for col in numeric_df.columns:
        if col in protected_columns:
            continue
        converted = pd.to_numeric(numeric_df[col], errors="coerce")
        if converted.notna().sum() > 0:
            numeric_df[col] = converted
    return numeric_df


def normalized_series(series: pd.Series, higher: bool = True) -> pd.Series:
    numeric_series = pd.to_numeric(series, errors="coerce")
    minimum, maximum = numeric_series.min(), numeric_series.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series([50.0] * len(numeric_series), index=numeric_series.index)
    score = (numeric_series - minimum) / (maximum - minimum) * 100
    if not higher:
        score = 100 - score
    return score.clip(0, 100)


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(scored: pd.DataFrame, active_metric_count: int) -> None:
    latest = scored.iloc[-1]
    latest_score = latest.get("Overall Score", np.nan)
    mean_score = scored["Overall Score"].mean() if "Overall Score" in scored else np.nan
    trend_delta = latest_score - mean_score if pd.notna(latest_score) and pd.notna(mean_score) else 0.0
    trend_text = f"{trend_delta:+.1f} vs season average"

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">Dalhousie Tigers Hockey</div>
            <h1 class="hero-title">Performance <span>Dashboard</span></h1>
            <p class="hero-copy">{APP_SUBTITLE}</p>
            <div class="hero-chip-row">
                <div class="hero-chip">Latest game: {latest['Opponent']} {latest['Result']}</div>
                <div class="hero-chip">Overall score: {latest_score:.1f}/100</div>
                <div class="hero-chip">{trend_text}</div>
                <div class="hero-chip">{len(scored)} games loaded</div>
                <div class="hero-chip">{active_metric_count} scoring metrics active</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def base_layout(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=DAL_WHITE),
        margin=dict(l=18, r=18, t=18, b=18),
        hoverlabel=dict(bgcolor=DAL_PANEL_ALT, font_color=DAL_WHITE),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    )
    return fig


def display_frame(df: pd.DataFrame, *, use_container_width: bool = True) -> None:
    width = "stretch" if use_container_width else "content"
    st.dataframe(df, width=width, hide_index=True)


cfg = load_config()
metric_cols = cfg[cfg["include_in_score"]]["metric_name"].tolist()
meta_cols = ["Date", "Opponent", "Result"]

inject_styles()

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <h2>Dal Tigers Hockey</h2>
            <p>Prototype performance lab for team scoring, game review, and anomaly tracking.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "View",
        [
            "Main Dashboard",
            "Category Deep Dive",
            "Game Breakdown",
            "Analyst View",
            "Raw Data + Export",
        ],
    )
    uploaded = st.file_uploader("Upload game data", type=["csv", "xlsx"])
    st.caption(
        "Upload a game-by-game file. Any columns matching the metric config are scored, "
        "and all numeric fields are scanned for anomalies."
    )

if uploaded is not None:
    data = read_uploaded_file(uploaded)
else:
    data = load_sample()

data = data.copy()

if "Date" in data.columns:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
else:
    data["Date"] = pd.date_range("2025-10-01", periods=len(data), freq="7D")

if "Opponent" not in data.columns:
    data["Opponent"] = [f"Game {index + 1}" for index in range(len(data))]

if "Result" not in data.columns:
    data["Result"] = ""

data = coerce_numeric_columns(data)
data = data.sort_values("Date").reset_index(drop=True)

available_metrics = [metric for metric in metric_cols if metric in data.columns]
missing_metrics = [metric for metric in metric_cols if metric not in data.columns]

score_parts = pd.DataFrame(index=data.index)
for _, row in cfg.iterrows():
    metric_name = row["metric_name"]
    if metric_name in data.columns and row["include_in_score"]:
        score_parts[metric_name] = normalized_series(data[metric_name], row["higher_is_better"])

scored = data.copy()
if available_metrics:
    for category in cfg["app_category"].dropna().unique():
        category_metrics = cfg[
            (cfg["app_category"] == category) & (cfg["metric_name"].isin(score_parts.columns))
        ]
        if len(category_metrics) == 0:
            continue
        weights = category_metrics.set_index("metric_name")["weight_pct"]
        weights = weights / weights.sum()
        scored[f"{category} Score"] = sum(score_parts[m] * weights.loc[m] for m in weights.index)
    weights_all = cfg[cfg["metric_name"].isin(score_parts.columns)].set_index("metric_name")["weight_pct"]
    weights_all = weights_all / weights_all.sum()
    scored["Overall Score"] = sum(score_parts[m] * weights_all.loc[m] for m in weights_all.index)
else:
    scored["Overall Score"] = 50.0

score_columns = [col for col in scored.columns if col.endswith(" Score") and col != "Overall Score"]
latest_idx = scored.index[-1]
latest = scored.loc[latest_idx]

weight_map = cfg.set_index("metric_name")["weight_pct"].to_dict()
cat_map = cfg.set_index("metric_name")["app_category"].to_dict()


def game_drivers(idx: int, n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not available_metrics or score_parts.empty:
        empty = pd.DataFrame(columns=["Metric", "Category", "Value", "Normalized Score", "Weighted Impact"])
        return empty, empty

    rows = []
    for metric in available_metrics:
        value = scored.loc[idx, metric]
        normalized_score = score_parts.loc[idx, metric]
        impact = (normalized_score - 50) * weight_map.get(metric, 0) / 100
        rows.append(
            {
                "Metric": metric,
                "Category": cat_map.get(metric, "Other"),
                "Value": value,
                "Normalized Score": round(normalized_score, 1),
                "Weighted Impact": round(impact, 2),
            }
        )

    drivers = pd.DataFrame(rows).sort_values("Weighted Impact", ascending=False)
    return drivers.head(n), drivers.tail(n).sort_values("Weighted Impact")


def make_takeaway(idx: int) -> str:
    positive, negative = game_drivers(idx, 3)
    best = ", ".join(positive["Metric"].tolist()) if len(positive) else "no clear positive drivers"
    weak = ", ".join(negative["Metric"].tolist()) if len(negative) else "no clear negative drivers"
    return (
        f"Positive drivers: {best}. Priority concerns: {weak}. "
        "Use this as a starting point for film review, not as a final conclusion."
    )


def render_upload_status() -> None:
    source_label = uploaded.name if uploaded is not None else "sample_game_upload.csv"
    st.markdown(
        f"""
        <span class="status-pill">Data source: {source_label}</span>
        <span class="status-pill">Metrics configured: {len(metric_cols)}</span>
        <span class="status-pill">Scoring active: {len(available_metrics)}</span>
        """,
        unsafe_allow_html=True,
    )
    if missing_metrics:
        with st.expander(f"Missing {len(missing_metrics)} scoring metrics from this upload"):
            st.write(missing_metrics)


render_hero(scored, len(available_metrics))
render_upload_status()

if page == "Main Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Latest Game Score", f"{latest['Overall Score']:.0f}/100", f"vs {latest['Opponent']}")
    with c2:
        metric_card("Season Average", f"{scored['Overall Score'].mean():.1f}/100", "Across all loaded games")
    with c3:
        best_idx = scored["Overall Score"].idxmax()
        metric_card(
            "Best Game",
            f"{scored['Overall Score'].max():.0f}/100",
            f"vs {scored.loc[best_idx, 'Opponent']}",
        )
    with c4:
        metric_card("Games Loaded", str(len(scored)), f"{len(available_metrics)} scoring metrics active")

    st.divider()
    left, right = st.columns([1.45, 1])
    with left:
        section_heading("Overall Performance Trend", "Score movement across the loaded season sample.")
        trend_fig = px.line(
            scored,
            x="Date",
            y="Overall Score",
            markers=True,
            hover_data=["Opponent", "Result"],
        )
        trend_fig.update_traces(
            line=dict(color=DAL_YELLOW, width=4),
            marker=dict(size=10, color=DAL_YELLOW, line=dict(width=2, color=DAL_BLACK)),
        )
        trend_fig.add_hline(
            y=scored["Overall Score"].mean(),
            line_dash="dash",
            line_color="rgba(255,255,255,0.65)",
            annotation_text="Season average",
            annotation_position="top left",
        )
        base_layout(trend_fig, height=430)
        st.plotly_chart(trend_fig, width="stretch")
    with right:
        section_heading("Latest Category Scores", "Strength profile from the latest game.")
        if score_columns:
            category_df = pd.DataFrame(
                {
                    "Category": [col.replace(" Score", "") for col in score_columns],
                    "Score": [latest[col] for col in score_columns],
                }
            ).sort_values("Score", ascending=True)
            category_fig = px.bar(
                category_df,
                x="Score",
                y="Category",
                orientation="h",
                range_x=[0, 100],
                text_auto=".0f",
            )
            category_fig.update_traces(
                marker_color=DAL_YELLOW,
                textfont_color=DAL_WHITE,
                hovertemplate="%{y}: %{x:.1f}<extra></extra>",
            )
            base_layout(category_fig, height=430)
            st.plotly_chart(category_fig, width="stretch")
        else:
            st.info("No category score columns are available for this upload.")

    section_heading("Coaching Takeaway", "Quick readout based on the weighted driver model.")
    st.markdown(f"<div class='insight-box'>{make_takeaway(latest_idx)}</div>", unsafe_allow_html=True)

    pos, neg = game_drivers(latest_idx, 5)
    a, b = st.columns(2)
    with a:
        section_heading("Top Positive Drivers")
        display_frame(pos)
    with b:
        section_heading("Top Priority Concerns")
        display_frame(neg)

elif page == "Category Deep Dive":
    categories = sorted(cfg["app_category"].dropna().unique())
    category = st.selectbox("Choose category", categories)
    category_score_col = f"{category} Score"
    category_metrics = cfg[cfg["app_category"] == category].sort_values("weight_pct", ascending=False)
    active_metrics = [metric for metric in category_metrics["metric_name"] if metric in data.columns]

    section_heading(
        category,
        "Configured category scoring preserved from the original prototype, now shown with a cleaner match-analysis layout.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        latest_category_value = f"{latest[category_score_col]:.0f}/100" if category_score_col in scored else "N/A"
        metric_card("Latest Category Score", latest_category_value, "Most recent game")
    with c2:
        average_value = f"{scored[category_score_col].mean():.1f}/100" if category_score_col in scored else "N/A"
        metric_card("Category Average", average_value, "Loaded sample")
    with c3:
        metric_card("Active Metrics", f"{len(active_metrics)}/{len(category_metrics)}", "Available in current file")

    if category_score_col in scored:
        category_fig = px.area(
            scored,
            x="Date",
            y=category_score_col,
            hover_data=["Opponent", "Result"],
        )
        category_fig.update_traces(
            line=dict(color=DAL_YELLOW, width=3),
            fillcolor="rgba(255, 210, 0, 0.22)",
        )
        base_layout(category_fig, height=390)
        st.plotly_chart(category_fig, width="stretch")

    left, right = st.columns([1.25, 1])
    with left:
        section_heading("Metric Weights", "Configuration table for this category.")
        display_frame(
            category_metrics[
                [
                    "metric_name",
                    "weight_pct",
                    "higher_is_better",
                    "r_win",
                    "dal_current_value",
                    "dal_dashboard_notes",
                ]
            ]
        )
    with right:
        section_heading("Latest Game Values", "Current-game metric values for active fields.")
        if active_metrics:
            latest_values = pd.DataFrame(
                {"Metric": active_metrics, "Latest Value": [latest[metric] for metric in active_metrics]}
            )
            display_frame(latest_values)
        else:
            st.info("No active metrics from this category are present in the current upload.")

elif page == "Game Breakdown":
    labels = [
        f"{i + 1}. {pd.to_datetime(scored.loc[i, 'Date']).date()} vs {scored.loc[i, 'Opponent']} {scored.loc[i, 'Result']}"
        for i in scored.index
    ]
    choice = st.selectbox("Select game", scored.index, format_func=lambda i: labels[list(scored.index).index(i)])
    game = scored.loc[choice]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Game Score", f"{game['Overall Score']:.0f}/100", "Weighted overall rating")
    with c2:
        metric_card("Opponent", str(game["Opponent"]), "Selected matchup")
    with c3:
        metric_card("Result", str(game["Result"]), str(pd.to_datetime(game["Date"]).date()))

    section_heading("Coach's Snapshot", "Single-game summary driven by the original scoring logic.")
    st.markdown(f"<div class='insight-box'>{make_takeaway(choice)}</div>", unsafe_allow_html=True)

    if score_columns:
        game_category_df = pd.DataFrame(
            {
                "Category": [col.replace(" Score", "") for col in score_columns],
                "Score": [game[col] for col in score_columns],
            }
        ).sort_values("Score", ascending=False)
        game_fig = px.bar(game_category_df, x="Category", y="Score", range_y=[0, 100], text_auto=".0f")
        game_fig.update_traces(marker_color=DAL_YELLOW, textfont_color=DAL_WHITE)
        base_layout(game_fig, height=390)
        st.plotly_chart(game_fig, width="stretch")
    else:
        st.info("No category score columns are available for this game selection.")

    pos, neg = game_drivers(choice, 8)
    a, b = st.columns(2)
    with a:
        section_heading("Positive Drivers")
        display_frame(pos)
    with b:
        section_heading("Negative Drivers")
        display_frame(neg)

elif page == "Analyst View":
    section_heading(
        "Analyst View",
        "Outliers, trend shifts, and anomalies across all numeric fields. This page does not change the scoring model.",
    )

    numeric_cols = [
        col for col in data.columns if col not in meta_cols and pd.api.types.is_numeric_dtype(data[col])
    ]
    controls_left, controls_right = st.columns(2)
    with controls_left:
        window = st.slider("Rolling baseline window", 3, 8, 5)
    with controls_right:
        threshold = st.slider("Flag threshold vs rolling average (%)", 10, 60, 20)

    flags = []
    if len(scored) >= 2:
        idx = scored.index[-1]
        history = scored.iloc[:-1]
        for col in numeric_cols:
            current = scored.loc[idx, col]
            baseline = history[col].tail(window).mean()
            if pd.isna(current) or pd.isna(baseline) or baseline == 0:
                continue
            change = (current - baseline) / abs(baseline) * 100
            if abs(change) >= threshold:
                direction = "Spike" if change > 0 else "Drop"
                in_score = "Yes" if col in available_metrics else "No"
                category = cat_map.get(col, "Extra/Context")
                flags.append(
                    {
                        "Metric": col,
                        "Category": category,
                        "Type": direction,
                        "Current": round(current, 2),
                        "Baseline": round(baseline, 2),
                        "Change %": round(change, 1),
                        "Scoring Metric": in_score,
                    }
                )

    flag_df = (
        pd.DataFrame(flags).sort_values("Change %", key=lambda series: abs(series), ascending=False)
        if flags
        else pd.DataFrame()
    )

    if len(flag_df):
        top_flags = flag_df.head(5)
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Flags Triggered", str(len(flag_df)), "Latest game vs rolling baseline")
        with c2:
            metric_card("Scoring Metrics Flagged", str((flag_df["Scoring Metric"] == "Yes").sum()), "Worth coaching review")
        with c3:
            metric_card("Largest Swing", f"{top_flags.iloc[0]['Change %']:.1f}%", top_flags.iloc[0]["Metric"])

        section_heading("Latest Game Flags", "Highest-magnitude deviations from recent baseline.")
        display_frame(flag_df)
        for _, row in top_flags.iterrows():
            css_class = "flag-green" if row["Type"] == "Spike" else "flag-red"
            st.markdown(
                (
                    f"<div class='insight-box {css_class}'><b>{row['Metric']}</b>: "
                    f"{row['Type']} of {row['Change %']}% vs rolling baseline. "
                    f"Category: {row['Category']}.</div>"
                ),
                unsafe_allow_html=True,
            )
    else:
        st.success("No major anomalies hit the current threshold for the latest game.")

    moves = []
    if len(scored) >= 2 and score_columns:
        for score_col in score_columns:
            current = scored.loc[scored.index[-1], score_col]
            baseline = scored[score_col].iloc[:-1].tail(window).mean()
            moves.append(
                {
                    "Category": score_col.replace(" Score", ""),
                    "Current": round(current, 1),
                    "Rolling Baseline": round(baseline, 1),
                    "Change": round(current - baseline, 1),
                }
            )

    section_heading("Category Score Movement", "Latest category shifts against recent form.")
    if moves:
        movement_df = pd.DataFrame(moves).sort_values("Change")
        display_frame(movement_df)
    else:
        st.info("Not enough category score history is available to show movement.")

else:
    section_heading("Raw Data + Export", "Inspect the upload, scored output, and preserved metric configuration.")
    st.subheader("Uploaded Data")
    st.dataframe(data, width="stretch")
    st.subheader("Scored Data")
    st.dataframe(scored, width="stretch")
    st.download_button(
        "Download scored data",
        scored.to_csv(index=False).encode("utf-8"),
        "scored_dal_dashboard_data.csv",
        "text/csv",
    )
    st.subheader("Metric Configuration")
    st.dataframe(cfg, width="stretch")
