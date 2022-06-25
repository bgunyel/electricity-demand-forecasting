import torch.nn as nn
import torch
import random


class EncoderRNN(nn.Module):
    def __init__(self,
                 n_layers=1,
                 input_size=1,
                 hidden_size=100,
                 dropout_prob=0.2,
                 device='cpu'):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.input_size = input_size
        self.num_layers = n_layers
        self.gru = nn.GRU(
            num_layers=n_layers,
            input_size=input_size,
            hidden_size=hidden_size,
            bidirectional=False,
            dropout=dropout_prob)
        self.device = device

        self.hidden_state = torch.zeros(self.num_layers, 1, self.hidden_size, device=device)

    def forward(self, x):
        out, hidden = self.gru(x, self.hidden_state)
        self.hidden_state = hidden
        return out

    def initialize_hidden(self):
        # self.hidden_state = torch.zeros(self.num_layers, input_seq.size(0), self.hidden_size, device=self.device)
        self.hidden_state = torch.zeros(self.num_layers, 1, self.hidden_size, device=self.device)

    def get_hidden_state(self):
        return self.hidden_state


class DecoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, device='cpu'):
        super(DecoderRNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.hidden_state = torch.zeros(1, 1, self.hidden_size)
        self.device = device

        self.gru = nn.GRU(input_size=input_size, hidden_size=hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        output, hidden = self.gru(x, self.hidden_state)
        self.hidden_state = hidden
        output = self.fc(output[0])
        return output

    def initialize_hidden(self):
        self.hidden_state = torch.zeros(1, 1, self.hidden_size, device=self.device)

    def set_hidden_state(self, hidden_state):
        self.hidden_state = hidden_state


class EncoderDecoderRNN(nn.Module):
    def __init__(self,
                 input_sequence_length,
                 output_sequence_length,
                 input_vector_length,
                 hidden_vector_size,
                 n_encoder_layers=1,
                 teacher_forcing_prob=0.25,
                 device='cpu'):
        super(EncoderDecoderRNN, self).__init__()

        self.encoder = EncoderRNN(n_layers=n_encoder_layers,
                                  input_size=input_vector_length,
                                  hidden_size=hidden_vector_size,
                                  device=device).to(device)
        self.decoder = DecoderRNN(input_size=input_vector_length,
                                  hidden_size=hidden_vector_size,
                                  output_size=1,
                                  device=device).to(device)
        self.device = device
        self.input_sequence_length = input_sequence_length
        self.output_sequence_length = output_sequence_length
        self.teacher_forcing_prob = teacher_forcing_prob

    def forward(self, x_past, x_future, y_future=None):

        self.encoder.initialize_hidden()
        self.decoder.initialize_hidden()

        teacher_forcing = True if random.random() < self.teacher_forcing_prob else False

        for i in range(self.input_sequence_length):
            out = self.encoder(x=x_past[i].view(1, 1, -1))
        encoder_hidden = self.encoder.get_hidden_state()
        self.decoder.set_hidden_state(encoder_hidden)
        decoder_input = None # TODO

        y_prev = x_past[-1, 0].view(1, 1)


        output = torch.zeros(self.output_sequence_length, device=self.device)

        dummy = -32



        if (y_future is not None) and teacher_forcing:
            for i in range(self.output_sequence_length):
                decoder_input = torch.cat((y_prev, x_future[i].view(-1, 1)), axis=0).view(1, 1, -1)
                output[i] = self.decoder(x=decoder_input)
                y_prev = y_future[i].view(1, 1)
                dummy = -1
        else:
            for i in range(self.output_sequence_length):
                decoder_input = torch.cat((y_prev, x_future[i].view(-1, 1)), axis=0).view(1, 1, -1)
                y_prev = self.decoder(x=decoder_input)
                output[i] = y_prev
                dummy = -3

        return output


    def get_encoder(self):
        return self.encoder

    def get_decoder(self):
        return self.decoder


