import streamlit as st
import pandas as pd
# import numpy as np
import altair as alt


@st.cache
def load_csv():
    df = pd.read_csv(
        '../data/APPA_data_merged.csv', encoding='windows-1252')
    df.Data = pd.to_datetime(df.Data)
    df.DataOra = pd.to_datetime(df.DataOra)
    return df


df = load_csv()
stations = df.Stazione.unique()
station = st.selectbox('Seleziona la Stazione', stations)
st.title(station)
station_df = df[df.Stazione == station]


start_date = pd.to_datetime(station_df.Data.min(), format="%Y-%m-%d")
end_date = pd.to_datetime(station_df.Data.max(), format="%Y-%m-%d")
first_selected_date = st.sidebar.date_input("Seleziona la data d'inizio",
                                            value=start_date, min_value=start_date, max_value=end_date)
last_selected_date = st.sidebar.date_input("Seleziona la data di fine",
                                           value=end_date, min_value=start_date, max_value=end_date)

date_mask = (df.Data >= pd.to_datetime(first_selected_date)) & (
    df.Data <= pd.to_datetime(last_selected_date))
station_df = station_df.loc[date_mask]

pollutants = station_df.Inquinante.unique()
selected_pollutants = st.multiselect('Seleziona gli inquinanti', pollutants)

for pollutant in selected_pollutants:
    pollutant_df = station_df[station_df.Inquinante == pollutant]
    st.markdown(f'**{pollutant}**')
    st.altair_chart(
        alt.Chart(pollutant_df).mark_line(color='#f09331').encode(
            x='DataOra',
            y='Valore',
        ),
        use_container_width=True
    )
