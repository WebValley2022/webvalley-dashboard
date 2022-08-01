import dash
from dash import dcc, html, Input, Output, Dash
import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

dash.register_page(__name__)

layout = html.Div([
    html.H1('Section 2'),
])
