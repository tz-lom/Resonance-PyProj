import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import copy


@declare_transformation
class baseline(Processor):

    def prepare(self, input, begin_offset, end_offset):
        if not isinstance(input, db.Window):
            raise Exception("BaseLine processor: received data block is not a window.")

        if input.SI.samples < begin_offset:
            raise Exception("BaseLine processor: offset value should not exceed the length of the window.")

        if (input.SI.samples < end_offset) or (input.SI.samples < begin_offset):
            raise Exception("BaseLine processor: the number of samples for averaging should not exceed the length of "
                            "the window.")

        self._si = si.Window(channels=input.SI.channels, samples=input.SI.samples, samplingRate=input.SI.samplingRate)
        self._begin_offset = begin_offset
        self._end_offset = end_offset
        self._averaging_window = slice(self._begin_offset, self._end_offset)

        return self._si

    def online(self, input):
        windows = copy.deepcopy(input)
        for window in windows:
            window -= np.mean(window[self._averaging_window, :])

        return db.Window(self._si, input.TS, windows)
