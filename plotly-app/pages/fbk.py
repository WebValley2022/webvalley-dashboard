import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("FBK Fitted Data", className="header-title")

dropdown = dbc.DropdownMenu(
    label="Stazione",
    children=[
        dbc.DropdownMenuItem("Trento - S. Chiara"),
        dbc.DropdownMenuItem("Trento - Via Bolzano")
    ],
    color="secondary"
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

header = html.Div(
    [title, dropdown, download_btn],
    className="section-header"
)

layout = html.Div(
    header,
    className="section")
