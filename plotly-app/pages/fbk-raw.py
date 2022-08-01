import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("FBK Raw Data", className="header-title")

dropdown = dbc.DropdownMenu(
    # html.I(className="fa-solid fa-location-dot"),
    label="Stazione",
    children=[
        dbc.DropdownMenuItem("Trento - S. Chiara"),
        dbc.DropdownMenuItem("Trento - Via Bolzano")
    ],
)

download_btn = dbc.Button(
    "Download full data",
    outline=True,
    color="primary",
    class_name="header-btn"
)

header = html.Div(
    [title, dropdown, download_btn],
    className="section-header"
)

layout = html.Div([
    header
])
