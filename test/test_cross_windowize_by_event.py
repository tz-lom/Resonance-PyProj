from resonance.tests.TestProcessor import TestProcessor
import resonance.si as si
import resonance.db as db
import resonance.cross.windowize_by_events
import numpy as np
import unittest


class TestCrossWindowizeByEvent(TestProcessor):

    def test_cross_empty(self):
        window_size = 11
        shift = 0
        drop_late_events = True
        late_time = 10

        c_si = si.Channels(2, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_block = db.Channels(c_si, 211, np.arange(26, 76))

        w_si = si.Window(2, 11, 100)
        expected_block = db.Channels.make_empty(w_si)

        self.check_processor(streams,
                             [src_block],
                             {'out_0': [expected_block]},
                             resonance.cross.windowize_by_events,
                             window_size,
                             shift,
                             drop_late_events,
                             late_time)

    def test_1(self):
        window_size = 11
        shift = 0
        drop_late_events = True
        late_time = 10

        c_si = si.Channels(1, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [db.Channels(c_si, 201, 1),
                      db.Channels(c_si, 225, np.arange(2, 26)),
                      db.Event(e_si, 202, True),
                      db.Event(e_si, 301, False)]

        w_si = si.Window(1, 11, 100)
        expected_block = [db.Channels.combine(db.Window(w_si, 212, np.arange(2, 13)))]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected_block},
                             resonance.cross.windowize_by_events,
                             window_size,
                             shift,
                             drop_late_events,
                             late_time)


