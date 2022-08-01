#import dash
from dash import dcc, html, Input, Output, Dash, callback
#import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
#from matplotlib import pyplot as plt
#import seaborn as sns

df=pd.read_csv("merged_APPA_data.csv", encoding='windows-1252') 
df=df[df.Valore != 'n.d.']
df.Valore= pd.to_numeric(df.Valore)
#df.head()

df["anno"]=df.Data.str[0:4]
df["mese"]=df.Data.str[5:7]
df=df.reset_index()

df=df.groupby(["Inquinante","Stazione","mese","anno"]).mean()
df=df.reset_index()

app=Dash(__name__)
app.layout= html.Div([
    html.H4 ("montly variations in pollutants"),
    dcc.Dropdown(
        id="dropdown",
        multi=True),
        dcc.Graph(id="graph"),
])

def update_plot2(input= "dropdown"):
    gas = "PM10"
    return

@app.callback(
    Output("graph","figure"),
    Input("dropdown","value")
)
def update_Graph(graph):
    fig= px.line(
        df,
        x="mese",
        y="Valore"
    )
    return fig  

app.run_server(debug=True,port=8052)
