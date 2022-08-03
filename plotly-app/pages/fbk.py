import dash
from dash import html, dcc, Input, Output, callback
import dash_daq as daq
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

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

comparison_graph = html.Div([dcc.Graph(id="comparison-graph"),
                            daq.ToggleSwitch(id="toggle-comparison",
                                             label="Compare with APPA",
                                             color="#0d6efd")])

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


@callback(Output("comparison-graph", "figure"),
          Input("selected-station", "value"),
          Input("selected-fbk-pollutant", "value"),
          Input("toggle-comparison", "value")
          )
def update_comparison_graph(
    selected_station,
    selected_pollutant,
    toggle_comparison,
):
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
        "w",
        selected_station,
        selected_pollutant
    )

    fig.add_trace(
        go.Scatter(
            x=estimated_data["Data"],
            y=estimated_data["Valore"],
            mode="lines+markers"
        )
    )

    if toggle_comparison:
        appa_data = get_mean(
            appa_df,
            'W',
            selected_station,
            selected_pollutant
        )

        fig.add_trace(
            go.Scatter(
                x=appa_data["Data"],
                y=appa_data["Valore"],
                mode="lines+markers"
            )
        )

    return fig


def get_mean(dataframe: pd.DataFrame, time_span: str, station: str, pollutant: str) -> pd.DataFrame:
    """
    Gets the mean of a given time span from the given station
    and pollutant in the given dataframe

    Args:
        dataframe (pd.DataFrame): the input dataframe to be processed
        time_span (str): values can be 'D': day, 'Y': year, 'H': hour
        station (str): the station where to get the data
        pollutant (str): the desired pollutant

    Returns:
        pd.DataFrame: the dataframe with the mean values
    """
    mean_temp = dataframe[
        (dataframe["Stazione"] == station) &
        (dataframe["Inquinante"] == pollutant)
    ].groupby(
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
