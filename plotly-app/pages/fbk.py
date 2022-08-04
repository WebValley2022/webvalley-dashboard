from statistics import mean
from time import time
import dash
from dash import html, dcc, Input, Output, callback
import dash_daq as daq
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

dash.register_page(__name__)


df = pd.read_csv("./data/appa1_predictions.csv")
df.Time = pd.to_datetime(df.Time)
df["Station"] = "Parco S. Chiara"

df["NO2_pred"] += np.random.rand(len(df)) * 10 - 5
df["CO_pred"] += np.random.rand(len(df)) - 0.5
df["O3_pred"] += np.random.rand(len(df)) * 10 - 5


fbk_stations = ["Parco S. Chiara", "Via Bolzano"]
pollutants = [dict(label="Biossido di Azoto", value="NO2"),
              dict(label="Ozono", value="O3"),
              dict(label="Ossido di Carbonio", value="CO")]


title = html.Div("Dati FBK - Fitted", className="header-title")

dropdown = dcc.Dropdown(
    fbk_stations, id="selected-station", className="dropdown", value=fbk_stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

gas_btns = html.Div(dbc.RadioItems(
    id="selected-fbk-pollutant",
    class_name="btn-group",
    input_class_name="btn-check",
    label_class_name="btn btn-outline-primary",
    label_checked_class_name="active",
    options=pollutants,
    value="NO2"
), className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

graph_selectors = html.Div([html.Div(["Visualizza: ",
                                      dcc.Dropdown(id="selected-period",
                                                   options=["ultime 24h", "ultima settimana",
                                                            "ultimo mese", "ultimo anno", "tutto"],
                                                   className="dropdown")],
                                     className="graph-dropdown"),
                            daq.ToggleSwitch(id="toggle-comparison",
                                             label="Compare with APPA",
                                             color="#0d6efd",
                                             className="ml-auto toggle")],
                           className="d-flex flex-grow justify-content-between")

comparison_graph = html.Div(
    [dcc.Graph(id="comparison-graph", style=dict(height="50vh"), config={
        'displayModeBar': False,
        'displaylogo': False,
    }), graph_selectors])


# TODO: Fix labels.


@callback(Output("comparison-graph", "figure"),
          Input("selected-station", "value"),
          Input("selected-fbk-pollutant", "value"),
          Input("toggle-comparison", "value"),
          Input("selected-period", "value")
          )
def update_comparison_graph(
        selected_station,
        selected_pollutant,
        toggle_comparison,
        selected_period):
    """
    Updates the graph representing the comparison between
    APPA data and model prediction

    Args:
        station (str): station name
        pollutant (str): pollutant name
        time_span (str): H: hour; D: day; W: week; M: month; Y: year
        compare_APPA (bool): wether to add a line of APPA"s data or not

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

    fig.add_trace(
        go.Scatter(
            x=data["Time"],
            y=data[pollutant_pred],
            mode="lines+markers",
            name="FBK"
        )
    )

    if toggle_comparison:
        fig.add_trace(
            go.Scatter(
                x=data["Time"],
                y=data[pollutant_real],
                mode="lines+markers",
                name="APPA",
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
        time_span (str): values can be "D": day, "W": week, "Y": year, "H": hour
        station (str): the station where to get the data
        pollutant (str): the desired pollutant

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

    mean_temp = dataframe[dataframe.Station == station]
    mean_temp = mean_temp[["Time", pollutant_real, pollutant_pred]]

    last_day = mean_temp.Time.max()

    if selected_period == "ultime 24h":
        time_span = "H"
        mean_temp = mean_temp.tail(24)
    elif selected_period == "ultima settimana":
        time_span = "H"
        mean_temp = mean_temp.tail(168)
    elif selected_period == "ultimo mese":
        time_span = "D"
        mean_temp = mean_temp[(mean_temp.Time.dt.month == last_day.month) & (
            mean_temp.Time.dt.year == last_day.year)]
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
    mean_temp.reset_index(inplace=True)

    return mean_temp


layout = html.Div(
    [header,
     html.Div([comparison_graph], className="fbk-main-plot")
     ],
    className="section")
