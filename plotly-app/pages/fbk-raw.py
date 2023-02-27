from dash import html, dcc, Input, Output, callback, State, callback_context
from db_utils import load_data_from_psql
from datetime import datetime
from .utils import utils, querys

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import logging
import dash
import os

from flask_caching import Cache

##################
# SECTION 1 PAGE #
##################


cache = Cache(dash.get_app().server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})


"""cache = Cache(dash.get_app().server, config={
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
})"""


dash.register_page(__name__, path="/")

@cache.memoize(timeout=360) #cached 5 min
def get_data_hours() -> pd.DataFrame:
    print("NOT CACHED HOURS")
    fbk_data = load_data_from_psql(querys.query_hour)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=1800) #cached 30 min
def get_data_day() -> pd.DataFrame:
    print("NOT CACHED DAY")
    fbk_data=  load_data_from_psql(querys.query_day)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=3600) #cached 1 hour
def get_data_week() -> pd.DataFrame:
    print("NOT CACHED WEEK")
    fbk_data=  load_data_from_psql(querys.query_week_test)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=864000)#cached 1 day
def get_data_month() -> pd.DataFrame:
    print("NOT CACHED MONTH")
    fbk_data = load_data_from_psql(querys.query_month_test)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=604800) #cached 7 day  
def get_data_6months() -> pd.DataFrame:
    print("NOT CACHED 6_MONTHS")
    fbk_data = load_data_from_psql(querys.query_6moths_test2)
    return utils.filter_fbk_data(fbk_data)


def cache_fbk_data(selected_period: str)  -> pd.DataFrame:
    if os.getenv("DEBUG"):
        fbk_data = utils.get_fbk_data()
    else:
        start = datetime.now()
        if selected_period  in "last hour":
            fbk_data = get_data_hours()
        elif selected_period  in "last day":
            fbk_data = get_data_day()
        elif selected_period  in "last week":
            fbk_data = get_data_week()
        elif selected_period  in "last month":
            fbk_data = get_data_month()
        elif selected_period  in "last 6 months":
            fbk_data = get_data_6months()    
        logging.info("Query time", datetime.now() - start)
        print("QUERY TIME: ", datetime.now() - start)
        return fbk_data

title = html.Div("Raw FBK Data", className="header-title")

periods = ["last 6 months", "last month", "last week", "last day", "last hour"]
stations = ["Trento - S. Chiara", "Trento - via Bolzano"]

dropdown_station = dcc.Dropdown(
    stations, id="selected-station", className="dropdown", value=stations[0]
)

yaxis_type  = dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='yaxis-type',
                #inline=False,
                className="radioitems",
                labelStyle={'display': 'block'}
            )
date_range = dcc.DatePickerRange(
    id='my-date-picker-range',
    month_format='MMMM Y',
    start_date_placeholder_text="Start Period",
    end_date_placeholder_text="End Period",
    clearable=True,
)

search = dbc.Button(
    children= html.I(
        className= "fas fa-search"
    ),
    id="btn_search_date",
    class_name="btn btn-primary",
    style={"width":"50px"}
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
    
    """global fbk_data
    return dcc.send_data_frame(get_fbk_data().to_csv, "fbk_raw_data.csv")"""
    cache.clear()


dropdown_period = dcc.Dropdown(
    periods, id="selected-period", className="dropdown", value=periods[4]
)

dropdown_wrapper = html.Div(
    [dropdown_station, dropdown_period], className="dropdownWrapper"
)

date_wrapper = html.Div(
    [date_range, search], className="right"
)

option_wrapper = html.Div(
    [yaxis_type, date_wrapper], className="dropdownWrapper"
)
header = html.Div(
    [title, download_btn, download_it, dropdown_wrapper, option_wrapper], className="section-header"
)
    

@callback(
    [
    Output("resistance-plot", "figure"),
    Output("top-right-plot", "figure"),
    Output("middle-right-plot", "figure"),
    Output("bottom-right-plot", "figure")],
    
    Input("selected-period", "value"),
    Input("selected-station", "value"),
    Input("yaxis-type", "value"),
    Input("btn_search_date", "n_clicks"),
    
    [State("resistance-plot","figure"),
    State("top-right-plot", "figure"),
    State("middle-right-plot", "figure"),
    State("bottom-right-plot", "figure"),
    State("my-date-picker-range","start_date"),
    State("my-date-picker-range","end_date"),]

)
def update_plots(selected_period, selected_station, yaxis_type, n_clicks, res_state, het_state, volt_state, bosch_state, start_date, end_date):
    
    if "yaxis-type" == callback_context.triggered_id:
        res_state["layout"]["yaxis"]["type"] = ('linear' if yaxis_type == 'Linear' else 'log')
        return res_state, het_state, volt_state, bosch_state
    
    if "btn_search_date" == callback_context.triggered_id:
        fbk_data = utils.query_custom(start_date, end_date)
    else:
        fbk_data = cache_fbk_data(selected_period)
        
    
    #print("madonna troia ",fbk_data)
    
    dfFBK1 = fbk_data[
        fbk_data["node_description"] == selected_station.split(" - ")[-1]
    ].dropna(inplace=False)

    dfFBK1["Data"] = pd.to_datetime(dfFBK1.ts.dt.date)
    
    if "btn_search_date" != callback_context.triggered_id:
        fbk_data_ResV = verify_period(selected_period, dfFBK1)
    else:
        fbk_data_ResV = dfFBK1
        
    #----------------------HEATER PLOT-----------------------------
    
    resistance_plot = go.Figure()
    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            resistance_plot.add_trace(
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
            resistance_plot.add_trace(
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

    # resistance_plot.update_yaxes(type="log", range=[1, 3])
    resistance_plot.update_layout(
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
    resistance_plot.update_yaxes(title_text="", fixedrange=True)
    
    #---------------------------RESISTANCE PLOT---------------------------
    
    heater_plot = go.Figure()

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            heater_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "ts"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "heater_res"
                    ],
                    name=SensingMaterial,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            heater_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "Data"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "heater_res"
                    ],
                    name=SensingMaterial,
                )
            )

    heater_plot.update_layout(
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
    heater_plot.update_yaxes(title_text="", fixedrange=True, type='linear' if yaxis_type == 'Linear' else 'log')

    #---------------------------VOLTAGE PLOT---------------------------
    
    volt_plot = go.Figure()
    # fig.update_yaxes(type="log")

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            volt_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "ts"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "volt"
                    ],
                    name=SensingMaterial,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            volt_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "Data"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "volt"
                    ],
                    name=SensingMaterial,
                ),
            )

    volt_plot.update_layout(
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
    volt_plot.update_yaxes(title_text="", fixedrange=True)
    
    #---------------------------BOSCH PLOT---------------------------
    if "btn_search_date" != callback_context.triggered_id:
        fbk_data_bosch = verify_period_TPH(selected_period, dfFBK1)
    else:
        fbk_data_bosch = dfFBK1
        
    fbk_data_bosch.sort_values(by="ts", inplace=True)
    
    # Temperature graph
    trace1 = go.Scatter(
        x=fbk_data_bosch["ts"],
        y=fbk_data_bosch["t"],
        name="Temp",
        mode="lines",
        yaxis="y1",
        hovertemplate="Parameter = Temperature<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    # Humidity graph
    trace2 = go.Scatter(
        x=fbk_data_bosch["ts"],
        y=fbk_data_bosch["rh"],
        name="RH",
        mode="lines",
        yaxis="y1",
        hovertemplate="Parameter = Humidity<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    # Pressure graph
    trace3 = go.Scatter(
        x=fbk_data_bosch["ts"],
        y=fbk_data_bosch["p"],
        name="Press",
        yaxis="y2",
        mode="lines",
        hovertemplate="Parameter = Pressure<br>Value = %{y}<br>Date = %{x}<extra></extra>",
    )

    data = [trace1, trace2, trace3]

    bosch_plot = go.Figure(data=data)

    bosch_plot.update_layout(
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

    bosch_plot.update_yaxes(fixedrange=True)
    
    return [heater_plot, resistance_plot, volt_plot, bosch_plot]
    
    
     
     


def verify_period(period, df):
    if period == "last 6 months":
        df = df.groupby(["Data", "sensor_description"]).mean(numeric_only= True)
        df = df.reset_index()
        df = df.set_index("Data")
        df = df.last("180D")
        df = df.reset_index()
        return df
    elif period == "last month":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean(numeric_only=True)
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("30D")
        df = df.reset_index()
        return df
    elif period == "last week":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean(numeric_only=True)
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
                            id="middle-right-plot",
                            className="side-plot",
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
