import pandas as pd
import constants


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