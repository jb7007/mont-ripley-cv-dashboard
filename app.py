import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

def load_dashboard_data():
    raw_df = pd.read_csv("data/example_data_campus.csv")

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

df = load_dashboard_data()

app = Dash(external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container(
    [
        html.H1("Mont Ripley CV Dashboard", className="app-title"),
        html.P("Now with one real callback.", className="app-subtitle"),

        html.Label("Filter by class"),
        dcc.Dropdown(
            id="class-filter",
            options=[{"label": c, "value": c} for c in sorted(df["class_name"].unique())],
            value=sorted(df["class_name"].unique()),
            multi=True
        ),

        html.Br(),

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

@callback(
    Output("detections-table", "rowData"),
    Input("class-filter", "value")
)
def filter_table(selected_classes):
    filtered_df = df[df["class_name"].isin(selected_classes)]
    return filtered_df.to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)