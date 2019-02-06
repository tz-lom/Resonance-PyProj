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

   def test_empty(self):
        c_si = si.Channels(5, 20)
        d = db.make_empty(c_si)

        self.assertEqual(d.shape, (0, 5))
        self.assertEqual(d.TS.shape, (0,))
        self.assertEqual(d.SI, c_si)


class TestEvents(unittest.TestCase):

    def test_merge(self):
        e_si = si.Event()

        ''' event test '''
        events = [db.Event(e_si, 3,  "a"),
                  db.Event(e_si, 5,  "b"),
                  db.Event.make_empty(e_si),
                  db.Event(e_si, 12, "c")]

        result = db.combine(*events)

        target = [db.Event(e_si, 0, "a"),
                  db.Event(e_si, 0, "b"),
                  db.Event(e_si, 0, "c")]

        type(target[0]).TS = 3
        type(target[1]).TS = 5
        type(target[2]).TS = 12

        self.assertEqual(result[0], target[0])
        self.assertEqual(result[1], target[1])
        self.assertEqual(result[2], target[2])

        ''' event empty test '''
        emptyEvents = [db.Event.make_empty(e_si),
                       db.Event.make_empty(e_si)]

        result2 = db.combine(*emptyEvents)

        self.assertEqual(result2, db.Event.make_empty(e_si))

        ''' event empty test 1 '''
        emptyEvent = [db.Event.make_empty(e_si)]

        result3 = db.combine(*emptyEvent)

        self.assertEqual(result3, db.Event.make_empty(e_si))

