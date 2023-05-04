from dash import html, dcc, Input, Output, callback, callback_context, State
from db_utils import load_data_from_psql
from datetime import datetime, date
from .utils import utils, querys


import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import logging
import dash
import os


from flask_caching import Cache

threshold = {
    'NO2' : {
                'very poor':400,
                'poor':200,
                'moderate':100,
                'decent': 40
            },
    'PM10' : {
                'very poor':100,
                'poor':50,
                'moderate':35,
                'decent': 20
            },
     'PM2.5' : {
                'very poor':50,
                'poor':25,
                'moderate':18,
                'decent': 10
            },
     'O3' : {
                'very poor':240,
                'poor':180,
                'moderate':120,
                'decent': 89
            },
     'CO' : {
                'very poor':20,
                'poor':10,
                'moderate':7.5,
                'decent': 5.0
            },
      'SO2' : {
                'very poor':500,
                'poor':350,
                'moderate':200,
                'decent': 100
                
            },
    
}

cache = Cache(dash.get_app().server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

dash.register_page(__name__)

stations = list(load_data_from_psql("select distinct stazione from appa_data;").stazione)


@cache.memoize(timeout= 604800*2) #cached 7 day  
def get_all_data() -> pd.DataFrame:  
    start = datetime.now()  
    df = load_data_from_psql("select stazione, inquinante, ts, valore from appa_data where date_part('year', ts) >= date_part('year', CURRENT_DATE) - 10")
    print(f"QUERY TIME just query: {datetime.now() - start}")
    df = df.rename(
        {
            "stazione": "Station",
            "inquinante": "Pollutant",
            "ts": "Date",
            "valore": "Value",
        },
        axis=1,
        )
    # keep only rows with a value that's not NA
    df = df[df.Value != "n.d."]
    df["Date"] = pd.to_datetime(df["Date"],utc=True)
    year = date.today().year
    year = f'{year-9}-01-01'
    df = df[df["Date"] >= year]
    df['Value'] = df['Value'].astype(float)
    print(f"QUERY TIME final df: {datetime.now() - start}")
    return df


def get_appa_data(selected_period: str)  -> pd.DataFrame:  
    start = datetime.now()    
    if selected_period  in "last day":
        query = "select stazione, inquinante, ts, valore from appa_data where ts >= NOW() - interval '24 hours';"
    elif selected_period  in "last week":
        query = "select stazione, inquinante, ts, valore from appa_data where ts >= NOW() - interval '7 days';"
    elif selected_period  in "last month":
        query = "select stazione, inquinante, ts, valore from appa_data where ts >= NOW() - interval '30 days';"
    elif selected_period  in "last 6 months":
        query = querys.q_custom_appa_from_now('180 days', 6)
    elif selected_period  in "last year":
        query = querys.q_custom_appa_from_now('1 years', 12)
    elif selected_period  in "all data":
        query =  querys.query_appa_one_data_per_week
    
    df = load_data_from_psql(query)    
    logging.info("Query time", datetime.now() - start)
    
    df = df.rename(
    {
        "stazione": "Station",
        "inquinante": "Pollutant",
        "ts": "Date",
        "valore": "Value",
    },
    axis=1,
    )
    # keep only rows with a value that's not NA
    df = df[df.Value != "n.d."]
    df["Date"] = pd.to_datetime(df["Date"],utc=True)
    print(f"QUERY TIME {selected_period}: {datetime.now() - start}")
    return df



def filter_df(df: pd.DataFrame, station: str, pollutant: str) -> pd.DataFrame:
    """
    returns a dataframe formed of all the records of the selected station and pollutant

    Args:
        df (pd.DataFrame): the dataframe to filter
        station (str): the station to select
        pollutant (str): the pollutant to select

    Returns:
        pd.DataFrame: the filtered dataframe
    """
    return df[(df.Station == station) & (df.Pollutant == pollutant)]

def plot_compare_years(start_date, end_date, selected_appa_station, pollutant):
    
    
    s = start_date.split('-')
    e = end_date.split('-')
    q = querys.query_appa_compare_years(s_day=s[2],s_month=s[1],e_day=e[2],e_month=e[1])
    df = load_data_from_psql(q)
    df = df.rename(
    {
        "stazione": "Station",
        "inquinante": "Pollutant",
        "ts": "Date",
        "valore": "Value",
    },
    axis=1,
    )
    # keep only rows with a value that's not NA
    df = df[df.Value != "n.d."]
    df["Date"] = pd.to_datetime(df["Date"],utc=False)
    df['Year'] = df.Date.dt.year
    df["Date"] = df['Date'].dt.strftime("2000-%m-%d %H")
    df["Date"] = pd.to_datetime(df["Date"],utc=False)
    
    df = filter_df(df, selected_appa_station, pollutant)
    df.sort_values(by='Date', inplace = True)
    
    
    fig = px.line(df,x='Date',y='Value',color='Year',category_orders={'Year': df['Year'].sort_values().unique()})
    fig.update_layout(
        margin=dict(l=0, r=5, t=30, b=0),
        plot_bgcolor="#fefefe",
        paper_bgcolor="rgba(0,0,0,0)",
        font= dict(family="Roboto, sans-serif", size=12, color="black"),
        title=dict(
            text="Pollutant concentration",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font_size=18,
        ),
        modebar=dict(
            bgcolor="#ffffff"
        )
    )
    fig.update_yaxes(
        title="μg/m3",
        fixedrange=False,
        title_font_size=12,
        showgrid=True,
        gridcolor='rgb(237, 232, 232)',
        gridwidth=0.5,
    )
    fig.update_xaxes(
         title_font_size=12,
         showgrid=True,
         gridcolor='rgb(237, 232, 232)',
         gridwidth=0.5,
    )
    fig.add_hrect(y0=0, y1=threshold[pollutant]['decent'], line_width=0, fillcolor='lightblue', opacity=0.1)
    fig.add_hrect(y0=threshold[pollutant]['decent'], y1=threshold[pollutant]['moderate'], line_width=0, fillcolor='green', opacity=0.1) if df['Value'].max() > threshold[pollutant]['decent'] else None
    fig.add_hrect(y0=threshold[pollutant]['moderate'], y1=threshold[pollutant]['poor'], line_width=0, fillcolor='yellow', opacity=0.1) if df['Value'].max() > threshold[pollutant]['moderate'] else None
    fig.add_hrect(y0=threshold[pollutant]['poor'], y1=threshold[pollutant]['very poor'], line_width=0, fillcolor='red', opacity=0.1)    if df['Value'].max() > threshold[pollutant]['poor'] else None
    fig.add_hrect(y0=threshold[pollutant]['very poor'], y1=1000, line_width=0, fillcolor='#660033', opacity=0.1) if df['Value'].max() > threshold[pollutant]['very poor'] else None
    fig.update_traces(line_width=1.5)
    fig.update_layout(yaxis_range=[0, df['Value'].max()+10])
    return fig
    


def line_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    pollutant: str = '',
    title_size: int = 14,
    color: str = None,
    sort=False,
) -> go.Figure:
    """
    Generates a line plot based on the dataframe, x and y given

    Args:
        df (pd.DataFrame): the dataframe to take the data from
        x (str): the column to select as X axis
        y (str): the column to select as Y axis
        color (str, optional): the column to assign different colors for multiple plots. Defaults to None.

    Returns:
        go.Figure: the line plot
    """
        
    colors=[]
    for i in df[y]:
        if any([i > threshold[pollutant]['very poor'] ]):
            colors.append('#800000')
        elif any([i > threshold[pollutant]['poor'] ]):
            colors.append('#ff4200')
        elif any([i > threshold[pollutant]['moderate'] ]):
            colors.append('#ffd100')
        elif any([i > threshold[pollutant]['decent'] ]):
            colors.append('green')
        else:
            colors.append('lightblue')
            
    fig = go.Figure()   
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode='lines+markers',
            line={'color': 'grey'},
            marker=dict(color=colors, size=5),
            showlegend=False,
            hovertemplate="%{x}<br>%{y} μg/m3 <extra></extra>" if not pollutant == 'CO' else "%{x}<br>%{y} ppm <extra></extra>" ,
        )
    )
    

    fig.update_layout(
        margin=dict(l=0, r=5, t=30, b=0),
        plot_bgcolor="#fefefe",
        paper_bgcolor="rgba(0,0,0,0)",
        font= dict(family="Roboto, sans-serif", size=12, color="black"),
        title=dict(
            text="Pollutant concentration",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font_size=title_size,
        ),
        modebar=dict(
            bgcolor="#ffffff"
        )
    )
    fig.update_yaxes(
        title="μg/m3",
        fixedrange=False,
        title_font_size=12,
        showgrid=True,
        gridcolor='rgb(237, 232, 232)',
        gridwidth=0.5,
    )
    fig.update_xaxes(
         title_font_size=12,
         showgrid=True,
         gridcolor='rgb(237, 232, 232)',
         gridwidth=0.5,
    )
    fig.add_hrect(y0=0, y1=threshold[pollutant]['decent'], line_width=0, fillcolor='lightblue', opacity=0.1)
    fig.add_hrect(y0=threshold[pollutant]['decent'], y1=threshold[pollutant]['moderate'], line_width=0, fillcolor='green', opacity=0.1)   if df['Value'].max() > threshold[pollutant]['decent'] else None
    fig.add_hrect(y0=threshold[pollutant]['moderate'], y1=threshold[pollutant]['poor'], line_width=0, fillcolor='yellow', opacity=0.1) if df['Value'].max() > threshold[pollutant]['moderate'] else None
    fig.add_hrect(y0=threshold[pollutant]['poor'], y1=threshold[pollutant]['very poor'], line_width=0, fillcolor='red', opacity=0.1)  if df['Value'].max() > threshold[pollutant]['poor'] else None 
    fig.add_hrect(y0=threshold[pollutant]['very poor'], y1=1000, line_width=0, fillcolor='#660033', opacity=0.1) if df['Value'].max() > threshold[pollutant]['very poor'] else None 
    fig.update_traces( line_width=0.5)
    fig.update_layout(yaxis_range=[0, df[y].max()+10])
    
    return fig


@callback(
    Output("appa-pollutants", "children"), Input("selected-appa-station", "value")
)
def get_pollutants(selected_appa_station: str) -> dbc.RadioItems:
    """
    Generates the radio items of pollutants of the given appa station

    Args:
        selected_appa_station (str): the selected station

    Returns:
        dbc.RadioItems: the radio items of the pollutants
    """
    
    df = load_data_from_psql(f"select distinct inquinante as Pollutant from appa_data where stazione = '{selected_appa_station}';")
    
    # get pollutants and build dict from it
    pollutants = df.pollutant.unique()
    pollutants_list = [
        {"label": pollutant, "value": pollutant} for pollutant in pollutants
    ]

    return dbc.RadioItems(
        id="selected-pollutant",
        class_name="btn-group",
        input_class_name="btn-check",
        label_class_name="btn btn-outline-primary",
        label_checked_class_name="active",
        options=pollutants_list,
        value="NO2",
    )
LAST_CLICKED = None

@callback(
    [Output("main-plot", "figure"),
     Output("year-plot", "figure"),
     Output("week-plot", "figure"),
    ],
    
    [State("selected-appa-station", "value"),
     State("my-date-picker-range","start_date"),
     State("my-date-picker-range","end_date"),
    ],
    
    
    Input("selected-pollutant", "value"),
    Input("selected-appa-period", "value"),
    Input("selected-weekday-period", "value"),
    Input("btn_search_date", "n_clicks"),
    Input("check_years", "value"),
    prevent_initial_call=True,
)
def update_main_plot(selected_appa_station: str, start_date, end_date, selected_pollutant: str, selected_appa_period: str, selected_weekday_period, btn_search, check_years):
    """
    Updates the main plot representing the pollutant level of the selected station over time

    Args:
        selected_appa_station (str): the station which to show the data
        selected_pollutant (str): the pollutant which to show the data

    Returns:
        go.Figure: the plot
    """
    global LAST_CLICKED

    
    if ("btn_search_date" == callback_context.triggered_id or ("selected-pollutant" == callback_context.triggered_id and LAST_CLICKED == "btn_search_date")
        or ("selected-weekday-period" == callback_context.triggered_id and LAST_CLICKED == "btn_search_date")
        ) and start_date and end_date:
        
        LAST_CLICKED = 'btn_search_date'
        q = querys.q_custom_appa(start_date, end_date,1)
        df = load_data_from_psql(q)    
        
        df = df.rename(
        {
            "stazione": "Station",
            "inquinante": "Pollutant",
            "min": "Date",
            "avg": "Value",
        },
        axis=1,
        )
        # keep only rows with a value that's not NA
        df = df[df.Value != "n.d."]
        df["Date"] = pd.to_datetime(df["Date"],utc=True)
    else: 
        LAST_CLICKED = 'else'
        df = get_appa_data(selected_appa_period)

    data = filter_df(df, selected_appa_station, selected_pollutant)
    data.sort_values(by='Date', inplace = True)
    
    if check_years:
        fig_main = plot_compare_years(start_date,end_date, selected_appa_station, selected_pollutant)
    else:
        fig_main = line_plot(
            data, "Date", "Value", title="Weekly mean over time", title_size=18, pollutant=selected_pollutant)
    #----------------------------------------------------------------------------------

    
    
    df = get_all_data()
    data = filter_df(df, selected_appa_station, selected_pollutant)
    
    
    df_year = data.groupby(
        [data.Date.dt.year, data.Date.dt.month_name(), data.Date.dt.month]
    ).mean(numeric_only=True)

    df_year.index.names = ["Year", "Month", "Month_num"]
    df_year = df_year.reset_index()

    # set the ordering (e.g. January < February) for the column 'Month'
    df_year["Month"] = pd.Categorical(df_year["Month"], categories=MONTHS, ordered=True)

    # sort the values based on the ordering given before
    df_year.sort_values("Month_num", inplace=True)
  
    fig_year = go.Figure()

    for year , group in df_year.groupby('Year'):
        fig_year.add_trace(go.Scatter(
            x=df_year[df_year["Year"] == year]["Month"],
            y=df_year[df_year["Year"] == year]["Value"], 
            name=year,
            mode='lines',
            line_shape='spline',
        ))
    fig_year.update_traces(line=dict(width=2), opacity=0.8, hovertemplate=None,)
    fig_year.update_layout(
        margin=dict(l=0, r=5, t=30, b=0),
        plot_bgcolor="#fefefe",
        paper_bgcolor="rgba(0,0,0,0)",
        font= dict(family="Roboto, sans-serif", size=12, color="#333333"),
        title=dict(
            text="Year comparison",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
            font_size=14,
        ),
        modebar=dict(
            bgcolor="#ffffff"
        )
    )
    fig_year.update_yaxes(
        title="μg/m3",
        fixedrange=True,
        title_font_size=12,
    )
    fig_year.update_xaxes(
        title="Months",
         title_font_size=12
    )
    fig_year.update_layout(hovermode='x unified')
    
    
    
    #-------------------------------------------------------------------------------------
    df_week = data
    if callback_context.triggered_id == "selected-weekday-period":
        if selected_weekday_period != 'All years':
            df_week = data[data['Date'].dt.year == selected_weekday_period]
            
    df_week["Month"] = data.Date.dt.month

    # add new column
    df_week["Season"] = "Summer"

    # set January to March and October to December as 'Inverno' True
    df_week.loc[(df_week.Month >= 4) & (df_week.Month <= 6), "Season"] = "Spring"
    df_week.loc[(df_week.Month >= 10) & (df_week.Month <= 12), "Season"] = "Fall"
    df_week.loc[(df_week.Month >= 1) & (df_week.Month <= 3), "Season"] = "Winter"

    # make daily average of pollutant level
    df_week = df_week.groupby(
        ["Season", df_week.Date.dt.day_name(), df_week.Date.dt.day_of_week]
    ).mean(numeric_only=True)
    df_week.index.names = ["Season", "Weekday", "Weekday_num"]
    df_week = df_week.reset_index()
    df_week = df_week.sort_values("Weekday_num")

    # draw main bar plot
    fig_week = px.bar(df_week, x="Weekday", y="Value", color="Season", barmode="group")
    fig_week.update_layout(
        plot_bgcolor="#fefefe",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=18, b=0),
        font= dict(family="Roboto, sans-serif", size=12, color="#333333"),
        title=dict(
            text="Weekday avg",
            x=0.5,
            y=0.95,
            xanchor="center",
            yanchor="top",
            font_family="Sans serif",
            font_size=14,
        ),
        modebar=dict(
            bgcolor="#ffffff"
        ),
        legend_title_text="",
    )
    fig_week.update_yaxes(   
        title="μg/m3",
        fixedrange=True,
        title_font_size=12,
    )
    fig_week.update_xaxes(

        title_font_size=12,
    )
    fig_week.update_traces(opacity=0.6, marker_line_width=1.5, marker_line_color='black')
    #-------------------------------------------------------------
    
   
    
    return [fig_main, fig_year,fig_week]

@callback(
    [Output("modal-appa-body", "figure"), Output("modal-appa-centered", "is_open") ],
    
    [Input("year-fs", "n_clicks"),
     Input("week-fs", "n_clicks"),],
    
    [State("modal-appa-centered", "is_open"),
     State("year-plot", "figure"),
     State("week-plot", "figure"),]
)
def toggle_modal(year_fs,week_fs, is_open, year_plot, week_plot):
    if year_fs or week_fs :
        if "year-fs" == callback_context.triggered_id:
            year_plot = go.Figure(year_plot)
            year_plot.update_yaxes(fixedrange=False)
            return [year_plot, not is_open]
        
        elif "week-fs" == callback_context.triggered_id:
            week_plot = go.Figure(week_plot)
            week_plot.update_yaxes(fixedrange=False)
            return [week_plot, not is_open]

    return [None, is_open]


@callback(
    Output("download-text", "data"),
    Input("btn_appa", "n_clicks"),
    prevent_initial_call=True,
)
def create_download_file(n_clicks):
    """global df
    return dcc.send_data_frame(df.to_csv, "appa_data.csv")"""
    cache.clear()
    

translate = {
     'NO2' : 'Nitrogen Dioxide',
     'PM10' : 'PM10',
     'PM2.5' : 'PM2.5',
     'O3' : 'Ozone',
     'CO' : 'Carbon Monoxide',
    'SO2' : 'Sulfur Dioxide',
}

@callback(
    Output("card-limit", "children"),
    Input("selected-pollutant", "value"),
    prevent_initial_call=True,
)
def create_card_limit(pollutant):
    return dbc.Card(
    [
        dbc.CardImg(
            src="/assets/img/airquality.jpg",
            top=True,
            style={"opacity": 0.3, "height": '24.9vh',"border-radius":'14px'},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("EU Air Quality Directives", className="card-title"),
                    html.P(
                        f"Limit value for {translate[pollutant]}",
                        className="card-text",
                    ),
                    html.Div(
                        [
                            html.H3("120",style={'color':'red'}),
                            html.P(f"this year has been exceeded {37} times")
                            ]),
                ],
            style={"background-color":"rgb(0,0,0,0)"}),
        ),
    ],
    style={"height":"25vh","border-radius":'15px'},
)
    
    

periods = ["all data","last year","last 6 months", "last month", "last week", "last day"]

dropdown_period = dcc.Dropdown(
    periods, id="selected-appa-period", className="dropdown", value=periods[4]
)
years = [y for y in range( date.today().year - 10, date.today().year + 1)]
years.append('All years')
dropdown_weekday = dcc.Dropdown(
    years, id="selected-weekday-period", className="dropdown", value=years[-1]
)

title = html.Div("APPA Data", className="header-title", style={'text-align':'center'})
dropdown = dcc.Dropdown(
    stations, id="selected-appa-station", className="dropdown", value=stations[3]
)
download_btn = dbc.Button(
    [html.I(className="fa-solid fa-download"), " Download full data"],
    color="primary",
    id="btn_appa",
    class_name="download-btn",
)
download_it = dcc.Download(id="download-text")


card = html.Div(id="card-limit")


def make_btn_fscreen(id :str):
    return dbc.Button(
                    children= html.I(className= "fa-solid fa-expand fa-xl", style={"color":"rgb(0 94 255 / 69%)",}),
                    className="full-screen",
                    id=id,
                )
    
search = dbc.Button(
    children= html.I(
        className= "fas fa-search"
    ),
    id="btn_search_date",
    color="secondary",
    outline=True,
    className="me-1",
    size="sm",
    style={"width":'100%',"border":'1px solid #ccc'}
)
    
date_range = dcc.DatePickerRange(
    id='my-date-picker-range',
    month_format='MMMM Y',
    start_date_placeholder_text="Start Period",
    end_date_placeholder_text="End Period",
    clearable=True,
)
    
toast = dbc.Toast(
                    [
                        html.H4("Filter by:",style={"font-weight":"bold"}),
                        dropdown_period,
                        date_range,
                        search,
                        dcc.Checklist(options=[' Show comparison over years'], id="check_years", style={"font-size": "14px"}),
                        html.Hr(),
                        html.H5("Weekday year:",style={"font-weight":"bold"}),
                        dropdown_weekday,
                    ],
                    id="toast",
                    header=html.P([html.I(className="fa-solid fa-gear"), " Settings"]),
                    #body_style={"margin-bottom":"2rem"},
                    style={"height":"100%"}
                )


gas_btns = html.Div(dbc.RadioItems(id='selected-pollutant'),id="appa-pollutants", className="radio-group ",style={'display': 'flex', 'justify-content': 'space-around'})

dropdownWrapper = html.Div(
    [dropdown, ], className="dropdownWrapper"
)

header = html.Div(
    [title, dropdownWrapper, download_btn, download_it, gas_btns], className="section-header"
)

modal = dbc.Modal(
            [
                dbc.ModalHeader(close_button=True),
                dbc.ModalBody(dcc.Graph(id="modal-appa-body",style={"height":"55vh",},)),
            ],
            id="modal-appa-centered",
            centered=True,
            className="fullscreen-modal",
            is_open=False,
        )

layout = html.Div(
    [
        header,
        modal,     
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="main-plot",
                        config={
                            "displayModeBar": False,
                            "displaylogo": False,
                        },
                        style={"height":"55vh",},
                        className="pretty_container",
                    ),
                style={"width":"80%"}),
                dbc.Col(
                    [
                        toast,
                    ],
                    width=1,
                    style={"min-width":"200px"}  
                ),
                
            ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        make_btn_fscreen("year-fs"),
                        dcc.Graph(
                            id="year-plot",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                            className="side-plot pretty_container",
                        ),],
                    width=4),
                dbc.Col([
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        make_btn_fscreen("week-fs"),
                        dcc.Graph(
                            id="week-plot",
                            className="side-plot pretty_container",
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                            },
                            style=dict(height="25vh"),
                        ),],
                    width=4),
                dbc.Col([
                        html.Div(style=dict(height="1vh"), className="transparent"),
                        card,

                        
                    ],
                    width=4),
            ],
        ),
    ],
    className="section fullHeight",
)
