import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
from numpy_ringbuffer import RingBuffer


@declare_transformation
class windowizer(Processor):
    def __init__(self):
        self._si = None
        self._window = None
        self._times = None
        self._unfilled = 0
        self._shift = 0

    def prepare(self, inp: db.Event, size, shift):
        if not isinstance(inp, db.Channels):
            raise Exception("input must be channels")

        self._si = si.Window(inp.SI.channels, size, inp.SI.samplingRate)
        self._window = RingBuffer(size, dtype=(float, (inp.SI.channels,)), allow_overwrite=True)
        self._times = RingBuffer(size, dtype=np.int64, allow_overwrite=True)
        self._unfilled = size
        self._shift = shift
        return self._si

    def online(self, inp: db.Event):
        total = np.size(inp, 0)
        add = total
        result = db.make_empty(self._si)
        while add > 0:
            if add >= self._unfilled:
                segment = inp[total - add: total - add + self._unfilled]
                self._window.extend(segment)
                self._times.extend(segment.TS)

                wnd = db.Window(self._si, np.asarray(self._times), self._window)
                result = db.combine(result, wnd)

                add = add - self._unfilled
                self._unfilled = self._shift
            else:
                self._window.extend(inp)
                self._times.extend(inp.TS)
                self._unfilled -= add
                add = 0

        return result
