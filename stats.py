import pandas as pd
import matplotlib.pyplot as plt

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


def examine_ramazan_impact():
    dummy = -32

    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-03-01'

        if year == 2022:
            end_date = f'{year}-04-30'
        else:
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

    plt.figure()

    for year in years:
        df = df_dict[str(year)]
        plt.plot(df['day_of_year'], df['weekly_average_consumption'], label=str(year))
        plt.plot(df.loc[df[constants.RAMAZAN], 'day_of_year'],
                 df.loc[df[constants.RAMAZAN], 'weekly_average_consumption'],
                 marker='*')
    plt.legend()
    plt.grid()
    plt.show()

    dummy = -32
