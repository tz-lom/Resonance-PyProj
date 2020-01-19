from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe
import numpy as np


class TestPipeTransformChannels(TestProcessor):
    def test_simple(self):
        si = resonance.si.Channels(2, 31)
        db = resonance.db.Channels(si, 3e9, np.arange(0, 26))

        def transform(x):
            return x

        self.check_processor([si], [db], {'out_0': [db]}, resonance.pipe.transform_channels, 2, transform)

    def test_simple_computation(self):
        si = resonance.si.Channels(1, 31)
        db = resonance.db.Channels(si, 3e9, np.arange(0, 5))

        scale = 1.12

        def transform(x):
            return x*scale

        self.check_processor([si], [db], {'out_0': [db*scale]}, resonance.pipe.transform_channels, 1, transform)

    def test_change_number_of_channels(self):
        si = resonance.si.Channels(1, 31)
        data = np.arange(0, 5)
        timestamp = 3e9
        db = resonance.db.Channels(si, timestamp, data)

        def transform(x):
            return np.concatenate((x, x*-0.5), 1)

        si2 = resonance.si.Channels(2, 31)
        expected = resonance.db.Channels(si2, timestamp, np.concatenate((db, db*-0.5), 1))
        self.check_processor([si], [db], {'out_0': [expected]}, resonance.pipe.transform_channels, 2, transform)


