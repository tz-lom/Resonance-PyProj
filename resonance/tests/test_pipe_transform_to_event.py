from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe
import numpy as np


class MyTestCase(TestProcessor):
    def test_simple(self):
        si = resonance.si.Window(2, 5, 10)
        db = resonance.db.Window(si, 3e9, np.arange(0, 10))

        def transform(x):
            return np.max(x)

        expected = resonance.db.Event(resonance.si.Event(), 2.6e9, 9)

        self.check_processor([si], [db], {'out_0': [expected]},
                             resonance.pipe.transform_to_event, transform)
