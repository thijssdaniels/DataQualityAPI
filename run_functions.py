from functions import *
import pandas as pd
import pathlib
import numpy as np
import yaml

import plotly.express as px
import plotly.graph_objects as go

BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath('data').resolve()

with open(DATA_PATH.joinpath('config.yml')) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    yaml_list = yaml.safe_load(file)
    completeness_cols = yaml_list['completeness']

df = pd.read_csv(DATA_PATH.joinpath('df.csv'), skiprows=4, delimiter=';', na_values='#')

# Parse Date Columns
df.columns = parse_column_names(df)
date_cols = returnDateCols(df, threshold=0.5, sample_size=1000)
df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

x, y = dim_completeness(df, completeness_cols)

print(x.info())

fig1 = go.Figure(data=[go.Bar(x=x.columns,
                              y=[len(x) - x[col].sum() for col in x.columns],
                              name='True',
                              marker_color=px.colors.qualitative.D3[2]),
                       go.Bar(x=x.columns,
                              y=[x[col].sum() for col in x.columns],
                              name='False',
                              marker_color=px.colors.qualitative.D3[3])])
fig1.update_layout(barmode='stack',
                   bargap=0.07,
                   width=600,
                   height=400)
fig1.show()
