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

###########################################################################################
    # May be it's a useless buns: BEGIN
###########################################################################################

    def time_interval(self, x, time):

        if time[[1]] > x:
            return 0

        if time[[len(time.size)]] < x:
            return np.inf

        low = 1
        high = len(time)

        while True:
            if (high - low) <= 1:
                return low

            boundary = math.ceil((high + low) / 2)
            if x > time[[boundary]]:
                low = boundary
            else:
                high = boundary

###########################################################################################
    # May be it's a useless buns: END
###########################################################################################

    def prepare(self, input_stream, events, window_size, shift=0, drop_late_events=True, late_time=10):
        if not isinstance(input_stream, db.Channels):
            raise Exception("windowize_by_events processor: data stream must be Channels.")

        self._signal = np_rb.RingBuffer(input_stream.SI.channels)
        self._pointer = 0
        self._times = np.zeros(self._signal.maxlen)
        self._lastTS = None
        self._lastSample = 0
        self._grabSampleQueue = []
        self._windowSelector = np.arange(1, window_size)
        self._samplingRate = input_stream.SI.samplingRate
        self._window_size = window_size
        self._shift = shift

        if drop_late_events:
            self._shiftBufferTo = math.ceil(late_time*input_stream.SI.samplingRate)
            self._maxBufferSize = self._shiftBufferTo*2
        else:
            self._maxBufferSize = None

        self._si = si.Window(input_stream.SI.channels, window_size, input_stream.SI.samplingRate)
        return self._si

    def online(self, input_stream, events):
        if not isinstance(input_stream, db.Channels):
            raise Exception("windowize_by_events processor: received stream type is not a window.")

        if not isinstance(events, db.Event):
            raise Exception("windowize_by_events processor: received events type is not a list object.")

        # @todo: windowize_by_events processor - implement work with a ring buffer !!!
        # combine signal
        # if input_stream.shape[1] > 0:
        #     if input_stream.shape[1]+self._pointer >= self._signal.maxlen:
        #         tmp = np_rb.RingBuffer(input_stream.SI.channels)

        # combine events
        if len(events) > 0:
            self._grabSampleQueue.append(events)

        result = []

        while len(self._grabSampleQueue) > 0:
            gs = self._grabSampleQueue.TS

            moar = self.time_interval(gs, self._times)

            if (moar > 0) and (moar < len(self._times)):
                pos = moar[1] + 1 + self._shift

                if pos < 1:
                    # early event, drop it
                    del self._grabSampleQueue[-1]
                    continue

                if self._pointer >= (pos + self._window_size):
                    # get window and move on
                    wnd = self._signal[pos + self._windowSelector, ]
                    wnd.TS(self._times[pos + self._windowSelector])
                    del self._grabSampleQueue[-1]
                    result.append([wnd])
                    continue

                break  # wait until full window arrives

            else:
                break  # waiting for samples

        return result


