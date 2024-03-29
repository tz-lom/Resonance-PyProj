from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe
import numpy as np


class MyTestCase(TestProcessor):
    def test_simple(self):
        si = resonance.si.Window(2, 5, 10)
        db = resonance.db.Window(si, 3e9, np.arange(0, 10))

        def transform(x):
            return np.max(x)

        expected = resonance.db.Event(resonance.si.Event(), 3e9, 9)

        self.check_processor([si], [db], {'out_0': [expected]},
                             resonance.pipe.transform_to_event, transform)

    def test_channels_to_event(self):
        si = resonance.si.Channels(3, 100)
        db = resonance.db.Channels(si, 1e9, np.arange(9))

        def transform(x):
            return 4

        si_out = resonance.si.Event()

        expected = [
            resonance.db.combine(resonance.db.Event(si_out, 0.98e9, 4),
                                 resonance.db.Event(si_out, 0.99e9, 4),
                                 resonance.db.Event(si_out, 1.00e9, 4))
        ]
        self.check_processor([si], [db], {'out_0': expected},
                             resonance.pipe.transform_to_event, transform)

    def test_event_to_event(self):
        si = resonance.si.Event()
        data = [resonance.db.Event(si, 1, '1'), resonance.db.Event(si, 2, '2')]

        def transform(x):
            return '_' + x

        expected = [
            resonance.db.Event(si, 1, '_1'),
            resonance.db.Event(si, 2, '_2')
        ]

        self.check_processor([si], data, {'out_0': expected},
                             resonance.pipe.transform_to_event, transform)

    def test_transform_which_return_event(self):
        si = resonance.si.Event()
        data = [resonance.db.Event(si, 1, '1'), resonance.db.Event(si, 2, '2')]

        def transform(x):
            dummy_si = resonance.si.Event()
            return resonance.db.Event(dummy_si, x.TS + 10, '_' + x)

        expected = [
            resonance.db.Event(si, 11, '_1'),
            resonance.db.Event(si, 12, '_2')
        ]

        self.check_processor([si], data, {'out_0': expected},
                             resonance.pipe.transform_to_event, transform, pass_metadata=True)
