import dash
from dash import Dash, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


sidebar = html.Div([
    html.H2("LOGO FBK", className="display-4"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("FBK Raw Data", href="/fbk-raw", active="exact"),
        dbc.NavLink("FBK Fitted Data", href="/fbk", active="exact"),
        dbc.NavLink("APPA Data", href="/appa", active="exact")
    ],
        vertical=True,
        pills=True,
    ),
],
    style=SIDEBAR_STYLE,
)

app.layout = html.Div([
    sidebar,

    dash.page_container
])


if __name__ == "__main__":
    app.run_server(debug=True)
