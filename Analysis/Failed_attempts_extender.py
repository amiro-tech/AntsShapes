import numpy as np
from Analysis.PathPy.network_functions import Network


class FailedAttempt:
    def __init__(self, name, path_length, time, final_state):
        self.name = name
        self.path_length = path_length
        self.time = time
        self.final_state = final_state

    def mean_speed(self) -> float:
        return self.path_length/self.time


class FailedAttemptPathLengthExtender:
    def __init__(self, failedAttempt: FailedAttempt, fundamental_matrix: np.array):
        """
        fundamental matrix must contain self_loops, or I have to define mean time spent in a certain state.
        """
        self.failedAttempt = failedAttempt
        self.fundamental_matrix = fundamental_matrix

    def expected_solving_time(self) -> float:
        t = np.matmul(self.fundamental_matrix, np.ones([1, self.fundamental_matrix.shape[0]]))
        return float()

    def expected_additional_path_length(self) -> float:
        return self.failedAttempt.mean_speed() * self.expected_solving_time()
