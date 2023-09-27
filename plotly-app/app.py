import os
from dash import Dash, html, dcc

import dash_bootstrap_components as dbc
import pandas as pd
import dash


from pages.utils.kerasWrapper import KerasWrapper

pd.options.mode.chained_assignment = None  # default='warn'

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

sidebar = html.Div( 
    [ 
        html.Div( 
            [ 
                # width: 3rem ensures the logo is the exact width of the 
                # collapsed sidebar (accounting for padding) 
                html.Img(src="/assets/img/logo_cut.png", style={"width": "5rem"}), 
                html.H2("Airwatching"), 
            ], 
            className="sidebar-header", 
        ), 
        html.Hr(className="sidebar-hr"), 
        dbc.Nav( 
            [ 
                dbc.NavLink( 
                    [ 
                        html.I(className="fa-solid fa-user fa-2x"), 
                        html.Br(), 
                        html.Span("Disclaimer"), 
                    ], 
                    href="/disclaimer", 
                    active="exact", 
                    style={"text-align": "center"}, 
                ), 
                html.Hr(className="sidebar-hr"), 
                dbc.NavLink( 
                    [ 
                        html.I(className="fa-solid fa-square-poll-vertical fa-2x"), 
                        html.Br(), 
                        html.Span("Raw FBK Data"), 
                    ], 
                    href="/", 
                    active="exact", 
                    style={"text-align": "center"}, 
                ), 
                dbc.NavLink( 
                    [ 
                        html.I(className="fa-solid fa-chart-line fa-2x"), 
                        html.Br(), 
                        html.Span("Fitted FBK Data"), 
                    ], 
                    href="/fbk", 
                    active="exact", 
                    style={"text-align": "center"}, 
                ), 
                dbc.NavLink( 
                    [ 
                        html.I(className="fa-solid fa-smog fa-2x"), 
                        html.Br(), 
                        html.Span("APPA Data"), 
                    ], 
                    href="/appa", 
                    active="exact", 
                    style={"text-align": "center"}, 
                ), 
            ], 
            vertical=True, 
            pills=True, 
        ), 
        html.Hr(className="sidebar-hr"), 
        html.Div( 
            html.Img(src="/assets/img/fbk-logo.png", className="fbk-logo"), 
            className="fbk-logo-div", 
        ), 
    ], 
    className="sidebar", 
)


content = html.Div([dash.page_container], id="page-content", className="content")

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
server = app.server
if __name__ == "__main__":
    if os.getenv("DEBUG"):
        app.run(debug=True)
    else:
        # Production
        app.run_server(port=8051, host="0.0.0.0", debug=False)
