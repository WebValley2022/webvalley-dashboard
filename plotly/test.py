from dash import dcc, html, Input, Output, Dash
import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Pollutant concentration for each station"),
    html.H4("Choose a year:"),
    dcc.Slider(2012, 2022, 1, 
        id="slider_year",
        value=1,
        marks={
            2012: {'label': '2012', 'style': {'color': '#77b0b1'}},
            2013: {'label': '2013'},
            2014: {'label': '2014'},
            2015: {'label': '2015'},
            2016: {'label': '2016'},
            2017: {'label': '2017'},
            2018: {'label': '2018'},
            2019: {'label': '2019'},
            2020: {'label': '2020'},
            2021: {'label': '2021'},
            2022: {'label': '2022'},
        }
    ),
    html.H4("Choose a month:"),
    dcc.Slider(1, 12, 1, 
        id="slider_month",
        value=1
    ),
    dcc.Graph(id="pollutants-graph")
])

@app.callback(
    Output('pollutants-graph', 'figure'),
    Input('slider_year', 'value'),
    Input('slider_month', 'value')
    )
def update_graph(slider_year, slider_month):
    if(slider_year != None):
        date = str(slider_year)+"-"+str(slider_month)
        print(date)
        df = pd.read_csv('APPA data merged.csv', encoding='windows-1252')
        df = df[df.Valore != "n.d."]
        df["Data"] = df.Data.str[0:7]
        df["Valore"] = pd.to_numeric(df.Valore)
        ds_curr_date = df[df.Data == date]
        print(ds_curr_date)
        df_month_poll = ds_curr_date.groupby(["Inquinante", "Stazione", "Data"]).mean().reset_index()
        print(df_month_poll)
        fig = px.bar(
            df_month_poll,
            x='Inquinante',
            y='Valore',
            color='Stazione'
        )
        return fig

#def update_container(slider_output_container):
 #   return 'You have selected "{}"'.format(slider_output_container)

if __name__ == "__main__":
    app.run_server(debug=True)