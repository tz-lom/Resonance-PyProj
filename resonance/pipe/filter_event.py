import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class filter_event(Processor):
    def __init__(self):
        self._si = None
        self._rule = None

    def prepare(self, inp: db.Event, rule):
        if not isinstance(inp, db.Event):
            raise Exception("input must be events")

        self._si = si.Event()
        self._rule = rule
        return self._si

    def online(self, events: db.Event):
        mask = np.fromiter(map(self._rule, events), dtype=bool)
        ret = events[mask]
        ret.SI = self._si
        return ret
