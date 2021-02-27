import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import copy


@declare_transformation
class baseline(Processor):

    def prepare(self, input_stream, begin_offset, end_offset):
        if not isinstance(input_stream, db.Window):
            raise Exception("BaseLine processor: received data block is not a window.")

        if input_stream.SI.samples < begin_offset:
            raise Exception("BaseLine processor: offset value should not exceed the length of the window.")

        if (input_stream.SI.samples < end_offset) or (begin_offset < -input_stream.SI.samples):
            raise Exception("BaseLine processor: the number of samples for averaging should not exceed the length of "
                            "the window.")

        self._si = si.Window(channels=input_stream.SI.channels,
                             samples=input_stream.SI.samples,
                             samplingRate=input_stream.SI.samplingRate)
        self._averaging_window = slice(begin_offset, end_offset+1)

        return self._si

    def online(self, input_stream):
        windows = copy.deepcopy(input_stream)
        for window in windows:
            window -= np.mean(window[self._averaging_window, :], axis=0)

        return db.Window(self._si, None, windows)

