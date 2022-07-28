from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv("../data/21_22_APPA.csv")

app.layout = html.Div([
    html.H1("Dati APPA"),
    html.Label("Seleziona la stazione"),
    dcc.Dropdown(df.Stazione.unique(), id="input-station"),
    dcc.Dropdown(df.Inquinante.unique(), id='pollutant'),
    dcc.Graph(id="pollutants-graph")
])


@app.callback(
    Output('pollutants-graph', 'figure'),
    Input('input-station', 'value'),
    Input('pollutant', 'value'))
def update_graph(input_station, pollutant):
    station_df = df[(df.Stazione == input_station)
                    & (df.Inquinante == pollutant)]

    fig = px.line(
        station_df,
        x='Data',
        y='Valore',
        color='Inquinante'
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
