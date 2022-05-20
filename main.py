import os
import pandas as pd


from utils import read_demand_data


def main(params):
    print(params['name'])
    print(params['start_date'])
    print(params['end_date'])

    file_name = 'RealTimeConsumption_2021-05.csv'
    input_file_path = os.path.join(params['data_folder'], file_name)

    df = read_demand_data(start_date=params['start_date'],
                          end_date=params['end_date'],
                          data_folder=params['data_folder'])

    dummy = -32


if __name__ == '__main__':
    parameters = {'name': 'Electricity Demand Forecasting',
                  'data_folder': './data/epias/',
                  'output_folder': './out/',
                  'start_date': '2021-04-12',
                  'end_date': '2021-07-19'}

    print('------------------')
    print('STARTED EXECUTION')
    print('------------------')

    main(params=parameters)

    print('------------------')
    print('FINISHED EXECUTION')
    print('------------------')
