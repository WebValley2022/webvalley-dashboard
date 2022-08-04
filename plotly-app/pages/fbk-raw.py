from calendar import day_abbr
from dash import html, dcc, Input, Output, callback
from db_utils import load_data_from_psql
from datetime import datetime
from typing import Tuple
from .utils import utils

import plotly.graph_objects as go
import pandas as pd
import logging
import dash
import os

##################
# SECTION 1 PAGE #
##################

# dash.register_page(__name__, redirect_from=["/"])
dash.register_page(__name__)

if os.getenv("DEBUG"):
    pass
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

periods = ["last 6 months", "last month", "last week", "last day", "last hour"]
stations = ["Trento - S. Chiara", "Trento - Via Bolzano"]

dropdown_station = dcc.Dropdown(
    stations,
    id = "selected_station",
    className = "dropdown",
    value = stations[0]
)

dropdown_period = dcc.Dropdown(
    periods,
    id = "selected_period",
    className = "dropdown",
    value = periods[0]
)

#resistance_plot = dcc.Graph(id="resistance_plot", className="side-plot")

#right_top_plot = dcc.Graph(id="right_top_plot", className="side-plot")

middle_right_plot = dcc.Graph(id = "middle_right_plot", className = "side-plot")

bottom_right_plot = dcc.Graph(id = "bottom_right_plot", className = "side-plot")

header = html.Div(
    [title, dropdown_period, dropdown_station, middle_right_plot, bottom_right_plot],
    className = "section-header"
)

layout = html.Div([
    header
])

# temperature, pressure and humidity graph
@callback(
    Output("middle_right_plot", "figure"),
    Input("selected_station", "value"),
    Input("selected_period", "value"),
)
def update_middle_right_plot(selected_period: str, selected_station: str) -> go.Figure:
    """
    Updates the graph in the 1st section representing the humidity, pressure and temperature

    Args:
        selected_period (str): the period which to show the data
        selected_station (str): the station which to show the data

    Returns:
        go.Figure: the plot
    """
    plot_width = 800
    plot_height = 400

    fbk_data = utils.get_fbk_data()

    # all the same station so remove only duplicates of readings
    fbk_data.drop_duplicates(["sensor_description", "ts"], inplace = True)
    # keep only Temperature, Humidity, Pressure
    fbk_data_THP = fbk_data.drop(["heater_res", "signal_res", "volt"], axis = 1)

    # make average of all data within a minute of difference
    fbk_data_THP = fbk_data_THP.groupby(
        ["sensor_description", "node_description"]
    ).resample("1T", on = "ts").mean()
    fbk_data_THP = fbk_data_THP.reset_index()
    
    # temperature plot
    trace1 = go.Scatter(
        x = fbk_data_THP["ts"],
        y = fbk_data_THP["t"],
        name = "Temperature",
        mode = "lines",
        yaxis = "y1",
        hovertemplate = "Parameter = Temperature<br>Value = %{y}<br>Date = %{x}<extra></extra>"
    )

    # relative humidity plot
    trace2 = go.Scatter(
        x = fbk_data_THP["ts"],
        y = fbk_data_THP["rh"],
        name = "Humidity",
        mode = "lines",
        yaxis = "y1",
        hovertemplate = "Parameter = Humidity<br>Value = %{y}<br>Date = %{x}<extra></extra>"
    )

    # pressure plot
    trace3 = go.Scatter(
        x = fbk_data_THP["ts"],
        y = fbk_data_THP["p"],
        name = "Pressure",
        mode = "lines",
        yaxis = "y2",
        hovertemplate = "Parameter = Pressure<br>Value = %{y}<br>Date = %{x}<extra></extra>"
    )

    data = [trace1, trace2, trace3]
    layout = go.Layout(
        title = "Temperature - Pressure - Humidity",
        yaxis  = dict(title="Humidity - Temperature"),
        yaxis2 = dict(
            overlaying = "y",
            title = "Pressure",
            side = "right"
        ),
        width = plot_width,
        height = plot_height,
        legend = dict(
            x = 1,
            y = 1.02,
            orientation = "h",
            yanchor = "bottom",
            xanchor = "right",
        )
    )

    return go.Figure(data=data, layout=layout)

# the resistance plot
@callback(
    Output("bottom_right_plot", "figure"),
    Input("selected_station", "value"),
    Input("selected_period", "value"),
)
def update_bottom_right_plot(selected_station: str, selected_period: str) -> Tuple[go.Figure, go.Figure]:
    """
    Updates the plot representing change of voltage of the various sensors over time

    Args:
        selected_station (str): the station which to show the data
        selected_period (str): the perdiod which to show the data

    Returns:
        Tuple[go.Figure, go.Figure]: the two plots
    """
    fbk_data = utils.get_fbk_data()
    
    # separate date from time
    fbk_data["Data"] = pd.to_datetime(fbk_data.ts.dt.date)

    # keep only Signal Resistance, drop Temperature, humidity, pressure
    # SRV = Signal Resistance and Volt
    fbk_data_SRV = fbk_data.drop(["p", "rh", "t"], axis=1)
    fbk_data_SRV = fbk_data_SRV.groupby(["Data", "sensor_description"]).mean()
    fbk_data_SRV.reset_index(inplace = True)

    fbk_data_SRV = fbk_data_SRV.drop(["signal_res", "heater_res"], axis=1)

    fig = go.Figure()
    for SensingMaterial, group in fbk_data_SRV.groupby("sensor_description"):
        # add trace to figure for each sensing material
        fig.add_trace(
            go.Scatter(
                x = fbk_data_SRV[
                    fbk_data_SRV["sensor_description"] == SensingMaterial
                ]["Data"],
                y = fbk_data_SRV[
                    fbk_data_SRV["sensor_description"] == SensingMaterial
                ]["volt"],
                name = SensingMaterial
            )
        )

    fig.update_layout(legend_title_text = "Sensing Material")
    fig.update_yaxes(title_text = "Value")

    return fig

def verify_period(period: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Retrieves only the last PERIOD specified

    Args:
        period (str): the period wanted
        dataframe (pd.DataFrame): the starting dataframe

    Returns:
        pd.DataFrame: the filtered dataframe
    """
    if period == "6 months":
        dataframe = dataframe.groupby(["Data", "sensor_description"]).mean()
        dataframe.reset_index(inplace = True)
        dataframe.set_index("Data", inplace = True)
        dataframe = dataframe.last("180D")
        return dataframe.reset_index()

    elif period == "last month":
        dataframe = dataframe.groupby(["Data", "sensor_description"]).mean()
        dataframe.reset_index(inplace = True)
        dataframe.set_index("Data", inplace = True)
        dataframe = dataframe.last("30D")
        return dataframe.reset_index()
    
    elif period == "last week":
        dataframe.reset_index(inplace = True)
        dataframe.set_index("ts", inplace = True)
        dataframe = dataframe.last("7D")
        return dataframe.reset_index()

    elif period == "last day":
        dataframe.reset_index(inplace = True)
        dataframe.set_index("ts", inplace = True)
        dataframe = dataframe.last("1D")
        return dataframe.reset_index()

    elif period == "last hour":
        dataframe.reset_index(inplace = True)
        dataframe.set_index("ts", inplace = True)
        dataframe = dataframe.last("1H")
        return dataframe.reset_index()
