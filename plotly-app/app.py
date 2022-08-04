import os
from dash import Dash, html, dcc

import dash_bootstrap_components as dbc
import pandas as pd
import dash

pd.options.mode.chained_assignment = None  # default='warn'

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

sidebar = html.Div(
    [
        html.Div(
            [html.Img(src="/assets/img/fbk-logo.png", className="sidebar-img")],
            # className="sidebar-img-div",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Raw FBK Data",
                    href="/fbk-raw",
                    active="exact",
                    class_name="sidebar-link",
                ),
                dbc.NavLink(
                    "Fitted FBK Data",
                    href="/fbk",
                    active="exact",
                    class_name="sidebar-link",
                ),
                dbc.NavLink(
                    "APPA Data", href="/appa", active="exact", class_name="sidebar-link"
                ),
                html.Hr(),
                dbc.NavLink(
                    "Settings",
                    href="/settings",
                    active="exact",
                    class_name="sidebar-link",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className = "fullHeight"
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.Row(
            [
                dbc.Col(sidebar, lg=3, xl=2, md=3, className="sidebar"),
                dbc.Col(dash.page_container, lg=9, xl=10, md=9, class_name="fullHeightAndPadding"),
            ],
            className = "fullHeight"
        ),
    ],
    className = "fullHeight"
)

server = app.server
if __name__ == "__main__":
    if os.getenv("DEBUG"):
        app.run(debug=True)
    else:
        # Production
        app.run_server(
            port=8050,
            host='0.0.0.0',
            debug=False
        )
