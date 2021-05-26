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

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
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

# Completeness Frame and Score
compl_frame, compl_array = dim_completeness(df, completeness_cols)
compl_score = 100 - (sum(compl_array) / len(compl_array) * 100)

# Page size for rows to display in DataTable
PAGE_SIZE = 5

# App Layout
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    brand="Palade - Data Quality Dashboard",
    brand_href="#",
    color="#567C4D",
    dark=True
)

sidebar = dbc.Container([
    dbc.Row([
        html.Div(
            [
                html.H2("Sidebar", className="display-4"),
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
                        dbc.NavLink("Accuracy", href="/accuracy", active="exact")
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            style=SIDEBAR_STYLE,
        ),
    ], className='h-100')
], style=SIDEBAR_STYLE)

content = dbc.Container([
    dbc.Row([

        # first column of first row
        dbc.Col(html.Div([html.P(f'{round(int(compl_score), 0)}%',
                                 style={'textAlign': 'center',
                                        'font-size': '10vh',
                                        'height': '100%',
                                        'padding-top': '40%',
                                        'color': '#567C4D'}
                                 ),
                          dcc.Dropdown(
                              options=[{'label': i, 'value': i} for i in completeness_cols],
                              multi=True,
                              placeholder='Select a column for individual scores',
                              style={'width': '100%', 'padding-left': '5%'}
                          )]),
                width=3
                ),

        # Barchart visualising the columns
        dbc.Col(
            dcc.Graph(figure=go.Figure(data=[go.Bar(x=compl_frame.columns,
                                                    y=[((len(compl_frame) - compl_frame[col].sum()) / len(compl_frame))
                                                       for col in compl_frame.columns],
                                                    name='True',
                                                    marker_color=px.colors.qualitative.D3[2]),
                                             go.Bar(x=compl_frame.columns,
                                                    y=[(compl_frame[col].sum() / len(compl_frame)) for col in
                                                       compl_frame.columns],
                                                    name='False',
                                                    marker_color=px.colors.qualitative.D3[3])]) \
                      .update_layout(barmode='stack',
                                     bargap=0.07,
                                     yaxis=dict(tickformat=".2%"),
                                     legend={
                                         'orientation': "h",
                                         'yanchor': "bottom",
                                         'y': 1,
                                         'x': 0.5,
                                         'xanchor': "center"},
                                     title={
                                         'text': "Completeness per Column",
                                         'y': 0.9,
                                         'x': 0.5,
                                         'xanchor': 'center',
                                         'yanchor': 'top'}),
                      style={
                          'height': '100%',
                          'width': '100%',
                          'padding': '0',
                          'verticalAlign': 'middle'}),
            width=9)
    ], className="h-50"),

    # second row
    dbc.Row([
        dbc.Col(children=[
            'Display Rows: ',
            dcc.Input(
                id='datatable-row-count',
                type='number',
                min=5,
                max=29,
                value=5
            ),
            dash_table.DataTable(
                id='datatable-paging',
                columns=[{"name": i, "id": i} for i in df[completeness_cols]],
                data=df.to_dict('records'),
                page_size=PAGE_SIZE,
                page_current=0,
                page_action='custom'
            )],
            width=12)
    ], className="h-50")
], style={
    "height": "100vh",
    "margin": "0vh",
    "border": "0vh",
    "padding": "0vh",
    "max-width": '100%',
})

app.layout = dbc.Container([
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


@app.callback(
    Output('datatable-paging', 'data'),
    Input('datatable-paging', "page_current"),
    Input('datatable-paging', "page_size"))
def update_table(page_current, page_size):
    return df.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


@app.callback(
    Output('datatable-paging', 'page_size'),
    Input('datatable-row-count', 'value'))
def update_table(use_row_count):
    return use_row_count


if __name__ == '__main__':
    app.run_server(debug=True)
