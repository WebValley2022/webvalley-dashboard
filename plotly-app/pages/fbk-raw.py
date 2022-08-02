import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, redirect_from=["/"])

title = html.Div("FBK Raw Data", className="header-title")

df = pd.read_csv("../data/merged_APPA_data.csv")
df = df[df.Valore != 'n.d.']
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()

dropdown = dcc.Dropdown(
    stations, id='selected-fbk-station', className="dropdown", value=stations[0]
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


layout = html.Div([
    header
])
