import dash
import dash_bootstrap_components as dbc
from flask_caching import Cache

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__,
                # these meta_tags ensure content is scaled correctly on different devices
                # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ],
                external_stylesheets=external_stylesheets)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

server = app.server

app.config.suppress_callback_exceptions = True




