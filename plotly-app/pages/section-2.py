import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1('Section 2'),
])
