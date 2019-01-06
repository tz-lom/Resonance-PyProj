import unittest

import resonance.si as si
import resonance.db as db
from resonance.time import timeoption2ts
import numpy as np


class TestChannels(unittest.TestCase):
    def test_merge(self):
        c_si = si.Channels(5, 20)

        A = db.Channels(c_si, timeoption2ts(c_si, 205), np.arange(1, 26))
        B = db.Channels(c_si, timeoption2ts(c_si, 215), np.arange(26, 76))
        C = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(76, 121))

        M = db.combine(A, B, C)
        O = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(1, 121))

        self.assertEqual(O, M)