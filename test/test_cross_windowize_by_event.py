from resonance.tests.TestProcessor import TestProcessor
import resonance.si as si
import resonance.db as db
import resonance.cross.windowize_by_events
from resonance.time import timeoption2ts
import numpy as np


class TestCrossWindowizeByEvent(TestProcessor):
    def setUp(self):
        self.window_size = 11
        self.shift = 0
        self.drop_late_events = True
        self.late_time = 10

    def test_cross_empty(self):
        c_si = si.Channels(2, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_block = db.Channels(c_si, timeoption2ts(c_si, 211), np.arange(26, 76))

        w_si = si.Window(2, 11, 100)
        expected_block = db.Window.make_empty(w_si)

        self.check_processor(streams,
                             [src_block],
                             {'out_0': [expected_block]},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             self.drop_late_events,
                             self.late_time)


    def test_1(self):
        c_si = si.Channels(1, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [db.Channels(c_si, timeoption2ts(c_si, 201), 1),
                      db.Channels(c_si, timeoption2ts(c_si, 201 + 24), np.arange(2, 26)),
                      db.Event(e_si, timeoption2ts(c_si, 202), True),
                      db.Event(e_si, timeoption2ts(c_si, 301), False)]

        w_si = si.Window(1, 11, 100)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 201 + 11), np.arange(2, 13)),
            db.Window.make_empty(w_si),
            ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             self.drop_late_events,
                             self.late_time)

    def test_2(self):
        c_si = si.Channels(1, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [
            db.Channels(c_si, timeoption2ts(c_si, 201), 1),
            db.Channels(c_si, timeoption2ts(c_si, 201 + 99), np.arange(2, 101)),
            db.Event(e_si, timeoption2ts(c_si, 202), "first event"),
            db.Event(e_si, timeoption2ts(c_si, 290), "last event")]

        w_si = si.Window(1, 11, 100)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 201 + 11), np.arange(2, 13)),
            db.Window(w_si, timeoption2ts(c_si, 289 + 11), np.arange(90, 101)),
        ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             self.drop_late_events,
                             self.late_time)


