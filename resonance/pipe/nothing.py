from resonance.internal import declare_transformation, Processor
from resonance.db import Base
from copy import deepcopy


@declare_transformation
class nothing(Processor):
    def __init__(self):
        self._si = None

    def prepare(self, data: Base):
        self._si = deepcopy(data.SI)

        return self._si

    def online(self, data: Base):
        ret = deepcopy(data)
        ret._si = self._si

        return ret
