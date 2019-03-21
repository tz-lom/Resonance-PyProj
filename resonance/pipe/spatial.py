import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class spatial(Processor):

    def prepare(self, input, matrix):
        if not isinstance(input, db.Channels):
            raise Exception
        if input.SI.channels != np.size(matrix, 1):
            raise Exception

        self._matrix = matrix
        self._si = si.Channels(channels=input.SI.channels, samplingRate=input.SI.samplingRate)

        return self._si

    def online(self, input):
        ret = np.matmul(input, self._matrix)
        return db.Channels(self._si, input.TS, ret)
