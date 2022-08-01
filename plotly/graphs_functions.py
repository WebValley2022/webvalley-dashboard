#####################
# NEEDED DATAFRAMES #
#####################

###########################################
# MAIN DAILY GRAPH OF PERCENTAGE TO LIMIT #
###########################################
@app.callback(
    Output('daily-percentage-graph', 'figure'),
    Input('radio-pollutant-selector', 'value')
)
def update_daily_graph(pollutant):
    # date used to separate data
    today = dt.date(2022, 7, 10)

    # condition <= in both so the chart will seem connected,
    # otherwhise there will be a hole in the data
    data_before = station_data_percentage[
        (station_data_percentage["station"] == SELECTED_STATION) &
        (station_data_percentage["pollutant"] == pollutant) &
        (station_data_percentage["date"] <= pd.to_datetime(today))
    ]
    data_previs = station_data_percentage[
        (station_data_percentage["station"] == SELECTED_STATION) &
        (station_data_percentage["pollutant"] == pollutant) &
        (station_data_percentage["date"] >= pd.to_datetime(today))
    ]
    
    before = px.line(
        data_before,
        x = "date",
        y = "value",
        markers = True
    )

    previs = px.line(
        data_previs,
        x = "date",
        y = "value",
        markers = True,
        line_dash_sequence = ["dash"]
    )

    fig = go.Figure(
        data = before.data + previs.data
    )
    # horizontal maximum line
    fig.add_hline(
        y = 1,
        line_color = "red",
        line_dash = "dash",
        annotation_text = "Threshold"
    )
    # vertical today line
    fig.add_vline(
        x = today,
        line_color = "green",
        line_dash = "dash"
    )
    return fig

####################
# SECTION 2 GRAPHS #
####################

# TODO: add callback
def update_comparison_graph(
    station: str,
    pollutant: str,
    time_span: int,
    compare_APPA: bool
):
    """
    Updates the graph representing the comparison between
    APPA data and model prediction

    Args:
        station (str): station name
        pollutant (str): pollutant name
        time_span (int): 0: hour; 1: day; 2: week; 3: month; 4: year
        compare_APPA (bool): wether to add a line of APPA's data or not
    """
    fig = go.Figure()
    prevision_data = data_before[
        (data_before["station"] == station) &
        (data_before["pollutant"] == pollutant)
    ]

    fig.add_trace(
        go.Scatter(
            x = prevision_data["date"],
            y = prevision_data["value"],
            mode = "lines+markers"
        )
    )

    if compare_APPA:
        appa_data = data_before[
            (data_before["station"] == station) &
            (data_before["pollutant"] == "PM2.5")
        ]

        fig.add_trace(
            go.Scatter(
                x = appa_data["date"],
                y = appa_data["value"],
                mode = "lines+markers"
            )
        )

    return fig


