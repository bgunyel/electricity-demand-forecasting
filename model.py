from torch.utils.data import DataLoader
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



    def pre_process(self, df, mode):

        out_df = df.copy(deep=True)

        if mode == constants.TRAIN:
            self.scaling_params[constants.YEAR][constants.MIN] = df[constants.YEAR].min()
            self.scaling_params[constants.YEAR][constants.MAX] = df[constants.YEAR].max()

            self.scaling_params[constants.CONSUMPTION][constants.MEAN] = df[constants.CONSUMPTION].mean()
            self.scaling_params[constants.CONSUMPTION][constants.STD] = df[constants.CONSUMPTION].std()
        elif mode == constants.TEST:
            pass
        else:
            raise Exception('Operation mode not supported!')

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


    def train(self, df_train):
        df = self.pre_process(df=df_train, mode=constants.TRAIN)
        train_ds = ElectricityDataset(df=df)

        train_data_loader = DataLoader(train_ds, batch_size=128, shuffle=True)

        for idx, batch in enumerate(train_data_loader):
            x, y = 

        dummy = -32


    def predict(self):
        pass
