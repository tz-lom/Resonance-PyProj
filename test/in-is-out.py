import unittest

import resonance.si as si
import resonance.db as db
import resonance.run as run
import resonance.time.timeoption2ts as timeoption2ts
import numpy as np

class TestInIsOut(unittest.TestCase):

    def check(self, si, blocks):
        code = "process <- function() { createOutput(input(1), 'out') }"
        online = run.online([si], blocks, code)
        offline = run.offline([si], blocks, code)

        if len(blocks)>0 :
            origin = db.combine(blocks)

        else:
            origin = db.makeEmpty(si)
        self.assertEqual(online, origin)
        self.assertEqual(online, offline)


    def test_events(self):
        si = si.Channels(5, 20)
        blocks = []
        check(si, blocks)

        blocks < - [
            db.Channels(si, timeoption2ts(si, 105), np.arange(1, 25)),
            db.Channels(si, timeoption2ts(si, 115), np.arange(26, 75)),
            db.Channels(si, timeoption2ts(si, 124), np.arange(76, 120))
        ]
        test(si, blocks)

    def test_channels(self):
        si < - SI.event()
        blocks < - list()
        test(si, blocks)

        blocks < - list(
            DB.event(si, 10, 'one'),
            DB.event(si, 40, 'two'),
            DB.event(si, 80, 'three')
        )
        test(si, blocks)