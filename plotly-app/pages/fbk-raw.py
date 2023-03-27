from dash import html, dcc, Input, Output, callback, State, callback_context
from db_utils import load_data_from_psql
from datetime import datetime
from .utils import utils, querys
import json

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import logging
import dash
import os
import dash_daq as daq

from flask_caching import Cache

##################
# SECTION 1 PAGE #
##################


cache = Cache(dash.get_app().server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

"""
cache = Cache(dash.get_app().server, config={
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
    fbk_data=  load_data_from_psql(querys.query_week_avg)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=864000)#cached 1 day
def get_data_month() -> pd.DataFrame:
    print("NOT CACHED MONTH")
    fbk_data = load_data_from_psql(querys.query_month_avg)
    return utils.filter_fbk_data(fbk_data)

@cache.memoize(timeout=604800) #cached 7 day  
def get_data_6months() -> pd.DataFrame:
    print("NOT CACHED 6_MONTHS")
    fbk_data = load_data_from_psql(querys.query_6moths_avg)
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


def make_card_sensor(sensor : str):
    return dbc.Card(
        dbc.CardBody(
                html.H5(sensor, className="", style={"text-align":"center", "padding-top":"0.9rem"})
        ),
        className="card-sensors",
        id = f"card-{sensor}"
    )

def make_tooltip_sensor(sensor : str):
    return dbc.Popover(
            [],
            target=f"card-{sensor}",
            trigger="hover",
            placement="bottom",
            id=f"toltip-{sensor}"
        )
    
def saturated(station):
    df = get_data_hours()
    d= {
        "S1_ID":None, "S2_ID":None,
        "S3_ID":None, "S4_ID":None,
        "S5_ID":None, "S6_ID":None,
        "S7_ID":None, "S8_ID":None,
    }
    for s in d.keys():
        tmp = df.loc[(df["sensor_description"]==s) & (df["node_description"] == station.split(" - ")[-1])].reset_index()
        if (tmp['signal_res'] == tmp['signal_res'][0]).all():
            d[s]= True
        else:
            d[s]= False
    return d
    

LAST_CLICKED = None

title = html.Div("Raw FBK Data", className="header-title",style={"text-align":"center","margin-bottom": "0.25rem"})

periods = ["last 6 months", "last month", "last week", "last day", "last hour"]
stations = ["Trento - S. Chiara", "Trento - via Bolzano"]

dropdown_station = dcc.Dropdown(
    stations, id="selected-station", className="dropdown", value=stations[0]
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
    color="secondary",
    outline=True,
    className="me-1",
    size="sm",
    style={"width":'100%',"border":'1px solid #ccc'}
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    id="btn_fbk_raw",
    class_name="download-btn",
)
download_it = dcc.Download(id="download-fbk-raw")


dropdown_period = dcc.Dropdown(
    periods, id="selected-period", className="dropdown", value=periods[4]
)

dropdown_wrapper = html.Div(
    [dropdown_station, ], className="dropdownWrapper"
)

sensors_wrapper = html.Div(
    [make_card_sensor("S"+str(s)) for s in range(1,9)] , className="wrapper-sersors" 
)

popovers_wrapper = html.Div(
    [make_tooltip_sensor("S"+str(s)) for s in range(1,9)]
)



toast = dbc.Toast(
                    [
                        html.H4("Filter by:",style={"font-weight":"bold"}),
                        dropdown_period,
                        date_range,
                        search,
                        #html.Br(),
                        daq.ToggleSwitch(
                            id="yaxis-type",
                            label=["Linear","Log"],
                            color="#9B51E0",
                            size=40,
                            value=False
                        ),
                        dcc.Checklist(options=[' Show history changes'], id="check_history", style={"font-size": "14px"}),
                
                    ],
                    id="toast",
                    header=html.P([html.I(className="fa-solid fa-gear"), " Settings"]),
                    #body_style={"margin-bottom":"2rem"},
                    style={"height":"100%"}
                )

header = html.Div(
    [title, download_btn, download_it, sensors_wrapper, dropdown_wrapper,  popovers_wrapper], className="section-header"
)


@callback(
    Output("download-fbk-raw", "data"),
    Input("btn_fbk_raw", "n_clicks"),
    prevent_initial_call=True,
)
def create_download_file(n_clicks):
    
    """global fbk_data
    return dcc.send_data_frame(get_fbk_data().to_csv, "fbk_raw_data.csv")"""
    cache.clear()


@callback(
    [
        Output("card-S1","className"),Output("card-S2","className"),
        Output("card-S3","className"),Output("card-S4","className"),
        Output("card-S5","className"),Output("card-S6","className"),
        Output("card-S7","className"),Output("card-S8","className"),
        
     ],
    Input("selected-station", "value"),
)
def update_color(station):
    ll = []
    d_saturation = saturated(station)
    for s in range(1,9):
        ll.append("card-sensors card-sensors-red" if d_saturation["S"+str(s)+"_ID"] else "card-sensors card-sensors-green")
        
    return ll
        
 
@callback(
    [
        Output("toltip-S1","children"),Output("toltip-S2","children"),
        Output("toltip-S3","children"),Output("toltip-S4","children"),
        Output("toltip-S5","children"),Output("toltip-S6","children"),
        Output("toltip-S7","children"),Output("toltip-S8","children"),
        
     ],
    Input("selected-station", "value"),
)
def update_desc(station):
    appa1 = 1
    appa2 = 6
    sensors = load_data_from_psql(querys.query_history_sensor)
    d= {
        "S1_ID":None, "S2_ID":None,
        "S3_ID":None, "S4_ID":None,
        "S5_ID":None, "S6_ID":None,
        "S7_ID":None, "S8_ID":None,
    }
    
    d_saturation = saturated(station)
    station = appa1 if (station.split(" - ")[-1] == "S. Chiara") else appa2
    params = load_data_from_psql(querys.query_params(station))
    sensors = sensors.loc[(sensors["node_id"] == station) & (sensors["active"] == True)]
    for _ , row in sensors.iterrows():
        s_id = row["name"]
        try:
            date = row["attrs"]["active since"]
        except:
            date = ""
    
        d[row["name"]] = dict(
                                description = row["description"], 
                                active_since = date,
                                res = params.loc[params["sensor_description"] == s_id]["heater_res"].values[0],
                                volt= params.loc[params["sensor_description"] == s_id]["volt"].values[0],
                            )    
    #print(d)
    list_tooltips = []
    for s in range(1,9):
        s=str(s)
        id= "S"+s+"_ID"
        body = dbc.PopoverBody([
                            html.Div([
                                html.P(f"{d[id]['description']}", id="desc-S"+s),
                                html.P(f"Resistance: {d[id]['res']}", id="res-S"+s),
                                html.P(f"Voltage: {d[id]['volt']}", id="volt-S"+s),
                                html.P(f"Installed on: {d[id]['active_since']}", id="inst-S"+s),
                                html.P("Saturated" if d_saturation[id] else "Good", id="status-S"+s, style={"color": "red" if d_saturation[id] else "green"}),
                            ],
                                className="text-muted px-4 mt-4",
                                id=f"body-pop-S{s}",
                                
                            )
                            ,
                    ] ,style={"font-size":"14px"})
        list_tooltips.append(body)
    return list_tooltips
        
        
    
    

@callback(
    [
    Output("resistance-plot", "figure"),
    Output("heater-plot", "figure"),
    Output("voltage-plot", "figure"),
    Output("bosch-plot", "figure")],
    
    Input("selected-period", "value"),
    Input("selected-station", "value"),
    Input("yaxis-type", "value"),
    Input("btn_search_date", "n_clicks"),
    Input("check_history", "value"),
    
    [State("resistance-plot","figure"),
    State("heater-plot", "figure"),
    State("voltage-plot", "figure"),
    State("bosch-plot", "figure"),
    State("my-date-picker-range","start_date"),
    State("my-date-picker-range","end_date"),]

)
def update_plots(selected_period, selected_station, yaxis_type, btn_date, history, res_state, het_state, volt_state, bosch_state, start_date, end_date):
    global LAST_CLICKED
    
    if "yaxis-type" == callback_context.triggered_id:    
        res_state["layout"]["yaxis"]["type"] = ('linear' if not yaxis_type else 'log')
        return res_state, het_state, volt_state, bosch_state
    
    elif "check_history" == callback_context.triggered_id:
        station = 1 if (selected_station.split(" - ")[-1] == "S. Chiara") else 6
        sensors = load_data_from_psql(querys.query_history_sensor)
        sensors = sensors .loc[sensors["node_id"] == station]
        sensors["attrs"] = sensors["attrs"].astype(str)
        res_state = go.Figure(res_state)
        sensors = sensors.groupby('attrs')
        for tmp, group in sensors:
            tmp = tmp.replace("'",'"')
            d = json.loads(tmp)
            try:
                pos_x = pd.to_datetime(d["active since"]).tz_localize(None)          
                first = res_state["data"][0]['x'][0]
                first  = pd.to_datetime(first).tz_localize(None)
                
                last = res_state["data"][0]['x'][-1]
                last  = pd.to_datetime(last).tz_localize(None)
                
                if first < pos_x and pos_x < last:
                    if history:
                        res_state.add_vline(x=pos_x, line_width=3, line_dash="dash", line_color="green")
                    else:
                        res_state.layout.shapes = None
            except Exception as e:
                pass
            
        return res_state, het_state, volt_state, bosch_state
            
    if "btn_search_date" == callback_context.triggered_id or ("selected-station" == callback_context.triggered_id and LAST_CLICKED == "btn_search_date"):
        fbk_data = utils.query_custom(start_date, end_date)
        LAST_CLICKED = "btn_search_date"
    else:
        fbk_data = cache_fbk_data(selected_period)
        LAST_CLICKED = "selected-period"
        
    
    dfFBK1 = fbk_data[
        fbk_data["node_description"] == selected_station.split(" - ")[-1]
    ].dropna(inplace=False)

    dfFBK1["Data"] = pd.to_datetime(dfFBK1.ts.dt.date)
    
    fbk_data_ResV = dfFBK1
    
    #---------------------------RESISTANCE PLOT---------------------------
    
    resistance_plot = go.Figure()

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month", "last 6 months"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            resistance_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "ts"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "signal_res"
                    ],
                    name=SensingMaterial,
                )
            )
    # use days as X axis maybe for perion bigger than 1 year?
    else:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            resistance_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "Data"
                    ],
                    y=fbk_data_ResV[fbk_data_ResV["sensor_description"] == SensingMaterial][
                        "signal_res"
                    ],
                    name=SensingMaterial,
                )
            )

    resistance_plot.update_layout(
        #legend_title_text="Sensing Material",
        plot_bgcolor="#fefefe",
        #paper_bgcolor="#fefefe",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=5, t=20, b=0),
        #plot_bgcolor="white",
        #font=dict(size=10),
        title=dict(
            x=0.5,
            text="Sensor Resistance (Ω)",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
        legend=dict(
            orientation="h",
            entrywidth=50,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    resistance_plot.update_yaxes(title_text="",  type= 'linear' if not yaxis_type else 'log')
    #----------------------HEATER PLOT-----------------------------
    
    heater_plot = go.Figure()
    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month", "last 6 months"]:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            heater_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["ts"],
                    y=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["heater_res"],
                    name=SensingMaterial,
                )
            )
    # use days as X axis
    else:
        for SensingMaterial, group in fbk_data_ResV.groupby("sensor_description"):
            heater_plot.add_trace(
                go.Scatter(
                    x=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["Data"],
                    y=fbk_data_ResV[
                        fbk_data_ResV["sensor_description"] == SensingMaterial
                    ]["heater_res"],
                    name=SensingMaterial,
                )
            )

    heater_plot.update_layout(
        legend_title_text="Sensing Material",
        margin=dict(l=0, r=5, t=20, b=0),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
        title=dict(
            x=0.5,
            text="Heater Resistance (Ω)",
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
        ),
    )
    heater_plot.update_yaxes(title_text="", fixedrange=True)
    
    #---------------------------VOLTAGE PLOT---------------------------
    
    volt_plot = go.Figure()

    # use hour as X axis
    if selected_period in ["last hour", "last week", "last day", "last month", "last 6 months"]:
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
        paper_bgcolor="rgba(0,0,0,0)",
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
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
        yaxis=dict(title="Temp (°C) & RH (%)"),
        yaxis2=dict(title="pressure (psi)", overlaying="y", side="right"),
        legend={
            "x": 0,
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
    
    return [resistance_plot, heater_plot, volt_plot, bosch_plot]


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
                        #style=dict(height="77vh"),
                        style={"height":"55vh",},
                        className="pretty_container",
                    ),
                    #lg=7,
                    #xl=8,
                style={"width":"80%"}),
                dbc.Col(
                    [
                        toast,
                    ],
                    width=1,
                    style={"min-width":"200px"}  
                ),
                
            ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        dcc.Graph(
                            id="heater-plot",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                            className="pretty_container",
                        ),],
                    width=4),
                dbc.Col([
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        dcc.Graph(
                            id="voltage-plot",
                            className="side-plot pretty_container",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),],
                    width=4),
                dbc.Col([
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        dcc.Graph(
                            id="bosch-plot",
                            className="side-plot pretty_container",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),],
                    width=4),
                    #],
                    #md=5,
                    #lg=5,
                    #xl=4,
                #),
            ],
        ),
    ],
    className="section fullHeight",
)
