import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from flask_login import current_user, LoginManager

from login.create_login_db import db, Users

from app import app
from apps import login, overview, completeness, uniqueness, validity, accuracy

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content', className='content'),
    dcc.Store(id='storing-data', storage_type='session')
])

server = app.server
db.init_app(server)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return login.create
    elif pathname == '/login':
        return login.login
    elif pathname == '/success':
        if current_user.is_authenticated:
            return login.layout
        else:
            return login.failed
    elif pathname == '/home':
        if current_user.is_authenticated:
            return login.layout
    elif pathname == '/overview':
        if current_user.is_authenticated:
            return overview.layout
    elif pathname == '/completeness':
        if current_user.is_authenticated:
            return completeness.layout
    elif pathname == '/uniqueness':
        if current_user.is_authenticated:
            return uniqueness.layout
    elif pathname == '/validity':
        if current_user.is_authenticated:
            return validity.layout
    elif pathname == '/accuracy':
        if current_user.is_authenticated:
            return accuracy.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
