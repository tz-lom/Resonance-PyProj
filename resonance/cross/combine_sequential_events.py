import resonance.db as db
import resonance.si as si
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class combine_sequential_events(Processor):
    def __init__(self):
        self._si = None
        self._action = None
        self._expected_proximity = None
        self._first_capture = None
        self._second_capture = None

    def prepare(self, first: db.Event, second: db.Event, action=lambda a,b: (a,b), expected_proximity=1e6):
        if not isinstance(first, db.Event):
            raise Exception("Type of first must be event")

        if not isinstance(second, db.Event):
            raise Exception("Type of second must be event")

        self._si = si.Event()
        self._action = action
        self._expected_proximity = expected_proximity
        self._first_capture = db.make_empty(first.SI)
        self._second_capture = db.make_empty(second.SI)
        return self._si

    def online(self, first: db.Event, second: db.Event):
        self._first_capture = db.combine(self._first_capture, first)
        self._second_capture = db.combine(self._second_capture, second)

        second_ts = self._second_capture.TS
        trim_second = -1
        result = []
        for idx, ts in enumerate(second_ts):
            first_ts = self._first_capture.TS
            if len(first_ts) == 0:
                break
            position = np.searchsorted(first_ts, ts, side='right')
            if position == len(first_ts) and (ts - first_ts[-1] < self._expected_proximity):
                break
            if position == 0:
                trim_second = idx
                continue

            res = self._action(self._first_capture[position - 1], self._second_capture[idx])
            self._first_capture = self._first_capture[position:]
            trim_second = idx
            if isinstance(res, db.Event):
                res.SI = self._si
            else:
                res = db.Event(self._si, second_ts[idx], res)
            result.append(res)
        if trim_second != -1:
            self._second_capture = self._second_capture[trim_second:]

        return db.combine(*result, si=self._si)
