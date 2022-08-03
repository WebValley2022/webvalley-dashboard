from statistics import mean
from time import time
import dash
from dash import html, dcc, Input, Output, callback
import dash_daq as daq
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from soupsieve import select

dash.register_page(__name__)

title = html.Div("FBK Fitted Data", className="header-title")

appa_df = pd.read_csv("./data/21_22_APPA.csv")
appa_df = appa_df[appa_df.Valore != 'n.d.']
appa_df.Data = pd.to_datetime(appa_df.Data)

fbk_df = pd.read_csv("./data/19_20_APPA.csv")
fbk_df = appa_df[appa_df.Valore != 'n.d.']
fbk_df.Data = pd.to_datetime(appa_df.Data)
fbk_stations = fbk_df.Stazione.unique()

dropdown = dcc.Dropdown(
    fbk_stations, id='selected-station', className="dropdown", value=fbk_stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

gas_btns = html.Div(id="pollutants", className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

graph_selectors = html.Div([dcc.Dropdown(id="selected-period",
                                         options=['day', 'week',
                                                  'month', 'year', 'all'],
                                         className="dropdown"),
                            daq.ToggleSwitch(id="toggle-comparison",
                                             label="Compare with APPA",
                                             color="#0d6efd",
                                             className="ml-auto")],
                           className="d-flex flex-grow")

comparison_graph = html.Div(
    [dcc.Graph(id="comparison-graph"), graph_selectors])

content = html.Div([comparison_graph], className="content")


@callback(Output("pollutants", "children"), Input("selected-station", "value"))
def get_pollutants(selected_station):
    filtered_df = appa_df[appa_df.Stazione == selected_station]
    pollutants = filtered_df.Inquinante.unique()
    pollutants_list = [{"label": pollutant, "value": pollutant}
                       for pollutant in pollutants]

    return dbc.RadioItems(
        id="selected-fbk-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants_list,
        value=pollutants_list[0]["value"]
    )

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
        compare_APPA (bool): wether to add a line of APPA's data or not

    Returns:
        plotly.graph_objs.Figure: the graph
    """

    fig = go.Figure()

    estimated_data = get_mean(
        fbk_df,
        selected_station,
        selected_pollutant,
        selected_period
    )

    fig.add_trace(
        go.Scatter(
            x=estimated_data["Data"],
            y=estimated_data["Valore"],
            mode="lines+markers",
            name="FBK"
        )
    )

    if toggle_comparison:
        appa_data = get_mean(
            appa_df,
            selected_station,
            selected_pollutant,
            selected_period
        )

        fig.add_trace(
            go.Scatter(
                x=appa_data["Data"],
                y=appa_data["Valore"],
                mode="lines+markers",
                name="APPA",
            )
        )

    return fig


def get_mean(dataframe: pd.DataFrame, station: str, pollutant: str, selected_period) -> pd.DataFrame:
    """
    Gets the mean of a given time span from the given station
    and pollutant in the given dataframe

    Args:
        dataframe (pd.DataFrame): the input dataframe to be processed
        time_span (str): values can be 'D': day, 'W': week, 'Y': year, 'H': hour
        station (str): the station where to get the data
        pollutant (str): the desired pollutant

    Returns:
        pd.DataFrame: the dataframe with the mean values
    """
    mean_temp = dataframe[
        (dataframe["Stazione"] == station) &
        (dataframe["Inquinante"] == pollutant)
    ]

    last_day = mean_temp.Data.max()

    if selected_period == "day":
        time_span = "H"
        mean_temp = mean_temp[mean_temp.Data == last_day]
    elif selected_period == "week":
        time_span = "H"
        mean_temp = mean_temp[mean_temp.Data.dt.week == last_day.week]
    elif selected_period == "month":
        time_span = "D"
        mean_temp = mean_temp[(mean_temp.Data.dt.month == last_day.month) & (
            mean_temp.Data.dt.year == last_day.year)]
    elif selected_period == "year":
        time_span = "W"
        mean_temp = mean_temp[(mean_temp.Data.dt.year == last_day.year)]
    else:
        time_span = "W"

    mean_temp = mean_temp.groupby(
        by=pd.Grouper(
            key="Data",
            freq=time_span
        )
    ).mean()
    mean_temp.insert(1, "Inquinante", pollutant)
    mean_temp.insert(1, "Stazione", station)
    mean_temp.reset_index(inplace=True)

    return mean_temp


layout = html.Div(
    [header,
     content],
    className="section")
