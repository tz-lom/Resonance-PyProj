import numpy as np




class Base:
    def __init__(self, si, timestamp, *kargs):
        self._si = si
        self._ts = np.asarray(timestamp, dtype=np.longlong)

    @property
    def SI(self):
        return self._si

    @SI.setter
    def SI(self, si):
        self._si = si

    @property
    def TS(self):
        return self._ts

    @TS.setter
    def TS(self, ts):
        self._ts = ts

    def __array_finalize__(self, obj):
        self._si = getattr(obj, '_si', None)
        self._ts = None


class Event(Base, np.chararray):
    def __new__(cls, si, ts, message):
        if isinstance(message, str):
            message = [message]

        obj = np.asarray(message, dtype=np.str).view(Event)

        if isinstance(ts, long) or isinstance(ts, int):
            ts = np.asarray([ts], dtype=np.longlong)

        Base.__init__(obj, si, ts)
        return obj


class Channels(Base, np.ndarray):
    def __new__(cls, si, ts, data):
        obj = np.asarray(data).view(Channels)

        if isinstance(ts, long) or isinstance(ts, int):
            ts = np.asarray([ts - i * 1E9 / si.samplingRate for i in xrange(np.size(obj, 0))], dtype=np.longlong)

        Base.__init__(obj, si, ts)
        return obj

