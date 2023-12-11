import numpy as np
from typing import Optional, Any, List
import numbers


def si_from_blocks(*blocks, si=None):
    if si is None:
        si = blocks[0].SI
        if any(map(lambda b: b.SI != si, blocks)):
            raise Exception("All combined must be the same type")
    return si


class Base(np.ndarray):
    def __new__(cls, si, timestamp: Optional[np.ndarray], *kargs):
        cls._si = si
        cls._ts = timestamp

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._si = getattr(obj, "_si", None)
        self._ts = getattr(obj, "_ts", None)

    def __reduce__(self):
        pickled = super(Base, self).__reduce__()
        return pickled[0], pickled[1], pickled[2] + (self.__dict__,)

    def __setstate__(self, state):
        self.__dict__.update(state[-1])
        super(Base, self).__setstate__(state[0:-1])

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
        self._si = getattr(obj, "_si", None)
        self._ts = getattr(obj, "_ts", None)

    def __getitem__(self, index):
        if not isinstance(index, tuple):
            index = (index,)
        ret = np.ndarray.__getitem__(self, index)
        if isinstance(ret, type(self)) and self._ts is not None:
            ret._ts = self._ts[index[0]]
        return ret

    def clone(self, new_si: None):
        copy = np.copy(self)
        if new_si is not None:
            copy._si = new_si
        return copy


class Event(Base):
    def __new__(cls, si, ts, message):
        obj = np.empty(1, dtype=object).view(Event)
        obj[0] = message

        timestamp = np.empty(1, dtype=np.int64)
        if isinstance(ts, np.ndarray):
            timestamp[0] = np.squeeze(ts)
        else:
            timestamp[0] = ts

        Base.__new__(obj, si, timestamp)
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Event):
            return (
                (self._si == other._si)
                and np.array_equal(self._ts, other._ts)
                and np.array_equal(self, other)
            )
        else:
            return np.array_equal(self[0], other)

    def is_similar(self, other):
        if isinstance(other, Event):
            return (
                self._si.is_similar(other._si)
                and np.array_equal(self._ts, other._ts)
                and np.array_equal(self, other)
            )
        else:
            return np.array_equal(self, other)

    @staticmethod
    def make_empty(si):
        obj = np.empty(0, dtype=object).view(Event)
        ts = np.empty(0, dtype=np.int64)
        Base.__new__(obj, si, ts)
        return obj

    @staticmethod
    def combine(*blocks, si=None):
        si = si_from_blocks(*blocks, si=si)
        if len(blocks) > 1:
            obj = np.concatenate(blocks).view(Event)
        else:
            obj = blocks[0]
        if len(blocks) > 0:
            ts = np.concatenate(list(map(lambda x: x.TS, blocks)))
        else:
            ts = np.empty(0, dtype=np.int64)
        Base.__new__(obj, si, ts)
        return obj


class Channels(Base):
    def __new__(cls, si, ts, data):
        obj = np.array(data, ndmin=2).view(Channels)

        if len(obj.shape) != 2 or np.size(obj, 1) != si.channels:
            obj = obj.reshape((int(obj.size / si.channels), si.channels))

        if isinstance(ts, numbers.Number):
            ts = np.asarray(
                ts - np.flip(np.arange(0, np.size(obj, 0))) * 1e9 / si.samplingRate,
                dtype=np.int64,
            )
        else:
            ts = np.asarray(ts, dtype=np.int64)

        Base.__new__(obj, si, ts)
        return obj

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Channels):
            return (
                (self._si == other._si)
                and np.array_equal(self._ts, other._ts)
                and np.array_equal(self, other)
            )
        else:
            return np.array_equal(self, other)

    def is_similar(self, other):
        if isinstance(other, Channels):
            return (
                self._si.is_similar(other._si)
                and np.array_equal(self._ts, other._ts)
                and np.array_equal(self, other)
            )
        else:
            return np.array_equal(self, other)

    @staticmethod
    def combine(*blocks, si=None):
        si = si_from_blocks(*blocks, si=si)
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
    def __new__(cls, timestamps: np.ndarray, data: np.ndarray, metadata: Any = None):
        obj = data.view(SingleWindow)
        obj._timestamps = timestamps
        obj._metadata = metadata
        return obj

    def __array_finalize(self, obj):
        if obj is None:
            return
        self._timestamps = getattr(obj, "_timestamps", None)
        self._metadata = getattr(obj, "_metadata", None)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, SingleWindow):
            return (
                np.array_equal(self._timestamps, other._timestamps)
                and np.array_equal(self, other)
                and np.array_equal(self.metadata, other.metadata)
            )
        else:
            return np.array_equal(self, other)

    def __array_finalize__(self, obj):
        self._timestamps = getattr(obj, "_timestamps", None)
        self._metadata = getattr(obj, "_metadata", None)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def timestamps(self):
        return self._timestamps

    @timestamps.setter
    def timestamps(self, ts):
        self._timestamps = ts


class Window(Base):
    def __new__(cls, si, ts, data, metadata: Any = None):
        if (
            isinstance(data, np.ndarray)
            and (len(data) > 0)
            and isinstance(data[0], SingleWindow)
        ):
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
                ts = (
                    ts - np.flip(np.arange(0, np.size(data, 0))) * 1e9 / si.samplingRate
                )

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
            return (self._si == other._si) and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    def is_similar(self, other):
        if isinstance(other, Window):
            return self._si.is_similar(other._si) and np.array_equal(self, other)
        else:
            return np.array_equal(self, other)

    @property
    def metadata(self):
        return np.asarray([window.metadata for window in self], dtype=object)

    @property
    def TS(self):
        return np.asarray([window.timestamps[-1] for window in self], dtype=np.int64)

    @staticmethod
    def combine(*blocks, si=None):
        si = si_from_blocks(*blocks, si=si)
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
        obj = np.empty(0, dtype=object).view(OutputStream)
        Base.__new__(obj, si, None)
        return obj

    @staticmethod
    def make_empty(si):
        obj = np.empty(0, dtype=object).view(OutputStream)
        Base.__new__(obj, si, None)
        return obj


def combine(*blocks, si=None):
    if si is None:
        return type(blocks[0]).combine(*blocks, si=si)
    else:
        if len(blocks) == 0:
            return make_empty(si)
        else:
            return si.db_type.combine(*blocks, si=si)


def make_empty(si):
    return si.db_type.make_empty(si)


def sort_by_timestamp(blocks: List[Base]) -> List[Base]:
    return sorted(blocks, key=lambda b: b.TS[0])
