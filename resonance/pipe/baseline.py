import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import copy


def baseline(input_stream: db.Window, averaging_window: slice = slice(None)):
    """
    Return db.Window with baselined data.

    Baseline is calculated per channel as mean of values in slice specified by averaging_window.
    Baseline value is calculated for each window separately.

    :param input_stream: input stream of db.Window type
    :param averaging_window: slice of the window which will be used to calculate mean value default is the full window
    """
    class Impl(Processor):
        def prepare(self, input_stream: db.Window, averaging_window: slice):

            if not isinstance(input_stream, db.Window):
                raise Exception("baseline: input_stream is not a window")

            self._si = si.Window(channels=input_stream.SI.channels,
                                 samples=input_stream.SI.samples,
                                 samplingRate=input_stream.SI.samplingRate)
            self._averaging_window = averaging_window

            return self._si

        def online(self, input_stream):
            windows = copy.deepcopy(input_stream)
            for window in windows:
                window -= np.mean(window[self._averaging_window, :], axis=0)

            return db.Window(self._si, None, windows)

    x = Impl()
    return x.call(input_stream, averaging_window)
