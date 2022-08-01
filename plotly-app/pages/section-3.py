import dash
from dash import Dash, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

dash.register_page(__name__)
df = pd.read_csv('./data/merged_APPA_data.csv', encoding='windows-1252')

layout = html.Div(
    [
    html.H1("APPA Data"),
    dcc.Dropdown(df.Stazione.unique(), id="input_station"),

    dbc.RadioItems(
        id="radios",
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn btn-outline-primary",
        labelCheckedClassName="active",
        options=[
        {"label": "CO", "value": "CO"},
        {"label": "NO2", "value": "NO2"},
        {"label": "SO2", "value": "SO2"},
        {"label": "O3", "value": "O3"},
        {"label": "PM10", "value": "PM10"},
        {"label": "PM2.5", "value": "PM2.5"},
        ],
    ),
    dcc.Graph(id="pollutants_graph"),
    ],
    className="radio-group"
)

@callback(
    Output('pollutants_graph', 'figure'),
    Input('radios', 'value'),
    Input('input_station', 'value')
    )
def return_button(radios):
    print("gases buttons" + str(radios))

