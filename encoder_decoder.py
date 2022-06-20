import torch.nn as nn
import torch


class UnidirectionalEncoder(nn.Module):
    def __init__(self, n_layers=1, input_feature_len=1, sequence_len=168, hidden_size=100, device='cpu', rnn_dropout=0.2):
        super().__init__()
        self.sequence_len = sequence_len
        self.hidden_size = hidden_size
        self.input_feature_len = input_feature_len
        self.num_layers = n_layers
        self.gru = nn.GRU(
            num_layers=n_layers,
            input_size=input_feature_len,
            hidden_size=hidden_size,
            batch_first=True,
            bidirectional=False,
            dropout=rnn_dropout
        )
        self.device = device

    def forward(self, input_seq):

        h_0 = torch.zeros(self.num_layers, input_seq.size(0), self.hidden_size, device=self.device)

        #if input_seq.ndim < 3:
        #    input_seq.unsqueeze_(2)

        gru_out, hidden = self.gru(input_seq, h_0)

        print(gru_out.shape)
        print(hidden.shape)

        if self.num_layers > 1:
            hidden = hidden.view(self.num_layers, 1, input_seq.size(0), self.hidden_size)
            hidden = hidden[-1]
            hidden = hidden.sum(axis=0)
        else:
            hidden.squeeze_(0)

        return gru_out, hidden

