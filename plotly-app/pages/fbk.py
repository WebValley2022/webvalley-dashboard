import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__)

title = html.Div("FBK Fitted Data", className="header-title")

df = pd.read_csv("../data/merged_APPA_data.csv")
df = df[df.Valore != 'n.d.']
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

gas_btns = html.Div(id="pollutants", className="radio-group")

header = html.Div(
    [title, dropdown, download_btn, gas_btns],
    className="section-header"
)


@callback(Output("pollutants", "children"), Input("selected-station", "value"))
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


layout = html.Div(
    header,
    className="section")
