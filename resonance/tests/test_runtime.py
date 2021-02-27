from resonance.tests.TestProcessor import TestProcessor
import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np


@declare_transformation
class DummyTransformation(Processor):
    def __init__(self):
        self._si = None

    def prepare(self, a, b):
        self._si = si.Event()
        return self._si

    def online(self, a, b):
        if len(a) > 0:
            return db.Event(self._si, a.TS, a[0])
        if len(b) > 0:
            return db.Event(self._si, b.TS, b[0])
        return db.make_empty(self._si)

    def offline(self, a, b):
        result = db.combine(a, b, si=self._si)
        order = np.argsort(result.TS)
        result = result[order]
        return result


class TestMultipleSources(TestProcessor):
    def test_multiple_sources(self):
        si1 = si.Event(id=1)
        si2 = si.Event(id=2)

        streams = [si1, si2]
        src_blocks = [
            db.Event(si1, 1, 1),
            db.Event(si2, 2, 2)
        ]

        si_exp = si.Event()
        expected = [
            db.Event(si_exp, 1, 1),
            db.Event(si_exp, 2, 2)
        ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             DummyTransformation)



