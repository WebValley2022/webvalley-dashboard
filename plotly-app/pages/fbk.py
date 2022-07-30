import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

TITLE_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div("FBK Data", style=TITLE_STYLE)

layout = html.Div([
    content
])
