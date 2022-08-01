from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv("../data/merged_APPA_data.csv")
df.Data = pd.to_datetime(df.Data)


# def filter_df(df, station, pollutant):
#     mask = (df.Inquinante == pollutant) & (df.Stazione == station)
#     filtered = df[mask]
#     return filtered


# def resample_df(df, resample_rule):
#     df_mean = df.resample(resample_rule, on='Data').mean()
#     df_mean = df_mean.reset_index()
#     return df_mean


# app=Dash(__name__)
# app.layout= html.Div([
#     html.H4 ("montly variations in pollutants"),
#     dcc.Dropdown(
#         id="dropdown",
#         multi=True),
#         dcc.Graph(id="graph"),
# ])

# def update_plot2(input= "dropdown"):
#     gas= "PM10"
#     return

# @app.callback(
#     Output("graph","figure"),
#     Input("dropdown","value")
# )
# def update_Graph():
#     return

app.run_server(debug=True,port=8052)
