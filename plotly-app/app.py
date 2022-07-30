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
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


sidebar = html.Div([
    html.H2("Sidebar", className="display-4"),
    dbc.Nav([
        dbc.NavLink("Section 1", href="/section-1", active="exact"),
        dbc.NavLink("Section 2", href="/section-2", active="exact"),
        dbc.NavLink("Section 3", href="/section-3", active="exact")
    ],
        vertical=True,
        pills=True,
        style=SIDEBAR_STYLE,
    ),
])

content = html.Div(id="page-content")

app.layout = html.Div([
    content,
    sidebar,

    dash.page_container
])


if __name__ == "__main__":
    app.run_server(debug=True)
