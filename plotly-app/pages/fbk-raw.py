from dash import html, dcc, Input, Output, callback
from db_utils import load_data_from_psql
from datetime import datetime
from .utils import utils

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import logging
import dash
import os

##################
# SECTION 1 PAGE #
##################

dash.register_page(__name__, path="/")

if os.getenv("DEBUG"):
    fbk_data = utils.get_fbk_data()
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
    fbk_data = load_data_from_psql(query)
    logging.info("Query time", datetime.now() - start)
    fbk_data = utils.filter_fbk_data(fbk_data)

title = html.Div("Raw FBK Data", className="header-title")

periods = ["last 6 months", "last month", "last week", "last day", "last hour"]
stations = ["Trento - S. Chiara", "Trento - via Bolzano"]

dropdown_station = dcc.Dropdown(
    stations, id="selected-station", className="dropdown", value=stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    id="btn_fbk_raw",
    class_name="download-btn",
)
download_it = dcc.Download(id="download-fbk-raw")


@callback(
    Output("download-fbk-raw", "data"),
    Input("btn_fbk_raw", "n_clicks"),
    prevent_initial_call=True,
)
def create_download_file(n_clicks):
    global fbk_data
    return dcc.send_data_frame(fbk_data.to_csv, "fbk_raw_data.csv")


dropdown_period = dcc.Dropdown(
    periods, id="selected-period", className="dropdown", value=periods[4]
)

dropdown_wrapper = html.Div(
    [dropdown_station, dropdown_period], className="dropdownWrapper"
)

header = html.Div(
    [title, download_btn, download_it, dropdown_wrapper], className="section-header"
)


@callback(
    Output("resistance-plot", "figure"),
    Input("selected-period", "value"),
    Input("selected-station", "value"),
)
def update_resistance_plot(selected_period, selected_station):
    # filter only valid values
    fbk_data_ResV = fbk_data[
        (fbk_data["node_description"] == selected_station.split(" - ")[-1])
        & (fbk_data["signal_res"] != pd.NA)
    ]

    # convert date to datetime
    fbk_data_ResV["Data"] = pd.to_datetime(fbk_data_ResV.ts.dt.date)

    # keep signal_resistance drop Temperature, humidity, pressure, voltage and heater resistance
    fbk_data_ResV = fbk_data_ResV.drop(["p", "rh", "t", "volt", "heater_res"], axis=1)
    fbk_data_ResV = fbk_data_ResV.reset_index()

    # filter for desired time span
    fbk_data_ResV = verify_period(selected_period, fbk_data_ResV)

    fig = go.Figure()
    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["ts"],
                    y=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["signal_res"],
                    name=SensingMaterial,
                    visible="legendonly" if SensingMaterial == "SnO2" else True,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["Data"],
                    y=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["signal_res"],
                    name=SensingMaterial,
                    visible="legendonly" if SensingMaterial == "SnO2" else True,
                )
            )

    # fig.update_yaxes(type="log", range=[1, 3])
    fig.update_layout(
        legend_title_text="Sensing Material",
        margin=dict(l=0, r=5, t=20, b=0),
        plot_bgcolor="white",
        title=dict(
            x=0.5,
            text="Sensor Resistance (Ω)",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
    )
    fig.update_yaxes(title_text="", fixedrange=True)
    return fig


@callback(
    Output("middle-right-plot", "figure"),
    Input("selected-period", "value"),
    Input("selected-station", "value"),
)
def update_bottom_right_plot(selected_period: str, selected_station: str) -> go.Figure:
    """
    Updates the plot that represents the variation of pressure, temperature and humidity
    over time

    Args:
        selected_period (str): the selected period
        selected_station (str): the selected station

    Returns:
        go.Figure: the plot
    """
    plot_width = 800
    plot_height = 400

    dfFBK1 = fbk_data[
        fbk_data["node_description"] == selected_station.split(" - ")[-1]
    ].dropna(inplace=False)

    dfFBK1["Data"] = pd.to_datetime(dfFBK1.ts.dt.date)

    dfFBK1TPH = dfFBK1.drop(["heater_res", "signal_res", "volt"], axis=1)
    dfFBK1TPH = (
        dfFBK1TPH.groupby(["sensor_description", "node_description"])
        .resample("1T", on="ts")
        .mean()
    )
    dfFBK1TPH = dfFBK1TPH.reset_index()

    # filter for desired time span
    dfFBK1TPH = verify_period_TPH(selected_period, dfFBK1TPH)
    dfFBK1TPH.sort_values(by="ts", inplace=True)

    # Temperature graph
    trace1 = go.Scatter(
        x=dfFBK1TPH["ts"],
        y=dfFBK1TPH["t"],
        name="Temp",
        mode="lines",
        yaxis="y1",
        hovertemplate="Parameter = Temperature<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    # Humidity graph
    trace2 = go.Scatter(
        x=dfFBK1TPH["ts"],
        y=dfFBK1TPH["rh"],
        name="RH",
        mode="lines",
        yaxis="y1",
        hovertemplate="Parameter = Humidity<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    # Pressure graph
    trace3 = go.Scatter(
        x=dfFBK1TPH["ts"],
        y=dfFBK1TPH["p"],
        name="Press",
        yaxis="y2",
        mode="lines",
        hovertemplate="Parameter = Pressure<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    data = [trace1, trace2, trace3]

    fig = go.Figure(data=data)

    fig.update_layout(
        margin=dict(l=0, r=5, t=50, b=10),
        plot_bgcolor="white",
        font=dict(size=10),
        yaxis=dict(title="Temp (°C) & RH (%)"),
        yaxis2=dict(title="pressure (psi)", overlaying="y", side="right"),
        legend={
            "x": 0.1,
            "y": 1.4,
            "yanchor": "top",
            "xanchor": "left",
            "orientation": "h",
            "bgcolor": "rgba(0,0,0,0)",
        },
        title=dict(
            x=0.5,
            y=0.95,
            text="Bosch sensor",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
    )

    fig.update_yaxes(fixedrange=True)

    return fig


@callback(
    Output("bottom-right-plot", "figure"),
    Input("selected-period", "value"),
    Input("selected-station", "value"),
)
def update_middle_right_plot(selected_period: str, selected_station: str) -> go.Figure:
    """
    Updates the plot representing the cange of voltage in the heater over time

    Args:
        selected_period (str): the selected period
        selected_station (str): the selected station

    Returns:
        go.Figure: the plot
    """

    dfFBK1 = fbk_data[fbk_data["node_description"] == selected_station.split(" - ")[-1]]

    # select only valid values
    dfFBK1 = dfFBK1[dfFBK1["volt"] != pd.NA]

    dfFBK1["Data"] = pd.to_datetime(dfFBK1.ts.dt.date)

    # drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1.drop(["p", "rh", "t", "signal_res", "heater_res"], axis=1)
    dfFBK1ResV = dfFBK1ResV.reset_index()

    # filter for desired time span
    dfFBK1ResV = verify_period(selected_period, dfFBK1ResV)

    fig = go.Figure()
    # fig.update_yaxes(type="log")

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in dfFBK1ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "ts"
                    ],
                    y=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "volt"
                    ],
                    name=SensingMaterial,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in dfFBK1ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "Data"
                    ],
                    y=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "volt"
                    ],
                    name=SensingMaterial,
                ),
            )

    fig.update_layout(
        legend_title_text="Sensing Material",
        margin=dict(l=0, r=5, t=20, b=0),
        plot_bgcolor="white",
        font=dict(size=10),
        title=dict(
            x=0.5,
            text="Heater Voltage (V)",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
    )
    fig.update_yaxes(title_text="", fixedrange=True)

    return fig


@callback(
    Output("top-right-plot", "figure"),
    Input("selected-period", "value"),
    Input("selected-station", "value"),
)
def update_top_right_plot(selected_period: str, selected_station: str) -> go.Figure:
    """
    Updates the plot representing the change of the heater resistance over  time

    Args:
        selected_period (str): the selected period to show
        selected_station (str): the selected station to show

    Returns:
        go.Figure: the plot
    """
    dfFBK1 = fbk_data[fbk_data["node_description"] == selected_station.split(" - ")[-1]]

    # select only valid values
    dfFBK1 = dfFBK1[dfFBK1["heater_res"] != pd.NA]

    dfFBK1["Data"] = pd.to_datetime(dfFBK1.ts.dt.date)

    # drop Temperature, humidity, pressure
    dfFBK1ResV = dfFBK1.drop(["p", "rh", "t", "signal_res", "volt"], axis=1)
    dfFBK1ResV = dfFBK1ResV.reset_index()
    dfFBK1ResV = verify_period(selected_period, dfFBK1ResV)

    fig = go.Figure()

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in dfFBK1ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "ts"
                    ],
                    y=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "heater_res"
                    ],
                    name=SensingMaterial,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in dfFBK1ResV.groupby("sensor_description"):
            fig.add_trace(
                go.Scatter(
                    x=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "Data"
                    ],
                    y=dfFBK1ResV[dfFBK1ResV["sensor_description"] == SensingMaterial][
                        "heater_res"
                    ],
                    name=SensingMaterial,
                )
            )

    fig.update_layout(
        legend_title_text="Sensing Material",
        margin=dict(l=0, r=5, t=20, b=0),
        plot_bgcolor="white",
        font=dict(size=10),
        title=dict(
            x=0.5,
            text="Heater Resistance (Ω)",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
    )
    fig.update_yaxes(title_text="", fixedrange=True)

    return fig


def verify_period(period, df):
    if period == "last 6 months":
        df = df.groupby(["Data", "sensor_description"]).mean()
        df = df.reset_index()
        df = df.set_index("Data")
        df = df.last("180D")
        df = df.reset_index()
        return df
    elif period == "last month":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean()
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("30D")
        df = df.reset_index()
        return df
    elif period == "last week":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean()
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("7D")
        df = df.reset_index()
        return df
    elif period == "last day":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1D")
        df = df.reset_index()
        return df
    elif period == "last hour":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1h")
        df = df.reset_index()

    return df


def verify_period_TPH(period, df):
    if period == "last 6 months":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("180D")
        df = df.reset_index()
        return df
    elif period == "last month":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("30D")
        df = df.reset_index()
        return df
    elif period == "last week":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("7D")
        df = df.reset_index()
        return df
    elif period == "last day":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1D")
        df = df.reset_index()
        return df
    elif period == "last hour":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1h")
        df = df.reset_index()

    return df


layout = html.Div(
    [
        header,
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="resistance-plot",
                        config={
                            "displayModeBar": False,
                            "displaylogo": False,
                        },
                        style=dict(height="77vh"),
                    ),
                    lg=7,
                    xl=8,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="top-right-plot",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        dcc.Graph(
                            id="bottom-right-plot",
                            className="side-plot",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        dcc.Graph(
                            id="middle-right-plot",
                            className="side-plot",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),
                    ],
                    md=5,
                    lg=5,
                    xl=4,
                ),
            ],
        ),
    ],
    className="section fullHeight",
)
