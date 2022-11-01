import datetime
from dateutil.rrule import rrule, MONTHLY, DAILY
import json
import os

import pandas as pd
import numpy as np

import wandb

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

    #########################################
    # Weekend - Year - Month - Day - Quarter
    #########################################
    out_df[constants.WEEKEND] = False
    out_df.loc[out_df[constants.WEEK_DAY].isin([6, 7]), constants.WEEKEND] = True

    out_df[constants.YEAR] = out_df.index.year
    out_df[constants.MONTH] = out_df.index.month
    out_df[constants.DAY] = out_df.index.day
    out_df[constants.QUARTER] = (out_df[constants.MONTH] - 1) // 3 + 1

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
    df_grouped = df.groupby(df.index.date)

    out[constants.CONSUMPTION] = df_grouped[constants.CONSUMPTION].sum()
    out[constants.WEEK_DAY] = df_grouped[constants.WEEK_DAY].mean().astype('int')

    out[constants.WEEKEND] = df_grouped[constants.WEEKEND].sum()
    out[constants.WEEKEND] = out[constants.WEEKEND] > 0

    out[constants.YEAR] = df_grouped[constants.YEAR].mean().astype('int')
    out[constants.MONTH] = df_grouped[constants.MONTH].mean().astype('int')
    out[constants.DAY] = df_grouped[constants.DAY].mean().astype('int')
    out[constants.QUARTER] = df_grouped[constants.QUARTER].mean().astype('int')

    out[constants.SCHOOLS_CLOSED] = df_grouped[constants.SCHOOLS_CLOSED].sum()
    out[constants.SCHOOLS_CLOSED] = out[constants.SCHOOLS_CLOSED] > 0

    out[constants.RAMAZAN] = df_grouped[constants.RAMAZAN].sum()
    out[constants.RAMAZAN] = out[constants.RAMAZAN] > 0

    out[constants.HOLIDAY] = df_grouped[constants.HOLIDAY].sum()
    out[constants.HOLIDAY] = out[constants.HOLIDAY] > 0

    out[constants.BEFORE_AFTER_HOLIDAY] = df_grouped[constants.BEFORE_AFTER_HOLIDAY].sum()
    out[constants.BEFORE_AFTER_HOLIDAY] = out[constants.BEFORE_AFTER_HOLIDAY] > 0

    out[constants.BRIDGE_DAY] = df_grouped[constants.BRIDGE_DAY].sum()
    out[constants.BRIDGE_DAY] = out[constants.BRIDGE_DAY] > 0

    return out


def convert_hourly_to_monthly(df_hourly):
    df_daily = convert_hourly_to_daily(df=df_hourly)
    df_grouped = df_daily.groupby([constants.YEAR, constants.MONTH])

    out = pd.DataFrame()
    out[constants.CONSUMPTION] = df_grouped[constants.CONSUMPTION].sum()
    out.index = out.index.map(lambda idx: f'{idx[0]:02}-{idx[1]:02}')

    return out



def read_demand_data_for_all_years():
    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-01-01'

        if year == 2022:
            end_date = f'{year}-09-30'
        else:
            end_date = f'{year}-12-31'

        df_dict[str(year)] = read_demand_data(start_date=start_date,
                                              end_date=end_date,
                                              data_folder=constants.EPIAS_FOLDER)

    return df_dict


def read_daily_demand_data_for_all_years():
    df_dict = read_demand_data_for_all_years()
    daily_dict = dict()

    for year in df_dict.keys():
        daily_dict[year] = convert_hourly_to_daily(df=df_dict[year])

    return daily_dict


def compute_daily_average_demand_for_all_years():

    df_dict = read_demand_data_for_all_years()

    out_dict = dict()

    for year in df_dict.keys():
        df_dict[year]['hour'] = df_dict[year].index.hour

        out_dict[year] = pd.DataFrame()
        out_dict[year][constants.AVERAGE] = df_dict[year].groupby(by='hour')[constants.CONSUMPTION].mean()

    return out_dict



def train_test_val_split(data_resolution):
    train_start_date = '2017-01-01'
    train_end_date = '2021-12-31'

    validation_start_date = '2022-01-01'
    validation_end_date = '2022-03-31'

    test_start_date = '2022-04-01'
    test_end_date = '2022-06-30'

    train_hourly = read_demand_data(start_date=train_start_date,
                                    end_date=train_end_date,
                                    data_folder=constants.EPIAS_FOLDER)

    validation_hourly = read_demand_data(start_date=validation_start_date,
                                         end_date=validation_end_date,
                                         data_folder=constants.EPIAS_FOLDER)

    test_hourly = read_demand_data(start_date=test_start_date,
                                   end_date=test_end_date,
                                   data_folder=constants.EPIAS_FOLDER)

    out_dict = dict()

    if data_resolution == constants.DAILY:
        out_dict[constants.TRAIN] = convert_hourly_to_daily(df=train_hourly)
        out_dict[constants.VALIDATION] = convert_hourly_to_daily(df=validation_hourly)
        out_dict[constants.TEST] = convert_hourly_to_daily(df=test_hourly)
    elif data_resolution == constants.HOURLY:
        out_dict[constants.TRAIN] = train_hourly
        out_dict[constants.VALIDATION] = validation_hourly
        out_dict[constants.TEST] = test_hourly
    else:
        raise Exception('Unsupported data resolution')

    return out_dict


def generate_wandb_run_name(root):
    time_now = datetime.datetime.now()
    time_now_str = time_now.strftime(format='%Y-%m-%d_%H:%M:%S')
    out = root + '__' + time_now_str
    return out


def upload_as_wandb_artifact(run_group, item, item_name):

    run = wandb.init(project=constants.WANDB_PROJECT_NAME,
                     entity=constants.WANDB_USER_NAME,
                     name=generate_wandb_run_name(root=run_group),
                     group=run_group)

    artifact_name = 'art_' + item_name

    artifact = wandb.Artifact(name=artifact_name, type=run_group)
    artifact.add(item, item_name)
    run.log_artifact(artifact)
    run.finish()


def upload_df_as_wandb_artifact(run_group, df, item_name):
    table = wandb.Table(dataframe=df.reset_index())
    upload_as_wandb_artifact(run_group=run_group, item=table, item_name=item_name)


def increment_months(start_date, months):
    m = (start_date.month + months) % 12
    y = start_date.year + (start_date.month + months) // 12
    d = start_date.day
    out_date = datetime.date(year=y, month=m, day=d)
    return out_date
