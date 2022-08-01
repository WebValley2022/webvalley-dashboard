import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, redirect_from=["/"])

title = html.Div("FBK Raw Data", className="header-title")

dropdown = dbc.DropdownMenu(
    # html.I(className="fa-solid fa-location-dot"),
    label="Select location",
    children=[
        dbc.DropdownMenuItem("Trento - S. Chiara"),
        dbc.DropdownMenuItem("Trento - Via Bolzano")
    ],
    color="secondary",
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="btn download-btn"
)

gas_btns = html.Div(
    [
        dbc.RadioItems(
            id="radios",
            class_name="btn-group",
            input_class_name="btn-check",
            label_class_name="btn btn-outline-primary",
            label_checked_class_name="active",
            options=[
                {"label": "Gas 1", "value": 1},
                {"label": "Gas 2", "value": 2},
                {"label": "Gas 3", "value": 3}
            ],
            value=1,
        )
    ],
    className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

layout = html.Div([
    header
])
