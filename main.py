import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt

import constants
import utils
import stats
import model


def experimentation():
    stats.examine_daily_averages_for_each_year()
    stats.examine_daily_averages_for_each_year()
    stats.examine_acf()
    stats.examine_schools_impact()
    stats.examine_ramazan_impact()
    stats.examine_covid_impact()
    stats.examine_daily_averages_for_each_year()


def development():
    dummy = -32


def train():
    model_params = {constants.HOURLY: {constants.INPUT_SEQUENCE_LENGTH: 168,
                                       constants.OUTPUT_SEQUENCE_LENGTH: 24,
                                       constants.NUMBER_OF_ENCODER_LAYERS: 1,
                                       constants.HIDDEN_LAYER_SIZE: 256,
                                       constants.TEACHER_FORCING_PROB: 0.50,
                                       constants.NUMBER_OF_EPOCHS: 1},
                    constants.DAILY: {constants.INPUT_SEQUENCE_LENGTH: 49,
                                      constants.OUTPUT_SEQUENCE_LENGTH: 7,
                                      constants.NUMBER_OF_ENCODER_LAYERS: 1,
                                      constants.HIDDEN_LAYER_SIZE: 256,
                                      constants.TEACHER_FORCING_PROB: 0.50,
                                      constants.NUMBER_OF_EPOCHS: 1}}

    train_params = {constants.HOURLY: {constants.INPUT_SEQUENCE_LENGTH: 168,
                                       constants.OUTPUT_SEQUENCE_LENGTH: 24},
                    constants.DAILY: {constants.INPUT_SEQUENCE_LENGTH: 49,
                                      constants.OUTPUT_SEQUENCE_LENGTH: 7}}

    data_resolution = constants.HOURLY
    df_dict = utils.train_test_val_split(data_resolution=data_resolution)
    model_handler = model.ModelHandler(model_params=model_params[data_resolution])
    model_handler.train(df_train=df_dict[constants.TRAIN],
                        df_validation=df_dict[constants.VALIDATION],
                        data_resolution=data_resolution,
                        param_dict=train_params[data_resolution])


def main(params):
    print(params['name'])

    # experimentation()
    # development()
    train()




    dummy = -32


if __name__ == '__main__':
    parameters = {'name': 'Electricity Demand Forecasting'}

    print('------------------')
    print(f'STARTED EXECUTION @ {datetime.datetime.now()}')
    print('------------------')

    main(params=parameters)

    print('------------------')
    print(f'FINISHED EXECUTION @ {datetime.datetime.now()}')
    print('------------------')
