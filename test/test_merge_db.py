import unittest

import resonance.si as si
import resonance.db as db
from resonance.time import timeoption2ts
import numpy as np


class TestChannels(unittest.TestCase):

    def test_single_channel(self):
        c_si = si.Channels(1, 20)
        single = db.Channels(c_si, 1e9, [1, 2, 3])

        self.assertEqual((3, 1), single.shape)
        self.assertEqual([[1], [2], [3]], single)

    def test_equality(self):
        c_si = si.Channels(5, 20)

        time = 100
        data = np.arange(25)
        origin = db.Channels(c_si, timeoption2ts(c_si, time), data)

        same = db.Channels(c_si, timeoption2ts(c_si, time), data)
        self.assertEqual(origin, same)

        different_size = db.Channels(c_si, timeoption2ts(c_si, time), data.repeat(2))
        self.assertNotEqual(origin, different_size)

        different_time = db.Channels(c_si, timeoption2ts(c_si, time * 2), data)
        self.assertNotEqual(origin, different_time)

        c_si2 = si.Channels(5, 21)
        different_si = db.Channels(c_si2, timeoption2ts(c_si2, time), data)
        self.assertNotEqual(origin, different_si)

        offset = 10
        same_by_calc = db.Channels(c_si, timeoption2ts(c_si, time), data + offset)
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

    def test_timestamp_subset(self):
        c_si = si.Channels(1, 20)
        data = db.Channels(c_si, 2e9, np.arange(0, 25))
        sub_data = data[1:3, :]
        expected = db.Channels(c_si, 9e8, np.arange(1, 3))
        self.assertEqual(expected, sub_data)

        sub_data = data[[2]]
        expected = db.Channels(c_si, 9e8, [2])
        self.assertEqual(expected, sub_data)


class TestEvents(unittest.TestCase):

    def test_merge(self):
        e_si = si.Event()

        # event test
        events = [db.Event(e_si, 3, "a"),
                  db.Event(e_si, 5, "b"),
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

        # event empty test
        emptyEvents = [db.Event.make_empty(e_si),
                       db.Event.make_empty(e_si)]

        emptyEventsResult = db.combine(*emptyEvents)

        self.assertEqual(emptyEventsResult, db.Event.make_empty(e_si))

        # event empty test 1
        emptyEvent = [db.Event.make_empty(e_si)]

        emptyEventResult = db.combine(*emptyEvent)

        self.assertEqual(emptyEventResult, db.Event.make_empty(e_si))

    def test_equality(self):
        e_si = si.Event()

        # wrong event message test
        self.assertNotEqual(db.Event(e_si, 1, "a"), db.Event(e_si, 2, "WRONG"))

        # wrong event timestamp test
        self.assertNotEqual(db.Event(e_si, 7, "a"), db.Event(e_si, 77, "a"))


class TestWindow(unittest.TestCase):
    def test_merge(self):
        # window test
        w_si = si.Window(3, 7, 250)

        data_a = np.arange(1, 22).reshape((7, 3))
        data_b = np.arange(22, 43).reshape((7, 3))
        data_c = np.arange(43, 64).reshape((7, 3))

        time_a = 3
        time_b = 6
        time_c = 35

        A = db.Window(w_si, time_a, data_a)
        B = db.Window(w_si, time_b, data_b)
        C = db.Window(w_si, time_c, data_c)

        M = db.combine(A, B, C)

        self.assertEqual(M[0], data_a)
        self.assertEqual(M[1], data_b)
        self.assertEqual(M[2], data_c)

        self.assertTrue(np.array_equal(M.TS, [time_a, time_b, time_c]))

        # self.assertNotEqual(db.SingleWindow(3, np.arange(1, 21)), np.arange(21, 41))

    def test_empty(self):
        w_si = si.Window(5, 20, 250)

        emptyWindows = [db.Window.make_empty(w_si), db.Window.make_empty(w_si)]

        result2 = db.combine(*emptyWindows)

        self.assertEqual(result2, db.Window.make_empty(w_si))

