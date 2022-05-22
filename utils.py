import datetime
from dateutil.rrule import rrule, MONTHLY
import json
import os

import pandas as pd

import constants


def read_demand_data(start_date, end_date, data_folder):
    file_name_root = 'RealTimeConsumption'
    file_extension = 'csv'

    date1 = datetime.date.fromisoformat(start_date)
    date2 = datetime.date.fromisoformat(end_date)

    d1 = datetime.date(year=date1.year, month=date1.month, day=1)
    d2 = datetime.date(year=date2.year, month=date2.month + 1, day=1) - datetime.timedelta(days=1)
    dates = [dt for dt in rrule(MONTHLY, dtstart=d1, until=d2)]
    file_names_list = [os.path.join(data_folder,
                                    f'{file_name_root}_{d.year}-{d.month:02d}.{file_extension}') for d in dates]

    out_df = read_monthly_demand_data(file_names_list[0])

    for i in range(1, len(file_names_list)):
        f = file_names_list[i]
        df = read_monthly_demand_data(f)
        out_df = pd.concat([out_df, df], axis=0, join='outer')

    out_df = out_df.loc[(out_df.index.date >= date1) & (out_df.index.date <= date2)]
    return out_df


def read_monthly_demand_data(file_path):
    df = pd.read_csv(file_path)
    df[constants.CONSUMPTION] = df[constants.CONSUMPTION].str.replace(',', '').astype(float)
    df['Date_Time'] = df[['Date', 'Hour']].agg(' '.join, axis=1)
    df['Date_Time'] = pd.to_datetime(df['Date_Time'], dayfirst=True)
    df.drop(columns=['Date', 'Hour'], inplace=True)
    df = df.set_index('Date_Time')
    df.index = pd.to_datetime(df.index)
    df[constants.WEEK_DAY] = df.index.weekday + 1

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
    out_df[constants.HOLIDAY] = False

    for holiday in holidays_list:
        out_df.loc[out_df.index.date == holiday, constants.HOLIDAY] = True

    return out_df


def get_holidays(min_date, max_date):
    constant_holidays = {1: [1], 4: [23], 5: [1, 19], 7: [15], 8: [30], 10: [29], 12: [31]}

    year = min_date.year
    month = min_date.month

    if month in constant_holidays.keys():
        holidays = constant_holidays[month]
    else:
        holidays = []

    f = open(constants.SLIDING_HOLIDAYS_JSON)
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


def convert_hourly_to_daily(df):
    out = pd.DataFrame()
    out[constants.CONSUMPTION] = df.groupby(df.index.date)[constants.CONSUMPTION].sum()
    out[constants.HOLIDAY] = df.groupby(df.index.date)[constants.HOLIDAY].sum()
    out[constants.HOLIDAY] = out[constants.HOLIDAY] > 0
    out[constants.WEEK_DAY] = df.groupby(df.index.date)[constants.WEEK_DAY].mean().astype('int')
    return out


