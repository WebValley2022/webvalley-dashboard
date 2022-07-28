import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


df = pd.read_csv('../proc_appa_data_26-07-2022.csv', encoding='windows-1252')

stations = df.Stazione.unique()
station = st.selectbox('Seleziona la Stazione', stations)
st.title(station)
station_df = df[df.Stazione == station]

pollutants = station_df.Inquinante.unique()
selected_pollutants = st.multiselect('Seleziona gli inquinanti', pollutants)

for pollutant in selected_pollutants:
    st.markdown(f'**{pollutant}**')
    st.altair_chart(
        alt.Chart(station_df[station_df.Inquinante == pollutant]).mark_line().encode(
            x='DataOra',
            y='Valore',
            color='Inquinante'
        ),
        use_container_width=True
    )
