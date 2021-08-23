import pandas as pd
import pathlib
import json

if pathlib.Path('data1') in pathlib.Path('.').iterdir():
    BASE_PATH = pathlib.Path(__file__).parent.parent.resolve()
    DATA_PATH = BASE_PATH.joinpath('data1').resolve()
else:
    pathlib.Path('data1').mkdir(parents=True, exist_ok=True)
    BASE_PATH = pathlib.Path(__file__).parent.parent.resolve()
    DATA_PATH = BASE_PATH.joinpath('data1').resolve()

'''
with open(DATA_PATH.joinpath('config.yml')) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    yaml_list = yaml.safe_load(file)
    completeness_cols = yaml_list['completeness']

df = pd.read_json(f'{DATA_PATH}/data.json')
# print(df.head())
'''

'''
df = pd.read_csv(DATA_PATH.joinpath('df.csv'), skiprows=4, delimiter=';', na_values='#')

# Parse Date Columns
df.columns = parse_column_names(df)
date_cols = returnDateCols(df, threshold=0.5, sample_size=1000)
df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

# Completeness Frame and Score
compl_frame, compl_array = dim_completeness(df, completeness_cols)
compl_score = 100 - (sum(compl_array) / len(compl_array) * 100)

df_new = pd.concat([df['notiftype'], compl_frame], axis=1)
df_new.set_index('notiftype', inplace=True)

values = df['notiftype'].unique()

counter = []
for v in values:
    c = Counter(df_new.loc[v].values.flatten())
    counter.append(c)


color_dict = {'False': '#D62728', 'True': '#2CA0C2'}
colors = np.array([''] * len(counter[0].values()), dtype=object)
for i in np.unique(list(counter[0].keys())):
    colors[np.where(list(counter[0].keys()) == i)] = color_dict[str(i)]
'''