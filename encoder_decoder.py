import torch.nn as nn
import torch
import random


class EncoderRNN(nn.Module):
    def __init__(self,
                 n_layers=1,
                 input_size=1,
                 hidden_size=100,
                 device='cpu',
                 dropout_prob=0.2):
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
        self.hidden_state = torch.zeros(self.num_layers, 1, self.hidden_size, device=self.device)

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
        self.device = device
        self.hidden_state = torch.zeros(1, 1, self.hidden_size, device=self.device)

        self.gru = nn.GRU(input_size=input_size, hidden_size=hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        output, hidden = self.gru(x, self.hidden_state)
        self.hidden_state = hidden
        output = self.fc(output[0])
        return output, hidden

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
                                  device=device)
        self.decoder = DecoderRNN(input_size=input_vector_length-1,
                                  hidden_size=hidden_vector_size,
                                  output_size=1,
                                  device=device)
        self.device = device
        self.input_sequence_length = input_sequence_length
        self.output_sequence_length = output_sequence_length
        self.teacher_forcing_prob = teacher_forcing_prob

    def forward(self, x_past, x_future, y_future=None):

        self.encoder.initialize_hidden()
        self.decoder.initialize_hidden()

        teacher_forcing = True if random.random() < self.teacher_forcing_prob else False

        for i in range(self.input_sequence_length):
            out = self.encoder(x=x_past[i])
        encoder_hidden = self.encoder.get_hidden_state()
        self.decoder.set_hidden_state(encoder_hidden)
        decoder_input = None # TODO

        if (y_future is not None) and teacher_forcing:
            pass
        else:
            pass


