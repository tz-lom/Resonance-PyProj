import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import numpy_ringbuffer as np_rb
import math
import datetime

@declare_transformation
# Split data stream to windows using event stream
# @param data Data stream
# @param events Events stream
# @param windowSize Size of resulting window
# @param dropLateEvents Don't expand buffer infinitely, lateTime controls buffer size and any events that arrive
#                       with timestamp earlier than last data timestamp-lateTime potentially can be dropped
# @param lateTime - allowed delay for events (in seconds)
# @return window
class windowize_by_events(Processor):

    def __init__(self):
        self._signal = None
        self._pointer = None
        self._times = None
        self._lastTS = None
        self._lastSample = None
        self._events = None
        self._windowSelector = None
        self._samplingRate = None
        self._si = None
        self._maxBufferSize = None
        self._shiftBufferTo = None
        self._window_size = None
        self._shift = None

    def prepare(self, input_stream, events, window_size, shift=0, drop_late_events=True, late_time=10):
        if not isinstance(input_stream, db.Channels):
            raise Exception("windowize_by_events processor: data stream must be Channels.")

        if not isinstance(events, db.Event):
            raise Exception("windowize_by_events processor: received events type is not a list object.")

        if input_stream.SI.channels <= 0:
            raise Exception("windowize_by_events processor: invalid channels count.")

        self._pointer = 0
        self._lastTS = None
        self._lastSample = 0
        self._events = db.make_empty(events.SI)
        self._windowSelector = np.arange(0, window_size-1)
        self._samplingRate = input_stream.SI.samplingRate
        self._window_size = window_size
        self._shift = shift

        if drop_late_events:
            self._shiftBufferTo = math.ceil(late_time*input_stream.SI.samplingRate)
            self._maxBufferSize = self._shiftBufferTo*2
        else:
            self._maxBufferSize = math.inf

        self._signal = np_rb.RingBuffer(capacity=self._maxBufferSize, dtype=(float, (input_stream.SI.channels,)))

        self._times = np_rb.RingBuffer(self._maxBufferSize, dtype=np.int64)

        self._si = si.Window(input_stream.SI.channels, self._window_size, input_stream.SI.samplingRate)

        return self._si

    def online(self, input_stream, events):
        # combine signal
        self._signal.extend(input_stream)
        self._times.extend(input_stream.TS)

        # combine events
        if len(events) > 0:
            self._events = db.combine(self._events, events)

        result = db.make_empty(self._si)

        while len(self._events) > 0 and len(self._times) > 0:
            gs = self._events.TS[0]

            ts_index = np.array(self._times).searchsorted(gs)

            if ts_index == 0 and self._times[0] > gs:
                # throw away that event cause data for it could not be received anyway
                self._events = self._events[1:]
                continue

            if ts_index < len(self._times):
                pos = ts_index + self._shift

                if pos < 1:
                    # early event, drop it
                    self._events = self._events[1:]
                    continue

                if len(self._times) >= (pos + self._window_size):
                    # get window and move on
                    window_range = range(pos, pos+self._window_size)
                    wnd = db.Window(self._si, self._times[window_range], self._signal[window_range, ])

                    print('[{}] windowize_by_events.online(): generate window, ID={}, data={}'.format(
                        datetime.datetime.now().time(),
                        wnd.SI.id,
                        wnd))

                    self._events = self._events[1:]

                    result = db.combine(result, wnd)

                    continue

                break  # wait until full window arrives

            else:
                break  # waiting for samples

        return result

    def offline(self, input_data, events_data):
        result = db.make_empty(self._si)

        if len(input_data) <= 0 or len(events_data) <= 0:
            return result

        while len(events_data) > 0:
            gs = events_data.TS[0]

            ts_index = np.array(input_data.TS).searchsorted(gs)

            if ts_index == 0 and input_data.TS[0] > gs:
                events_data = events_data[1:]
                continue

            if ts_index < len(input_data.TS):
                pos = ts_index + self._shift

                if pos < 1:
                    # early event, drop it
                    events_data = events_data[1:]
                    continue

                if len(input_data.TS) >= (pos + self._window_size):
                    window_range = range(pos, pos+self._window_size)
                    wnd = db.Window(self._si, input_data.TS[window_range], input_data[window_range, ])

                    print('[{}] windowize_by_events.offline(): generate window, ID={}, data={}'.format(
                        datetime.datetime.now().time(),
                        wnd.SI.id,
                        wnd))

                    events_data = events_data[1:]
                    result = db.combine(result, wnd)
                    continue
        return result

