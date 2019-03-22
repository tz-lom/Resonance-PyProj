from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.filter
import numpy as np


class TestPipeFilter(TestProcessor):
    def test_something(self):
        si = resonance.si.Channels(2, 31)
        db = resonance.db.Channels(si, 3e9, np.arange(0, 26))

        matrix = np.asarray([[1, 0], [0, 1]])

        self.check_processor([si], [db], {'out_0': db}, resonance.pipe.spatial, matrix)



