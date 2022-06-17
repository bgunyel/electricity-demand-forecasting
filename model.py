from torch.utils.data import DataLoader
import torch
import numpy as np

import constants
import utils
from data_set import ElectricityDataset


def sin_transform(values, K):
    return np.sin(2 * np.pi * values / K)


def cos_transform(values, K):
    return np.cos(2 * np.pi * values / K)


class ModelHandler:
    def __init__(self):

        self.scaling_params = {constants.YEAR: {constants.MIN: -1, constants.MAX: -1},
                               constants.CONSUMPTION: {constants.MEAN: -1, constants.STD: -1}}

        self.data_split = {constants.TRAIN: {constants.START: '0000-00-00', constants.END: '0000-00-00'},
                           constants.VALIDATION: {constants.START: '0000-00-00', constants.END: '0000-00-00'},
                           constants.TEST: {constants.START: '0000-00-00', constants.END: '0000-00-00'}}

        self.data_resolution = 'NaN'

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f'Device: {self.device}')


    def load_model(self):
        pass


    def save_model(self):
        pass


    def pre_process(self, df, mode, data_resolution):

        out_df = df.copy(deep=True)

        if mode == constants.TRAIN:
            self.scaling_params[constants.YEAR][constants.MIN] = df[constants.YEAR].min()
            self.scaling_params[constants.YEAR][constants.MAX] = df[constants.YEAR].max()

            self.scaling_params[constants.CONSUMPTION][constants.MEAN] = df[constants.CONSUMPTION].mean()
            self.scaling_params[constants.CONSUMPTION][constants.STD] = df[constants.CONSUMPTION].std()

            self.data_resolution = data_resolution

        elif mode in [constants.VALIDATION, constants.TEST]:
            if data_resolution != self.data_resolution:
                raise Exception(f'Data Resolution in {mode} and training are inconsistent!')
        else:
            raise Exception('Operation mode NOT supported!')

        self.data_split[mode][constants.START] = df.index.min().date().isoformat()
        self.data_split[mode][constants.END] = df.index.max().date().isoformat()

        out_df[constants.YEAR_MOD] = \
            (out_df[constants.YEAR] - self.scaling_params[constants.YEAR][constants.MIN]) / \
            (self.scaling_params[constants.YEAR][constants.MAX] - self.scaling_params[constants.YEAR][constants.MIN])

        out_df[constants.WEEK_DAY_SINE] = sin_transform(values=out_df[constants.WEEK_DAY], K=7)
        out_df[constants.WEEK_DAY_COS] = cos_transform(values=out_df[constants.WEEK_DAY], K=7)

        out_df[constants.MONTH_SINE] = sin_transform(values=out_df[constants.MONTH], K=12)
        out_df[constants.MONTH_COS] = cos_transform(values=out_df[constants.MONTH], K=12)

        out_df[constants.DAY_SINE] = sin_transform(values=out_df[constants.DAY], K=31)
        out_df[constants.DAY_COS] = cos_transform(values=out_df[constants.DAY], K=31)

        out_df[constants.QUARTER_SINE] = sin_transform(values=out_df[constants.QUARTER], K=4)
        out_df[constants.QUARTER_COS] = cos_transform(values=out_df[constants.QUARTER], K=4)

        out_df[constants.CONSUMPTION] = \
            (out_df[constants.CONSUMPTION] - self.scaling_params[constants.CONSUMPTION][constants.MEAN]) / \
            self.scaling_params[constants.CONSUMPTION][constants.STD]


        out_df = out_df.drop(columns=[constants.YEAR, constants.WEEK_DAY, constants.MONTH, constants.DAY, constants.QUARTER])

        out_df[constants.WEEKEND] = out_df[constants.WEEKEND].astype('float64')
        out_df[constants.SCHOOLS_CLOSED] = out_df[constants.SCHOOLS_CLOSED].astype('float64')
        out_df[constants.RAMAZAN] = out_df[constants.RAMAZAN].astype('float64')
        out_df[constants.HOLIDAY] = out_df[constants.HOLIDAY].astype('float64')
        out_df[constants.BEFORE_AFTER_HOLIDAY] = out_df[constants.BEFORE_AFTER_HOLIDAY].astype('float64')
        out_df[constants.BRIDGE_DAY] = out_df[constants.BRIDGE_DAY].astype('float64')

        return out_df


    def post_process(self, df):
        pass


    def update(self, train_loader):
        print('Update')


    def validate(self, validation_loader):
        print('Validate')


    def train(self, df_train, df_validation, data_resolution, param_dict):
        df_tr = self.pre_process(df=df_train, mode=constants.TRAIN, data_resolution=data_resolution)
        df_val = self.pre_process(df=df_validation, mode=constants.VALIDATION, data_resolution=data_resolution)

        train_ds = ElectricityDataset(df=df_tr)
        validation_ds = ElectricityDataset(df=df_val)

        train_data_loader = DataLoader(train_ds,
                                       batch_size=param_dict[constants.TRAIN_BATCH_SIZE],
                                       shuffle=True)
        validation_data_loader = DataLoader(validation_ds,
                                            batch_size=param_dict[constants.VALIDATION_BATCH_SIZE],
                                            shuffle=True)

        encoder_optimizer = torch.optim.AdamW(encoder.parameters(), lr=1e-3, weight_decay=1e-2)
        decoder_optimizer = torch.optim.AdamW(decoder_cell.parameters(), lr=1e-3, weight_decay=1e-2)

        encoder_scheduler = optim.lr_scheduler.OneCycleLR(encoder_optimizer, max_lr=1e-3,
                                                          steps_per_epoch=len(train_dataloader), epochs=6)
        decoder_scheduler = optim.lr_scheduler.OneCycleLR(decoder_optimizer, max_lr=1e-3,
                                                          steps_per_epoch=len(train_dataloader), epochs=6)

        for epoch in range(numberOfEpochs):
            self.update(train_loader=train_data_loader, optimizer=optimizer)
            self.validate(validation_loader=validation_data_loader)

            trainingLossVector[epoch] = trLoss
            trainingAccuracyVector[epoch] = trAccuracy
            validationLossVector[epoch] = vlLoss
            validationAccuracyVector[epoch] = vlAccuracy


        for idx, batch in enumerate(train_data_loader):
            x = batch['x']
            y = batch['y']
            print(f'{idx}: {x} -- {y}')
            dummy = -43

        dummy = -32


    def predict(self):
        pass
