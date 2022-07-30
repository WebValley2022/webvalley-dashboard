from dash import Dash, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv("../data/merged_APPA_data.csv")
df.Data = pd.to_datetime(df.Data)


def filter_df(df, station, pollutant):
    mask = (df.Inquinante == pollutant) & (df.Stazione == station)
    filtered = df[mask]
    return filtered


def resample_df(df, resample_rule):
    df_mean = df.resample(resample_rule, on='Data').mean()
    df_mean = df_mean.reset_index()
    return df_mean


app.layout = html.Div([
    html.H1(str(df.dtypes)),
    html.Label("Seleziona la stazione"),
    dcc.Dropdown(df.Stazione.unique(), id="input-station"),
    dcc.Dropdown(df.Inquinante.unique(), id='pollutant'),
    dcc.Graph(id="pollutants-graph")
])


@callback(
    Output('pollutants-graph', 'figure'),
    Input('input-station', 'value'),
    Input('pollutant', 'value'))
def update_graph(input_station, pollutant):
    filtered_df = filter_df(df, input_station, pollutant)
    compressed_df = resample_df(filtered_df, 'W')

    if compressed_df.shape[0] > 0:
        fig = px.line(
            compressed_df,
            y='Valore',
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
