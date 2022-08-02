from click import option
import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("APPA Data", className="header-title")

df = pd.read_csv(
    "/home/davidef/Documents/webvalley-dashboard/plotly-app/data/21_22_APPA.csv")
df = df[df.Valore != 'n.d.']
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()

dropdown = dcc.Dropdown(
    stations, id='selected-appa-station', className="dropdown", value=stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

gas_btns = html.Div(id="appa-pollutants", className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

main_plot = html.Div(dcc.Graph(id="main-plot"),
                     className="main-plot-ct")

year_plot = dcc.Graph(id="year-plot", className="side-plot")

weekly_plot = dcc.Graph(id="weekly-plot", className="side-plot")

side_plots = html.Div([year_plot, weekly_plot], className="side-plots-ct")

content = html.Div([main_plot, side_plots], className="content")


@callback(Output("appa-pollutants", "children"), Input("selected-appa-station", "value"))
def get_pollutants(selected_appa_station):
    filtered_df = df[df.Stazione == selected_appa_station]
    pollutants = filtered_df.Inquinante.unique()
    pollutants_dict = [{"label": pollutant, "value": pollutant}
                       for pollutant in pollutants]

    return dbc.RadioItems(
        id="selected-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants_dict,
        value=pollutants_dict[0]
    )


@callback(Output("main-plot", "figure"),
          Input("selected-appa-station", "value"),
          Input("selected-pollutant", "value"))
def update_main_plot(selected_appa_station, selected_pollutant):
    data = df[(df.Stazione == selected_appa_station) &
              (df.Inquinante == selected_pollutant)]
    data_resampled = data.resample("W", on='Data').mean()
    data_resampled = data_resampled.reset_index()
    fig = px.line(
        data_resampled,
        x="Data",
        y="Valore"
    )
    return fig


@callback(Output("year-plot", "figure"),
          Input("selected-appa-station", "value"),
          Input("selected-pollutant", "value"))
def update_year_plot(selected_appa_station, selected_pollutant):
    data = df[(df.Stazione == selected_appa_station) &
              (df.Inquinante == selected_pollutant)]
    df_year = data.groupby(pd.PeriodIndex(data['Data'], freq="M"))[
        'Valore'].mean()
    df_year = df_year.reset_index()
    df_year = df_year.groupby(
        [df_year.Data.dt.year, df_year.Data.dt.month]).mean()
    df_year.index.names = ["Year", "Month"]
    df_year = df_year.reset_index()
    fig = px.line(
        df_year,
        y="Valore",
        x="Month",
        color="Year"
    )

    return fig


@callback(Output("weekly-plot", "figure"),
          Input("selected-appa-station", "value"),
          Input("selected-pollutant", "value"))
def update_weekly_plot(selected_appa_station, selected_pollutant):
    data2 = df[(df.Stazione == selected_appa_station) &
               (df.Inquinante == selected_pollutant)]
    print(data2)
    df_weekly = data2.groupby(
        [data2.Data.dt.month, data2.Data.dt.day_of_week]).mean()
    df_weekly.index.names = ["Month", "WeekDay"]
    print(df_weekly)
    df_weekly = df_weekly.reset_index()

    fig = px.line(
        df_weekly,
        y="Valore",
        x="WeekDay",
        color="Month"
    )

    return fig


layout = html.Div(
    [header,
     content],
    className="section")
