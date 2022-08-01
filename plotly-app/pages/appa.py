from click import option
import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from matplotlib.pyplot import xticks 
import matplotlib as plt
import seaborn as sns

dash.register_page(__name__)

title = html.Div("APPA Data", className="header-title")

df = pd.read_csv("./data/merged_APPA_data.zip")
stations = df.Stazione.unique()

dropdown = dcc.Dropdown(
    stations, placeholder="Select station", id='selected_station', className="dropdown"
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    class_name="download-btn"
)

gas_btns = html.Div(id="buttons", className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns, plot1],
    className="section-header"
)

@callback(
    #Output("filtered-df", "df"),
    Output('pollutants_plot', 'figure'),
    Input("selected_station", "value")
    )

@callback(Output("buttons", "children"), Input("selected-station", "value"))
def get_pollutants(selected_station):
    filtered_df = df[df.Stazione == selected_station]
    pollutants = filtered_df.Inquinante.unique()
    pollutants_dict = [{"label": pollutant, "value": pollutant}
                       for pollutant in pollutants]

    return dbc.RadioItems(
        id="pollutants",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants_dict
    )


layout = html.Div(
    [header,
     html.P(id="response", children=[], style={"display": "none"})],
    className="section")

# dropdown1 = dbc.DropdownMenu(
#     # html.I(className="fa-solid fa-location-dot"),
#     label="Select location",
#     children=[
#         dbc.DropdownMenuItem(station) for station in stations
#         # dbc.DropdownMenuItem("Trento - S. Chiara"),
#         # dbc.DropdownMenuItem("Trento - Via Bolzano")
#     ],
#     color="secondary",)