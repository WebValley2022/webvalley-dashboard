
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
        color = "pollutant",
        markers = True
    )

    previs = px.line(
        data_previs,
        x = "date",
        y = "value",
        color = "pollutant",
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


