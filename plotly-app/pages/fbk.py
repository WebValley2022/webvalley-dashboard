from dash import html, dcc, Input, Output, callback
from .utils import utils

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd
import numpy as np
import dash
import logging

dash.register_page(__name__)


df = utils.get_prediction_data()
df["Time"] = pd.to_datetime(df["Time"])

# add static station to simulate query
df["Station"] = "Parco S. Chiara"

# add random noise to dataframe
df["NO2_pred"] += np.random.rand(len(df)) * 10 - 5
df["CO_pred"] += np.random.rand(len(df)) - 0.5
df["O3_pred"] += np.random.rand(len(df)) * 10 - 5


fbk_stations = ["Parco S. Chiara", "Via Bolzano"]
pollutants = [
    dict(label="Biossido di Azoto", value="NO2"),
    dict(label="Ozono", value="O3"),
    dict(label="Ossido di Carbonio", value="CO")
]

title = html.Div("Dati FBK - Fitted", className="header-title")

# build dropdown of stations
dropdown = dcc.Dropdown(
    fbk_stations,
    id = "selected-station",
    className = "dropdown",
    value = fbk_stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    id="btn_fbk_fitted",
    class_name="download-btn",
)
download_it = dcc.Download(id="download-fbk-fitted")


@callback(
    Output("download-fbk-fitted", "data"),
    Input("btn_fbk_fitted", "n_clicks"),
    prevent_initial_call=True,
)
def create_download_file(n_clicks):
    global df
    return dcc.send_data_frame(df.to_csv, "fbk_fitted_data.csv")


# build gas buttons
gas_btns = html.Div(dbc.RadioItems(
    id = "selected-fbk-pollutant",
    class_name = "btn-group",
    input_class_name = "btn-check",
    label_class_name = "btn btn-outline-primary",
    label_checked_class_name = "active",
    options=pollutants,
    value = "NO2"
), className = "radio-group")

header = html.Div(
    [title, dropdown, download_btn, download_it, gas_btns],
    className = "section-header"
)

graph_selectors = html.Div(
    [
        html.Div(
            [
                "Visualizza: ",
                dcc.Dropdown(
                    id = "selected-period",
                    options = [
                        "ultime 24h",
                        "ultima settimana",
                        "ultimo mese",
                        "ultimo anno",
                        "tutto"
                    ],
                    className = "dropdown"
                )
            ],
            className = "graph-dropdown"
        ),
        daq.ToggleSwitch(
            id = "toggle-comparison",
            label = "Compare with APPA",
            color = "#0d6efd",
            className = "ml-auto toggle"
        )
    ],
    className = "d-flex flex-grow justify-content-between"
)

comparison_graph = html.Div(
    [dcc.Graph(id="comparison-graph", style=dict(height="50vh"), config={
        'displayModeBar': False,
        'displaylogo': False,
    }), graph_selectors])


# TODO: Fix labels.


@callback(
    Output("comparison-graph", "figure"),
    Input("selected-station", "value"),
    Input("selected-fbk-pollutant", "value"),
    Input("toggle-comparison", "value"),
    Input("selected-period", "value")
)
def update_comparison_graph(
        selected_station: str,
        selected_pollutant: str,
        toggle_comparison: str,
        selected_period: str
    ) -> go.Figure:
    """
    Updates the graph representing the comparison between
    APPA data and model prediction

    Args:
        slected_station (str): station name
        selected_pollutant (str): pollutant name
        selected_period (str): H: hour; D: day; W: week; M: month; Y: year
        toggle_comparison (bool): wether to add a line of APPA"s data or not

    Returns:
        plotly.graph_objs.Figure: the graph
    """
    pollutant_real = selected_pollutant + "_real"
    pollutant_pred = selected_pollutant + "_pred"

    fig = go.Figure()

    data = get_mean(
        df,
        selected_station,
        selected_pollutant,
        selected_period
    )

    # data = df[df.Station == selected_station]

    data = data[["Time", pollutant_real, pollutant_pred]]

    # prediction graph
    fig.add_trace(
        go.Scatter(
            x = data["Time"],
            y = data[pollutant_pred],
            mode = "lines+markers",
            name = "FBK"
        )
    )

    if toggle_comparison:
        # appa data graph
        fig.add_trace(
            go.Scatter(
                x = data["Time"],
                y = data[pollutant_real],
                mode = "lines+markers",
                name = "APPA",
            )
        )

    fig.update_layout(margin=dict(l=5, r=5, t=0, b=0), plot_bgcolor="white")
    fig.update_yaxes(fixedrange=True)

    return fig


def get_mean(dataframe: pd.DataFrame, station: str, selected_pollutant: str, selected_period) -> pd.DataFrame:
    """
    Gets the mean of a given time span from the given station
    and pollutant in the given dataframe

    Args:
        dataframe (pd.DataFrame): the input dataframe to be processed
        station (str): the station where to get the data
        selected_pollutant (str): the desired pollutant
        selected_period (str): values can be "D": day, "W": week, "Y": year, "H": hour

    Returns:
        pd.DataFrame: the dataframe with the mean values
    """
    pollutants = {
        "Biossido di Azoto": "NO2",
        "Ozono": "O3",
        "Ossido di Carbonio": "CO"
    }

    pollutant_real = selected_pollutant + "_real"
    pollutant_pred = selected_pollutant + "_pred"

    # filter station
    mean_temp = dataframe[dataframe.Station == station]
    # get sub-dataframe
    mean_temp = mean_temp[["Time", pollutant_real, pollutant_pred]]

    # get the last date available
    last_day = mean_temp.Time.max()

    if selected_period == "ultime 24h":
        time_span = "H"
        mean_temp = mean_temp.tail(24)
    elif selected_period == "ultima settimana":
        time_span = "H"
        mean_temp = mean_temp.tail(168)
    elif selected_period == "ultimo mese":
        time_span = "D"
        mean_temp = mean_temp[
            (mean_temp.Time.dt.month == last_day.month) &
            (mean_temp.Time.dt.year == last_day.year)
        ]
    elif selected_period == "ultimo anno":
        time_span = "W"
        mean_temp = mean_temp[(mean_temp.Time.dt.year == last_day.year)]
    else:
        time_span = "W"

    mean_temp = mean_temp.groupby(
        by=pd.Grouper(
            key="Time",
            freq=time_span
        )
    ).mean()
    # mean_temp.insert(1, "Inquinante", pollutant)
    # mean_temp.insert(1, "Stazione", station)
    mean_temp.reset_index(inplace = True)

    return mean_temp

layout = html.Div(
    [
        header,
        html.Div([comparison_graph], className = "fbk-main-plot")
    ],
    className = "section"
)
