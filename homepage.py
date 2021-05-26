# Data Quality: Dash App
import pathlib
import pandas as pd

import functions as fn

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath('data').resolve()

# Read Data
df = pd.read_csv(DATA_PATH.joinpath('df.csv'), delimiter=';', skiprows=4, na_values='#')

# Parse Date Columns
date_cols = fn.returnDateCols(df, threshold=0.5, sample_size=1000)
print(date_cols)
#df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), skiprows=4, delimiter=';', na_values='#')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # Clean column names and parse date columns
    df.columns = parse_column_names(df)

    date_cols = returnDateCols(df, threshold=0.5, sample_size=1000)
    df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

    dropdown = dcc.Dropdown(
        id='dropdown-selection',
        options=[{'label': i, 'value': i} for i in df.columns],
        placeholder="Select your columns",
        multi=True
    )

    return dropdown


@app.callback(Output('dropdown-columns', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children