import dash_html_components as html
import dash_bootstrap_components as dbc

from components.header import navbar
from utils.functions import *

sidebar = dbc.Container([
    dbc.Row([
        html.Div(
            [
                html.H2("Overview", className="display-4"),
                html.Hr(),
                html.P(
                    "A simple sidebar layout with navigation links", className="lead"
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/home", active="exact"),
                        dbc.NavLink("Overview", href="/overview", active="exact"),
                        dbc.NavLink("Completeness", href="/completeness", active="exact"),
                        dbc.NavLink("Uniqueness", href="/uniqueness", active="exact"),
                        dbc.NavLink("Validity", href="/validity", active="exact"),
                        dbc.NavLink("Accuracy", href="/accuracy", active="exact")
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
        ),
    ], className='h-100')
])

content = dbc.Container([], style={
    "height": "100vh",
    "margin": "0vh",
    "border": "0vh",
    "padding": "0vh",
    "max-width": '100%',
})

layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col(html.Div(sidebar),
                width=2, style={
                "margin": "0",
                "border": "0",
                "padding-left": '3vh',
                "height": "100%",
                "background-color": "#f8f9fa"
                }),
        dbc.Col(html.Div(content),
                width=10),
    ], style={
        "margin": "0",
        "border": "0",
        "padding": "0",
        "height": "100vh"}),
], style={
    'padding-right': '0',
    'padding-left': '0',
    'margin-right': '0',
    'margin-left': '0',
    'max-width': '100%'
})
