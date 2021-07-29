import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_user

from login.create_login_db import Users, Users_tbl, engine

from utils.functions import *

from app import app

create = dbc.Container([
    html.Div([html.H1('Create User Account'),
              dcc.Location(id='create_user', refresh=True),
              dcc.Input(id='username',
                        type='text',
                        placeholder='user name',
                        maxLength=15),
              dcc.Input(id='password',
                        type='password',
                        placeholder='password'),
              dcc.Input(id='email',
                        type='email',
                        placeholder='email',
                        maxLength=50),
              html.Button('Create User', id='submit-val', n_clicks=0),
              html.Div(id='container-button-basic'),
              ])
])

login = dbc.Container([
    html.Div([dcc.Location(id='url_login', refresh=True),
              html.H2('''Please log in to continue:''', id='h1'),
              dcc.Input(placeholder='Enter your username',
                        type='text',
                        id='uname-box'),
              dcc.Input(placeholder='Enter your password',
                        type='password',
                        id='pwd-box'),
              html.Button(children='Login',
                          n_clicks=0,
                          type='submit',
                          id='login-button'),
              html.Div(children='', id='output-state')
              ])
])

success = dbc.Container([
    html.Div([dcc.Location(id='url_login_success', refresh=True),
              html.Div([html.H2('Login successful.'),
                        html.Br(),
                        html.P('Select a Dataset'),
                        dcc.Link('Completeness', href='/completeness'),
                        ]),  # End div
              html.Div([html.Br(),
                        html.Button(id='back-button', children='Go back', n_clicks=0)
                        ])  # End div
              ])  # End div
])

failed = dbc.Container([
    html.Div([dcc.Location(id='url_login_df', refresh=True),
              html.Div([html.H2('Log in Failed. Please try again.'),
                        html.Br(),
                        html.Div([login]),
                        html.Br(),
                        html.Button(id='back-button', children='Go back', n_clicks=0)
                        ])  # End div
              ])  # End div
])

logout = dbc.Container([
    html.Div([dcc.Location(id='logout', refresh=True),
              html.Br(),
              html.Div(html.H2('You have been logged out - Please login')),
              html.Br(),
              html.Div([login]),
              html.Button(id='back-button', children='Go back', n_clicks=0),
              ])  # End div
])

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


@app.callback(
    [Output('container-button-basic', 'children')],
    [Input('submit-val', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value'),
     State('email', 'value')])
def insert_users(n_clicks, username, password, email):
    hashed_password = generate_password_hash(password, method='sha256')
    if None not in [username, password, email]:
        new_user = Users_tbl.insert().values(username=username,
                                             password=hashed_password,
                                             email=email)
        conn = engine.connect()
        conn.execute(new_user)
        conn.close()
        return [login]
    else:
        return [html.Div([html.H2('Already have a user account?'),
                          dcc.Link('Click here to Log In', href='/login')]
                         )]


@app.callback(
    Output('url', 'pathname'),
    [Input('login-button', 'n_clicks')],
    [State('uname-box', 'value'),
     State('pwd-box', 'value')])
def successful(n_clicks, input1, input2):
    user = Users.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            return '/success'
        else:
            'Incorrect Password'
    else:
        pass


@app.callback(
    Output('output-state', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('uname-box', 'value'),
     State('pwd-box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'Incorrect username or password'
        else:
            return 'Incorrect username or password'
    else:
        return ''


# TESTING WITH HOMEPAGE INTEGRATION
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
