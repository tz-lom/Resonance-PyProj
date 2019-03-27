import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import copy


@declare_transformation
class baseline(Processor):

    def prepare(self, input, beginOffset, endOffset):
        if not isinstance(input, db.Window):
            raise Exception("BaseLine processor: received data block is not a window.")

        if input.SI.samples < beginOffset:
            raise Exception("BaseLine processor: offset value should not exceed the length of the window.")

        if (input.SI.samples < endOffset) or (input.SI.samples < beginOffset):
            raise Exception("BaseLine processor: the number of samples for averaging should not exceed the length of "
                            "the window.")

        self._si = si.Window(channels=input.SI.channels, samples=input.SI.samples, samplingRate=input.SI.samplingRate)
        self._beginOffset = beginOffset
        self._endOffset = endOffset

        return self._si

    def online(self, input):
        windows = copy.deepcopy(input)

        for window in windows:
            for channel in window:
                channel -= np.mean(channel[range(self._beginOffset, self._endOffset)])

        return windows
        # return db.Window(self._si, input.TS, windows)

