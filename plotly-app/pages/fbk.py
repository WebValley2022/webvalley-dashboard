from statistics import mean
from dash import html, dcc, Input, Output, callback
from .utils import utils, querys
from db_utils import load_data_from_psql
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd
import numpy as np
import dash
import joblib
from tensorflow.keras.models import load_model
from datetime import timedelta, datetime


dash.register_page(__name__)


def get_data_day(start, end) -> pd.DataFrame:
    print("NOT CACHED DAY")
    fbk_data=  load_data_from_psql(testnewdf(start, end))
    #print(fbk_data)
    return (fbk_data)

def testnewdf(start, end):
    
    return f"""WITH sensor_data AS (
    SELECT
        n.description AS node_description,
        s.name AS sensor_description,
        p.sensor_ts AS ts,
        pd.r1 AS heater_res,
        pd.r2 AS signal_res,
        pd.volt AS volt,
        p.attrs::json->>'P' AS p,
        p.attrs::json->>'T' AS t,
        p.attrs::json->>'RH' AS rh
    FROM packet_data pd
        LEFT JOIN packet p ON p.id = pd.packet_id
        LEFT JOIN sensor s ON s.id = pd.sensor_id
        LEFT JOIN node n ON n.id = p.node_id
    where p.sensor_ts BETWEEN '{start}' AND '{end}' and n.id = 1
)
SELECT
    ts,
    MAX(p) AS p,
    MAX(t) AS t,
    MAX(rh) AS rh,
    MAX(CASE WHEN sensor_description = 'S1_ID' THEN heater_res END) AS S1_R1,
    MAX(CASE WHEN sensor_description = 'S1_ID' THEN signal_res END) AS S1_R2,
    MAX(CASE WHEN sensor_description = 'S1_ID' THEN volt END) AS S1_Voltage,
    MAX(CASE WHEN sensor_description = 'S2_ID' THEN heater_res END) AS S2_R1,
    MAX(CASE WHEN sensor_description = 'S2_ID' THEN signal_res END) AS S2_R2,
    MAX(CASE WHEN sensor_description = 'S2_ID' THEN volt END) AS S2_Voltage,
    MAX(CASE WHEN sensor_description = 'S3_ID' THEN heater_res END) AS S3_R1,
    MAX(CASE WHEN sensor_description = 'S3_ID' THEN signal_res END) AS S3_R2,
    MAX(CASE WHEN sensor_description = 'S3_ID' THEN volt END) AS S3_Voltage,
    MAX(CASE WHEN sensor_description = 'S4_ID' THEN heater_res END) AS S4_R1,
    MAX(CASE WHEN sensor_description = 'S4_ID' THEN signal_res END) AS S4_R2,
    MAX(CASE WHEN sensor_description = 'S4_ID' THEN volt END) AS S4_Voltage,
    MAX(CASE WHEN sensor_description = 'S5_ID' THEN heater_res END) AS S5_R1,
    MAX(CASE WHEN sensor_description = 'S5_ID' THEN signal_res END) AS S5_R2,
    MAX(CASE WHEN sensor_description = 'S5_ID' THEN volt END) AS S5_Voltage,
    MAX(CASE WHEN sensor_description = 'S6_ID' THEN heater_res END) AS S6_R1,
    MAX(CASE WHEN sensor_description = 'S6_ID' THEN signal_res END) AS S6_R2,
    MAX(CASE WHEN sensor_description = 'S6_ID' THEN volt END) AS S6_Voltage,
    MAX(CASE WHEN sensor_description = 'S7_ID' THEN heater_res END) AS S7_R1,
    MAX(CASE WHEN sensor_description = 'S7_ID' THEN signal_res END) AS S7_R2,
    MAX(CASE WHEN sensor_description = 'S7_ID' THEN volt END) AS S7_Voltage,
    MAX(CASE WHEN sensor_description = 'S8_ID' THEN heater_res END) AS S8_R1,
    MAX(CASE WHEN sensor_description = 'S8_ID' THEN signal_res END) AS S8_R2,
    MAX(CASE WHEN sensor_description = 'S8_ID' THEN volt END) AS S8_Voltage
FROM sensor_data
GROUP BY ts
ORDER BY ts;"""
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  





pipeline2 = joblib.load('data/pipeline.pkl')

# Load the Keras model separately

model = load_model('data/model.h5')
#predictions = inference_func(input_data)['output'].numpy()

# Assign the loaded model to the pipeline
pipeline2.steps[-1][1].model = model

print(pipeline2.steps[-1][1].model)

pipeline2.steps[-1][1].model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_squared_error'])






df = utils.get_prediction_data()
df["Time"] = pd.to_datetime(df["Time"])

# add static station to simulate query
df["Station"] = "Parco S. Chiara"

# add random noise to dataframe
df["NO2_pred"] += np.random.rand(len(df)) * 10 - 5
df["CO_pred"] += np.random.rand(len(df)) - 0.5
df["O3_pred"] += np.random.rand(len(df)) * 10 - 5


fbk_stations = ["Parco S. Chiara", "Via Bolzano"]
pollutants = [
    dict(label="Ozone", value="O3"),
    dict(label="Nitrogen Dioxide", value="NO2"),
    dict(label="PM10", value="PM10"),
    dict(label="Sulfur Dioxide", value="SO2"),
]

title = html.Div("Fitted FBK Data", className="header-title")

# build dropdown of stations
dropdown = dcc.Dropdown(
    fbk_stations, id="selected-station", className="dropdown", value=fbk_stations[0]
)

download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    id="btn_fbk_fitted",
    class_name="download-btn",
)
download_it = dcc.Download(id="download-fbk-fitted")


@callback(
    Output("download-fbk-fitted", "data"),
    Input("btn_fbk_fitted", "n_clicks"),
    prevent_initial_call=True,
)
def create_download_file(n_clicks):
    global df
    return dcc.send_data_frame(df.to_csv, "fbk_fitted_data.csv")


# build gas buttons
gas_btns = html.Div(
    dbc.RadioItems(
        id="selected-fbk-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants,
        value="O3",
    ),
    className="radio-group",
)

header = html.Div(
    [title, dropdown, download_btn, download_it, gas_btns], className="section-header"
)

graph_selectors = html.Div(
    [
        html.Div(
            [
                "Display: ",
                dcc.Dropdown(
                    id="selected-period",
                    options=["March","April", "May", "June", "July"],
                    className="dropdown",
                    value="April",
                ),
            ],
            className="graph-dropdown",
        ),
        daq.ToggleSwitch(
            id="toggle-comparison",
            label="Compare with APPA",
            color="#0d6efd",
            className="ml-auto toggle",
            value=True,
        ),
    ],
    className="d-flex flex-grow justify-content-between",
)

comparison_graph = html.Div(
    [
        dcc.Graph(
            id="comparison-graph",
            style=dict(height="50vh"),
            config={
                "displayModeBar": False,
                "displaylogo": False,
            },
        ),
        graph_selectors,
        dcc.Graph(
            id="test-graph",
            style=dict(height="50vh"),
        ),
    ]
)


@callback(
    Output("comparison-graph", "figure"),
    Input("selected-station", "value"),
    Input("selected-fbk-pollutant", "value"),
    Input("toggle-comparison", "value"),
    Input("selected-period", "value"),
)
def update_comparison_graph(
    selected_station: str,
    selected_pollutant: str,
    toggle_comparison: str,
    selected_period: str,
) -> go.Figure:
    """
    Updates the graph representing the comparison between
    APPA data and model prediction

    Args:
        slected_station (str): station name
        selected_pollutant (str): pollutant name
        selected_period (str): H: hour; D: day; W: week; M: month; Y: year
        toggle_comparison (bool): wether to add a line of APPA"s data or not

    Returns:
        plotly.graph_objs.Figure: the graph
    """

    
    months= {
    'January': ('2023-01-01', '2023-01-31'),
    'February': ('2023-02-01', '2023-02-28'),
    'March': ('2023-03-01', '2023-03-31'),
    'April': ('2023-04-01', '2023-04-30'),
    'May': ('2023-05-01', '2023-05-31'),
    'June': ('2023-06-01', '2023-06-30'),
    'July': ('2023-07-01', '2023-07-31'),
    'August': ('2023-08-01', '2023-08-31'),
    'September': ('2023-09-01', '2023-09-30'),
    'October': ('2023-10-01', '2023-10-31'),
    'November': ('2023-11-01', '2023-11-30'),
    'December': ('2023-12-01', '2023-12-31')
    }
    start = months[selected_period][0]
    end = months[selected_period][1]
    
    raw_data = get_data_day(start, end)
    
    utc_now = datetime.utcnow()
    asd = datetime.now() - utc_now
    raw_data['ts'] = raw_data['ts'] + asd
    test = raw_data.drop('ts',axis=1)
    
    y_pred=pipeline2.predict(test.values)

    appa_data = load_data_from_psql(querys.q_custom_appa(start=start, end=end))
    
    fig = go.Figure()
    
    new_df = pd.DataFrame()
    new_df['ts'] = raw_data['ts'].copy()

    new_df['O3'] = y_pred[:,3].tolist()
    new_df['PM10'] = y_pred[:,0].tolist()
    new_df['NO2'] = y_pred[:,1].tolist()
    new_df['SO2'] = y_pred[:,2].tolist()
    
    
    new_df= new_df.set_index('ts').resample('1H').mean().reset_index()
    data = appa_data[(appa_data['stazione'] == 'Parco S. Chiara') & (appa_data['inquinante'] == selected_pollutant) & (['avg'])] 
    df = new_df.merge(data[['min','avg']], left_on='ts', right_on='min', how="left").drop('min',axis=1)
    
    fig.add_trace(
        go.Scatter(
            x=df["ts"], y=df[selected_pollutant], mode="lines+markers", name="FBK"
        )
    )

    title = "Pollutant concentration prediction"

    if toggle_comparison:
        # appa data graph
        fig.add_trace(
            go.Scatter(
                x=df["ts"],
                y=df['avg'],
                mode="lines+markers",
                name="APPA",
            )
        )

        title += " compared to APPA readings"

    fig.update_layout(
        margin=dict(l=5, r=5, t=20, b=0),
        plot_bgcolor="white",
        title=dict(
            x=0.5,
            text=title,
            font_family="Sans serif",
            xanchor="center",
            yanchor="top",
        ),
    )
    fig.update_yaxes(title_text="Value", fixedrange=True)

    return fig


def get_mean(
    dataframe: pd.DataFrame, station: str, selected_pollutant: str, selected_period
) -> pd.DataFrame:
    """
    Gets the mean of a given time span from the given station
    and pollutant in the given dataframe

    Args:
        dataframe (pd.DataFrame): the input dataframe to be processed
        station (str): the station where to get the data
        selected_pollutant (str): the desired pollutant
        selected_period (str): values can be "D": day, "W": week, "Y": year, "H": hour

    Returns:
        pd.DataFrame: the dataframe with the mean values
    """
    pollutants = {"Biossido di Azoto": "NO2", "Ozono": "O3", "Ossido di Carbonio": "CO"}

    pollutant_real = selected_pollutant + "_real"
    pollutant_pred = selected_pollutant + "_pred"

    # filter station
    mean_temp = dataframe[dataframe.Station == station]
    # get sub-dataframe
    mean_temp = mean_temp[["Time", pollutant_real, pollutant_pred]]
    mean_temp.Time += pd.Timedelta(11, "D")

    # get the last date available
    last_day = mean_temp.Time.max()

    if selected_period == "last 24h":
        time_span = "H"
        mean_temp = mean_temp.tail(24)
    elif selected_period == "last week":
        time_span = "H"
        mean_temp = mean_temp.tail(168)
    elif selected_period == "last month":
        time_span = "D"
        mean_temp = mean_temp[
            (mean_temp.Time.dt.month == last_day.month)
            & (mean_temp.Time.dt.year == last_day.year)
        ]
    elif selected_period == "last year":
        time_span = "W"
        mean_temp = mean_temp[(mean_temp.Time.dt.year == last_day.year)]
    else:
        time_span = "W"

    mean_temp = mean_temp.groupby(by=pd.Grouper(key="Time", freq=time_span)).mean()
    # mean_temp.insert(1, "Inquinante", pollutant)
    # mean_temp.insert(1, "Stazione", station)
    mean_temp.reset_index(inplace=True)

    return mean_temp


layout = html.Div(
    [header, html.Div([comparison_graph], className="fbk-main-plot")],
    className="section fullHeight",
)
