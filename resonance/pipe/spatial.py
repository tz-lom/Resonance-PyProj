import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class spatial(Processor):
    def __init__(self):
        self._matrix = None
        self._si = None

    def prepare(self, channels: db.Channels, matrix: np.ndarray):
        """
        :param channels: db.Channels
        :param matrix: np.ndarray
        :return:
        """
        if not isinstance(channels, db.Channels):
            raise Exception("Input must be Channels")
        if len(matrix.shape) != 2:
            raise Exception("Matrix should be 2 dimensional")
        if channels.SI.channels != np.size(matrix, 0):
            raise Exception("Number of rows in matrix should match number of channels")

        self._matrix = matrix
        self._si = si.Channels(
            channels=np.size(matrix, 1), samplingRate=channels.SI.samplingRate
        )

        return self._si

    def online(self, channels):
        ret = np.matmul(channels, self._matrix)
        return db.Channels(self._si, channels.TS, ret)
