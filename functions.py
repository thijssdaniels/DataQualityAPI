import pandas as pd
import numpy as np
import operator as op
import re
from functools import reduce
import base64
import io
import pathlib

from app import cache


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    # Path
    BASE_PATH = pathlib.Path(__file__).parent.resolve()
    DATA_PATH = BASE_PATH.joinpath('data').resolve()

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=';', skiprows=4, na_values='#')

            # Clean column names and parse date columns
            df.columns = parse_column_names(df)

            date_cols = returnDateCols(df, threshold=0.5, sample_size=1000)
            df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')

            df.to_json(path_or_buf=f'{DATA_PATH}/data.json', orient='records')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

            return df
    except Exception as e:
        print(e)


@cache.memoize(timeout=120)
def query_data():
    # Path
    BASE_PATH = pathlib.Path(__file__).parent.resolve()
    DATA_PATH = BASE_PATH.joinpath('data').resolve()

    df = pd.read_json(f'{DATA_PATH}/data.json')
    return df


def multiStatement(condition, dataframe, reason=np.nan, include_reason=True):
    final = []

    for i in range(len(condition)):
        # Find operator item to seperate & and | statement
        idx = [-1] + [idx for idx, value in enumerate(condition[i]) if (value == '&') | (value == '|')]
        cond = [condition[i][s + 1:e].strip() for s, e in zip(idx, idx[1:] + [None])]

        # Find operators to test assumptions
        operators = [key for key in ops.keys() for c in cond if key in c]
        oper_before = rf'.*(?=\{operators[0]})'
        oper_after = rf'(?<={operators[1]}).*$'

        # Get inputs and validations
        inputs = [re.match(oper_before, c).group().strip() for c in cond]
        validations = [re.findall(oper_after, c)[0].strip() for c in cond]

        inp_testing = [dataframe[item] for item in inputs if item in dataframe.columns]
        val_testing = [int(item) if item.isdigit() else str(item) for item in validations]

        # Test both assumptions from the instance
        temp = []
        for c in range(len(inputs)):
            temp.append(pd.Series(ops.get(operators[i])(inp_testing[c], val_testing[c])))

        # Evaluate if either one instance is False.
        # If either one is False, return False. Else True
        if ('|' in condition[i]) & ('&' in condition[i]):
            # First & second condition before the or statement
            s = cond.index(condition[i][:condition[0].find('|')].strip())
            e = cond.index(condition[i][condition[0].find('|') + 1:condition[i].find('&')].strip())
            idx = [s, e]

            res_one = [any(res) for res in zip(temp[min(idx)][:], temp[max(idx)][:])]
            res_two = [x[i] for i in range(len(temp)) if i not in idx for x in zip(*temp)]

            f = pd.Series([True if all(r) else False for r in zip(res_one, res_two)],
                          name=f'assumption_{i + 1}')
        elif '|' in condition[i]:
            f = pd.Series([True if any(x) else False for x in zip(*temp)],
                          name=f'assumption_{i + 1}')
        elif '&' in condition[i]:
            f = pd.Series([True if all(x) else False for x in zip(*temp)],
                          name=f'assumption_{i + 1}')

        if include_reason:
            reason_expl = pd.Series(np.where(f, np.nan, reason[i]), name=f'reason_{i + 1}')
            multiple_appends(final, f, reason_expl)
        else:
            multiple_appends(final, f)

    # Get first column from conditions
    final = pd.DataFrame(list(map(list, zip(*final))), columns=[l.name for l in final])
    return final


def singleStatement(condition, dataframe, reason=np.nan, include_reason=True):
    final = []

    for i in range(0, len(condition)):
        # Get inputs and operator from condition input
        operator = ''.join([key for key in ops.keys() if key in condition[i]])
        input1 = ''.join(
            map(str, re.findall(rf'.*(?=\{operator})', condition[i]))).strip()  # Condition before operator
        input2 = ''.join(
            map(str, re.findall(rf'(?<={operator}).*$', condition[i]))).strip()  # Condition after operator

        # Check if value is a digit, a column or a string
        inputs = [input1, input2]
        output = [int(item) if item.isdigit() else df[item] if item in df.columns else item for item in inputs]

        # Replace True/False to get scores
        result = pd.Series((ops.get(operator)(output[0], output[1])), name=f'assumption_{i + 1}')
        final.append(result)

        if include_reason:
            reason_expl = pd.Series(np.where(result, np.nan, reason[i]), name=f'reason_{i + 1}')
            final.append(reason_expl)

    # Get first column from conditions
    final = pd.DataFrame(list(map(list, zip(*final))), columns=[l.name for l in final])
    return final


def parse_column_names(dataframe):
    columns = dataframe.columns.tolist()
    repls = (' ', '_'), ('(', ''), (')', ''), ('.', '')

    clean_columns = []

    for c in columns:
        c = c.strip().lower()
        c = reduce(lambda a, kv: a.replace(*kv), repls, c)
        clean_columns.append(c)

    return clean_columns


def returnDateCols(dataframe, threshold=0.75, sample_size=200):
    # Create empty lists
    date_cols = []

    # List regex for all possible date patterns
    date_pattern = ['\d{2}(-|/|.)\d{2}(-|/|.)\d{4}', '\d{2}(-|/|.)\w{3}(-|/|.)\d{4}']
    regex = "|".join([date for date in date_pattern])
    sample = dataframe.sample(sample_size)
    # Loop over column names. If column returns > 75% True values, add column name to the empty list
    # Extract patterns for added columns
    for column in sample.columns:

        sample[column] = sample[column].astype(str)
        if (sum(sample[column].str.match(regex, na=False)) / len(sample[column].dropna()) > threshold) & (
                sample[column].dtype == 'object'):
            date_cols.append(column)

    return date_cols


def dim_completeness(dataframe, columns):
    # List comprehension to iterate over each column, where FALSE is a non-null value
    df_completeness = pd.concat([pd.isnull(dataframe[col]) for col in columns], axis=1)

    # Completeness score
    completeness_score = df_completeness.values.flatten()

    return df_completeness, completeness_score


def uniquenessFrame(dataframe, columns):
    # List comprehension to iterate over each column, where FALSE is a unique value
    df_uniqueness = pd.concat([dataframe[c].duplicated() for c in columns], axis=1)

    return df_uniqueness


# Create get_pattern function to derive pattern from variable
def get_pattern(x, show_ws=True, ws_char='<>'):
    if pd.isnull(x):
        x = np.nan
    else:
        if not isinstance(x, str):
            x = str(x)

            x = re.sub('[a-z]', "a", x)
            x = re.sub('[A-Z]', "A", x)
            x = re.sub('[0-9]', "9", x)

        if isinstance(x, str):
            x = re.sub('[a-z]', "a", x)
            x = re.sub('[A-Z]', "A", x)
            x = re.sub('[0-9]', "9", x)

        if show_ws == True:
            x = re.sub("\\s", ws_char, x)

    return x


def validityFrame(dataframe, columns, patterns):
    # Create flat list for subset
    if len(columns) > 1:
        columns_used = set(sum(columns, []))
    else:
        columns_used = set(columns)

    # Perform Basic Pattern Analysis
    df_pattern = pd.concat([pd.Series(dataframe[col]).map(get_pattern) for col in columns_used], axis=1)

    # Loop over values to test and append patterns
    temp = []

    for column, pattern in zip(columns, patterns):
        temp.append(
            np.where(
                pd.isnull(df_pattern.loc[:, column]), np.nan,
                np.where(df_pattern.loc[:, column] == ''.join(pattern), 'Y', 'N')
            )
        )

    temp = pd.concat([pd.DataFrame(df) for df in temp], axis=1)

    # Paste results into one columns
    validity_quality = pd.Series(map(';'.join, temp.values.astype(str).tolist()))

    return df_pattern, validity_quality


ops = {'+': op.add,
       '-': op.sub,
       '*': op.mul,
       '/': op.truediv,
       '%': op.mod,
       '^': op.xor,
       '==': op.eq,
       '!=': op.ne,
       '<=': op.le,
       '<': op.lt,
       '>=': op.ge,
       '>': op.gt
       }


def multiple_appends(listname, *element):
    listname.extend(element)


def accuracyFun(dataframe, condition, reason=np.nan, include_reason=True):
    final = []

    for i in range(len(condition)):
        if ('&' in condition[i]) | ('|' in condition[i]):
            # Find operator item to separate & and | statement
            idx = [-1] + [idx for idx, value in enumerate(condition[i]) if (value == '&') | (value == '|')]
            cond = [condition[i][s + 1:e].strip() for s, e in zip(idx, idx[1:] + [None])]

            # Find operators to test assumptions
            operators = [key for key in ops.keys() for c in cond if key in c]
            oper_before = rf'.*(?=\{operators[0]})'
            oper_after = rf'(?<={operators[1]}).*$'

            # Get inputs and validations
            inputs = [re.match(oper_before, c).group().strip() for c in cond]
            validations = [re.findall(oper_after, c)[0].strip() for c in cond]

            inp_testing = [dataframe[item] for item in inputs if item in df.columns]
            val_testing = [int(item) if item.isdigit() else str(item) for item in validations]

            # Test both assumptions from the instance
            temp = []
            for c in range(len(inputs)):
                temp.append(pd.Series(ops.get(operators[i])(inp_testing[c], val_testing[c])))

            # Evaluate if either one instance is False.
            # If either one is False, return False. Else True
            if ('|' in condition[i]) & ('&' in condition[i]):
                # First & second condition before the operator statement
                s = cond.index(condition[i][:condition[0].find('|')].strip())
                e = cond.index(condition[i][condition[0].find('|') + 1:condition[i].find('&')].strip())
                idx = [s, e]

                res_one = [any(res) for res in zip(temp[min(idx)][:], temp[max(idx)][:])]
                res_two = [x[i] for i in range(len(temp)) if i not in idx for x in zip(*temp)]

                f = pd.Series([True if all(r) else False for r in zip(res_one, res_two)],
                              name=f'assumption_{i + 1}')
            elif '|' in condition[i]:
                f = pd.Series([True if any(x) else False for x in zip(*temp)],
                              name=f'assumption_{i + 1}')
            elif '&' in condition[i]:
                f = pd.Series([True if all(x) else False for x in zip(*temp)],
                              name=f'assumption_{i + 1}')

            if include_reason:
                reason_expl = pd.Series(np.where(f, np.nan, reason[i]), name=f'reason_{i + 1}')
                multiple_appends(final, f, reason_expl)
            else:
                multiple_appends(final, f)
        else:
            # Get inputs and operator from condition input
            operator = ''.join([key for key in ops.keys() if key in condition[i]])
            input1 = ''.join(
                map(str, re.findall(rf'.*(?=\{operator})', condition[i]))).strip()  # Condition before operator
            input2 = ''.join(
                map(str, re.findall(rf'(?<={operator}).*$', condition[i]))).strip()  # Condition after operator

            # Check if value is a digit, a column or a string
            inputs = [input1, input2]
            output = [int(item) if item.isdigit() else dataframe[item] if item in dataframe.columns else item for item
                      in inputs]

            # Replace True/False to get scores
            result = pd.Series((ops.get(operator)(output[0], output[1])), name=f'assumption_{i + 1}')
            final.append(result)

            if include_reason:
                reason_expl = pd.Series(np.where(result, np.nan, reason[i]), name=f'reason_{i + 1}')
                final.append(reason_expl)

    # Get first column from conditions
    final = pd.DataFrame(list(map(list, zip(*final))), columns=[l.name for l in final])
    return final
