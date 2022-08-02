from click import option
import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("APPA Data", className="header-title")

df = pd.read_csv("../data/merged_APPA_data.csv")
df.Data = pd.to_datetime(df.Data)
stations = df.Stazione.unique()

dropdown = dcc.Dropdown(
    stations, id='selected-station', className="dropdown", value=stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

gas_btns = html.Div(id="buttons", className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)

main_plot = html.Div([dcc.Graph(id="main-plot"),
                      "Show: ",
                      dcc.Dropdown(options=[
                                   "last day", "last week", "last month", "last year", "all"],
                                   id="selected-time", value="last month", className="dropdown")],
                     className="main-plot-ct"
                     )

content = html.Div([main_plot], className="content")


@callback(Output("buttons", "children"), Input("selected-station", "value"))
def get_pollutants(selected_station):
    filtered_df = df[df.Stazione == selected_station]
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
          Input("selected-station", "value"),
          Input("selected-pollutant", "value"),
          Input("selected-time", "value"))
def update_main_plot(selected_station, selected_pollutant, selected_time):
    data = df[(df.Stazione == selected_station) &
              (df.Inquinante == selected_pollutant)]
    if selected_time == "last day":
        last_day = data.Data.max().day
        data = data[data.Data.day == last_day]
    elif selected_time == "last week":
        last_week = data.Data.max().week
        data = data[data.Data.week == last_week]
    # elif selected_time == "last month":
    #     last_month = data.Data
    fig = px.line(
        data,
        x="Data",
        y="Valore"
    )
    return fig


layout = html.Div(
    [header,
     content],
    className="section")
