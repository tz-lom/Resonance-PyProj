from resonance.tests.TestProcessor import TestProcessor
import resonance.si as si
import resonance.db as db
import numpy as np
from resonance.time import timeoption2ts
import unittest


class TestCrossWindowizeByEvent(TestProcessor):
    def test_cross_empty(self):
        c_si = si.Channels(2, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_block = db.Channels(c_si, timeoption2ts(c_si, 211), np.arange(26, 76))

        w_si = si.Window(2, 11, 100)
        out_block = db.Channels.make_empty(w_si)

        self.check_processor(streams, src_block, {'out_0': out_block})

    def test_1(self):
        c_si = si.Channels(1, 100)
        e_si = si.Event()

        streams = [c_si, e_si]
        src_blocks = [db.Channels(c_si, timeoption2ts(c_si, 201), 1),
                      db.Channels(c_si, timeoption2ts(c_si, 225), np.arange(2, 26)),
                      db.Event(e_si, timeoption2ts(e_si, 202), True),
                      db.Event(e_si, timeoption2ts(e_si, 301), False)]

        w_si = si.Window(1, 11, 100)
        out_blocks = db.Channels.combine(db.Channels(w_si, timeoption2ts(c_si, 212), np.arange(2, 12)))

        self.check_processor(streams, src_blocks, {'out_0': out_blocks})

