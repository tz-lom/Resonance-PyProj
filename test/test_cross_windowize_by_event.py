from resonance.tests.TestProcessor import TestProcessor
import resonance.si as si
import resonance.db as db
import resonance.cross.windowize_by_events
from resonance.time import timeoption2ts
import numpy as np


class TestCrossWindowizeByEvent(TestProcessor):
    def setUp(self):
        self.channels = 1
        self.sampling_rate = 100
        self.window_size = 11
        self.shift = 0
        self.drop_late_events = True
        self.late_time = 10

    def test_empty_events(self):
        channels = 2
        c_si = si.Channels(channels, self.sampling_rate)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_block = db.Channels(c_si, timeoption2ts(c_si, 211), np.arange(26, 76))

        w_si = si.Window(channels, self.window_size, self.sampling_rate)
        expected_block = db.Window.make_empty(w_si)

        self.check_processor(streams,
                             [src_block],
                             {'out_0': [expected_block]},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             self.late_time)

    def test_data_smaller_than_ring_buffer_length(self):
        c_si = si.Channels(self.channels, self.sampling_rate)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [
            db.Channels(c_si, timeoption2ts(c_si, 201), 1),
            db.Channels(c_si, timeoption2ts(c_si, 201 + 99), np.arange(2, 101)),
            db.Event(e_si, timeoption2ts(c_si, 202), "first event"),
            db.Event(e_si, timeoption2ts(c_si, 290), "last event")]

        w_si = si.Window(self.channels, self.window_size, self.sampling_rate)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 201 + self.window_size), np.arange(2, 13)),
            db.Window(w_si, timeoption2ts(c_si, 289 + self.window_size), np.arange(90, 101)),
        ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             self.late_time)

    def test_data_bigger_than_ring_buffer_length(self):
        late_time = 2
        c_si = si.Channels(self.channels, self.sampling_rate)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_data = [
            db.Channels(c_si, timeoption2ts(c_si, 201), 1),
            db.Channels(c_si, timeoption2ts(c_si, 201 + 99), np.arange(2, 101)),
            db.Event(e_si, timeoption2ts(c_si, 202), "first event"),
            db.Channels(c_si, timeoption2ts(c_si, 301 + 99), np.arange(101, 201)),
            db.Channels(c_si, timeoption2ts(c_si, 401 + 99), np.arange(201, 301)),
            db.Channels(c_si, timeoption2ts(c_si, 501 + 99), np.arange(301, 401)),
            db.Event(e_si, timeoption2ts(c_si, 513), "second event"),
            db.Channels(c_si, timeoption2ts(c_si, 601 + 99), np.arange(401, 501))
        ]

        w_si = si.Window(self.channels, self.window_size, self.sampling_rate)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 201 + self.window_size), np.arange(2, 13), src_data[2]),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 512 + self.window_size), np.arange(313, 324), src_data[6]),
            db.Window.make_empty(w_si)
        ]

        self.check_processor(streams,
                             src_data,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             self.shift,
                             late_time)

    def test_data_collect_before_event(self):
        shift = -15
        c_si = si.Channels(self.channels, self.sampling_rate)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [
            db.Channels(c_si, timeoption2ts(c_si, 101), 1),
            db.Channels(c_si, timeoption2ts(c_si, 101 + 9), np.arange(2, 11)),
            db.Channels(c_si, timeoption2ts(c_si, 111 + 9), np.arange(11, 21)),
            db.Channels(c_si, timeoption2ts(c_si, 121 + 9), np.arange(21, 31)),
            db.Event(e_si, timeoption2ts(c_si, 122), "window starts with offset -15"),
            db.Channels(c_si, timeoption2ts(c_si, 131 + 9), np.arange(31, 41))]

        w_si = si.Window(self.channels, self.window_size, self.sampling_rate)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 121 + self.window_size + shift), np.arange(7, 18)),
            db.Window.make_empty(w_si),
        ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             shift,
                             self.late_time)

    def test_data_collect_after_event(self):
        shift = 17
        c_si = si.Channels(self.channels, self.sampling_rate)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [
            db.Channels(c_si, timeoption2ts(c_si, 101), 1),
            db.Channels(c_si, timeoption2ts(c_si, 101 + 9), np.arange(2, 11)),
            db.Event(e_si, timeoption2ts(c_si, 102), "window starts with offset +17"),
            db.Channels(c_si, timeoption2ts(c_si, 111 + 9), np.arange(11, 21)),
            db.Channels(c_si, timeoption2ts(c_si, 121 + 9), np.arange(21, 31)),
            db.Channels(c_si, timeoption2ts(c_si, 131 + 9), np.arange(31, 41))]

        w_si = si.Window(self.channels, self.window_size, self.sampling_rate)
        expected = [
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window.make_empty(w_si),
            db.Window(w_si, timeoption2ts(c_si, 101 + self.window_size + shift), np.arange(19, 30)),
            db.Window.make_empty(w_si),
        ]

        self.check_processor(streams,
                             src_blocks,
                             {'out_0': expected},
                             resonance.cross.windowize_by_events,
                             self.window_size,
                             shift,
                             self.late_time)
