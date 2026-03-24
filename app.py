import pandas as pd
import plotly.express as px
from datetime import datetime

from dash import Dash, html, dcc, Input, Output, callback
import dash_ag_grid as dag
import dash_bootstrap_components as dbc


# ---------- Data loading ----------

def load_raw_data():
    """Load the raw detection CSV exported by the CV pipeline."""
    return pd.read_csv("data/example_data_campus.csv")


def build_dashboard_data(raw_df):
    """Convert raw detection data into the cleaned columns used by the dashboard table."""
    dashboard_df = pd.DataFrame({
        "timestamp": raw_df["time_sec"],
        "camera": "mont_ripley_cam_1",
        "track_id": None,
        "class_name": raw_df["class_name"],
        "confidence": raw_df["confidence"],
        "x1": raw_df["x1"],
        "y1": raw_df["y1"],
        "x2": raw_df["x2"],
        "y2": raw_df["y2"],
        "zone": "unknown"
    })

    return dashboard_df


def build_time_series(raw_df):
    """
    Build demo time-series data from time_sec.
    For now, treat time_sec as elapsed seconds and bucket detections by whole second.
    """
    ts_df = raw_df.copy()
    ts_df["second_bin"] = ts_df["time_sec"].astype(int)

    counts_by_second = (
        ts_df.groupby("second_bin")
        .size()
        .reset_index(name="detections")
        .sort_values("second_bin")
    )

    counts_by_second["cumulative_detections"] = counts_by_second["detections"].cumsum()
    return counts_by_second

# raw_df keeps the original detection output for calculations.
# df is the cleaned version shown in the dashboard table.
raw_df = load_raw_data()
df = build_dashboard_data(raw_df)
time_df = build_time_series(raw_df)


# ---------- KPI calculations ----------

# use the highest frame number as the most recent frame in the dataset.
latest_frame = raw_df["frame"].max()

# count how many detections appear in that most recent frame.
visible_now = int((raw_df["frame"] == latest_frame).sum())

# demo metric: total number of detections in the CSV
cumulative_detections_demo = int(len(raw_df))

# placeholder values until tracking/zone logic is added 
on_lift_now = "—"
off_lift_now = "—"

# Initial timestamp for first page load.
initial_dt = datetime.now()
initial_date = initial_dt.strftime("%B %d, %Y")
initial_time = initial_dt.strftime("%I:%M:%S %p")

# ---------- Figures ----------

detections_fig = px.line(
    time_df,
    x="second_bin",
    y="detections",
    markers=True,
    title="Detections per Second"
)
detections_fig.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Elapsed Time (s)",
    yaxis_title="Detections"
)

cumulative_fig = px.line(
    time_df,
    x="second_bin",
    y="cumulative_detections",
    markers=True,
    title="Cumulative Detections (Demo)"
)
cumulative_fig.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Elapsed Time (s)",
    yaxis_title="Cumulative Detections"
)

# ---------- Dash app setup ----------
app = Dash(external_stylesheets=[dbc.themes.DARKLY])

# ---------- Layout ----------
app.layout = dbc.Container(
    [
        # Fires every second so the date/time header can update live.
        dcc.Interval(
            id="clock-interval",
            interval=1000,
            n_intervals=0
        ),
        
        # header row: title on the left, date/time on the right
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Mont Ripley Lift Dashboard", className="app-title"),
                        html.P("AI-based skier detection and lift monitoring", className="app-subtitle"),
                    ],
                    md=8
                ),
                dbc.Col(
                    [
                        html.Div(f"Date: {initial_date}", id="current-date", className="datetime-text"),
                        html.Div(f"Time: {initial_time}", id="current-time", className="datetime-text"),
                    ],
                    md=4,
                    className="text-md-end"
                )
            ],
            className="mb-4"
        ),

        # kpi card row
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Visible Now", className="kpi-label"),
                            html.H3(visible_now, className="kpi-value")
                        ]), 
                        className="main-card"
                    ), 
                    md=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Cumulative Detections (Demo)", className="kpi-label"),
                            html.H3(f"{cumulative_detections_demo}", className="kpi-value")
                        ]),
                        className="main-card"
                    ),
                    md=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("On Lift", className="kpi-label"),
                            html.H3(on_lift_now, className="kpi-value")
                        ]),
                        className="main-card"
                    ),
                    md=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Off Lift", className="kpi-label"),
                            html.H3(off_lift_now, className="kpi-value")
                        ]),
                        className="main-card"
                    ),
                    md=3
                ),
            ],
            className="mb-4"
        ),
        
        # Chart row
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id="detections-graph",
                                figure=detections_fig
                            )
                        ]),
                        className="main-card"
                    ),
                    md=6
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id="cumulative-graph",
                                figure=cumulative_fig
                            )
                        ]),
                        className="main-card"
                    ),
                    md=6
                ),
            ],
            className="mb-4"
        ),
                
        # raw detections table
        dbc.Card(
            dbc.CardBody([
                html.H4("Raw Detections", className="section-title"),
                dag.AgGrid(
                    id="detections-table",
                    rowData=df.to_dict("records"),
                    columnDefs=[{"field": col} for col in df.columns],
                    defaultColDef={
                        "sortable": True,
                        "filter": True,
                        "resizable": True,
                    },
                    dashGridOptions={"pagination": True},
                    className="ag-theme-alpine-dark",
                    style={"height": "500px", "width": "100%"},
                )
            ]),
            className="main-card"
        )
    ],
    fluid=True,
    className="app-shell"
)

# ---------- Callbacks ----------

@callback(
    Output("current-date", "children"),
    Output("current-time", "children"),
    Input("clock-interval", "n_intervals")
)
def update_clock(n):
    now = datetime.now()
    return (
        f"Date: {now.strftime('%B %d, %Y')}", 
        f"Time: {now.strftime('%I:%M:%S %p')}"
    )


if __name__ == "__main__":
    app.run(debug=True)