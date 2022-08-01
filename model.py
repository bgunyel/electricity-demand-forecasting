import datetime
import pickle
import copy

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
        self.train_loss_matrix = None
        self.validation_loss_matrix = None

    def initialize_model(self, source_model=None):
        self.model = EncoderDecoderRNN(input_sequence_length=self.model_params[constants.INPUT_SEQUENCE_LENGTH],
                                       output_sequence_length=self.model_params[constants.OUTPUT_SEQUENCE_LENGTH],
                                       input_vector_length=self.model_params[constants.INPUT_VECTOR_LENGTH],
                                       hidden_vector_size=self.model_params[constants.HIDDEN_LAYER_SIZE],
                                       n_encoder_layers=self.model_params[constants.NUMBER_OF_ENCODER_LAYERS],
                                       teacher_forcing_prob=self.model_params[constants.TEACHER_FORCING_PROB],
                                       device=self.device)

    def copy_from(self, model_handler):

        print(f'TODO: Model Params copying shall be corrected!')
        self.model_params = copy.deepcopy(model_handler.model_params)
        self.model_params[constants.INPUT_VECTOR_LENGTH] = 18

        self.scaling_params = copy.deepcopy(model_handler.scaling_params)
        self.data_resolution = copy.deepcopy(model_handler.data_resolution)

        self.train_loss_matrix = copy.deepcopy(model_handler.train_loss_matrix)
        self.validation_loss_matrix = copy.deepcopy(model_handler.validation_loss_matrix)

        self.initialize_model(source_model=model_handler)

        print(f'-- DEBUG START --')

        encoder_params_dict = dict()
        decoder_params_dict = dict()

        for pn, p in model_handler.model.encoder.named_parameters():
            encoder_params_dict[pn] = p

        for pn, p in model_handler.model.decoder.named_parameters():
            decoder_params_dict[pn] = p

        for pn, p in self.model.encoder.named_parameters():
            p.data = encoder_params_dict[pn].data.to(self.device)

        for pn, p in self.model.decoder.named_parameters():
            p.data = decoder_params_dict[pn].data.to(self.device)


        print(f'-- DEBUG END --')

        dummy = -32

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

        if data_resolution == constants.HOURLY:
            out_df[constants.HOUR] = out_df.index.hour
            out_df[constants.HOUR_SINE] = sin_transform(values=out_df[constants.HOUR], K=24)
            out_df[constants.HOUR_COS] = cos_transform(values=out_df[constants.HOUR], K=24)
            out_df = out_df.drop(columns=[constants.HOUR])

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

        if mode == constants.TRAIN:
            self.model_params[constants.INPUT_VECTOR_LENGTH] = out_df.shape[1]

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

    def validate(self, df_val, loss_function, input_sequence_length, output_sequence_length):
        self.model.eval()

        number_of_validation_samples = df_val.shape[0]
        loss = 0

        with torch.no_grad():
            for idx in range(input_sequence_length, number_of_validation_samples - output_sequence_length):
                df_past = df_val.iloc[idx - input_sequence_length: idx]
                df_future = df_val.iloc[idx: idx + output_sequence_length]

                x_past = torch.tensor(df_past.values, dtype=torch.float32).to(self.device)
                x_future = torch.tensor(df_future.drop(columns=[constants.CONSUMPTION]).values, dtype=torch.float32).to(
                    self.device)
                y_future = torch.tensor(df_future[constants.CONSUMPTION].values, dtype=torch.float32).to(self.device)

                out = self.model(x_past=x_past, x_future=x_future, y_future=y_future)
                loss += loss_function(out, y_future)

        loss = loss / number_of_validation_samples

        return loss

    def train(self, df_train, df_validation, data_resolution, param_dict):
        df_tr = self.pre_process(df=df_train, mode=constants.TRAIN, data_resolution=data_resolution)
        df_val = self.pre_process(df=df_validation, mode=constants.VALIDATION, data_resolution=data_resolution)

        self.initialize_model()

        input_sequence_length = self.model_params[constants.INPUT_SEQUENCE_LENGTH]
        output_sequence_length = self.model_params[constants.OUTPUT_SEQUENCE_LENGTH]

        number_of_training_samples = df_tr.shape[0]
        n_epochs = self.model_params[constants.NUMBER_OF_EPOCHS]

        encoder_optimizer = torch.optim.AdamW(self.model.get_encoder().parameters(), lr=1e-3, weight_decay=1e-2)
        decoder_optimizer = torch.optim.AdamW(self.model.get_decoder().parameters(), lr=1e-3, weight_decay=1e-2)

        loss_function = torch.nn.MSELoss()

        validation_period = 240

        self.train_loss_matrix = np.zeros((n_epochs, number_of_training_samples - input_sequence_length))
        self.validation_loss_matrix = np.zeros((n_epochs, number_of_training_samples - input_sequence_length))

        for epoch in range(n_epochs):
            print(f'EPOCH: {epoch} -- {datetime.datetime.now()}')

            for idx in range(input_sequence_length, number_of_training_samples - output_sequence_length):
                df_past = df_tr.iloc[idx - input_sequence_length: idx]
                df_future = df_tr.iloc[idx: idx + output_sequence_length]

                x_past = torch.tensor(df_past.values, dtype=torch.float32).to(self.device)
                x_future = torch.tensor(df_future.drop(columns=[constants.CONSUMPTION]).values, dtype=torch.float32).to(
                    self.device)
                y_future = torch.tensor(df_future[constants.CONSUMPTION].values, dtype=torch.float32).to(self.device)

                train_loss = self.update(x_past=x_past, x_future=x_future, y_future=y_future,
                                         encoder_optimizer=encoder_optimizer, decoder_optimizer=decoder_optimizer,
                                         loss_function=loss_function)

                self.train_loss_matrix[epoch, idx - input_sequence_length] = train_loss

                if (idx - input_sequence_length) % validation_period == 0:
                    validation_loss = self.validate(df_val=df_val,
                                                    loss_function=loss_function,
                                                    input_sequence_length=input_sequence_length,
                                                    output_sequence_length=output_sequence_length)
                    self.validation_loss_matrix[epoch, idx - input_sequence_length] = validation_loss

                    print(f'{df_future.index[0]} @ {datetime.datetime.now()}')
                    print(f'Train Loss: {train_loss}')
                    print(f'Validation Loss: {validation_loss}')

                    dummy = -32

            self.save()  # save after each epoch

        dummy = -32

    def predict(self, df_test_data):
        print('PREDICT')

        df_test = self.pre_process(df=df_test_data, mode=constants.TEST, data_resolution=self.data_resolution)

        self.model.eval()
        number_of_test_samples = df_test.shape[0]

        input_sequence_length = self.model_params[constants.INPUT_SEQUENCE_LENGTH]
        output_sequence_length = self.model_params[constants.OUTPUT_SEQUENCE_LENGTH]

        error_matrix = np.zeros((number_of_test_samples, output_sequence_length))

        with torch.no_grad():
            for idx in range(input_sequence_length, number_of_test_samples - output_sequence_length):
                df_past = df_test.iloc[idx - input_sequence_length: idx]
                df_future = df_test.iloc[idx: idx + output_sequence_length]

                x_past = torch.tensor(df_past.values, dtype=torch.float32).to(self.device)
                x_future = torch.tensor(df_future.drop(columns=[constants.CONSUMPTION]).values, dtype=torch.float32).to(
                    self.device)
                y_future = torch.tensor(df_future[constants.CONSUMPTION].values, dtype=torch.float32).to(self.device)
                out = self.model(x_past=x_past, x_future=x_future, y_future=y_future)

                y_gt = y_future * self.scaling_params[constants.CONSUMPTION][constants.STD] + \
                       self.scaling_params[constants.CONSUMPTION][constants.MEAN]
                y_pred = out * self.scaling_params[constants.CONSUMPTION][constants.STD] + \
                         self.scaling_params[constants.CONSUMPTION][constants.MEAN]

                y_gt_cpu = y_gt.cpu()
                y_pred_cpu = y_pred.cpu()
                error_matrix[idx, :] = abs(y_gt_cpu - y_pred_cpu) / y_gt_cpu

                dummy = -32

        return error_matrix

    def save(self):
        model_name = f'./out/model_handler_{datetime.datetime.now()}.pkl'
        with open(model_name, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
