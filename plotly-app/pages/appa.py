import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("APPA Data", className="header-title")

df = pd.read_csv("../data/merged_APPA_data.csv")
stations = df.Stazione.unique()

# dropdown1 = dbc.DropdownMenu(
#     # html.I(className="fa-solid fa-location-dot"),
#     label="Select location",
#     children=[
#         dbc.DropdownMenuItem(station) for station in stations
#         # dbc.DropdownMenuItem("Trento - S. Chiara"),
#         # dbc.DropdownMenuItem("Trento - Via Bolzano")
#     ],
#     color="secondary",)

dropdown = dcc.Dropdown(
    stations, placeholder="Select station", id='selected-station', className="dropdown"
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
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
                {}
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


@callback(Output("filtered-df", "df"), Input("selected-station", "value"))
def get_station_df(selected_station):
    filtered_df = df[df.Stazione == selected_station]
    return filtered_df


layout = html.Div(
    [header,
     html.P(id="response", children=[], style={"display": "none"})],
    className="section")
