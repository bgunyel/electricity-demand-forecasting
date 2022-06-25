import datetime

from torch.utils.data import DataLoader
import torch
import numpy as np

import constants
import utils
from data_set import ElectricityDataset
from encoder_decoder import EncoderDecoderRNN


def sin_transform(values, K):
    return np.sin(2 * np.pi * values / K)


def cos_transform(values, K):
    return np.cos(2 * np.pi * values / K)


class ModelHandler:
    def __init__(self, model_params):

        self.scaling_params = {constants.YEAR: {constants.MIN: -1, constants.MAX: -1},
                               constants.CONSUMPTION: {constants.MEAN: -1, constants.STD: -1}}

        self.data_split = {constants.TRAIN: {constants.START: '0000-00-00', constants.END: '0000-00-00'},
                           constants.VALIDATION: {constants.START: '0000-00-00', constants.END: '0000-00-00'},
                           constants.TEST: {constants.START: '0000-00-00', constants.END: '0000-00-00'}}

        self.data_resolution = 'NaN'

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f'Device: {self.device}')

        self.model_params = model_params

        self.model = None

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

        out_df = out_df.drop(
            columns=[constants.YEAR, constants.WEEK_DAY, constants.MONTH, constants.DAY, constants.QUARTER])

        out_df[constants.WEEKEND] = out_df[constants.WEEKEND].astype('float64')
        out_df[constants.SCHOOLS_CLOSED] = out_df[constants.SCHOOLS_CLOSED].astype('float64')
        out_df[constants.RAMAZAN] = out_df[constants.RAMAZAN].astype('float64')
        out_df[constants.HOLIDAY] = out_df[constants.HOLIDAY].astype('float64')
        out_df[constants.BEFORE_AFTER_HOLIDAY] = out_df[constants.BEFORE_AFTER_HOLIDAY].astype('float64')
        out_df[constants.BRIDGE_DAY] = out_df[constants.BRIDGE_DAY].astype('float64')

        return out_df

    def post_process(self, df):
        pass

    def update(self, x_past, x_future, y_future, encoder_optimizer, decoder_optimizer, loss_function):
        target_length = y_future.size(0)
        self.model.train()

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        out = self.model(x_past=x_past, x_future=x_future, y_future=y_future)

        loss = loss_function(out, y_future)
        loss.backward()

        encoder_optimizer.step()
        decoder_optimizer.step()

        return loss.item() / target_length


    def validate(self, validation_loader):
        print('Validate')
        self.model.eval()

    def train(self, df_train, df_validation, data_resolution, param_dict):
        df_tr = self.pre_process(df=df_train, mode=constants.TRAIN, data_resolution=data_resolution)
        df_val = self.pre_process(df=df_validation, mode=constants.VALIDATION, data_resolution=data_resolution)

        self.model = EncoderDecoderRNN(input_sequence_length=self.model_params[constants.INPUT_SEQUENCE_LENGTH],
                                       output_sequence_length=self.model_params[constants.OUTPUT_SEQUENCE_LENGTH],
                                       input_vector_length=df_tr.shape[1],
                                       hidden_vector_size=self.model_params[constants.HIDDEN_LAYER_SIZE],
                                       n_encoder_layers=self.model_params[constants.NUMBER_OF_ENCODER_LAYERS],
                                       teacher_forcing_prob=self.model_params[constants.TEACHER_FORCING_PROB],
                                       device=self.device)

        input_sequence_length = self.model_params[constants.INPUT_SEQUENCE_LENGTH]
        output_sequence_length = self.model_params[constants.OUTPUT_SEQUENCE_LENGTH]

        number_of_training_samples = df_tr.shape[0]
        n_epochs = self.model_params[constants.NUMBER_OF_EPOCHS]

        encoder_optimizer = torch.optim.AdamW(self.model.get_encoder().parameters(), lr=1e-3, weight_decay=1e-2)
        decoder_optimizer = torch.optim.AdamW(self.model.get_decoder().parameters(), lr=1e-3, weight_decay=1e-2)

        loss_function = torch.nn.MSELoss()

        train_loss_matrix = np.zeros((n_epochs, number_of_training_samples - input_sequence_length))

        for epoch in range(n_epochs):
            print(f'EPOCH: {epoch} -- {datetime.datetime.now()}')

            for idx in range(input_sequence_length, number_of_training_samples):
                df_past = df_tr.iloc[idx - input_sequence_length: idx]
                df_future = df_tr.iloc[idx: idx + output_sequence_length]



                x_past = torch.tensor(df_past.values, dtype=torch.float32).to(self.device)
                x_future = torch.tensor(df_future.drop(columns=[constants.CONSUMPTION]).values, dtype=torch.float32).to(
                    self.device)
                y_future = torch.tensor(df_future[constants.CONSUMPTION].values, dtype=torch.float32).to(self.device)

                loss = self.update(x_past=x_past, x_future=x_future, y_future=y_future,
                                   encoder_optimizer=encoder_optimizer, decoder_optimizer=decoder_optimizer,
                                   loss_function=loss_function)

                train_loss_matrix[epoch, idx - input_sequence_length] = loss

                if idx % 240 == 0:
                    print(f'{df_future.index[0]} @ {datetime.datetime.now()}')
                    print(f'Loss: {loss}')

                dummy = -32

        dummy = -32

    def predict(self):
        pass
