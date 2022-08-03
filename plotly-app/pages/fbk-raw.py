from dash import html, dcc, Input, Output, callback
from db_utils import load_data_from_psql
from datetime import datetime

import plotly.graph_objects as go
import pandas as pd
import logging
import dash
import os

dash.register_page(__name__, redirect_from=["/"])
global dfFBK1

if os.getenv("DEBUG"):
    dfFBK1 = pd.read_csv('../FBK data/data_fbk_from_db.csv',
                         encoding='windows-1252')
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
    logging.info("Query time", datetime.now() - start)
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

#resistance_plot = dcc.Graph(id="resistance_plot", className="side-plot")

#right_top_plot = dcc.Graph(id="right_top_plot", className="side-plot")

middle_right_plot = dcc.Graph(id="middle_right_plot", className="side-plot")

bottom_right_plot = dcc.Graph(id="bottom_right_plot", className="side-plot")

header = html.Div(
    [title, dropdown_period, dropdown_station, middle_right_plot, bottom_right_plot],
    className="section-header"
)

layout = html.Div([
    header
])

def update_middle_right_plot(selected_period, selected_station):
    plot_width = 800
    plot_height = 400

    dfFBK1 = pd.read_csv('FBK data/data_fbk_from_db.csv', encoding='windows-1252')

    dfFBK1 = dfFBK1.dropna()
    dfFBK1=dfFBK1.drop(["Unnamed: 0", "node_name", "g", "h", "th", "cfg", "iaq", "co2", "voc", "iac_comp"], axis=1)
    dfFBK1["signal_res"] = dfFBK1["signal_res"].astype(float)
    dfFBK1["heater_res"] = dfFBK1["heater_res"].astype(float)
    dfFBK1["volt"] = dfFBK1["volt"].astype(float)
    dfFBK1["t"] = dfFBK1["t"].astype(float)
    dfFBK1["rh"] = dfFBK1["rh"].astype(float)
    dfFBK1["p"] = dfFBK1["p"].astype(float)

    dfFBK1 = dfFBK1.drop_duplicates(['sensor_description','ts'])
    dfFBK1['ts'] = pd.to_datetime(dfFBK1.ts)
    dfFBK1['Data'] = pd.to_datetime(dfFBK1.ts.dt.date)
    dfFBK1['Hour'] = dfFBK1.ts.dt.hour
    dfFBK1['Minute'] = dfFBK1.ts.dt.minute
    dfFBK1['Ora'] = str(dfFBK1.ts.dt.time)

    dfFBK1TPH = dfFBK1.drop(["heater_res", "signal_res", "volt"], axis=1) #drop Temperature, humidity, pressure

    dfFBK1TPH = dfFBK1TPH.groupby(["sensor_description", "node_description"]).resample("1T", on="ts").mean()
    dfFBK1TPH = dfFBK1TPH.reset_index()
    
    #print("AA")
    #print(dfFBK1TPH)

    # dfFBK1TPH["Data"] = pd.to_datetime(dfFBK1TPH["Data"])
    # dfFBK1TPH = dfFBK1TPH.reset_index()
    #dfFBK1TPH = verify_period(selected_period, dfFBK1TPH)

    trace1 = go.Scatter(x=dfFBK1TPH['ts'],
                            y=dfFBK1TPH['t'],
                            name='Temperature',
                            mode='lines',
                            yaxis='y1',
                            hovertemplate="Parameter = Temperature<br>Value = %{y}<br>Date = %{x}<extra></extra>")

    trace2 = go.Scatter(x=dfFBK1TPH['ts'],
                            y=dfFBK1TPH['rh'],
                            name='Humidity',
                            mode='lines',
                            yaxis='y1',
                            hovertemplate="Parameter = Humidity<br>Value = %{y}<br>Date = %{x}<extra></extra>")

    trace3 = go.Scatter(x=dfFBK1TPH['ts'],
                        y=dfFBK1TPH['p'],
                        name='Pressure',
                        yaxis='y2',
                        mode = 'lines',
                        hovertemplate="Parameter = Pressure<br>Value = %{y}<br>Date = %{x}<extra></extra>"
                        )

    data = [trace1, trace2, trace3]
    layout = go.Layout(title='Temperature - Pressure - Humidity',
                        yaxis=dict(title='Humidity - Temperature'),
                        yaxis2=dict(title='Pressure',
                                    overlaying='y',
                                    side='right'
                                    ),
                            width= plot_width,
                            height= plot_height,
                            legend = dict(orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1)
                        )

    return go.Figure(data=data, layout=layout)

@callback(Output("bottom_right_plot", "figure"),
        Output("middle_right_plot", "figure"),
        Input("selected_period", "value"),
        Input("selected_station", "value"),
        )

def update_bottom_right_plot(selected_period, selected_station):
    dfFBK1 = pd.read_csv('FBK data/data_fbk_from_db.csv', encoding='windows-1252')
    #dfFBK1 = dfFBK1.dropna()
    dfFBK1 = dfFBK1[
        dfFBK1["volt"] != pd.NA
    ]
    dfFBK1=dfFBK1.drop(["Unnamed: 0", "node_name", "g", "h", "th", "cfg", "iaq", "co2", "voc", "iac_comp"], axis=1)

    dfFBK1["signal_res"] = dfFBK1["signal_res"].astype(float)
    dfFBK1["heater_res"] = dfFBK1["heater_res"].astype(float)
    dfFBK1["volt"] = dfFBK1["volt"].astype(float)
    dfFBK1["t"] = dfFBK1["t"].astype(float)
    dfFBK1["rh"] = dfFBK1["rh"].astype(float)
    dfFBK1["p"] = dfFBK1["p"].astype(float)

    dfFBK1 = dfFBK1.drop_duplicates(['sensor_description','ts'])
    
    dfFBK1['ts'] = pd.to_datetime(dfFBK1.ts)
    dfFBK1['Data'] = pd.to_datetime(dfFBK1.ts.dt.date)
    dfFBK1['Minute'] = dfFBK1.ts.dt.minute
    dfFBK1['Ora'] = str(dfFBK1.ts.dt.time)

    dfFBK1ResV = dfFBK1.drop(["p", "rh", "t"], axis=1) #drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1ResV.groupby(["Data", "sensor_description"]).mean()
    dfFBK1ResV = dfFBK1ResV.reset_index()

    dfFBK1ResV["Data"] = pd.to_datetime(dfFBK1ResV["Data"])
    dfFBK1ResV = dfFBK1ResV.drop(["signal_res", "heater_res"], axis=1)

    #dfFBK1ResV = verify_period(selected_period, dfFBK1ResV)
    fig = go.Figure()
    for SensingMaterial, group in dfFBK1ResV.groupby("sensor_description"):
        fig.add_trace(go.Scatter(
            x = dfFBK1ResV[
                dfFBK1ResV["sensor_description"] == SensingMaterial
            ]["Data"],
            y = dfFBK1ResV[
                dfFBK1ResV["sensor_description"] == SensingMaterial
            ]["volt"],
            name=SensingMaterial)
        )

    fig.update_layout(legend_title_text="Sensing Material")
    fig.update_yaxes(title_text="Value")

    return (
        fig,
        update_middle_right_plot(
            selected_period,
            selected_station
        )
    )

def verify_period(period, dfFBK1ResV):
    #print(period)

    if period == "6 months":
        dfFBK1ResV = dfFBK1ResV
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by month":
        dfFBK1ResV = dfFBK1ResV
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by day":
        dfFBK1ResV = dfFBK1ResV
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
    if period == "by hour":
        dfFBK1ResV = dfFBK1ResV
        dfFBK1ResV = dfFBK1ResV.reset_index()
        return dfFBK1ResV
