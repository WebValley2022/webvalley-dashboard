import random
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
from db_utils import load_data_from_psql
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np


dash.register_page(__name__, path="/disclaimer")
description_box = html.Div(id="description-box", className="description-box")

# rand = random.seed(57)
periods = ["last 6 months", "last month", "last week", "last day", "last hour"]
stations = ["Trento - via Bolzano", "Trento - S. Chiara"]
station_labels_to_df_keys = {
    "Trento - via Bolzano": "Via Bolzano",
    "Trento - S. Chiara": "Parco S. Chiara",
}

points = {
    (11.11022, 46.10433): "Trento - via Bolzano",
    (11.1262, 46.06292): "Trento - S. Chiara",
}
pollutants = [
    dict(label="Nitrogen Dioxide", value="NO2"),
    dict(label="Ozone", value="O3"),
    dict(label="Carbon Monoxide", value="CO"),
    dict(label="Particulate Matter 2.5", value="PM2.5"),
    dict(label="Particulate Matter 10", value="PM10"),
]
df = load_data_from_psql(
    """select stazione, inquinante, ts, valore from 
    appa_data where ts >= NOW() - interval '7 day';"""
)

df_s_p = df.sort_values(["stazione", "inquinante", "ts"]).set_index(
    ["stazione", "inquinante"]
)

pollutants_bars = html.Div(
    [
        html.Div(
            [
                html.Div(
                    "NO2 | value: 0/410 µg/m³", id="no2-label", className="progress-label", style={"fontSize": "1.35rem"}
                ),
                dbc.Progress(
                    id="no2-progress",
                    max=410,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
        html.Div(
            [
                html.Div(
                    "O3 | value: 0/250 µg/m³", id="o3-label", className="progress-label", style={"fontSize": "1.35rem"}
                ),
                dbc.Progress(
                    id="o3-progress",
                    max=250,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
        html.Div(
            [
                html.Div(
                    "CO | value: 0/30 µg/m³", id="co-label", className="progress-label", style={"fontSize": "1.35rem"}
                ),
                dbc.Progress(
                    id="co-progress",
                    max=30,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
    ],
    className="post-box",
)

pm_bars = html.Div(
    [
        html.Div(
            [
                html.Div(
                    "PM 2.5 | value: 0/45 µg/m³", id="pm2_5-label", className="progress-label", style={"fontSize": "1.35rem"}
                ),
                dbc.Progress(
                    id="pm2_5-progress",
                    max=45,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
        html.Div(
            [
                html.Div(
                    "PM 10 | value: 0/110 µg/m³", id="pm10-label", className="progress-label", style={"fontSize": "1.35rem"}
                ),
                dbc.Progress(
                    id="pm10-progress",
                    max=110,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
    ],
    className="post-box",
)

wd_bars = html.Div(
    [
        html.Div(
            [
                html.Div(
                    "Temperature",
                    className="progress-label",
                    style={"fontSize": "1.35rem"},
                ),
                dbc.Progress(
                    id="temp-progress",
                    max=100,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
        html.Div(
            [
                html.Div(
                    "Humidity",
                    className="progress-label",
                    style={"fontSize": "1.35rem"},
                ),
                dbc.Progress(
                    id="rh-progress",
                    max=100,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
        html.Div(
            [
                html.Div(
                    "Pressure",
                    className="progress-label",
                    style={"fontSize": "1.35rem"},
                ),
                dbc.Progress(
                    id="press-progress",
                    max=100,
                    striped=True,
                    animated=True,
                ),
            ],
            className="progress-container",
        ),
    ],
    className="post-box",
)

toast_descriptions = {
    "pollutants": """
            The main monitored gasses are Nitrogen oxides (NO2), Ozone (O3) and Carbon Oxide (CO).
            Nitrogen oxides are commonly produced by fuel combustion and a long term exposure to a high
            concentration of this gas can be dangerous. Carbon oxide is also produced by combustion but
            it is odorless and more toxic gas. Ozone is formed through a reaction with gases in presence
            of sunlight, so it is more common to find it during sunny days.
            """,
    "particulate_matter": """
            Particulate Matter, usually referred as PM followed by a number indicating the
            size of the particulate (e.g. PM10 and PM2.5), is a very common and meaningful
            indicator of air quality, as there is a strong evidence of negative health impact
            associated with the exposure of high concentration of PM. Usually PM are produced by
            combustion and its main components are sulfates, nitrates or black carbon, among others.
            """,
    "weather_data": """
            Temperature, Humidity and Pressure come
            from wheater stations. They are essential to understand
            patterns and correlations with changes in air quality.
            """,
}

descriptions = {
    "NO2": "Nitrogen dioxide, commonly known as NO2, is an important air pollutant that significantly affects both air quality and global warming. It is primarily produced by the combustion of fossil fuels and certain industrial processes. Understanding the effects of NO2 is crucial for addressing air pollution and mitigating climate change.\n\n"
    "NO2 is a harmful gas that contributes to the formation of smog and poor air quality. It is a key component of photochemical smog, which forms when sunlight interacts with pollutants in the atmosphere. High concentrations of NO2 are often found in urban areas with heavy traffic and industrial activities.\n\n"
    "Inhaling NO2 can have adverse effects on human health, particularly affecting the respiratory system. It can irritate the respiratory tract, leading to respiratory symptoms such as coughing, wheezing, and shortness of breath. Prolonged exposure to high levels of NO2 may also aggravate respiratory conditions such as asthma and increase the risk of respiratory infections.",
    "O3": "Ozone, often referred to as O3, is an essential component of the Earth's atmosphere. While ozone in the upper atmosphere plays a critical role in protecting life on Earth by filtering harmful ultraviolet (UV) radiation, its presence at ground level can have detrimental effects on both air quality and global warming.\n\n"
    "At ground level, ozone is considered a harmful air pollutant and a key component of smog. It is formed when nitrogen oxides (NOx) and volatile organic compounds (VOCs) react in the presence of sunlight. Ozone levels tend to be higher in urban and industrial areas where emissions from vehicles, industrial processes, and certain chemicals are more prevalent.\n\n"
    "Breathing ozone can have adverse effects on human health, particularly for sensitive groups such as children, the elderly, and individuals with respiratory conditions. It can lead to respiratory symptoms, including coughing, throat irritation, and reduced lung function. Prolonged exposure to high ozone levels may also exacerbate asthma and other respiratory diseases.",
    "CO": "Carbon monoxide (CO) is a colorless, odorless gas that is released into the atmosphere through various natural and human activities. Although it is a natural component of the Earth's carbon cycle, excessive amounts of CO can have significant implications for air quality and global warming.\n\n"
    "CO is one of the primary contributors to air pollution, especially in urban areas. It is released during the incomplete combustion of fossil fuels from sources such as vehicles, power plants, and industrial processes. Accumulation of CO in the lower atmosphere contributes to the formation of smog and the degradation of air quality.\n\n"
    "Inhaling high levels of CO can be harmful to human health. It reduces the oxygen-carrying capacity of blood, leading to fatigue, dizziness, and, at extremely high concentrations, even death. People with cardiovascular diseases, infants, and the elderly are particularly vulnerable.",
    "PM2.5": "Particulate Matter (PM2.5) is a critical air pollutant that significantly affects air quality and contributes to global warming. It refers to fine particles with a diameter of 2.5 micrometers or smaller, which are small enough to be inhaled deep into the lungs. Understanding the effects of PM2.5 is crucial for addressing air pollution and mitigating climate change.\n\n"
    "PM2.5 poses significant risks to human health and the environment. These tiny particles can penetrate deep into the respiratory system, bypassing the body's natural defenses, and enterthe bloodstream. Prolonged exposure to PM2.5 has been linked to respiratory and cardiovascular diseases, such as asthma, bronchitis, heart attacks, and even premature death. People with pre-existing respiratory or cardiovascular conditions, children, and the elderly are particularly vulnerable.\n\n"
    "Moreover, PM2.5 can impair visibility, leading to haze and reduced air clarity. It also contributes to the formation of smog, which is a mixture of pollutants that can negatively impact air quality in urban areas.",
    "PM10": "Particulate Matter (PM10) is a significant air pollutant that greatly affects air quality and contributes to global warming. It refers to airborne particles with a diameter of 10 micrometers or smaller, which can be inhaled into the respiratory system. Understanding the effects of PM10 is crucial for addressing air pollution and mitigating climate change.\n\n"
    "PM10 particles have various detrimental effects on human health and the environment. When inhaled, these particles can penetrate the respiratory system and cause or worsen respiratory conditions, such as asthma, bronchitis, and allergies. Prolonged exposure to PM10 can lead to reduced lung function, cardiovascular issues, and increased risk of respiratory infections.\n\n"
    "Additionally, PM10 particles can contribute to reduced visibility by scattering and absorbing light. This results in hazy conditions and decreased visual range, impacting the overall air quality and aesthetic appeal of the surroundings.",
    "SO2": "Sulfur dioxide (SO2) is an important air pollutant that significantly affects air quality and contributes to global warming.\n\n"
    "It is primarily emitted by the burning of fossil fuels, especially coal and oil.\n\n"
    "Understanding the effects of SO2 is crucial for addressing air pollution and mitigating climate change.\n\n"
    "SO2 is a harmful gas that can have detrimental effects on both human health and the environment.\n\n"
    "When released into the atmosphere, SO2 reacts with other pollutants and moisture to form sulfate particles.\n\n"
    "These particles contribute to the formation of fine particulate matter (PM2.5), which can be inhaled deep into the lungs and cause various respiratory and cardiovascular problems.\n\n"
    "In addition to its direct health effects, SO2 also contributes to the formation of acid rain.\n\n"
    "When SO2 reacts with moisture in the atmosphere, it forms sulfuric acid, which can fall back to the Earth's surface as acid rain.\n\n"
    "Acid rain can harm ecosystems, damage crops and forests, and degrade buildings and infrastructure.",
}

# Define the available pollutants for each location
available_pollutants = {
    "Trento - via Bolzano": ["CO", "NO2", "PM10"],
    "Trento - S. Chiara": ["NO2", "O3", "PM2.5", "PM10"],
}

# Define the dropdown for selecting the location
location_dropdown = dcc.Dropdown(
    options=[{"label": station, "value": station} for station in stations],
    id="location-dropdown",
    value="Trento - via Bolzano",
    className="dropdown",
)

# Define the buttons for selecting the pollutants
radio_btns = html.Div(
    dbc.RadioItems(
        id="selected-fbk-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=available_pollutants,
        value="NO2",
    ),
    className="radio-group",
)


popup_menus = {
    "pollutants": dbc.Modal(
        [
            dbc.ModalHeader("Gas pollutants", style={"fontSize": "4rem"}),
            dbc.ModalBody(toast_descriptions["pollutants"], style={"fontSize": "1.8rem"}),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="close-popup-no2",
                    className="ml-auto",
                    n_clicks=0,
                    style={"fontSize": "2.5rem"},
                )
            ),
        ],
        id="popup-menu-no2",
        size="lg",
    ),
    "particulate_matter": dbc.Modal(
        [
            dbc.ModalHeader("Particulate matter", style={"fontSize": "4rem"}),
            dbc.ModalBody(
                toast_descriptions["particulate_matter"], style={"fontSize": "1.8rem"}
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="close-popup-o3",
                    className="ml-auto",
                    n_clicks=0,
                    style={"fontSize": "2.5rem"},
                )
            ),
        ],
        id="popup-menu-o3",
        size="lg",
    ),
    "weather_data": dbc.Modal(
        [
            dbc.ModalHeader("Weather data", style={"fontSize": "4rem"}),
            dbc.ModalBody(
                toast_descriptions["weather_data"], style={"fontSize": "1.8rem"}
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="close-popup-co",
                    className="ml-auto",
                    n_clicks=0,
                    style={"fontSize": "2.5rem"},
                )
            ),
        ],
        id="popup-menu-co",
        size="lg",
    ),
}

info_icons = {
    "pollutants": html.Div(
        [
            dbc.Tooltip(
                "Click for more info",
                target="info-icon-no2",
            ),
            html.I(
                className="fa-solid fa-info-circle",
                id="info-icon-no2",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
        ],
        className="info-icon-container",
    ),
    "particulate_matter": html.Div(
        [
            dbc.Tooltip(
                "Click for more info",
                target="info-icon-o3",
            ),
            html.I(
                className="fa-solid fa-info-circle",
                id="info-icon-o3",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
        ],
        className="info-icon-container",
    ),
    "weather_data": html.Div(
        [
            dbc.Tooltip(
                "Click for more info",
                target="info-icon-co",
            ),
            html.I(
                className="fa-solid fa-info-circle",
                id="info-icon-co",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
        ],
        className="info-icon-container",
    ),
}

toast_p = dbc.Toast(
    [pollutants_bars],
    id="pl_toast",
    header=[
        dbc.Row(
            [
                dbc.Col(
                    html.H4(["Gas Pollutants (last 24 hrs avg)"], className="section-header"),
                    width=10,
                ),
                dbc.Col(
                    html.H4([info_icons["pollutants"]], className="section-header"),
                    width={"size": 1, "offset": 1},
                ),
            ],
            style={"": ""},
        )
    ],
    style={"height": "100%"},
)

toast_pm = dbc.Toast(
    [pm_bars,],
    id="pm_toast",
    header=[
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        ["Particulate Matter (last 24 hrs avg)"],
                        className="section-header",
                    ),
                    width=11,
                ),
                dbc.Col(
                    html.H4(
                        [info_icons["particulate_matter"]],
                        className="section-header",
                    ),
                    width=1,
                ),
            ]
        ),
    ],
    style={"height": "100%"},
)

toast_wd = dbc.Toast(
    [wd_bars,],
    id="wd_toast",
    header=[
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        ["Weather Data (last 24 hrs avg)"],
                        className="section-header",
                    ),
                    width=11,
                ),
                dbc.Col(
                    html.H4(
                        [info_icons["weather_data"]],
                        className="section-header",
                    ),
                    width=1,
                ),
            ]
        )
    ],
    style={"height": "100%"},
)




layout = html.Div(
    children=[
        html.Label("Select location: ", style={"fontSize": "1.5rem"}),
        dcc.Dropdown(
            options=[{"label": station, "value": station} for station in stations],
            id="location-dropdown",
            value="Trento - via Bolzano",
            className="dropdown",
            style={"maxWidth": "50rem"},
        ),
        radio_btns,
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Row(
                                [toast_p, html.Br()], className="vertical-spacing"
                            ),
                            dbc.Row(
                                [toast_pm, html.Br()], className="vertical-spacing"
                            ),
                            #dbc.Row(
                            #    [toast_wd, html.Br()], className="vertical-spacing"
                            #),
                        ],
                    ),
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="pollutant-graph",
                            config={"displayModeBar": True},
                            className="pretty_container",
                            style={"margin": "4rem"},
                        ),
                        description_box,
                    ],
                    width=9,
                ),
            ],
            className="graph-container",
        ),
        popup_menus["pollutants"],
        popup_menus["particulate_matter"],
        popup_menus["weather_data"],
    ],
)


# @callback(
#     Output("no2-progress", "color"),
#     Output("o3-progress", "color"),
#     Output("co-progress", "color"),
#     Input("no2-progress", "value"),
#     Input("o3-progress", "value"),
#     Input("co-progress", "value"),
# )
# def update_progress_colors(no2_value, o3_value, co2_value):
#     no2_color = determine_color(no2_value)
#     o3_color = determine_color(o3_value)
#     co2_color = determine_color(co2_value)
#     return no2_color, o3_color, co2_color


# def determine_color(value):
#     if value <= 30:
#         return "success"  # Green color for values <= 30
#     elif value <= 70:
#         return "warning"  # Yellow color for values between 30 and 70
#     else:
#         return "danger"  # Red color for values > 70


@callback(
    Output("popup-menu-no2", "is_open"),
    [Input("info-icon-no2", "n_clicks"),
     Input("close-popup-no2", "n_clicks")],
    [State("popup-menu-no2", "is_open")],
)
def toggle_popup_no2(n_clicks_open, n_clicks_close, is_open):
    if n_clicks_open or n_clicks_close:
        return not is_open
    return is_open

@callback(
    Output("popup-menu-o3", "is_open"),
    [Input("info-icon-o3", "n_clicks"),
     Input("close-popup-o3", "n_clicks")],
    [State("popup-menu-o3", "is_open")],
)
def toggle_popup_o3(n_clicks_open, n_clicks_close, is_open):
    if n_clicks_open or n_clicks_close:
        return not is_open
    return is_open

@callback(
    Output("description-box", "children"), [Input("selected-fbk-pollutant", "value")]
)
def update_description_box(selected_pollutant):
    return descriptions[selected_pollutant]

@callback(
    Output("selected-fbk-pollutant", "options"), [Input("location-dropdown", "value")]
)
def update_pollutant_buttons(selected_location):
    pollutants = available_pollutants.get(selected_location, [])
    options = [{"label": pollutant, "value": pollutant} for pollutant in pollutants]
    return options


"""@callback(
    Output("popup-menu-co", "is_open"),
    [Input("info-icon-co", "n_clicks"),
     Input("close-popup-co", "n_clicks")],
    [State("popup-menu-co", "is_open")],
)
def toggle_popup_co(n_clicks_open, n_clicks_close, is_open):
    if n_clicks_open or n_clicks_close:
        return not is_open
    return is_open"""


@callback(
    Output("pollutant-graph", "figure"),
    [Input("selected-fbk-pollutant", "value"), Input("location-dropdown", "value")],
)
def update_pollutant_graph(selected_pollutant, selected_location):
    # Generate some sample data
    station_df_key = station_labels_to_df_keys[selected_location]
    df_graph = df_s_p.loc[(station_df_key, selected_pollutant)]

    x = df_graph.ts
    y = df_graph.valore

    # Create a Plotly figure
    figure = go.Figure(data=go.Scatter(x=x, y=y, mode="lines+markers"))

    # Set the graph title and axes labels
    figure.update_layout(
        title=f"{selected_pollutant} Levels at {selected_location}",
        xaxis_title="Time",
        yaxis_title=f"{selected_pollutant} Levels",
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        legend={
            "bgcolor": "rgba(0,0,0,0)",
        },
        modebar=dict(bgcolor="#ffffff"),
    )
    figure.update_xaxes(
        title_font_size=12,
        showgrid=True,
        gridcolor="rgb(237, 232, 232)",
        gridwidth=0.5,
    )

    return figure


# Define the function to calculate the initial value for NO2
@callback(
    [Output("no2-progress", "value"),
     Output("no2-label", "children")],
    Input("location-dropdown", "value"),
)
def no2_value(selected_location):
    # Perform calculations or retrieve the initial value dynamically
    if pollutants[0]["value"] in available_pollutants[selected_location]:
        station_df_key = station_labels_to_df_keys[selected_location]
        df_graph = df_s_p.loc[(station_df_key, pollutants[0]["value"])]
        return df_graph.valore.mean(), f"NO2 | value: {df_graph.valore.mean().round()}/410 µg/m³"
    else:
        return 0, f"NO2 -> not measured"



@callback(
    [Output("o3-progress", "value"),
     Output("o3-label", "children")],
     Input("location-dropdown", "value"),
)
def o3_value(selected_location):
    # Perform calculations or retrieve the initial value dynamically
    if pollutants[1]["value"] in available_pollutants[selected_location]:
        station_df_key = station_labels_to_df_keys[selected_location]
        df_graph = df_s_p.loc[(station_df_key, pollutants[1]["value"])]
        return df_graph.valore.mean(), f"O3 | value: {df_graph.valore.mean().round()}/250 µg/m³"
    else:
        return 0, f"O3 -> not measured"


@callback(
    [Output("co-progress", "value"),
    Output("co-label", "children")],
    Input("location-dropdown", "value"),
)
def co_value(selected_location):
    # Perform calculations or retrieve the initial value dynamically
    if pollutants[2]["value"] in available_pollutants[selected_location]:
        station_df_key = station_labels_to_df_keys[selected_location]
        df_graph = df_s_p.loc[(station_df_key, pollutants[2]["value"])]
        return df_graph.valore.mean(), f"CO | value: {df_graph.valore.mean().round()}/30 µg/m³"
    else:
        return 0, f"CO -> not measured"


@callback(
    [Output("pm2_5-progress", "value"),
    Output("pm2_5-label", "children")],
    Input("location-dropdown", "value"),
)
def pm25_value(selected_location):
    # Perform calculations or retrieve the initial value dynamically
    if pollutants[3]["value"] in available_pollutants[selected_location]:
        station_df_key = station_labels_to_df_keys[selected_location]
        df_graph = df_s_p.loc[(station_df_key, pollutants[3]["value"])]
        return df_graph.valore.mean(), f"PM 2.5 | value: {df_graph.valore.mean().round()}/45 µg/m³"
    else:
        return 0, f"PM 2.5 -> not measured"


@callback(
    [Output("pm10-progress", "value"),
    Output("pm10-label", "children")],
    Input("location-dropdown", "value"),
)
def pm10_value(selected_location):
    # Perform calculations or retrieve the initial value dynamically
    if pollutants[4]["value"] in available_pollutants[selected_location]:
        station_df_key = station_labels_to_df_keys[selected_location]
        df_graph = df_s_p.loc[(station_df_key, pollutants[4]["value"])]
        return df_graph.valore.mean(), f"PM 10 | value: {df_graph.valore.mean().round()}/110 µg/m³"
    else:
        return 0, f"PM 10 -> not measured"


"""@callback(
    Output("temp-progress", "value"),
    Input("location-dropdown", "value"),
)
def temp_value(selected_location):
    station_df_key = station_labels_to_df_keys[selected_location]
    df_graph = df_s_p.loc[(station_df_key, pollutants[0]["value"])]
    return df_graph.valore.mean() + random.randint(5, 20)


@callback(
    Output("rh-progress", "value"),
    Input("location-dropdown", "value"),
)
def rh_value(selected_location):
    station_df_key = station_labels_to_df_keys[selected_location]
    df_graph = df_s_p.loc[(station_df_key, pollutants[1]["value"])]
    return df_graph.valore.mean() + random.randint(5, 20)


@callback(
    Output("press-progress", "value"),
    [Input("selected-fbk-pollutant", "value"),
     Input("location-dropdown", "value")],
)
def press_value(selected_pollutant, selected_location):
    station_df_key = station_labels_to_df_keys[selected_location]
    df_graph = df_s_p.loc[(station_df_key, pollutants[3]["value"])]
    return df_graph.valore.mean() + random.randint(5, 20)
"""