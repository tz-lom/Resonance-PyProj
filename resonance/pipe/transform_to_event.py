import resonance.si as si
import resonance.db as db
import numpy as np
from resonance.internal import declare_transformation, Processor


@declare_transformation
class transform_to_event(Processor):
    def __init__(self):
        self._si = None
        self._transform = None

    def prepare(self, input: db.Base, transform, pass_metadata=False):
        self._si = si.Event()
        self._transform = transform
        self._pass_metadata = pass_metadata
        return self._si

    def online(self, input: db.Base):
        def per_row(i):
            if self._pass_metadata:
                result = self._transform(input[i:i+1])  # use slice to prevent unboxing from container
            else:
                result = self._transform(input[i])
            if isinstance(result, db.Event):
                result.SI = self._si
                return result
            else:
                return db.Event(self._si, input.TS[i], result)

        return db.combine(*[per_row(i) for i in range(len(input))],
                          si=self._si)
