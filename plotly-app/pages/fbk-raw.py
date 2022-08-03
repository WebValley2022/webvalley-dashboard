import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import os
from db_utils import load_data_from_psql
from datetime import datetime
import logging

dash.register_page(__name__, redirect_from=["/"])
global dfFBK1

if os.getenv("DEBUG"):
    dfFBK1 = pd.read_csv('FBK data/appa1_new.csv', encoding='windows-1252')
else:
    query = """
    select
        n.node_name as node_name,
        n.description as node_description,
        s.description as sensor_description,
        p.sensor_ts as ts,
        pd.r1 as signal_res,
        pd.r2 as heater_res,
        pd.volt as volt,
        p.attrs::json->'G' as g,
        p.attrs::json->'H' as h,
        p.attrs::json->'P' as p,
        p.attrs::json->'T' as t,
        p.attrs::json->'RH' as rh,
        p.attrs::json->'TH' as th,
        p.attrs::json->'CFG' as cfg,
        p.attrs::json->'CO2' as co2,
        p.attrs::json->'IAQ' as iaq,
        p.attrs::json->'VOC' as voc,
        p.attrs::json->'IAC_comp' as iac_comp
    from packet_data pd
        left join packet p on p.id = pd.packet_id
        left join sensor s on s.id = pd.sensor_id
        left join node n on n.id = p.node_id
    order by p.sensor_ts;
    """
    start = datetime.now()
    df = load_data_from_psql(query)
    logging.debug("Query time", datetime.now() - start)
    df.to_csv("data_fbk_from_db.csv")

title = html.Div("FBK Raw Data", className="header-title")

periods = ["6 months", "by month", "by day", "by hour"]
stations = ["Trento - S. Chiara", "Trento - Via Bolzano"]

dropdown_station = dcc.Dropdown(
    stations, id='selected_station', className="dropdown", value=stations[0]
)

dropdown_period = dcc.Dropdown(
    periods, id='selected_period', className="dropdown", value=periods[0]
)

resistance_plot = dcc.Graph(id="resistance_plot", className="side-plot")

right_top_plot = dcc.Graph(id="right_top_plot", className="side-plot")

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    value=stations[0],
    color="primary",
    class_name="download-btn"
)

header = html.Div(
    [title, dropdown_station, resistance_plot,
        right_top_plot, dropdown_period, download_btn],
    className="section-header"
)

layout = html.Div([
    header
])


def update_right_top_plot(selected_period, selected_station):
    print(stations[0])
    print(selected_station)

    if selected_station == stations[0]:
        dfFBK1 = pd.read_csv('FBK data/appa1_new.csv', encoding='windows-1252')
    elif selected_station == stations[1]:
        dfFBK1 = pd.read_csv('FBK data/appa2_new.csv', encoding='windows-1252')

    dfFBK1 = dfFBK1.dropna()
    dfFBK1 = dfFBK1.drop(dfFBK1.columns[[8, 9, 10, 11, 12, 13]], axis=1)
    dfFBK1["signal_res"] = dfFBK1["signal_res"].astype(float)
    dfFBK1["heater_res"] = dfFBK1["heater_res"].astype(float)
    dfFBK1["heater_V"] = dfFBK1["heater_V"].astype(float)
    dfFBK1["T"] = dfFBK1["T"].astype(float)
    dfFBK1["RH"] = dfFBK1["RH"].astype(float)
    dfFBK1["P"] = dfFBK1["P"].astype(float)
    dfFBK1["T"] = dfFBK1["T"].astype(float)

    print(dfFBK1)
    dfFBK1 = dfFBK1.drop_duplicates(['sensing_,material', 'ts'])
    dfFBK1['ts'] = pd.to_datetime(dfFBK1['ts'])
    dfFBK1['Data'] = pd.to_datetime(dfFBK1.ts.dt.date)
    dfFBK1['Ora'] = str(dfFBK1.ts.dt.time)

    global dfFBK1ResV
    # drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1.drop(dfFBK1.columns[[5, 6, 7]], axis=1)
    dfFBK1ResV = dfFBK1ResV.groupby(["Data", "sensing_,material"]).mean()
    dfFBK1ResV = dfFBK1ResV.reset_index()

    dfFBK1ResV["Data"] = pd.to_datetime(dfFBK1ResV["Data"])
    dfFBK1ResV = dfFBK1ResV.drop(dfFBK1.columns[[2, 4]], axis=1)

    dfFBK1ResV = verify_period(selected_period, dfFBK1ResV)

    fig = go.Figure()
    for SensingMaterial, group in dfFBK1ResV.groupby("sensing_,material"):
        fig.add_trace(go.Scatter(
            x=dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["Data"],
            y=dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["heater_res"],
            name=SensingMaterial)
        )

    fig.update_layout(legend_title_text="Sensing Material")
    fig.update_yaxes(title_text="Value")

    return fig

<<<<<<< HEAD
def update_right_top_plot(selected_period, selected_station):
    print(stations[0])
    print(selected_station)

    if selected_station == stations[0]:
        dfFBK1 = pd.read_csv('FBK data/appa1_new.csv', encoding='windows-1252')
    elif selected_station == stations[1]:
        dfFBK1 = pd.read_csv('FBK data/appa2_new.csv', encoding='windows-1252')

    dfFBK1 = dfFBK1.dropna()
    dfFBK1=dfFBK1.drop(dfFBK1.columns[["Unamed: 0", "node_name", "g", "h", "th", "cfg", "iaq", "co2", "voc", "iac_comp"]], axis=1)
    dfFBK1["signal_res"] = dfFBK1["signal_res"].astype(float)
    dfFBK1["heater_res"] = dfFBK1["heater_res"].astype(float)
    dfFBK1["volt"] = dfFBK1["volt"].astype(float)
    dfFBK1["t"] = dfFBK1["t"].astype(float)
    dfFBK1["rh"] = dfFBK1["th"].astype(float)
    dfFBK1["p"] = dfFBK1["p"].astype(float)
    dfFBK1["t"] = dfFBK1["t"].astype(float)

    dfFBK1 = dfFBK1.drop_duplicates(['sensor_description','ts'])
    dfFBK1['Data'] = pd.to_datetime(dfFBK1.ts.dt.date)
    dfFBK1['Ora'] = str(dfFBK1.ts.dt.time)

    print(dfFBK1)
    
    global dfFBK1ResV
    dfFBK1ResV = dfFBK1.drop(dfFBK1.columns[[5,6,7]], axis=1) #drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1ResV.groupby(["Data", "sensing_,material"]).mean()
    dfFBK1ResV = dfFBK1ResV.reset_index()

    dfFBK1ResV["Data"] = pd.to_datetime(dfFBK1ResV["Data"])
    dfFBK1ResV = dfFBK1ResV.drop(dfFBK1.columns[[2,3]], axis=1)

    fig = go.Figure()
    for SensingMaterial, group in dfFBK1ResV.groupby("sensing_,material"):
        fig.add_trace(go.Scatter(
            x = dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["Data"],
            y = dfFBK1ResV[
                dfFBK1ResV["sensing_,material"] == SensingMaterial
            ]["heater_V"],
            name=SensingMaterial)
        )

    fig.update_layout(legend_title_text = "Sensing Material")
    fig.update_yaxes(title_text="Value")

    return fig
    
=======

>>>>>>> 3c37cc42a694c4b1ff6d2853c631bb38d4265f20
@callback(Output("resistance_plot", "figure"),
          Output("right_top_plot", "figure"),
          Input("selected_period", "value"),
          Input("selected_station", "value"))
def update_resistance_plot(selected_period, selected_station):
    #print("station 0" +stations[0])
    #print("station selec" + selected_station)

    if selected_station == stations[0]:
        dfFBK1 = pd.read_csv('FBK data/appa1_new.csv', encoding='windows-1252')
    elif selected_station == stations[1]:
        dfFBK1 = pd.read_csv('FBK data/appa2_new.csv', encoding='windows-1252')

    # print(dfFBK1)
    dfFBK1 = dfFBK1.dropna()
    #dfFBK1 = dfFBK1.drop(dfFBK1.columns[[8,9,10,11,12,13]], axis=1)
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
        fig.add_trace(
            go.Scatter(
                x=dfFBK1ResV[
                    dfFBK1ResV["sensing_,material"] == SensingMaterial
                ]["Data"],
                y=dfFBK1ResV[
                    dfFBK1ResV["sensing_,material"] == SensingMaterial
                ]["signal_res"],
                name=SensingMaterial
            )
        )

    fig.update_layout(legend_title_text="Sensing Material")
    fig.update_yaxes(title_text="Value")

    return (
        fig,
        update_right_top_plot(
            selected_period,
            selected_station
        )
    )


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
