import numpy as np
from itertools import filterfalse
from typing import Optional


class Base:
    def __new__(cls, si, timestamp: Optional[np.ndarray], *kargs):
        cls._si = si
        cls._ts = timestamp

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
        self._ts = getattr(obj, '_ts', None)

    def __getitem__(self, item):
        ret = np.ndarray.__getitem__(self, item)
        if hasattr(ret, '_ts') and not self._ts is None:
            if isinstance(item, tuple):
                ret._ts = self._ts[item[0]]
            elif isinstance(item, list) or isinstance(item, slice):
                ret._ts = self._ts[item]
        return ret

    @staticmethod
    def combine(*blocks, si=None):
        if si is None:
            si = blocks[0].SI
            if any(map(lambda b: b.SI != si, blocks)):
                raise Exception("All combined must be the same type")
        return si


class Event(Base, np.chararray):
    def __new__(cls, si, ts, message):
        if isinstance(message, np.ndarray):
            obj = np.array(message, dtype=np.object).view(Event)
        else:
            obj = np.empty(1, dtype=np.object).view(Event)
            obj[0] = message

        if isinstance(ts, float) or isinstance(ts, int):
            ts = np.asarray([ts], dtype=np.int64)

        Base.__new__(obj, si, ts)
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Event):
            return (self._si == other._si) and np.array_equal(self._ts, other._ts) and np.array_equal(self, other)
        else:
            return np.array_equal(self[0], other)

    def is_similar(self, other):
        if isinstance(other, Event):
            return self._si.is_similar(other._si) and np.array_equal(self._ts, other._ts) and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    @staticmethod
    def make_empty(si):
        obj = np.empty(0, dtype=np.object).view(Event)
        ts = np.empty(0, dtype=np.int64)
        Base.__new__(obj, si, ts)
        return obj

    @staticmethod
    def combine(*blocks, si=None):
        si = Base.combine(*blocks, si=si)
        message = np.concatenate(blocks)
        if len(message) > 0:
            ts = np.concatenate(list(map(lambda x: x.TS, blocks)))
        else:
            ts = np.empty(0, dtype=np.int64)

        return Event(si, ts, message)


class Channels(Base, np.ndarray):
    def __new__(cls, si, ts, data):
        obj = np.array(data, ndmin=2).view(Channels)

        if len(obj.shape) != 2 or np.size(obj, 1) != si.channels:
            obj = obj.reshape((int(obj.size / si.channels), si.channels))

        if isinstance(ts, int) or isinstance(ts, float):
            ts = np.asarray(ts - np.flip(np.arange(0, np.size(obj, 0))) * 1E9 / si.samplingRate, dtype=np.int64)

        Base.__new__(obj, si, ts)
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Channels):
            return (self._si == other._si) and np.array_equal(self._ts, other._ts) and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    def is_similar(self, other):
        if isinstance(other, Channels):
            return self._si.is_similar(other._si) and np.array_equal(self._ts, other._ts) and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    @staticmethod
    def combine(*blocks, si=None):
        si = Base.combine(*blocks, si=si)
        data = np.concatenate(blocks)
        ts = np.concatenate([block.TS for block in blocks])
        return Channels(si, ts, data)

    @staticmethod
    def make_empty(si):
        obj = np.empty((0, si.channels)).view(Channels)
        ts = np.array([], dtype=np.int64)
        Base.__new__(obj, si, ts)
        return obj


class SingleWindow(np.ndarray):
    def __new__(cls, ts: np.ndarray, data: np.ndarray, metadata: any = None):
        obj = data.view(SingleWindow)
        obj._ts = ts
        obj._metadata = metadata
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, SingleWindow):
            return np.array_equal(self._ts, other._ts) \
                   and np.array_equal(self, other) \
                   and np.array_equal(self.metadata, other.metadata)
        else:
            return np.array_equal(self, other)

    def __array_finalize__(self, obj):
        self._ts = getattr(obj, '_ts', None)
        self._metadata = getattr(obj, '_metadata', None)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def TS(self):
        return self._ts

    @TS.setter
    def TS(self, ts):
        self._ts = ts


class Window(Base, np.ndarray):
    def __new__(cls, si, ts, data, metadata:any = None):

        if isinstance(data, np.ndarray) and (len(data) > 0) and isinstance(data[0], SingleWindow):
            obj = data.view(Window)
            Base.__new__(obj, si, None)
            return obj
        else:
            data = np.asarray(data)
            if len(data) == 0:
                return make_empty(si)
            if len(data.shape) != 2 or np.size(data, 1) != si.channels:
                try:
                    data = data.reshape((si.samples, si.channels))
                except ValueError:
                    raise Exception("Reshape error")

            if np.size(data, 0) != si.samples:
                raise Exception("Invalid window size")

            if not isinstance(ts, np.ndarray):
                ts = ts - np.flip(np.arange(0, np.size(data, 0))) * 1E9 / si.samplingRate

            ts = np.array(ts, dtype=np.int64)

            window = SingleWindow(ts, data, metadata)
            obj = np.ndarray((1,), dtype=object).view(Window)
            obj[0] = window

            Base.__new__(obj, si, None)
            return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Window):
            return (self._si == other._si) \
                   and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    def is_similar(self, other):
        if isinstance(other, Window):
            return self._si.is_similar(other._si) \
                   and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    @property
    def metadata(self):
        return np.asarray([window.metadata for window in self], dtype=object)

    @property
    def TS(self):
        return np.asarray([window.TS[-1] for window in self], dtype=np.int64)

    @staticmethod
    def combine(*blocks, si=None):
        si = Base.combine(*blocks, si=si)
        obj = np.concatenate(blocks).view(Window)
        Base.__new__(obj, si, None)
        return obj

    @staticmethod
    def make_empty(si):
        obj = np.empty(0, dtype=object).view(Window)
        Base.__new__(obj, si, None)
        return obj


class OutputStream(Base):
    def __new__(cls, si):
        obj = object.__new__(cls)
        Base.__new__(obj, si, None)
        return obj

    @staticmethod
    def make_empty(si):
        obj = np.empty(0, dtype=object).view(Window)
        Base.__new__(obj, si, None)
        return obj


def combine(*blocks, si=None):
    return type(blocks[0]).combine(*blocks, si=si)


def make_empty(si):
    return si.db_type.make_empty(si)
