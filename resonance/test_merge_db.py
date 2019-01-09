import unittest

import resonance.si as si
import resonance.db as db
from resonance.time import timeoption2ts
import numpy as np


class TestChannels(unittest.TestCase):

    def test_equality(self):
        c_si = si.Channels(5, 20)

        time = 100
        data = np.arange(25)
        origin = db.Channels(c_si, timeoption2ts(c_si, time), data)

        same = db.Channels(c_si, timeoption2ts(c_si, time), data)
        self.assertEqual(origin, same)

        different_size = db.Channels(c_si, timeoption2ts(c_si, time), data.repeat(2))
        self.assertNotEqual(origin, different_size)

        different_time = db.Channels(c_si, timeoption2ts(c_si, time*2), data)
        self.assertNotEqual(origin, different_time)

        c_si2 = si.Channels(5, 21)
        different_si = db.Channels(c_si2, timeoption2ts(c_si2, time), data)
        self.assertNotEqual(origin, different_si)

        offset = 10
        same_by_calc = db.Channels(c_si, timeoption2ts(c_si, time), data+offset)
        self.assertNotEqual(origin, same_by_calc)
        same_by_calc -= offset
        self.assertEqual(origin, same_by_calc)


    def test_merge(self):
        c_si = si.Channels(5, 20)

        A = db.Channels(c_si, timeoption2ts(c_si, 205), np.arange(1, 26))
        B = db.Channels(c_si, timeoption2ts(c_si, 215), np.arange(26, 76))
        C = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(76, 121))

        M = db.combine(A, B, C)
        O = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(1, 121))

        self.assertEqual(O, M)