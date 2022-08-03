import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import os
from db_utils import load_data_from_psql
from datetime import datetime
import logging

dash.register_page(__name__)

if os.getenv("DEBUG"):
    df = pd.read_csv("./data/21_22_APPA.csv")
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
    # df.to_csv("data_appa_from_db.csv")
    df = df.rename({
        "stazione": "Stazione",
        "inquinante": "Inquinante",
        "ts": "Data",
        "valore": "Valore",
    }, axis=1)

df = df[df.Valore != "n.d."]
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()

def filter_df(df, station, pollutant):
    return df[
        (df.Stazione == station) & (
            df.Inquinante == pollutant)
    ]


def line_plot(df, x, y, color=None):
    fig = px.line(df, x=x, y=y, color=color)

    fig.update_layout(margin=dict(l=0, r=5, t=0, b=0), plot_bgcolor="white")
    fig.update_yaxes(fixedrange=True)

    return fig


@callback(
    Output("appa-pollutants", "children"), Input("selected-appa-station", "value")
)
def get_pollutants(selected_appa_station):
    filtered_df = df[df.Stazione == selected_appa_station]
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
        value=pollutants_list[0]["value"],
    )


@callback(
    Output("main-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_main_plot(selected_appa_station, selected_pollutant):
    data = filter_df(df, selected_appa_station, selected_pollutant)

    data_resampled = data.resample("W", on="Data").mean()
    data_resampled = data_resampled.reset_index()
    fig = line_plot(data_resampled, "Data", "Valore")
    return fig


@callback(
    Output("year-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_year_plot(selected_appa_station, selected_pollutant):
    data = filter_df(df, selected_appa_station, selected_pollutant)

    df_year = data.groupby([data.Data.dt.year, data.Data.dt.month]).mean()
    df_year.index.names = ["Year", "Month"]
    df_year = df_year.reset_index()
    fig = line_plot(df_year, "Month", "Valore", "Year")
    return fig


@callback(
    Output("week-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_week_plot(selected_appa_station, selected_pollutant):
    data = filter_df(df, selected_appa_station, selected_pollutant)
    data["Month"] = data.Data.dt.month

    data["Inverno"] = False
    data.loc[(data.Month >= 10) | (data.Month <= 3), "Inverno"] = True
    data = data.groupby(["Inverno", data.Data.dt.day_of_week]).mean()
    data.index.names = ["Inverno", "Week day"]
    data = data.reset_index()

    fig = px.bar(
        data,
        x="Week day",
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
def update_day_plot(selected_appa_station, selected_pollutant):
    data = filter_df(df, selected_appa_station, selected_pollutant)

    df_day = data.groupby(data.Data.dt.hour).mean()
    df_day.index.names = ["Hour"]
    df_day = df_day.reset_index()
    print(df_day)
    fig = line_plot(df_day, "Hour", "Valore")

    return fig


title = html.Div("APPA Data", className="header-title")
dropdown = dcc.Dropdown(
    stations, id="selected-appa-station", className="dropdown", value=stations[0]
)
download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn",
)
gas_btns = html.Div(id="appa-pollutants", className="radio-group")

layout = html.Div(
    [
        title,
        dropdown,
        download_btn,
        gas_btns,
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="main-plot", config={
                    'displayModeBar': False,
                    'displaylogo': False,
                }, style=dict(height="80vh")
                ), lg=7, xl=8),
                dbc.Col(
                    [
                        dcc.Graph(id="year-plot", config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        }, style=dict(height="40vh")),
                        dcc.Graph(id="week-plot", className="side-plot", config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        }, style=dict(height="20vh")),
                        dcc.Graph(id="day-plot", className="side-plot", config={
                            'displayModeBar': False,
                            'displaylogo': False,
                        }, style=dict(height="20vh"))
                    ],
                    md=5, lg=5, xl=4
                ),
            ],
        ),
    ],
    className="section"
)
