import dash

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table

import pandas as pd

from functions import *
from app import app, cache

navbar = dbc.NavbarSimple(
    brand="Vault - Data Quality Dashboard",
    brand_href="#",
    dark=True
)

sidebar = dbc.Container([
    dbc.Row([
        html.Div(
            [
                html.H2("Home", className="display-4"),
                html.Hr(),
                html.P(
                    "A simple sidebar layout with navigation links", className="lead"
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", active="exact"),
                        dbc.NavLink("Overview", href="/overview", active="exact"),
                        dbc.NavLink("Completeness", href="/completeness", active="exact"),
                        dbc.NavLink("Uniqueness", href="/uniqueness", active="exact"),
                        dbc.NavLink("Validity", href="/validity", active="exact"),
                        dbc.NavLink("Accuracy", href="/accuracy", active="exact"),
                        dbc.NavLink("Data", href="/data", active="exact")
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
        ),
    ], className='h-100')
])

content = dbc.Container([
    dbc.Row([

        # first column of first row
        dbc.Col(
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '100%',
                    'lineHeight': '100px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'margin': '2vh',
                    'paddingLeft': '2em',
                    'paddingRight': '2em'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
            width=3),

        dbc.Col(
            html.Div(id='datatable'),
            width=9
        )
    ], className="h-50"),

    # second row
    dbc.Row([])
], style={
    "height": "100vh",
    "margin": "0vh",
    "border": "0vh",
    "padding": "0vh",
    "maxWidth": '100%',
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


# Store data as JSON string for future use
@app.callback(Output('storing-data', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:

        parse_contents(list_of_contents, list_of_names)


# Call DataFrame from memory
@app.callback(Output('datatable', 'children'),
              [Input('storing-data', 'data')])
def update_output(data):
    if data is None:
        raise PreventUpdate

    list_of_contents = data['contents']
    list_of_names = data['filenames']

    df = parse_contents(list_of_contents, list_of_names)

    return html.Div([
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{"name": i, "id": i} for i in df.columns]
            )
        ])

