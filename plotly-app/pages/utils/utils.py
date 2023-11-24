import pandas as pd
import os
from db_utils import load_data_from_psql
from datetime import date
from . import querys

# paths relative to THIS script
FBK_FILE_PATH = "../../../FBK data/data_fbk_from_db.csv"
APPA_FILE_PATH = "../../data/21_22_APPA.csv"
PREDICTION_FILE_PATH = "../../data/appa1_predictions.csv"



def filter_fbk_data(dataframe: pd.DataFrame) -> pd.DataFrame:
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
    dataframe["heater_res"] = dataframe["heater_res"].astype(float) 
    dataframe["signal_res"] = dataframe["signal_res"].astype(float)
    
    #dataframe.rename(columns = {'heater_res':'signal_res', 'signal_res':'heater_res'}, inplace = True) #data are passed wrong in the db
    
    dataframe["volt"] = dataframe["volt"].astype(float)
    dataframe["p"] = dataframe["p"].astype(float)
    dataframe["t"] = dataframe["t"].astype(float)
    dataframe["rh"] = dataframe["rh"].astype(float)
    
    #dataframe["sensor_description"] = (
     #   dataframe["sensor_description"].str.split(pat="_").str.get(0)
    #)
    
    #dataframe['sensor_description'] = dataframe.apply (lambda row: str(row['sensor_description'])+'_'+df_sensor.loc[int(row["sensor_description"])]["description"].split("_")[0] , axis=1)
    """try:
        dataframe['sensor_description'] = dataframe.apply (lambda row: row['sensor_description'].split('_')[0] +"_"+row['sensor_description'].split('_')[-1].split("-")[-1] ,axis=1)
    except Exception as e:
        print(e)
        print("Usually this error with empty dataframe")"""
        
    dataframe.drop_duplicates(["sensor_description", "ts", "node_id"], inplace=True)

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
    
def query_custom(start_date, end_date)-> pd.DataFrame:
    
    
    if start_date is not None and end_date is not None:
        start_date_object = date.fromisoformat(start_date)
        end_date_object = date.fromisoformat(end_date)
        
        days_range = (end_date_object - start_date_object).days
        
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        
        end_date_string = end_date_object.strftime('%Y-%m-%d')

        if(days_range <= 3):
            fbk_data = load_data_from_psql(querys.q_custom_all(start_date_string, end_date_string))
            
        elif(days_range > 3 and days_range <= 7):
            fbk_data = load_data_from_psql(querys.q_custom_30min(start_date_string, end_date_string))
            
        elif(days_range > 7 and days_range <= 30):
            fbk_data = load_data_from_psql(querys.q_custom_1H(start_date_string, end_date_string))
            
        elif(days_range > 30 and days_range <= 90):
            fbk_data = load_data_from_psql(querys.q_custom_H(start_date_string, end_date_string, 2))
            
        elif(days_range > 90):
            fbk_data = load_data_from_psql(querys.q_custom_H(start_date_string, end_date_string, 3))
        
    else:
        return pd.DataFrame    
    return filter_fbk_data(fbk_data)




def verify_period(period, df):
    if period == "last 6 months":
         # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="3H"), pd.Grouper("sensor_description")]
        ).mean(numeric_only=True)
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("180D")
        df = df.reset_index()
        return df
    elif period == "last month":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean(numeric_only=True)
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("30D")
        df = df.reset_index()
        return df
    elif period == "last week":
        # make hour average
        df = df.groupby(
            [pd.Grouper(key="ts", freq="1H"), pd.Grouper("sensor_description")]
        ).mean(numeric_only=True)
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("7D")
        df = df.reset_index()
        return df
    elif period == "last day":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1D")
        df = df.reset_index()
        return df
    elif period == "last hour":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1h")
        df = df.reset_index()

    return df


def verify_period_TPH(period, df):
    if period == "last 6 months":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("180D")
        df = df.reset_index()
        return df
    elif period == "last month":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("30D")
        df = df.reset_index()
        return df
    elif period == "last week":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("7D")
        df = df.reset_index()
        return df
    elif period == "last day":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1D")
        df = df.reset_index()
        return df
    elif period == "last hour":
        df = df.reset_index()
        df = df.set_index("ts")
        df = df.last("1h")
        df = df.reset_index()

    return df

