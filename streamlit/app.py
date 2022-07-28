from curses import start_color
from xml.etree.ElementPath import get_parent_map
from more_itertools import first
import streamlit as st
import pandas as pd
# import numpy as np
import altair as alt
from yaml import load


@st.cache
def load_csv():
    df = pd.read_csv(
        '../proc_appa_data_merged.csv', encoding='windows-1252')
    df.Data = pd.to_datetime(df.Data, format="%Y-%m-%d")
    return df


df = load_csv()
stations = df.Stazione.unique()
station = st.selectbox('Seleziona la Stazione', stations)
st.title(station)
station_df = df[df.Stazione == station]

pollutants = station_df.Inquinante.unique()
# first_date, last_date = st.slider('Seleziona la data',
#                                   int(station_df.Data.min()), int(station_df.Data.max()))

start_date = pd.to_datetime(station_df.Data.min(), format="%Y-%m-%d")
end_date = pd.to_datetime(station_df.Data.max(), format="%Y-%m-%d")
first_selected_date = st.sidebar.date_input("Seleziona la data d'inizio",
                                            value=start_date, min_value=start_date, max_value=end_date)
last_selected_date = st.sidebar.date_input("Seleziona la data d'inizio",
                                           value=end_date, min_value=start_date, max_value=end_date)

date_mask = (df.Data >= pd.to_datetime(first_selected_date)) & (
    df.Data <= pd.to_datetime(last_selected_date))
station_df = station_df.loc[date_mask]

selected_pollutants = st.multiselect('Seleziona gli inquinanti', pollutants)

for pollutant in selected_pollutants:
    st.markdown(f'**{pollutant}**')
    st.altair_chart(
        alt.Chart(station_df[station_df.Inquinante == pollutant]).mark_line(color='#f09331').encode(
            x='DataOra',
            y='Valore',
        ),
        use_container_width=True
    )

# st.altair_chart(
#     alt.Chart(station_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
#         x='Inquinante',
#         y='average(Valore)'
#     )
# )
