import pandas as pd
from dash import Dash, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

# ---------- Data loading ----------

def load_raw_data():
    """Load the raw detection CSV exported by the CV pipeline."""
    return pd.read_csv("data/example_data_campus.csv")


def build_dashboard_data(raw_df):
    """Convery raw detection data into the cleaned columns used by the dashboard table."""
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


raw_df = load_raw_data()
df = build_dashboard_data(raw_df)


# ---------- KPI calculations ----------

# use the highest frame number as the most recent frame in the dataset.
latest_frame = raw_df["frame"].max()

# count how many detections appear in that most recent frame.
visible_now = int((raw_df["frame"] == latest_frame).sum())

# demo metric: total number of detections in the csv
cumulative_detections_demo = int(len(raw_df))

# placeholder values until tracking/zone logic is added 
on_lift_now = "—"
off_lift_now = "—"

# ---------- Dash app setup ----------
app = Dash(external_stylesheets=[dbc.themes.DARKLY])

# ---------- Layout ----------
app.layout = dbc.Container(
    [
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
                        html.Div("Date: TODO", className="datetime-text"),
                        html.Div("Time: TODO", className="datetime-text"),
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
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.Div("Visible Now", className="kpi-label"),
                    html.H3(visible_now, className="kpi-value")
                ]), className="main-card"), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.Div("Cumulative Detections (Demo)", className="kpi-label"),
                    html.H3(cumulative_detections_demo, className="kpi-value")
                ]), className="main-card"), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.Div("On Lift", className="kpi-label"),
                    html.H3(on_lift_now, className="kpi-value")
                ]), className="main-card"), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.Div("Off Lift", className="kpi-label"),
                    html.H3(off_lift_now, className="kpi-value")
                ]), className="main-card"), md=3),
            ],
            className="mb-4"
        ),
                
        # raw detections table
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
    ],
    fluid=True,
    className="app-shell"
)

if __name__ == "__main__":
    app.run(debug=True)