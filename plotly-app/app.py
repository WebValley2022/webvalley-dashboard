import dash
from dash import Dash, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])


sidebar = html.Div([
    html.Div([
        html.Img(src="/assets/fbk-logo.png", className="sidebar-img")],
        className="sidebar-img-div"),
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
    className="sidebar",
)

app.layout = html.Div([
    sidebar,

    dash.page_container
])


if __name__ == "__main__":
    app.run_server(debug=True)
