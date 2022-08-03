from dash import html

import dash

dash.register_page(__name__)

title = html.Div("Settings", className="header-title")

header = html.Div(
    [title],
    className="section-header"
)

layout = html.Div(
    header,
    className="section")
