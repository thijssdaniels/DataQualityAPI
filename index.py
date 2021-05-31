import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import accuracy, homepage, overview, completeness, uniqueness, validity, data


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/overview':
        return overview.layout
    elif pathname == '/completeness':
        return completeness.layout
    elif pathname == '/uniqueness':
        return uniqueness.layout
    elif pathname == '/validity':
        return validity.layout
    elif pathname == '/accuracy':
        return accuracy.layout
    elif pathname == '/data':
        return data.layout
    else:
        return homepage.layout


if __name__ == '__main__':
    app.run_server(debug=True)