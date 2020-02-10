import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import numpy_ringbuffer as np_rb
import math


@declare_transformation
# Split Channels stream to windows using Event stream
# @param input_stream - Channels stream
# @param events       - Events stream
# @param window_size  - size of resulting window
# @param shift        - the shift size of the beginning of data selection in the window (in samples)
# @param late_time    - allowed delay for events (in seconds)
# @return windows for corresponding events
class windowize_by_events(Processor):
    def __init__(self):
        self._events = None
        self._window_size = None
        self._shift = None
        self._signal = None
        self._times = None
        self._si = None

    def prepare(self, input_stream, events, window_size, shift=0, late_time=10):
        if not isinstance(input_stream, db.Channels):
            raise Exception("windowize_by_events processor: data stream must be Channels.")

        if not isinstance(events, db.Event):
            raise Exception("windowize_by_events processor: received events type is not a list object.")

        if input_stream.SI.channels <= 0:
            raise Exception("windowize_by_events processor: invalid channels count.")

        if window_size <= 0:
            raise Exception("windowize_by_events processor: invalid window size.")

        self._events = db.make_empty(events.SI)
        self._window_size = window_size
        self._shift = shift

        max_buffer_size = (math.ceil(late_time * input_stream.SI.samplingRate)) * 2

        self._signal = np_rb.RingBuffer(capacity=max_buffer_size, dtype=(float, (input_stream.SI.channels,)))

        self._times = np_rb.RingBuffer(max_buffer_size, dtype=np.int64)

        self._si = si.Window(input_stream.SI.channels, self._window_size, input_stream.SI.samplingRate)

        return self._si

    def _split_data(self, signal, times, events):
        result = db.make_empty(self._si)

        while len(events) > 0 and len(signal) > 0:
            gs = events.TS[0]

            ts_index = np.array(times).searchsorted(gs)

            if ts_index == 0 and times[0] > gs:
                events = events[1:]
                continue

            if ts_index < len(times):
                pos = ts_index + self._shift

                if pos < 1:
                    events = events[1:]
                    continue

                if len(times) >= (pos + self._window_size):
                    window_range = range(pos, pos + self._window_size)
                    wnd = db.Window(self._si, times[window_range], signal[window_range, ])
                    events = events[1:]
                    result = db.combine(result, wnd)
                    continue
                break
            else:
                break
        return result, events

    def online(self, input_stream, events):
        # combine signal
        self._signal.extend(input_stream)
        self._times.extend(input_stream.TS)

        # combine events
        if len(events) > 0:
            self._events = db.combine(self._events, events)

        (result, self._events) = self._split_data(self._signal, self._times, self._events)

        return result

    def offline(self, input_data, events):
        (result, _) = self._split_data(input_data, input_data.TS, events)

        return result

