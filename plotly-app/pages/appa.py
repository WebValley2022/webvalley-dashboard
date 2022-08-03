import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)


df = pd.read_csv(
    "./data/21_22_APPA.csv")
df = df[df.Valore != "n.d."]
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()


def filter_df(df, station, pollutant):
    return df[
        (df.Stazione == station) & (
            df.Inquinante == pollutant)
    ]


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
    fig = px.line(data_resampled, x="Data", y="Valore")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_yaxes(fixedrange=True)
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
    fig = px.line(df_year, y="Valore", x="Month", color="Year")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_yaxes(fixedrange=True)
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
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_yaxes(fixedrange=True)
    return fig


@callback(
    Output("day-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value")
)
def update_day_plot(selected_appa_station, selected_pollutant):
    data = filter_df(df, selected_appa_station, selected_pollutant)

    df_year = data.groupby(data.Data.dt.hour).mean()
    data.index.names = ["Hour"]
    df_year = df_year.reset_index()
    fig = px.line(df_year, y="Valore", x="Data",)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_yaxes(fixedrange=True)
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
                # className="main-plot-ct"
                dbc.Col(dcc.Graph(id="main-plot",config={
                    'displayModeBar': False,
                    'displaylogo': False,                                       
                },
                ), lg=7, xl=8),
                dbc.Col(
                    [
                        dcc.Graph(id="year-plot"),
                        dcc.Graph(id="week-plot", className="side-plot"),
                        dcc.Graph(id="day-plot", className="side-plot")
                    ],
                    # className="side-plots-ct",
                    md=5, lg=5, xl=4
                ),
            ],
            # className="content"
        ),
    ],
    # fluid=True,
)
