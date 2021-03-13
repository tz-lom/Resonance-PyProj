import resonance.si as si
import resonance.db as db
import numpy as np
from resonance.internal import declare_transformation, Processor


@declare_transformation
class transform_to_event(Processor):
    def __init__(self):
        self._si = None
        self._transform = None

    def prepare(self, input: db.Base, transform):
        self._si = si.Event()
        self._transform = transform
        return self._si

    def online(self, input: db.Base):
        def per_row(i):
            return db.Event(self._si, input.TS[i], self._transform(input[i]))

        return db.combine(*[per_row(i) for i in range(len(input))],
                          si=self._si)
