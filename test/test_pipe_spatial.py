from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.spatial
import numpy as np


class TestPipeFilter(TestProcessor):
    def test_simple(self):
        si = resonance.si.Channels(2, 31)
        db = resonance.db.Channels(si, 3e9, np.arange(0, 26))
        matrix = np.identity(2)
        self.check_processor([si], [db], {'out_0': db}, resonance.pipe.spatial, matrix)

    def test_single_channel(self):
        si = resonance.si.Channels(1, 31)
        db = resonance.db.Channels(si, 3e9, np.arange(0, 5))
        matrix = np.identity(1)*np.pi
        self.check_processor([si], [db], {'out_0': db*np.pi}, resonance.pipe.spatial, matrix)

    def test_increased_number_of_channels(self):
        si = resonance.si.Channels(1, 31)
        data = np.arange(0, 5)
        db = resonance.db.Channels(si, 3e9, data)
        matrix = np.asarray([[1, -0.5, np.pi]], ).reshape((1, 3))
        expected = np.concatenate((db, db*-0.5, db*np.pi), 1)
        self.check_processor([si], [db], {'out_0': expected}, resonance.pipe.spatial, matrix)


