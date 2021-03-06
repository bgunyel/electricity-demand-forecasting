import os
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pickle

import constants
import utils
import stats
import model


def experimentation():
    stats.examine_acf()
    stats.examine_daily_averages_for_each_year()
    stats.examine_daily_averages_for_each_year()

    stats.examine_schools_impact()
    stats.examine_ramazan_impact()
    stats.examine_covid_impact()
    stats.examine_daily_averages_for_each_year()


def development():
    dummy = -32


def train(data_resolution, df_train, df_validation):
    model_params = {constants.HOURLY: {constants.INPUT_SEQUENCE_LENGTH: 168,
                                       constants.OUTPUT_SEQUENCE_LENGTH: 24,
                                       constants.NUMBER_OF_ENCODER_LAYERS: 1,
                                       constants.HIDDEN_LAYER_SIZE: 256,
                                       constants.TEACHER_FORCING_PROB: 0.50,
                                       constants.NUMBER_OF_EPOCHS: 15},
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



    model_handler = model.ModelHandler(model_params=model_params[data_resolution])
    model_handler.train(df_train=df_train,
                        df_validation=df_validation,
                        data_resolution=data_resolution,
                        param_dict=train_params[data_resolution])


def test(data_resolution, df_test):
    with open('./out/model_handler_2022-07-06 19:38:48.019984.pkl', 'rb') as file:
        model_handler = pickle.load(file)

    handler = model.ModelHandler(model_params=model_handler.model_params)
    handler.scaling_params = model_handler.scaling_params
    handler.model = model_handler.model
    handler.data_resolution = model_handler.data_resolution
    handler.train_loss_matrix = model_handler.train_loss_matrix
    handler.validation_loss_matrix = model_handler.validation_loss_matrix

    error_matrix = handler.predict(df_test_data=df_test)
    percent_error_matrix = error_matrix * 100
    percent_error_vec = np.mean(percent_error_matrix[168:2160, :], axis=0)
    percent_error = np.mean(percent_error_vec)

    dummy = -32


def main(params):
    print(params['name'])

    data_resolution = constants.HOURLY
    df_dict = utils.train_test_val_split(data_resolution=data_resolution)

    # experimentation()
    # development()
    train(data_resolution=data_resolution, df_train=df_dict[constants.TRAIN], df_validation=df_dict[constants.VALIDATION])
    # test(data_resolution=data_resolution, df_test=df_dict[constants.TEST])





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
