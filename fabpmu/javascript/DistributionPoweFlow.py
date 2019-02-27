import numpy as np
from scipy import sparse as sp
from scipy.sparse.linalg import inv


class DistributionPowerFlow:

    def __init__(self, slack_voltage=1.02):
        self.slack_voltage = slack_voltage
        self.build_network()

    def build_network(self):
        # because this data was taken from MATLAB, 1 was subtracted to match the index
        f = np.asarray([1, 2, 3, 4, 5, 6]) - 1
        t = np.asarray([2, 3, 4, 5, 6, 7]) - 1
        self.nl = len(f)
        self.nb = self.nl + 1
        #       Custom Values
        r = 0.015
        x = 0.01
        F = sp.csc_matrix((np.full(self.nl, 1), (np.arange(self.nl), f)), shape=(self.nl, self.nb))
        T = sp.csc_matrix((np.full(self.nl, 1), (np.arange(self.nl), t)), shape=(self.nl, self.nb))
        M = F - T
        TFT = np.dot(T, np.transpose(F))
        I = sp.eye(TFT.shape[0])
        Rline = r * sp.eye(self.nl)
        Xline = x * sp.eye(self.nl)

        M = M[:, 1:]
        self.R = 2 * np.dot(np.dot(inv(M), Rline), np.dot(inv(I - TFT), T))
        self.X = 2 * np.dot(np.dot(inv(M), Xline), np.dot(inv(I - TFT), T))
        self.update_load()
        # Randomly set the load values

    def update_load(self):
        #        np.random.seed(time.time())
        self.pc = np.random.uniform(low=0.25, high=0.99, size=(self.nb,))
        self.qc = np.random.uniform(low=0.15, high=0.89, size=(self.nb,))
        self.pc[0], self.qc[0] = 0, 0
