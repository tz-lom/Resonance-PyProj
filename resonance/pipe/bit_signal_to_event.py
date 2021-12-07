import resonance.db as db
import resonance.si as si
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class bit_signal_to_event(Processor):
    def __init__(self):
        self._si = None
        self._channel = None
        self._mask = None
        self._rising_edge = None
        self._falling_edge = None
        self._prev = False

    def prepare(self, inp: db.Channels, bit: int, channel: int = 0, rising_edge=True, falling_edge=None):
        if not isinstance(inp, db.Channels):
            raise Exception("input must be channels")

        self._si = si.Event()
        self._channel = channel
        self._mask = 1 << bit
        self._rising_edge = rising_edge
        self._falling_edge = falling_edge
        self._prev = False
        return self._si

    def online(self, inp: db.Channels):
        nothing = db.make_empty(self._si)
        if inp.shape[0] == 0:
            return nothing

        active = np.bitwise_and(inp[:, self._channel], self._mask) > 0
        diff = np.diff(active, prepend=self._prev)

        def create_event(idx):
            # fall
            if not active[idx] and self._falling_edge is not None:
                return db.Event(self._si, inp.TS[idx], self._falling_edge)
            # raise
            if active[idx] and self._rising_edge is not None:
                return db.Event(self._si, inp.TS[idx], self._rising_edge)
            return nothing

        self._prev = active[-1]

        return db.combine(nothing, *[create_event(c) for c in diff.nonzero()[0]])