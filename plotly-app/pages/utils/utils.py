import pandas as pd
import os

# paths relative to THIS script
FBK_FILE_PATH = "../../../FBK data/data_fbk_from_db.csv"
APPA_FILE_PATH = "../../data/21_22_APPA.csv"
PREDICTION_FILE_PATH = "../../data/appa1_predictions.csv"


def filter_fbk_data(dataframe: pd.DataFrame, df_sensor) -> pd.DataFrame:
    """
    Filters the data given as input

    Args:
        dataframe (pd.DataFrame): the starting dataframe

    Returns:
        pd.DataFrame: the filtered dataframe
    """
    #dataframe = dataframe.drop(
    #    ["node_name", "g", "h", "th", "cfg", "iaq", "co2", "voc", "iac_comp"], axis=1
    #)
    dataframe["ts"] = pd.to_datetime(dataframe["ts"], utc=True)
    # Set CEST Summer time zone
    dataframe["ts"] += pd.Timedelta(hours=2)
    dataframe["signal_res"] = dataframe["signal_res"].astype(float)
    dataframe["heater_res"] = dataframe["heater_res"].astype(float)
    dataframe["volt"] = dataframe["volt"].astype(float)
    dataframe["p"] = dataframe["p"].astype(float)
    dataframe["t"] = dataframe["t"].astype(float)
    dataframe["rh"] = dataframe["rh"].astype(float)
    
    #dataframe["sensor_description"] = (
    #    dataframe["sensor_description"].str.split(pat="_").str.get(0)
    #)
    #print(df_sensor.loc[2]["description"])
    #dataframe["sensor_description"] = (
    #    dataframe["sensor_description"].astype(str) + df_sensor.loc[int(dataframe["sensor_description"])]["description"].str.split(pat="_").str.get(0)
    #)
    #for index, row in dataframe.iterrows():
    #    dataframe.loc[index]["sensor_description"] = df_sensor.loc[int(row["sensor_description"])] ["description"]
    
    #if dataframe["sensor_description"].dtypes == "int64":
    dataframe['sensor_description'] = dataframe.apply (lambda row: str(row['sensor_description'])+'_'+df_sensor.loc[int(row["sensor_description"])]["description"].split("_")[0] , axis=1)
    
    dataframe.drop_duplicates(["sensor_description", "ts"], inplace=True)

    dataframe["node_description"] = dataframe["node_description"].str.replace(
        "Appa 1 - ", ""
    )
    dataframe["node_description"] = dataframe["node_description"].str.replace(
        "Appa 2 - ", ""
    )
    #print(dataframe)
    return dataframe


def get_fbk_data() -> pd.DataFrame:
    """
    Fetches the fbk local csv, filters it and returns it

    Returns:
        pd.DataFrame: the dataframe
    """
    dataframe = pd.read_csv(
        os.path.join(os.path.dirname(__file__), FBK_FILE_PATH), encoding="windows-1252"
    )

    dataframe = filter_fbk_data(dataframe)
    # Drop FBK csv column
    return dataframe.drop(["Unnamed: 0"], axis=1)


def get_appa_data() -> pd.DataFrame:
    """
    Fetches the local APPA data

    Returns:
        pd.DataFrame: the dataframe
    """
    return pd.read_csv(
        os.path.join(os.path.dirname(__file__), APPA_FILE_PATH), encoding="windows-1252"
    )


def get_prediction_data() -> pd.DataFrame:
    """
    Fetches the local prediction

    Returns:
        pd.DataFrame: the dataframe
    """
    return pd.read_csv(
        os.path.join(os.path.dirname(__file__), PREDICTION_FILE_PATH),
        encoding="windows-1252",
    )
