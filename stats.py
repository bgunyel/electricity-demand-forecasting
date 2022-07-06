import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf, pacf

import constants
import utils


def compute_hourly_averages_for_each_day(df):
    df['hour'] = df.index.hour
    out = pd.DataFrame()

    out[constants.MONDAY] = df.loc[df[constants.WEEK_DAY] == 1].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.TUESDAY] = df.loc[df[constants.WEEK_DAY] == 2].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.WEDNESDAY] = df.loc[df[constants.WEEK_DAY] == 3].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.THURSDAY] = df.loc[df[constants.WEEK_DAY] == 4].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.FRIDAY] = df.loc[df[constants.WEEK_DAY] == 5].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.SATURDAY] = df.loc[df[constants.WEEK_DAY] == 6].groupby(by='hour')[constants.CONSUMPTION].mean()
    out[constants.SUNDAY] = df.loc[df[constants.WEEK_DAY] == 7].groupby(by='hour')[constants.CONSUMPTION].mean()

    return out


def examine_covid_impact():
    start_date_before_covid = '2017-01-01'
    end_date_before_covid = '2019-12-31'

    start_date_during_covid = '2020-01-01'
    end_date_during_covid = '2020-12-31'

    start_date_after_covid = '2021-01-01'
    end_date_after_covid = '2022-06-30'

    df_before = utils.read_demand_data(start_date=start_date_before_covid,
                                       end_date=end_date_before_covid,
                                       data_folder=constants.EPIAS_FOLDER)
    df_during = utils.read_demand_data(start_date=start_date_during_covid,
                                       end_date=end_date_during_covid,
                                       data_folder=constants.EPIAS_FOLDER)
    df_after = utils.read_demand_data(start_date=start_date_after_covid,
                                      end_date=end_date_after_covid,
                                      data_folder=constants.EPIAS_FOLDER)

    df_all = utils.read_demand_data(start_date=start_date_before_covid,
                                    end_date=end_date_after_covid,
                                    data_folder=constants.EPIAS_FOLDER)

    hourly_averages_before = compute_hourly_averages_for_each_day(df_before)
    hourly_averages_during = compute_hourly_averages_for_each_day(df_during)
    hourly_averages_after = compute_hourly_averages_for_each_day(df_after)

    hourly_averages_all = compute_hourly_averages_for_each_day(df_all)

    plt.figure(figsize=(18, 8))

    for day in hourly_averages_all.columns:
        plt.plot(hourly_averages_all[day], label=day)
        plt.legend()
        plt.grid(visible=True)
        plt.xlabel('Hour')
        plt.title('Daily Average Consumptions')

    plt.show()

    fig, axes = plt.subplots(1, 3, figsize=(18, 8), sharey='all')

    for day in hourly_averages_before.columns:

        axes[0].plot(hourly_averages_before[day], label=day)
        axes[0].legend()
        axes[0].grid(visible=True)
        axes[0].set_xlabel('Hour')
        axes[0].set_title('Before Covid')

        axes[1].plot(hourly_averages_during[day], label=day)
        axes[1].legend()
        axes[1].grid(visible=True)
        axes[1].set_xlabel('Hour')
        axes[1].set_title('During Covid')

        axes[2].plot(hourly_averages_after[day], label=day)
        axes[2].legend()
        axes[2].grid(visible=True)
        axes[2].set_xlabel('Hour')
        axes[2].set_title('After Covid')

    plt.show()

    dummy = -32


def examine_daily_averages_for_each_year():
    df_dict = utils.read_demand_data_for_all_years()
    hourly_averages_dict = dict()

    years = [*df_dict.keys()]

    for year in years:
        hourly_averages_dict[year] = compute_hourly_averages_for_each_day(df_dict[year])

    days = [*hourly_averages_dict[years[0]].columns]

    fig, axes = plt.subplots(3, 3, figsize=(18, 18), sharey='all')

    for idx, day in enumerate(days):

        for year in years:
            idx_y = idx // 3
            idx_x = idx % 3
            axes[idx_y, idx_x].plot(hourly_averages_dict[year][day], label=year)
            axes[idx_y, idx_x].legend()
            axes[idx_y, idx_x].grid()
            axes[idx_y, idx_x].set_xlabel('Hour')
            axes[idx_y, idx_x].set_title(day)

    plt.show()

    df_dict = utils.compute_daily_average_demand_for_all_years()

    plt.figure(figsize=(18, 8))

    for year in df_dict.keys():
        plt.plot(df_dict[year][constants.AVERAGE], label=year)

    plt.grid(visible=True)
    plt.legend()
    plt.title('Daily Average Consumption (MWh)')
    plt.show()

    dummy = -32


def examine_weekly_averages_for_each_year():

    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-03-01'

        if year == 2022:
            end_date = f'{year}-06-30'
        else:
            end_date = f'{year}-12-31'

        df = utils.read_demand_data(start_date=start_date,
                                    end_date=end_date,
                                    data_folder=constants.EPIAS_FOLDER)
        df_dict[str(year)] = utils.convert_hourly_to_daily(df=df)
        df_dict[str(year)]['day_of_year'] = df_dict[str(year)].index
        df_dict[str(year)]['day_of_year'] = df_dict[str(year)]['day_of_year'].apply(lambda x: x.timetuple().tm_yday)
        df_dict[str(year)]['weekly_average_consumption'] = df_dict[str(year)][constants.CONSUMPTION].rolling(7).mean()
        # df_dict[str(year)].month_day = df_dict[str(year)].month_day.apply(lambda x: f'{x.month:02d}-{x.day:02d}')


    plt.figure(figsize=(18, 8))

    for year in years:
        df = df_dict[str(year)]
        plt.plot(df['day_of_year'], df['weekly_average_consumption'], label=str(year))

    plt.legend()
    plt.grid()
    plt.title('Weekly Average Consumptions')
    plt.xlabel('Index of day in year')
    plt.show()

    dummy = -32


def examine_ramazan_impact():
    dummy = -32

    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-03-01'
        end_date = f'{year}-06-30'

        df = utils.read_demand_data(start_date=start_date,
                                    end_date=end_date,
                                    data_folder=constants.EPIAS_FOLDER)
        df_dict[str(year)] = utils.convert_hourly_to_daily(df=df)
        df_dict[str(year)]['day_of_year'] = df_dict[str(year)].index
        df_dict[str(year)]['day_of_year'] = df_dict[str(year)]['day_of_year'].apply(lambda x: x.timetuple().tm_yday)
        df_dict[str(year)]['weekly_average_consumption'] = df_dict[str(year)][constants.CONSUMPTION].rolling(7).mean()
        # df_dict[str(year)].month_day = df_dict[str(year)].month_day.apply(lambda x: f'{x.month:02d}-{x.day:02d}')

        dummy = -43

    dummy = -32

    plt.figure(figsize=(18, 8))

    for year in years:
        df = df_dict[str(year)]
        plt.plot(df['day_of_year'], df['weekly_average_consumption'], label=str(year))
        plt.plot(df.loc[df[constants.RAMAZAN], 'day_of_year'],
                 df.loc[df[constants.RAMAZAN], 'weekly_average_consumption'],
                 marker='*')
    plt.legend()
    plt.grid()
    plt.title('Ramazan Impact')
    plt.xlabel('Index of day in year')
    plt.show()

    dummy = -32


def examine_schools_impact():
    df_daily_dict = utils.read_daily_demand_data_for_all_years()
    years = [*df_daily_dict.keys()]

    fig, axes = plt.subplots(2, 3, figsize=(18, 8), sharey='all')

    for idx, year in enumerate(years):
        df_daily_dict[year]['day_of_year'] = df_daily_dict[year].index
        df_daily_dict[year]['day_of_year'] = df_daily_dict[year]['day_of_year'].apply(lambda x: x.timetuple().tm_yday)
        df_daily_dict[year]['weekly_average_consumption'] = df_daily_dict[year][constants.CONSUMPTION].rolling(7).mean()

        idx_y = idx // 3
        idx_x = idx % 3

        df = df_daily_dict[year]
        axes[idx_y, idx_x].plot(df['day_of_year'], df['weekly_average_consumption'], label=year)
        axes[idx_y, idx_x].scatter(df.loc[df[constants.SCHOOLS_CLOSED], 'day_of_year'],
                                   df.loc[df[constants.SCHOOLS_CLOSED], 'weekly_average_consumption'],
                                   marker='*', label='Schools Closed', c='r')
        axes[idx_y, idx_x].legend()
        axes[idx_y, idx_x].grid(visible=True)
        axes[idx_y, idx_x].set_xlabel('Index of day in year')
        # axes[axis_id].set_title(title)

    plt.show()

    dummy = -32


def examine_acf():
    start_date = '2017-01-01'
    end_date = '2022-05-31'

    df_hourly = utils.read_demand_data(start_date=start_date, end_date=end_date, data_folder=constants.EPIAS_FOLDER)
    df_daily = utils.convert_hourly_to_daily(df=df_hourly)

    fig, axes = plt.subplots(2, 1, figsize=(18, 8))

    n_lags = 30
    acf_daily = acf(df_daily[constants.CONSUMPTION], nlags=n_lags)
    lags = [*range(0, n_lags + 1)]

    axes[0].stem(lags, acf_daily)
    axes[0].grid(visible=True)
    axes[0].set_title('Daily ACF')

    n_lags = 50
    acf_hourly = acf(df_hourly[constants.CONSUMPTION], nlags=n_lags)
    lags = [*range(0, n_lags + 1)]

    axes[1].stem(lags, acf_hourly)
    axes[1].grid(visible=True)
    axes[1].set_title('Hourly ACF')

    plt.show()

    dummy = -32



