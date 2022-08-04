from dash import html, dcc, Input, Output, callback
from db_utils import load_data_from_psql
from datetime import datetime
from .utils import utils

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import logging
import dash
import os

dash.register_page(__name__)

if os.getenv("DEBUG"):
    df = utils.get_appa_data()
else:
    query = """
    select
        stazione,
        inquinante,
        ts,
        valore
    from appa_data
    where ts > '2020-01-01';
    """
    start = datetime.now()
    df = load_data_from_psql(query)
    logging.info("Query time", datetime.now() - start)
    df = df.rename({
        "stazione": "Stazione",
        "inquinante": "Inquinante",
        "ts": "Data",
        "valore": "Valore",
    }, axis=1)

# keep only rows with a value that's not NA
df = df[df.Valore != "n.d."]

df["Data"] = pd.to_datetime(df["Data"])
stations = df.Stazione.unique()


def filter_df(df: pd.DataFrame, station: str, pollutant: str) -> pd.DataFrame:
    """
    returns a dataframe formed of all the records of the selected station and pollutant

    Args:
        df (pd.DataFrame): the dataframe to filter
        station (str): the station to select
        pollutant (str): the pollutant to select

    Returns:
        pd.DataFrame: the filtered dataframe
    """
    return df[
        (df.Stazione == station) &
        (df.Inquinante == pollutant)
    ]


def line_plot(df: pd.DataFrame, x: str, y: str, color: str = None) -> go.Figure:
    """
    Generates a line plot based on the dataframe, x and y given

    Args:
        df (pd.DataFrame): the dataframe to take the data from
        x (str): the column to select as X axis
        y (str): the column to select as Y axis
        color (str, optional): the column to assign different colors for multiple plots. Defaults to None.

    Returns:
        go.Figure: the line plot
    """
    fig = px.line(df, x=x, y=y, color=color)

    fig.update_layout(margin=dict(l=0, r=5, t=0, b=0), plot_bgcolor="white")
    fig.update_yaxes(fixedrange=True)

    return fig


@callback(
    Output("appa-pollutants", "children"),
    Input("selected-appa-station", "value")
)
def get_pollutants(selected_appa_station: str) -> dbc.RadioItems:
    """
    Generates the radio items of pollutants of the given appa station

    Args:
        selected_appa_station (str): the selected station

    Returns:
        dbc.RadioItems: the radio items of the pollutants
    """
    # filter station
    filtered_df = df[df.Stazione == selected_appa_station]

    # get pollutants and build dict from it
    pollutants = filtered_df.Inquinante.unique()
    pollutants_list = [
        {"label": pollutant, "value": pollutant} for pollutant in pollutants
    ]

    return dbc.RadioItems(
        id="selected-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants_list,
        # value = pollutants_list[0]["value"],
        value="Biossido di Azoto"
    )


@callback(
    Output("main-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_main_plot(selected_appa_station: str, selected_pollutant: str) -> go.Figure:
    """
    Updates the main plot representing the pollutant level of the selected station over time

    Args:
        selected_appa_station (str): the station which to show the data
        selected_pollutant (str): the pollutant which to show the data

    Returns:
        go.Figure: the plot
    """
    data = filter_df(df, selected_appa_station, selected_pollutant)

    # make week average of data
    data_resampled = data.resample("W", on="Data").mean()
    data_resampled = data_resampled.reset_index()
    fig = line_plot(data_resampled, "Data", "Valore")
    return fig


@callback(
    Output("year-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_year_plot(selected_appa_station: str, selected_pollutant: str) -> go.Figure:
    """
    Updates the yearly change over time of the selected pollutant of the selected station

    Args:
        selected_appa_station (str): the station which to show the data
        selected_pollutant (str): the pollutant which to show the data

    Returns:
        go.Figure: the plot
    """
    data = filter_df(df, selected_appa_station, selected_pollutant)

    # make month average of data
    df_year = data.groupby([data.Data.dt.year, data.Data.dt.month]).mean()
    df_year.index.names = ["Anno", "Mese"]
    df_year = df_year.reset_index()
    fig = line_plot(df_year, "Mese", "Valore", "Anno")
    return fig


@callback(
    Output("week-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_week_plot(selected_appa_station: str, selected_pollutant: str) -> go.Figure:
    """
    Updates the weekly change over time of the selected pollutant of the selected station

    Args:
        selected_appa_station (str): the station which to show the data
        selected_pollutant (str): the pollutant which to show the data

    Returns:
        go.Figure: the plot
    """
    data = filter_df(df, selected_appa_station, selected_pollutant)
    data["Month"] = data.Data.dt.month

    # add new column
    data["Inverno"] = False

    # set January to March and October to December as 'Inverno' True
    data.loc[(data.Month >= 10) | (data.Month <= 3), "Inverno"] = True

    # make daily average of pollutant level
    data = data.groupby(["Inverno", data.Data.dt.day_of_week]).mean()
    data.index.names = ["Inverno", "Giorno della settimana"]
    data = data.reset_index()

    # draw main bar plot
    fig = px.bar(
        data,
        x="Giorno della settimana",
        y="Valore",
        color="Inverno",
        barmode="group"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), plot_bgcolor="white")
    fig.update_yaxes(fixedrange=True)
    return fig


@callback(
    Output("day-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_day_plot(selected_appa_station: str, selected_pollutant: str) -> go.Figure:
    """
    Updates the daily change over time of the selected pollutant of the selected station

    Args:
        selected_appa_station (str): the station which to show the data
        selected_pollutant (str): the pollutant which to show the data

    Returns:
        go.Figure: the  plot
    """
    data = filter_df(df, selected_appa_station, selected_pollutant)

    # make hourly average of data
    df_day = data.groupby(data.Data.dt.hour).mean()
    df_day.index.names = ["Ora"]
    df_day = df_day.reset_index()
    fig = line_plot(df_day, "Ora", "Valore")

    return fig


title = html.Div("Dati APPA", className="header-title")
dropdown = dcc.Dropdown(
    stations,
    id="selected-appa-station",
    className="dropdown",
    value=stations[0]
)
download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), "Download full data"],
    color="primary",
    class_name="download-btn",
)
gas_btns = html.Div(
    id="appa-pollutants",
    className="radio-group"
)

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

layout = html.Div(
    [
        header,
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id="main-plot",
                    config={
                        'displayModeBar': False,
                        'displaylogo': False,
                    },
                    style=dict(height="70vh")
                ),
                lg=7,
                xl=8
            ),
            dbc.Col(
                [
                    dcc.Graph(
                        id="year-plot",
                        config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        },
                        style=dict(height="30vh")
                    ),
                    dcc.Graph(
                        id="week-plot",
                        className="side-plot",
                        config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        },
                        style=dict(height="20vh")
                    ),
                    dcc.Graph(
                        id="day-plot",
                        className="side-plot",
                        config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        },
                        style=dict(height="20vh")
                    )
                ],
                md=5,
                lg=5,
                xl=4
            ),
        ]),
    ],
    className="section"
)
