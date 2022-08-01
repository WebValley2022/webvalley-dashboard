import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("Settings", className="header-title")

header = html.Div(
    [title],
    className="section-header"
)

layout = html.Div(
    header,
    className="section")
