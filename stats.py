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


def examine_covid_impact():
    start_date_before_covid = '2019-01-01'
    end_date_before_covid = '2020-03-10'

    start_date_after_covid = '2020-03-11'
    end_date_after_covid = '2022-05-31'

    df_before = utils.read_demand_data(start_date=start_date_before_covid,
                                       end_date=end_date_before_covid,
                                       data_folder=constants.EPIAS_FOLDER)
    df_after = utils.read_demand_data(start_date=start_date_after_covid,
                                      end_date=end_date_after_covid,
                                      data_folder=constants.EPIAS_FOLDER)

    df_before_daily = utils.convert_hourly_to_daily(df_before)
    df_after_daily = utils.convert_hourly_to_daily(df_after)

    hourly_averages_before = compute_hourly_averages_for_each_day(df_before)
    hourly_averages_after = compute_hourly_averages_for_each_day(df_after)

    for day in hourly_averages_before.columns:
        ax1 = plt.subplot(1, 2, 1)
        plt.plot(hourly_averages_before[day], label=day)
        plt.legend()
        plt.grid()
        plt.title('Before Covid')

        ax2 = plt.subplot(1, 2, 2, sharey=ax1)
        plt.plot(hourly_averages_after[day], label=day)
        plt.legend()
        plt.grid()
        plt.title('After Covid')

    plt.show()

    dummy = -32


def examine_daily_averages_for_each_year():
    df_dict = utils.read_daily_demand_data_for_all_years()
    dummy = -32



def examine_ramazan_impact():
    dummy = -32

    years = [2017, 2018, 2019, 2020, 2021, 2022]
    df_dict = dict()

    for year in years:
        start_date = f'{year}-03-01'

        if year == 2022:
            end_date = f'{year}-05-31'
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


