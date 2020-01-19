import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import numpy_ringbuffer as np_rb
import math


@declare_transformation
# Split data stream to windows using event stream
# @param data Data stream
# @param events Events stream
# @param windowSize Size of resulting window
# @param backBuffer Size of buffer for data, may be increased in case of big delay in events arrival
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
        self._grabSampleQueue = None
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
        self._grabSampleQueue = np.zeros(0)
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
        # @todo: windowize_by_events processor - implement work with a ring buffer !!!
        # combine signal
        self._signal.extend(input_stream)
        self._times.extend(events)

        # combine events
        if len(events) > 0:
            np.append(self._grabSampleQueue, events)

        result = np.zeros((0, self._si.channels))

        while len(self._grabSampleQueue) > 0:
            gs = self._grabSampleQueue[0]

            moar = self._times.__array__().searchsorted(gs)

            if moar == np.nan:
                raise Exception("windowize_by_events processor: event timestamp has not found in data.")
                #  break

            if (moar > 0) and (moar < len(self._times)):
                pos = moar[0] + 1 + self._shift

                if pos < 1:
                    # early event, drop it
                    del self._grabSampleQueue[-1]
                    continue

                if self._pointer >= (pos + self._window_size):
                    # get window and move on
                    wnd = db.Window(self._si, self._times[pos + self._windowSelector], self._signal[pos + self._windowSelector, ])
                    del self._grabSampleQueue[-1]
                    result.append([wnd])
                    continue

                break  # wait until full window arrives

            else:
                break  # waiting for samples

        if np.size(result, 0) > 0:
            return db.Window(self._si, None, result)
        else:
            return db.Window.make_empty(self._si)

