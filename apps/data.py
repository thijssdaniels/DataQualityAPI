import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table
import dash

import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import pathlib
import yaml
from functions import *
from styling import *

from app import app

# Path
BASE_PATH = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = BASE_PATH.joinpath('data').resolve()

# Read Data
df = pd.read_csv(DATA_PATH.joinpath('df.csv'), delimiter=';', skiprows=4, na_values='#')
df[' index'] = range(1, len(df) + 1)

with open(DATA_PATH.joinpath('config.yml')) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    yaml_list = yaml.safe_load(file)
    completeness_cols = yaml_list['completeness']

# Clean column names and parse date columns
df.columns = parse_column_names(df)

date_cols = returnDateCols(df, threshold=0.5, sample_size=1000)
df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

navbar = dbc.NavbarSimple(
    brand="Vault - Data Quality Dashboard",
    brand_href="#",
    dark=True
)

sidebar = dbc.Container([
    dbc.Row([
        html.Div(
            [
                html.H2("Data", className="display-4"),
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
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records')
    )
], style={
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


#if __name__ == '__main__':
#    app.run_server(debug=True)
