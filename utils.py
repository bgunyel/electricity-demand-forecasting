import datetime
import json
import pandas as pd


def read_demand_data(start_date, end_date, data_folder):
    dummy = -32



def read_monthly_demand_data(file_path):
    df = pd.read_csv(file_path)
    df['Consumption (MWh)'] = df['Consumption (MWh)'].str.replace(',', '').astype(float)
    df['Date_Time'] = df[['Date', 'Hour']].agg(' '.join, axis=1)
    df['Date_Time'] = pd.to_datetime(df['Date_Time'], dayfirst=True)
    df.drop(columns=['Date', 'Hour'], inplace=True)
    df = df.set_index('Date_Time')
    df.index = pd.to_datetime(df.index)

    df = implement_special_days(df)
    return df


def implement_special_days(df):

    min_datetime = df.index.min()
    max_datetime = df.index.max()

    if min_datetime.year != max_datetime.year:
        raise Exception(f'Min & max year should be the same within a month -- {min_datetime} & {max_datetime}')
    elif min_datetime.month != max_datetime.month:
        raise Exception(f'Min & max month should be the same within a month -- {min_datetime} & {max_datetime}')

    holidays_list = get_holidays(min_date=min_datetime.date(), max_date=max_datetime.date())

    out_df = df.copy(deep=True)
    out_df['holiday'] = 0

    for holiday in holidays_list:
        out_df.loc[out_df.index.date == holiday, 'holiday'] = 1


    return out_df


def get_holidays(min_date, max_date):
    constant_holidays = {1: [1], 4: [23], 5: [1, 19], 7: [15], 8: [30], 10: [29], 12: [31]}

    year = min_date.year
    month = min_date.month

    holidays = constant_holidays[month]

    f = open('./data/sliding_holidays.json')
    data = json.load(f)
    sliding_holidays = data[str(year)]
    f.close()

    out_list = []
    for i in holidays:
        d = datetime.date(year=year, month=month, day=i)
        if (d <= max_date) and (d >= min_date):
            out_list.append(d)

    for s in sliding_holidays:
        d = datetime.date.fromisoformat(s)

        if (d <= max_date) and (d >= min_date):
            out_list.append(d)

    return out_list





