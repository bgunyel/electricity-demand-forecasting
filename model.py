import numpy as np

import constants
import utils


def sin_transform(values, K):
    return np.sin(2 * np.pi * values / K)


def cos_transform(values, K):
    return np.cos(2 * np.pi * values / K)


class ModelHandler:
    def __init__(self):
        self.min_year = -1
        self.max_year = -1

    def pre_process(self, df, mode):

        out_df = df.copy(deep=True)

        if mode == constants.TRAIN:
            self.min_year = df[constants.YEAR].min()
            self.max_year = df[constants.YEAR].max()
        elif mode == constants.TEST:
            pass
        else:
            raise Exception('Operation mode not supported!')

        out_df[constants.YEAR_MOD] = (out_df[constants.YEAR] - self.min_year) / (self.max_year - self.min_year)

        out_df[constants.WEEK_DAY_SINE] = sin_transform(values=out_df[constants.WEEK_DAY], K=7)
        out_df[constants.WEEK_DAY_COS] = cos_transform(values=out_df[constants.WEEK_DAY], K=7)

        out_df[constants.MONTH_SINE] = sin_transform(values=out_df[constants.MONTH], K=12)
        out_df[constants.MONTH_COS] = cos_transform(values=out_df[constants.MONTH], K=12)

        out_df[constants.DAY_SINE] = sin_transform(values=out_df[constants.DAY], K=31)
        out_df[constants.DAY_COS] = cos_transform(values=out_df[constants.DAY], K=31)

        out_df[constants.QUARTER_SINE] = sin_transform(values=out_df[constants.QUARTER], K=4)
        out_df[constants.QUARTER_COS] = cos_transform(values=out_df[constants.QUARTER], K=4)


        dummy = -32




    def train(self, df_train):
        self.pre_process(df=df_train)


    def predict(self):
        pass
