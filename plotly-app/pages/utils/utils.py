import pandas as pd
import os

# paths relative to THIS script
FBK_FILE_PATH        = "../../../FBK data/data_fbk_from_db.csv"
APPA_FILE_PATH       = "../../data/21_22_APPA.csv"
PREDICTION_FILE_PATH = "../../data/appa1_predictions.csv"

def get_fbk_data() -> pd.DataFrame:
    """
    Fetches the fbk local csv, filters it and returns it

    Returns:
        pd.DataFrame: the dataframe
    """
    dataframe = pd.read_csv(
        os.path.join(os.path.dirname(__file__), FBK_FILE_PATH),
        encoding='windows-1252'
    )

    dataframe = dataframe.drop([
        "Unnamed: 0",
        "node_name",
        "g",
        "h",
        "th",
        "cfg",
        "iaq",
        "co2",
        "voc",
        "iac_comp"
    ], axis=1)
    dataframe["ts"]         = pd.to_datetime(dataframe["ts"])
    dataframe["signal_res"] = dataframe["signal_res"].astype(float)
    dataframe["heater_res"] = dataframe["heater_res"].astype(float)
    dataframe["volt"]       = dataframe["volt"].astype(float)
    dataframe["p"]          = dataframe["p"].astype(float)
    dataframe["t"]          = dataframe["t"].astype(float)
    dataframe["rh"]         = dataframe["rh"].astype(float)

    dataframe.drop_duplicates(['sensor_description','ts'], inplace = True)

    return dataframe

def get_appa_data() -> pd.DataFrame:
    """
    Fetches the local APPA data

    Returns:
        pd.DataFrame: the dataframe
    """
    return pd.read_csv(
        os.path.join(os.path.dirname(__file__), APPA_FILE_PATH),
        encoding='windows-1252'
    )

def get_prediction_data() -> pd.DataFrame:
    """
    Fetches the local prediction

    Returns:
        pd.DataFrame: the dataframe
    """
    return pd.read_csv(
        os.path.join(os.path.dirname(__file__), PREDICTION_FILE_PATH),
        encoding='windows-1252'
    )
