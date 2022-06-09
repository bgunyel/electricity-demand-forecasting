import datetime
from dateutil.rrule import rrule, MONTHLY, DAILY
import json
import os

import pandas as pd
import numpy as np

import constants


def read_demand_data(start_date, end_date, data_folder):
    file_name_root = 'RealTimeConsumption'
    file_extension = 'csv'

    date1 = datetime.date.fromisoformat(start_date)
    date2 = datetime.date.fromisoformat(end_date)

    d1 = datetime.date(year=date1.year, month=date1.month, day=1)

    if date2.month == 12:
        y = date2.year + 1
        m = 1
    else:
        y = date2.year
        m = date2.month + 1

    d2 = datetime.date(year=y, month=m, day=1) - datetime.timedelta(days=1)
    dates = [dt for dt in rrule(MONTHLY, dtstart=d1, until=d2)]
    file_names_list = [os.path.join(data_folder,
                                    f'{file_name_root}_{d.year}-{d.month:02d}.{file_extension}') for d in dates]

    out_df = read_monthly_demand_data(file_names_list[0])

    for i in range(1, len(file_names_list)):
        f = file_names_list[i]
        df = read_monthly_demand_data(f)
        out_df = pd.concat([out_df, df], axis=0, join='outer')

    out_df = out_df.loc[(out_df.index.date >= date1) & (out_df.index.date <= date2)]
    out_df = implement_special_days(out_df)

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

    return df


def implement_special_days(df):
    min_datetime = df.index.min()
    max_datetime = df.index.max()

    years_list = np.unique(df.index.year)

    out_df = df.copy(deep=True)

    #################
    # Ramazan
    #
    # Schools Closed
    #################

    out_df[constants.SCHOOLS_CLOSED] = False
    out_df[constants.RAMAZAN] = False

    for year in years_list:
        ramazan_days_list = get_special_days_as_a_list(year=year, special_day=constants.RAMAZAN)
        the_list = [get_special_days_as_a_list(year=year, special_day=constants.SCHOOLS_WINTER_BREAK),
                    get_special_days_as_a_list(year=year, special_day=constants.SCHOOLS_SPRING_BREAK),
                    get_special_days_as_a_list(year=year, special_day=constants.SCHOOLS_SUMMER_BREAK),
                    get_special_days_as_a_list(year=year, special_day=constants.SCHOOLS_AUTUMN_BREAK)]

        for sub_list in the_list:
            for d in sub_list:
                if (d >= min_datetime.date()) and (d <= max_datetime.date()):
                    out_df.loc[out_df.index.date == d, constants.SCHOOLS_CLOSED] = True

        for d in ramazan_days_list:
            if (d >= min_datetime.date()) and (d <= max_datetime.date()):
                out_df.loc[out_df.index.date == d, constants.RAMAZAN] = True

    ##########################################
    # Official Holidays (National + Religious)
    ##########################################

    out_df[constants.HOLIDAY] = False
    out_df[constants.BEFORE_AFTER_HOLIDAY] = False
    out_df[constants.BRIDGE_DAY] = False

    for year in years_list:
        holidays_list = get_holidays(year=year)

        for sub_list in holidays_list:
            for d in sub_list:
                day_before = d - datetime.timedelta(days=1)
                day_after = d + datetime.timedelta(days=1)

                if (d >= min_datetime.date()) and (d <= max_datetime.date()):
                    out_df.loc[out_df.index.date == d, constants.HOLIDAY] = True
                    out_df.loc[out_df.index.date == d, constants.SCHOOLS_CLOSED] = True

                if is_inside(in_date=day_before, min_date=min_datetime.date(), max_date=max_datetime.date()):
                    out_df.loc[out_df.index.date == day_before, constants.BEFORE_AFTER_HOLIDAY] = True

                    if day_before.isoweekday() == 1:
                        out_df.loc[out_df.index.date == day_before, constants.BRIDGE_DAY] = True

                if is_inside(in_date=day_after, min_date=min_datetime.date(), max_date=max_datetime.date()):
                    out_df.loc[out_df.index.date == day_after, constants.BEFORE_AFTER_HOLIDAY] = True

                    if day_after.isoweekday() == 5:
                        out_df.loc[out_df.index.date == day_after, constants.BRIDGE_DAY] = True

    for year in years_list:
        holidays_list = get_holidays(year=year)

        for sub_list in holidays_list:
            for d in sub_list:
                out_df.loc[out_df.index.date == d, constants.BEFORE_AFTER_HOLIDAY] = False
                out_df.loc[out_df.index.date == d, constants.BRIDGE_DAY] = False

    return out_df


def is_inside(in_date, min_date, max_date):
    out = True if (in_date >= min_date) and (in_date <= max_date) else False
    return out


def get_holidays(year):
    the_list = [get_constant_holidays(year=year),
                get_special_days_as_a_list(year=year, special_day=constants.RAMAZAN_BAYRAM),
                get_special_days_as_a_list(year=year, special_day=constants.KURBAN_BAYRAM)]

    return the_list


def get_constant_holidays(year):
    constant_holidays = ['-01-01', '-04-23', '-05-01', '-05-19', '-07-15', '-08-30', '-10-29', '-12-31']
    out = [datetime.date.fromisoformat(str(year) + s) for s in constant_holidays]
    return out


def get_special_days_as_a_list(year, special_day):
    f = open(constants.SLIDING_HOLIDAYS_JSON)
    data = json.load(f)
    f.close()

    special_days = data[str(year)][special_day]

    dates = []
    if (special_days['start'] not in ['TODO', 'NA']) and (special_days['end'] not in ['TODO', 'NA']):
        d1 = datetime.date.fromisoformat(special_days['start'])
        d2 = datetime.date.fromisoformat(special_days['end'])
        dates = [dt.date() for dt in rrule(DAILY, dtstart=d1, until=d2)]

    return dates


def convert_hourly_to_daily(df):
    out = pd.DataFrame()
    out[constants.CONSUMPTION] = df.groupby(df.index.date)[constants.CONSUMPTION].sum()
    out[constants.WEEK_DAY] = df.groupby(df.index.date)[constants.WEEK_DAY].mean().astype('int')

    out[constants.HOLIDAY] = df.groupby(df.index.date)[constants.HOLIDAY].sum()
    out[constants.HOLIDAY] = out[constants.HOLIDAY] > 0

    out[constants.SCHOOLS_CLOSED] = df.groupby(df.index.date)[constants.SCHOOLS_CLOSED].sum()
    out[constants.SCHOOLS_CLOSED] = out[constants.SCHOOLS_CLOSED] > 0

    out[constants.RAMAZAN] = df.groupby(df.index.date)[constants.RAMAZAN].sum()
    out[constants.RAMAZAN] = out[constants.RAMAZAN] > 0

    out[constants.BEFORE_AFTER_HOLIDAY] = df.groupby(df.index.date)[constants.BEFORE_AFTER_HOLIDAY].sum()
    out[constants.BEFORE_AFTER_HOLIDAY] = out[constants.BEFORE_AFTER_HOLIDAY] > 0

    out[constants.BRIDGE_DAY] = df.groupby(df.index.date)[constants.BRIDGE_DAY].sum()
    out[constants.BRIDGE_DAY] = out[constants.BRIDGE_DAY] > 0

    return out


def read_demand_data_for_all_years():
    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-03-01'

        if year == 2022:
            end_date = f'{year}-05-31'
        else:
            end_date = f'{year}-06-30'

        df_dict[str(year)] = read_demand_data(start_date=start_date,
                                              end_date=end_date,
                                              data_folder=constants.EPIAS_FOLDER)

    return df_dict


def read_daily_demand_data_for_all_years():

    df_dict = read_daily_demand_data_for_all_years()
    hourly_dict = dict()

    for year in df_dict.keys():
        hourly_dict[year] = convert_hourly_to_daily(df=df_dict[year])

    return hourly_dict
