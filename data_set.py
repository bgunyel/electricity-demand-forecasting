from torch.utils.data import Dataset
import torch

import constants


class ElectricityDataset(Dataset):
    def __init__(self, df):
        super().__init__()
        self.df = None
        self.load_data(df=df)

    def load_data(self, df):
        self.df = df

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[[idx]]
        y = torch.tensor(row[constants.CONSUMPTION].values[0], dtype=torch.float32)
        x = [torch.tensor(row.drop([constants.CONSUMPTION]).values[0], dtype=torch.float32)]

        return x, y





