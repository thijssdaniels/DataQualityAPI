import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
import plotly.express as px

import yaml
from utils.functions import *
from collections import Counter

from app import app

# Path
BASE_PATH = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = BASE_PATH.joinpath('data').resolve()

# Read Data
dff = pd.read_csv(DATA_PATH.joinpath('df.csv'), delimiter=';', skiprows=4, na_values='#')
dff['index'] = range(1, len(dff) + 1)

with open(DATA_PATH.joinpath('config.yml')) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    yaml_list = yaml.safe_load(file)
    completeness_cols = yaml_list['completeness']

# Clean column names and parse date columns
dff.columns = parse_column_names(dff)

date_colss = returnDateCols(dff, threshold=0.5, sample_size=1000)
dff[date_colss] = dff[date_colss].apply(pd.to_datetime, errors='coerce')

# Completeness Frame and Score
compll_frame, compll_array = dim_completeness(dff, completeness_cols)


navbar = dbc.NavbarSimple(
    brand="Vault - Data Quality Dashboard",
    brand_href="#",
    dark=True
)

sidebar = dbc.Container([
    dbc.Row([
        html.Div(
            [
                html.H2("Completeness", className="display-4"),
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

content = dbc.Container([
    dbc.Row([

        # first column of first row
        dbc.Col(html.Div([html.P(
            id='completeness_score',
            style={'textAlign': 'center',
                   'font-size': '10vh',
                   'height': '100%',
                   'paddingTop': '40%',
                   'color': '#567C4D'}
        ),
            dcc.Dropdown(
                id='completeness_column',
                options=[{'label': i, 'value': i} for i in completeness_cols],
                multi=True,
                placeholder='Select a column for individual scores',
                style={'width': '100%', 'paddingLeft': '5%'}
            )]),
            width=3
        ),

        # Barchart visualising the columns
        dbc.Col(
            dcc.Graph(figure=go.Figure(data=[go.Bar(x=compll_frame.columns,
                                                    y=[((len(compll_frame) - compll_frame[col].sum()) / len(compll_frame))
                                                       for col in compll_frame.columns],
                                                    name='True',
                                                    marker_color=px.colors.qualitative.D3[2]),
                                             go.Bar(x=compll_frame.columns,
                                                    y=[(compll_frame[col].sum() / len(compll_frame)) for col in
                                                       compll_frame.columns],
                                                    name='False',
                                                    marker_color=px.colors.qualitative.D3[3])]) \
                      .update_layout(barmode='stack',
                                     bargap=0.07,
                                     yaxis={'tickformat': ".2%"},
                                     legend={
                                         'orientation': "h",
                                         'yanchor': "bottom",
                                         'y': 1,
                                         'x': 0.5,
                                         'xanchor': "center"},
                                     title={
                                         'text': "Completeness per Column",
                                         'font': {'size': 18},
                                         'y': 0.92,
                                         'x': 0.5,
                                         'xanchor': 'center',
                                         'yanchor': 'top'}),
                      style={
                          'height': '95%',
                          'width': '100%',
                          'padding': '0',
                          'verticalAlign': 'middle'}),
            width=9)
    ], className="h-50"),

    # second row
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='completeness_pies'),
            width=12)
    ], className="h-50")
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
                width=2),
        dbc.Col(html.Div(content),
                width=10),
    ], style={
        "margin": "0",
        "border": "0",
        "padding": "0",
        "height": "100vh"}),
], style={
    'paddingRight': '0',
    'paddingLeft': '0',
    'marginRight': '0',
    'marginLeft': '0',
    'maxWidth': '100%'
})


@app.callback(Output('completeness_score', 'children'),
              [Input('completeness_column', 'value'),
               Input('storing-data', 'data')])
def display_score(value, data):
    if data is None:
        raise PreventUpdate

    # Read data from local folder
    df = query_data()

    compl_frame, compl_array = dim_completeness(df, completeness_cols)

    if (value is None) | (value == []):
        compl_score = 100 - (sum(compl_array) / len(compl_array) * 100)
        return f'{round(int(compl_score), 0)}%'
    else:
        compl_array = compl_frame[value].values.flatten()
        compl_score = 100 - (sum(compl_array) / len(compl_array) * 100)
        return f'{round(int(compl_score), 0)}%'


@app.callback(Output('completeness_pies', 'figure'),
              [Input('completeness_column', 'value'),
               Input('storing-data', 'data')])
def display_pies(value, data):
    if data is None:
        raise PreventUpdate

    # Read data from local folder
    df = query_data()

    compl_frame = dim_completeness(df, completeness_cols)[0]

    if (value is None) | (value == []):
        df_new = pd.concat([df['notiftype'], compl_frame], axis=1)
        df_new.set_index('notiftype', inplace=True)

        values = df['notiftype'].unique()

        counter = []
        for v in values:
            c = Counter(df_new.loc[v].values.flatten())
            counter.append(c)

        color_dict = {'True': '#D62728', 'False': '#2CA02C'}
        colors = np.array([''] * len(counter[0].values()), dtype=object)
        for i in np.unique(list(counter[0].keys())):
            colors[np.where(list(counter[0].keys()) == i)] = color_dict[str(i)]

        data = []
        for i in range(len(counter)):
            d = {
                "values": list(counter[i].values()),
                "labels": list(counter[i].keys()),
                "marker": {"colors": colors},
                "domain": {"column": i},
                "name": values[i],
                "hole": .4,
                "type": "pie"
            }
            data.append(d)

        layout = go.Layout(
            {
                "title": {"text": "Completeness per Notification Type"},
                "grid": {"rows": 1, "columns": len(data)},
                "showlegend": False,
                "title_x": 0.5,
                "annotations": [
                    {
                        "font": {"size": 18},
                        "showarrow": False,
                        "text": "KT",
                        "font": {"size": 18},
                        "x": 0.225,
                        "y": 0.5
                    },
                    {
                        "font": {"size": 18},
                        "showarrow": False,
                        "text": "K1",
                        "font": {"size": 18},
                        "x": 0.775,
                        "y": 0.5
                    }
                ]
            }
        )
        return go.Figure(data=data, layout=layout)
    else:
        df_new = pd.concat([df['notiftype'], compl_frame[value]], axis=1)
        df_new.set_index('notiftype', inplace=True)

        values = df['notiftype'].unique()

        counter = []
        for v in values:
            c = Counter(df_new.loc[v].values.flatten())
            counter.append(c)

        color_dict = {'True': '#D62728', 'False': '#2CA02C'}
        colors = np.array([''] * len(counter[0].values()), dtype=object)
        for i in np.unique(list(counter[0].keys())):
            colors[np.where(list(counter[0].keys()) == i)] = color_dict[str(i)]

        data = []
        for i in range(len(counter)):
            d = {
                "values": list(counter[i].values()),
                "labels": list(counter[i].keys()),
                "marker": {"colors": colors},
                "domain": {"column": i},
                "name": values[i],
                "hole": .4,
                "type": "pie"
            }
            data.append(d)

        layout = go.Layout(
            {
                "title": {"text": "Completeness per Notification Type"},
                "grid": {"rows": 1, "columns": len(data)},
                "showlegend": False,
                "title_x": 0.5,
                "annotations": [
                    {
                        "font": {"size": 20},
                        "showarrow": False,
                        "text": "KT",
                        "font": {"size": 18},
                        "x": 0.225,
                        "y": 0.5
                    },
                    {
                        "font": {"size": 20},
                        "showarrow": False,
                        "text": "K1",
                        "font": {"size": 18},
                        "x": 0.775,
                        "y": 0.5
                    }
                ]
            }
        )
        return go.Figure(data=data, layout=layout)
