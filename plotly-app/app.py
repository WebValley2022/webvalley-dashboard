from dash import Dash, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv("../data/merged_APPA_data.csv")
df.Data = pd.to_datetime(df.Data)

app.layout = html.Div([
    html.H1('Dashboard'),
    html.Label("Seleziona la stazione"),
    dcc.Dropdown(df.Stazione.unique(), id="input-station"),
    dcc.Dropdown(df.Inquinante.unique(), id='pollutant'),
    dcc.Graph(id="pollutants-graph")
])


if __name__ == "__main__":
    app.run_server(debug=True)
