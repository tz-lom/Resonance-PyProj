import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
from typing import Union, Callable, List


@declare_transformation
class split(Processor):
    def __init__(self):
        self._streams = None
        self._rule = None

    def prepare(self, inp: Union[db.Event, db.Window], outputs: int,
                rule: Callable[[Union[db.Event, db.Window]], Union[bool, int, List[int], List[bool], np.ndarray]]):
        if not (isinstance(inp, db.Event) or isinstance(inp, db.Window)):
            raise Exception("input is unsupported")

        self._streams = tuple(inp.SI.clone() for i in range(outputs))
        self._rule = rule
        return self._streams

    def online(self, inp: Union[db.Event, db.Window]):
        mask = np.zeros((len(self._streams), len(inp)), dtype=bool)

        for idx, elem in enumerate(inp):
            opts = self._rule(elem)
            mask[opts, idx] = True

        def filter_input(si_and_mask):
            (si, mask_for_stream) = si_and_mask
            ret = inp[mask_for_stream]
            ret.SI = si
            return ret

        return tuple(map(filter_input, zip(self._streams, mask)))
