from click import option
import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)


df = pd.read_csv(
    "./data/21_22_APPA.csv")
df = df[df.Valore != 'n.d.']
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()


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
    Input("selected-pollutant", "value"),
)
def update_main_plot(selected_appa_station, selected_pollutant):
    data = df[
        (df.Stazione == selected_appa_station) & (df.Inquinante == selected_pollutant)
    ]
    data_resampled = data.resample("W", on="Data").mean()
    data_resampled = data_resampled.reset_index()
    fig = px.line(data_resampled, x="Data", y="Valore")
    return fig


@callback(
    Output("year-plot", "figure"),
    Input("selected-appa-station", "value"),
    Input("selected-pollutant", "value"),
)
def update_year_plot(selected_appa_station, selected_pollutant):
    data = df[
        (df.Stazione == selected_appa_station) & (df.Inquinante == selected_pollutant)
    ]
    df_year = data.groupby([data.Data.dt.year, data.Data.dt.month]).mean()
    df_year.index.names = ["Year", "Month"]
    df_year = df_year.reset_index()
    fig = px.line(df_year, y="Valore", x="Month", color="Year")

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

layout = dbc.Container(
    [
        title,
        dropdown,
        download_btn,
        gas_btns,
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="main-plot"), lg=7, xl=8),  # className="main-plot-ct"
                dbc.Col(
                    [
                        dcc.Graph(id="year-plot", className="side-plot"),
                        dcc.Graph(id="weekly-plot", className="side-plot"),
                    ],
                    # className="side-plots-ct",
                    lg=5, xl=4
                ),
            ]
        ),
    ],
    # fluid=True,
)
