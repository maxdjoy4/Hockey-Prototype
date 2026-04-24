# Dal Tigers Performance Intelligence Dashboard v2

This is a Streamlit prototype built from the AUS/Dal metric-weight workbook.

## What is included

- Main Dashboard
- Category Deep Dive
- Game Breakdown
- Analyst View for anomalies/outliers
- Raw Data + Export
- Dal-style black/yellow/white visual theme
- `metrics_config.csv` with correlation-based + coaching-adjusted weights
- `sample_game_upload.csv` as a working upload template

## How the scoring works

The app uses the configured KPI list in `metrics_config.csv`.

- Base signal = absolute correlation with winning
- Coaching adjustment = small manual modifier to prevent the model from becoming too outcome-heavy and to emphasize controllable coaching areas
- Adjusted weight = normalized weighted signal
- Direction tells the app whether higher or lower is better
- Each uploaded game is normalized relative to the uploaded dataset

## How to use

1. Open the folder.
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
streamlit run app.py
```

4. Upload your real game-by-game data.

## Upload format

Your upload should include:

- Date
- Opponent
- Result
- Any of the metric columns listed in `metrics_config.csv`

You can also include extra numeric stats. They will not affect the main score unless they are in the config, but they will be scanned in the Analyst View for anomalies.

## Important note

This is a prototype. Once you have the final 30 metrics and preferred weights, update `metrics_config.csv` or ask Codex to update it.
