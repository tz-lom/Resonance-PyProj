import numpy as np
from itertools import filterfalse


class Base:
    def __new__(cls, si, timestamp, *kargs):
        cls._si = si
        cls._ts = np.asarray(timestamp, dtype=np.int64)

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

    @staticmethod
    def combine(*blocks):
        si = blocks[0].SI
        if len(list(filterfalse(lambda b: b.SI == si, blocks))) > 0:
            raise Exception("All combined must be the same type")


class Event(Base, np.chararray):
    def __new__(cls, si, ts, message):
        if isinstance(message, str):
            message = [message]

        obj = np.asarray(message, dtype=np.str).view(Event)

        if isinstance(ts, float) or isinstance(ts, int):
            ts = np.asarray([ts], dtype=np.longlong)

        Base.__new__(obj, si, ts)
        return obj

    def __eq__(self, other):
        if isinstance(other, Event):
            return (self._si == other._si) and (self._ts == other._ts).all() and np.chararray.__eq__(self, other).all()
        else:
            return np.chararray.__eq__(self, other)


class Channels(Base, np.ndarray):
    def __new__(cls, si, ts, data):
        obj = np.asarray(data).view(Channels)

        if len(obj.shape) != 2 or np.size(obj, 1) != si.channels:
            obj = obj.reshape((int(obj.size / si.channels), si.channels))

        if isinstance(ts, int) or isinstance(ts, float):
            ts = ts - np.flip(np.arange(0, np.size(obj, 0))) * 1E9/si.samplingRate

        Base.__new__(obj, si, ts)
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Channels):
            return (self._si == other._si) and np.array_equal(self._ts, other._ts) and np.array_equal(self, other)
        else:
            return np.ndarray.__eq__(self, other)

    @staticmethod
    def combine(*blocks):
        Base.combine(*blocks)
        data = np.concatenate(blocks)
        ts = np.concatenate(list(map(lambda x: x.TS, blocks)))
        return Channels(blocks[0].SI, ts, data)

    @staticmethod
    def make_empty(si):
        obj = np.empty((0, si.channels)).view(Channels)
        ts =  np.array([], dtype=np.int64)
        Base.__new__(obj, si, ts)
        return obj


class OutputStream(Base):
    def __new__(cls, si):
        obj = object.__new__(cls)
        Base.__new__(obj, si, 0)
        return obj


def combine(*blocks):
    return type(blocks[0]).combine(*blocks)


def make_empty(si):
    return si.db_type.make_empty(si)
