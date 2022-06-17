import os
import pandas as pd

import constants
import utils
import stats
import model


def experimentation():
    stats.examine_acf()
    stats.examine_schools_impact()
    stats.examine_ramazan_impact()
    stats.examine_covid_impact()
    stats.examine_daily_averages_for_each_year()


def development():
    start_date = '2021-01-01'
    end_date = '2022-05-31'

    df = utils.read_demand_data(start_date=start_date,
                                end_date=end_date,
                                data_folder=constants.EPIAS_FOLDER)

    df_daily = utils.convert_hourly_to_daily(df=df)



def main(params):
    print(params['name'])

    # experimentation()
    # development()

    train_params = {constants.TRAIN_BATCH_SIZE: 128,
                    constants.VALIDATION_BATCH_SIZE: 128}

    data_resolution = constants.HOURLY
    df_dict = utils.train_test_val_split(data_resolution=data_resolution)
    model_handler = model.ModelHandler()
    model_handler.train(df_train=df_dict[constants.TRAIN], data_resolution=data_resolution, param_dict=train_params)


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
