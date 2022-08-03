import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import date

dash.register_page(__name__, redirect_from=["/"])
global dfFBK1
dfFBK1 = pd.read_csv('../../FBK data/appa1_new.csv', encoding='windows-1252')

title = html.Div("FBK Raw Data", className="header-title")

periods = ["6 months", "by month", "by day", "by hour"]

dropdown_period = dcc.Dropdown(
    periods, id='selected_period', className="dropdown", value=periods[0]
)

resistance_plot = dcc.Graph(id="resistance_plot", className="side-plot")

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

header = html.Div(
    [title, resistance_plot, dropdown_period, download_btn],
    className="section-header"
)

layout = html.Div([
    header
])


@callback(Output("resistance_plot", "figure"),
          Input("selected_period", "value"))
def update_resistance_plot(selected_period):
    dfFBK1 = pd.read_csv('FBK data/appa1_new.csv', encoding='windows-1252')
    print(selected_period)
    dfFBK1 = dfFBK1.dropna()
    dfFBK1 = dfFBK1.drop(dfFBK1.columns[[8, 9, 10, 11, 12, 13]], axis=1)
    dfFBK1["signal_res"] = dfFBK1["signal_res"].astype(float)
    dfFBK1["heater_res"] = dfFBK1["heater_res"].astype(float)
    dfFBK1["heater_V"] = dfFBK1["heater_V"].astype(float)
    dfFBK1["T"] = dfFBK1["T"].astype(float)
    dfFBK1["RH"] = dfFBK1["RH"].astype(float)
    dfFBK1["P"] = dfFBK1["P"].astype(float)
    dfFBK1["T"] = dfFBK1["T"].astype(float)
    dfFBK1["ts"] = pd.to_datetime(dfFBK1["ts"])

    dfFBK1 = dfFBK1.drop_duplicates(['sensing_,material', 'ts'])
    dfFBK1['Data'] = pd.to_datetime(dfFBK1.ts.dt.date)
    dfFBK1['Ora'] = str(dfFBK1.ts.dt.time)

    global dfFBK1ResV
    # drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1.drop(dfFBK1.columns[[5, 6, 7]], axis=1)
    dfFBK1ResV = dfFBK1ResV.groupby(["Data", "sensing_,material"]).mean()
    dfFBK1ResV = dfFBK1ResV.reset_index()

    dfFBK1ResV["Data"] = pd.to_datetime(dfFBK1ResV["Data"])

    dfFBK1ResV = dfFBK1ResV.drop(dfFBK1.columns[[3, 4]], axis=1)

    dfFBK1ResV = verify_period(selected_period, dfFBK1ResV)
    print(dfFBK1ResV)
    fig = go.Figure()
    for SensingMaterial, group in dfFBK1ResV.groupby("sensing_,material"):
        fig.add_trace(go.Scatter(
            x=dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["Data"],
            y=dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["signal_res"],
            name=SensingMaterial)
        )

    fig.update_layout(legend_title_text="Sensing Material")
    fig.update_yaxes(title_text="Value")

    return fig


def verify_period(period, dfFBK1ResV):
    print(period)
    if period == "6 months":
        dfFBK1ResV = dfFBK1ResV.tail(720)
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by month":
        dfFBK1ResV = dfFBK1ResV.tail(120)
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by day":
        dfFBK1ResV = dfFBK1ResV.tail(120)
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by hour":
        dfFBK1ResV = dfFBK1ResV.tail(120)
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
