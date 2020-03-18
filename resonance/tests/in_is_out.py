import unittest

import resonance
import resonance.si as si
import resonance.db as db
import resonance.run as run
from resonance.time import timeoption2ts
import numpy as np


class TestInIsOut(unittest.TestCase):
    def check(self, i_si, blocks):
        def code():
            resonance.createOutput(resonance.input(0), 'out')

        online = run.online([i_si], blocks, code)
        offline = run.offline([i_si], blocks, code)

        if len(blocks) > 0:
            origin = db.combine(*blocks)
        else:
            origin = db.make_empty(i_si)
        self.assertEqual(online['out'], origin)
        self.assertEqual(online['out'], offline['out'])

    def test_channels(self):
        c_si = si.Channels(5, 20)
        blocks = []
        self.check(c_si, blocks)

        blocks = [
            db.Channels(c_si, timeoption2ts(c_si, 124), np.arange(75, 120)),
            db.Channels(c_si, timeoption2ts(c_si, 105), np.arange(0, 25)),
            db.Channels(c_si, timeoption2ts(c_si, 115), np.arange(25, 75)),
        ]
        self.check(c_si, blocks)

    def test_events(self):
        e_si = si.Event()
        blocks = []
        self.check(e_si, blocks)

        blocks = [
            db.Event(e_si, 10, 'one'),
            db.Event(e_si, 40, 'two'),
            db.Event(e_si, 80, 'three'),
            db.Event(e_si, 110, True),
            db.Event(e_si, 120, 123),
            db.Event(e_si, 121, ['foo', 'bar']),
            db.Event(e_si, 122, (1, 2)),
            db.Event(e_si, 125, {'a': 'b'}),
        ]
        self.check(e_si, blocks)
