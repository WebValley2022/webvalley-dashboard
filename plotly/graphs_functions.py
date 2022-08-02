import plotly
import plotly.graph_objs as go
import datetime as dt
import pandas as pd

#####################
#  UTILS FUNCTIONS  #
#####################

pollutant_limit = {
    "Ossido di Carbonio": 10, # daily mean maximum, correct
    "Biossido di Azoto": 200, # daily mean mixxing, used hour, incorrect, aprroximated
    "Biossido Zolfo": 125,    # daily mean maximum, correct
    "Ozono": 120,             # daily mean maximum, correct
    "PM10": 50,               # daily mean maximum, correct
    "PM2.5": 25               # daily mean missing, used year, incorrect, approximated
}

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
        (dataframe["station"] == station) &
        (dataframe["pollutant"] == pollutant)
    ].groupby(
        by = pd.Grouper(
            key  = "date",
            freq = time_span
        )
    ).mean()
    mean_temp.insert(1, "pollutant", pollutant)
    mean_temp.insert(1, "station", station)
    mean_temp.reset_index(inplace = True)
    
    return mean_temp

def get_percentage(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the percentage of the value of each pollutant
    of the maximum legal level

    Args:
        dataframe (pd.DataFrame): the input dataframe

    Returns:
        pd.DataFrame: the processed dataframe
    """

    percentage_df = dataframe.copy()

    val = percentage_df["value"]
    pol = percentage_df["pollutant"]
    for i in range(len(percentage_df)):
        percentage_df.loc[i, "value"] = val[i]/pollutant_limit[pol[i]]

    return percentage_df

###########################################
# MAIN DAILY GRAPH OF PERCENTAGE TO LIMIT #
###########################################

# VARIABLES NEEDED:
#   - past: dataframe with past pollutant records
#   - prevision: dataframe with prevision data (will be processed into prevision_data)
def update_daily_graph(station: str,  pollutant: str, time_span: str) -> plotly.graph_objs.Figure:
    """
    Updates the graph representing the daily trend
    of the given pollutant in the given station

    Args:
        station (str): the station to be displayed
        pollutant (str): the pollutant to be displayed
        time_span (str): values can be 'D': day, 'Y': year, 'H': hour

    Returns:
        plotly.graph_objs.Figure: the graph
    """
    fig = go.Figure()
    today = dt.date.today()

    past_data = get_percentage(
        get_mean(
            past,
            time_span,
            station,
            pollutant
        )
    )

    prevision_data = get_percentage(
        get_mean(
            prevision,
            time_span,
            station,
            pollutant
        )
    )

    # past data
    fig.add_trace(
        go.Scatter(
            x = past_data["date"],
            y = past_data["value"],
            mode = "lines+markers"
        )
    )

    # prevision_data
    fig.add_trace(
        go.Scatter(
            x = prevision_data["date"],
            y = prevision_data["value"],
            mode = "lines+markers",
            line = {"dash": "dash"}
        )
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

# VARIABLES NEEDED: VERIFIED_DATA  -> appa's certified data
#                   PREVISION_DATA -> FBK model's prediction 
def update_comparison_graph(
    station: str,
    pollutant: str,
    time_span: str,
    compare_APPA: bool
) -> plotly.graph_objs.Figure:
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

    prevision_data = get_mean(
        PREVISION_DATA,
        time_span,
        station,
        pollutant
    )

    fig.add_trace(
        go.Scatter(
            x = prevision_data["date"],
            y = prevision_data["value"],
            mode = "lines+markers"
        )
    )

    if compare_APPA:
        appa_data = get_mean(
            VERIFIED_DATA,
            time_span,
            station,
            pollutant
        )

        fig.add_trace(
            go.Scatter(
                x = appa_data["date"],
                y = appa_data["value"],
                mode = "lines+markers"
            )
        )

    return fig

########################################
# SECTION 2 GRAPH FOR POLLUTANT TRENDS #
########################################


