import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Hockey KPI Dashboard", layout="wide")

st.title("🏒 Hockey KPI Performance Dashboard")
st.caption("Upload game-by-game team data. Analyze. Score. Improve.")

REQUIRED_COLUMNS = [
    "Date", "Opponent", "Result", "Goals For", "Goals Against", "Shots For", "Shots Against",
    "Scoring Chances For", "Scoring Chances Against", "High Danger Chances For",
    "High Danger Chances Against", "Power Play Goals", "Power Play Opportunities",
    "Penalty Kill Goals Against", "Times Shorthanded", "Faceoff Win %",
    "Giveaways", "Takeaways", "Penalty Minutes"
]

DEFAULT_WEIGHTS = {
    "Offense": 0.22,
    "Defense": 0.22,
    "Special Teams": 0.16,
    "Puck Management": 0.18,
    "Discipline": 0.10,
    "Goaltending/Prevention": 0.12
}

def clamp_score(x):
    return max(0, min(100, round(x, 1)))

def pct(n, d):
    if d == 0 or pd.isna(d):
        return np.nan
    return n / d

def score_game(row):
    gf = row["Goals For"]
    ga = row["Goals Against"]
    sf = row["Shots For"]
    sa = row["Shots Against"]
    scf = row["Scoring Chances For"]
    sca = row["Scoring Chances Against"]
    hdcf = row["High Danger Chances For"]
    hdca = row["High Danger Chances Against"]
    ppg = row["Power Play Goals"]
    ppo = row["Power Play Opportunities"]
    pkga = row["Penalty Kill Goals Against"]
    tsh = row["Times Shorthanded"]
    fow = row["Faceoff Win %"]
    giveaways = row["Giveaways"]
    takeaways = row["Takeaways"]
    pim = row["Penalty Minutes"]

    pp_pct = pct(ppg, ppo)
    pk_pct = 1 - pct(pkga, tsh) if tsh > 0 else np.nan

    offense = (
        gf * 12 +
        sf * 0.7 +
        scf * 2.2 +
        hdcf * 3.2
    )

    defense = (
        100 -
        ga * 13 -
        sa * 0.45 -
        sca * 1.9 -
        hdca * 3.0
    )

    special_teams = 50
    if not pd.isna(pp_pct):
        special_teams += pp_pct * 55
    if not pd.isna(pk_pct):
        special_teams += (pk_pct - 0.75) * 80

    puck_management = (
        60 +
        takeaways * 3.0 -
        giveaways * 3.4 +
        (fow - 50) * 0.7
    )

    discipline = 100 - pim * 3.2
    goaltending_prevention = 100 - ga * 11 - hdca * 1.8

    category_scores = {
        "Offense": clamp_score(offense),
        "Defense": clamp_score(defense),
        "Special Teams": clamp_score(special_teams),
        "Puck Management": clamp_score(puck_management),
        "Discipline": clamp_score(discipline),
        "Goaltending/Prevention": clamp_score(goaltending_prevention),
    }

    overall = sum(category_scores[k] * DEFAULT_WEIGHTS[k] for k in DEFAULT_WEIGHTS)
    category_scores["Overall Score"] = clamp_score(overall)
    return pd.Series(category_scores)

def insight_text(row):
    strengths = []
    improvements = []

    if row["Offense"] >= 75:
        strengths.append("created strong offensive value through shot/chance generation")
    if row["Defense"] >= 75:
        strengths.append("limited opponent volume and dangerous looks")
    if row["Puck Management"] >= 75:
        strengths.append("managed the puck well and created more positive possessions")
    if row["Special Teams"] >= 75:
        strengths.append("special teams added meaningful value")
    if row["Discipline"] >= 75:
        strengths.append("discipline helped protect game flow")

    if row["Offense"] < 65:
        improvements.append("offensive generation")
    if row["Defense"] < 65:
        improvements.append("defensive-zone prevention")
    if row["Puck Management"] < 65:
        improvements.append("puck management")
    if row["Special Teams"] < 65:
        improvements.append("special teams")
    if row["Discipline"] < 65:
        improvements.append("discipline")

    strength_sentence = "Key strength: " + (", ".join(strengths) if strengths else "no clear category separated strongly from the profile") + "."
    improve_sentence = "Priority area: " + (", ".join(improvements) if improvements else "maintain current profile and look for smaller tactical edges") + "."
    return strength_sentence + " " + improve_sentence

def load_sample():
    return pd.read_csv("sample_game_data.csv")

with st.sidebar:
    st.header("Upload Data")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    st.markdown("Use the included sample file as your template.")

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
else:
    df = load_sample()

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])
scores = df.apply(score_game, axis=1)
dash = pd.concat([df, scores], axis=1)
dash["Insight"] = dash.apply(insight_text, axis=1)
dash = dash.sort_values("Date")

latest = dash.iloc[-1]
season_avg = dash["Overall Score"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Game Score", f"{latest['Overall Score']:.0f}/100", f"{latest['Overall Score'] - season_avg:.1f} vs avg")
col2.metric("Season Average", f"{season_avg:.1f}/100")
col3.metric("Best Game", f"{dash['Overall Score'].max():.0f}/100")
col4.metric("Games Loaded", len(dash))

st.divider()

left, right = st.columns([1.4, 1])

with left:
    st.subheader("Performance Score Trend")
    fig = px.line(dash, x="Date", y="Overall Score", markers=True, hover_data=["Opponent", "Result"])
    fig.add_hline(y=season_avg, line_dash="dash", annotation_text=f"Season Avg: {season_avg:.1f}")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Latest Game Category Breakdown")
    category_df = pd.DataFrame({
        "Category": list(DEFAULT_WEIGHTS.keys()),
        "Score": [latest[k] for k in DEFAULT_WEIGHTS.keys()]
    })
    fig2 = px.bar(category_df, x="Category", y="Score", range_y=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Game Insight")
st.info(latest["Insight"])

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Positive Drivers")
    category_cols = list(DEFAULT_WEIGHTS.keys())
    positive = category_df.sort_values("Score", ascending=False).head(5)
    st.dataframe(positive, use_container_width=True, hide_index=True)

with c2:
    st.subheader("Areas to Improve")
    improve = category_df.sort_values("Score", ascending=True).head(5)
    st.dataframe(improve, use_container_width=True, hide_index=True)

st.subheader("Full Game Table")
display_cols = ["Date", "Opponent", "Result", "Overall Score"] + list(DEFAULT_WEIGHTS.keys()) + ["Insight"]
st.dataframe(dash[display_cols], use_container_width=True, hide_index=True)

csv = dash.to_csv(index=False).encode("utf-8")
st.download_button("Download scored data as CSV", csv, "scored_hockey_kpi_data.csv", "text/csv")