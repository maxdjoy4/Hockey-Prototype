# Hockey KPI Dashboard Prototype

This is a simple Streamlit dashboard for hockey team performance analysis.

## What it does

- Upload CSV or Excel game data
- Calculates category scores
- Calculates an overall game performance score
- Shows trends over time
- Identifies top strengths and areas to improve
- Generates simple coaching insights
- Allows scored data export

## How to run

1. Install Python.
2. Open this folder in VS Code or your terminal.
3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

## Data template

Use `sample_game_data.csv` as the template.

The scoring formula is only a starting point. You should adjust the category weights and scoring logic based on what you believe matters most for Dal/AUS performance.