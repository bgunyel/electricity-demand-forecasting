import os
import pandas as pd

import constants
from utils import read_demand_data, convert_hourly_to_daily
from stats import compute_hourly_averages_for_each_day


def main(params):
    print(params['name'])

    start_date_before_covid = '2017-01-01'
    end_date_before_covid = '2020-03-10'

    start_date_after_covid = '2020-03-11'
    end_date_after_covid = '2022-04-30'

    df_before = read_demand_data(start_date=start_date_before_covid,
                                 end_date=end_date_before_covid,
                                 data_folder=constants.EPIAS_FOLDER)
    df_after = read_demand_data(start_date=start_date_after_covid,
                                end_date=end_date_after_covid,
                                data_folder=constants.EPIAS_FOLDER)

    # df_before_daily = convert_hourly_to_daily(df_before)
    # df_after_daily = convert_hourly_to_daily(df_after)

    hourly_averages_before = compute_hourly_averages_for_each_day(df_before)
    hourly_averages_after = compute_hourly_averages_for_each_day(df_after)

    dummy = -32


if __name__ == '__main__':
    parameters = {'name': 'Electricity Demand Forecasting'}

    print('------------------')
    print('STARTED EXECUTION')
    print('------------------')

    main(params=parameters)

    print('------------------')
    print('FINISHED EXECUTION')
    print('------------------')
