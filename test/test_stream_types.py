import unittest
import resonance.si as si
import resonance.db as db
from resonance.time import timeoption2ts
import numpy as np
import copy


class TestChannels(unittest.TestCase):
    def test_si_comparisons(self):
        si1 = si.Channels(1, 20)
        si2 = si.Channels(2, 20)
        self.assertNotEqual(si1, si2)

        si3 = si.Channels(1, 21)
        self.assertNotEqual(si1, si3)

        si4 = si.Channels(1, 20)
        self.assertEqual(si1, si4)

        si5 = si.Channels(1, 20, id=3)
        self.assertNotEqual(si1, si5)

        self.assertTrue(si1.is_similar(si1))
        self.assertFalse(si1.is_similar(si2))
        self.assertFalse(si1.is_similar(si3))
        self.assertTrue(si1.is_similar(si4))
        self.assertTrue(si1.is_similar(si5))

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

    def test_is_similar(self):
        si1 = si.Channels(1, 20, id=1)
        si2 = si.Channels(1, 20, id=2)

        db1 = db.Channels(si1, 300, [1])
        db2 = db.Channels(si2, 300, [1])

        self.assertNotEqual(db1, db2)
        self.assertTrue(db1.is_similar(db2))

    def test_merge(self):
        c_si = si.Channels(5, 20)

        A = db.Channels(c_si, timeoption2ts(c_si, 205), np.arange(1, 26))
        B = db.Channels(c_si, timeoption2ts(c_si, 215), np.arange(26, 76))
        C = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(76, 121))

        M = db.combine(A, B, C)
        O = db.Channels(c_si, timeoption2ts(c_si, 224), np.arange(1, 121))

        self.assertEqual(O, M)

    def test_merge_si_override(self):
        si1 = si.Channels(1, 20, id=1)
        si2 = si.Channels(1, 20, id=2)
        si3 = si.Channels(1, 20, id=3)
        A = db.Channels(si1, timeoption2ts(si1, 205), [1])
        B = db.Channels(si2, timeoption2ts(si2, 206), [2])

        merged = db.combine(A, B, si=si3)
        expected = db.Channels(si3, timeoption2ts(si3, 206), [1, 2])

        self.assertEqual(merged, expected)

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
    def test_si_comparisons(self):
        si1 = si.Event(id=1)
        si2 = si.Event(id=2)
        si3 = si.Event(id=1)

        self.assertNotEqual(si1, si2)
        self.assertEqual(si1, si3)
        self.assertTrue(si1.is_similar(si2))
        self.assertTrue(si1.is_similar(si3))

    def test_db_comparisons(self):
        si1 = si.Event(id=1)
        si2 = si.Event(id=2)
        si3 = si.Event(id=1)

        db1 = db.Event(si1, 11, 'A')
        db2 = db.Event(si2, 11, 'A')
        db3 = db.Event(si3, 11, 'A')
        db4 = db.Event(si1, 11, 'B')
        db5 = db.Event(si1, 12, 'A')

        self.assertNotEqual(db1, db2)
        self.assertEqual(db1, db3)
        self.assertNotEqual(db1, db4)
        self.assertNotEqual(db1, db5)

        self.assertTrue(db1.is_similar(db2))
        self.assertTrue(db1.is_similar(db3))
        self.assertFalse(db1.is_similar(db4))
        self.assertFalse(db1.is_similar(db5))

    def test_merge(self):
        e_si = si.Event()

        # event test
        events = [db.Event(e_si, 3, "a"),
                  db.Event(e_si, 5, "b"),
                  db.Event.make_empty(e_si),
                  db.Event(e_si, 12, "c")]

        result = db.combine(*events)

        self.assertEqual(result[0], "a")
        self.assertEqual(result[1], "b")
        self.assertEqual(result[2], "c")
        self.assertTrue(np.array_equal(result.TS, np.asarray([3, 5, 12])))
        self.assertEqual(result.SI, e_si)

        # event empty test
        empty_events = [db.Event.make_empty(e_si),
                       db.Event.make_empty(e_si)]

        empty_events_result = db.combine(*empty_events)

        self.assertEqual(empty_events_result, db.Event.make_empty(e_si))

        # event empty test 1
        empty_event = [db.Event.make_empty(e_si)]

        empty_event_result = db.combine(*empty_event)

        self.assertEqual(empty_event_result, db.Event.make_empty(e_si))

    def test_equality(self):
        e_si = si.Event()

        # wrong event message test
        self.assertNotEqual(db.Event(e_si, 1, "a"), db.Event(e_si, 2, "WRONG"))

        # wrong event timestamp test
        self.assertNotEqual(db.Event(e_si, 7, "a"), db.Event(e_si, 77, "a"))


class TestWindow(unittest.TestCase):

    def test_window_construct_from_other(self):
        time = 3
        channels = 2
        samples = 20
        sampling_rate = 250

        w_si = si.Window(channels, samples, sampling_rate)

        time = 3
        data_a = np.arange(1, 41, dtype=np.float64).reshape(samples, channels)
        data_b = np.arange(42, 82, dtype=np.float64).reshape(samples, channels)

        new_window = db.Window(w_si, time, [data_a])

    def test_merge(self):
        # window test
        w_si = si.Window(3, 7, 250)

        data_a = np.arange(1, 22).reshape((7, 3))
        data_b = np.arange(22, 43).reshape((7, 3))
        data_c = np.arange(43, 64).reshape((7, 3))

        time_a = 3
        time_b = 6
        time_c = 35

        A = db.Window(w_si, time_a, data_a, '1')
        B = db.Window(w_si, time_b, data_b, '2')
        C = db.Window(w_si, time_c, data_c, '3')

        M = db.combine(A, B, C)

        self.assertEqual(M[0], data_a)
        self.assertEqual(M[1], data_b)
        self.assertEqual(M[2], data_c)

        self.assertTrue(np.array_equal(M.TS, [time_a, time_b, time_c]))
        # self.assertNotEqual(db.SingleWindow(3, np.arange(1, 21)), np.arange(21, 41))
        self.assertTrue(np.array_equal(M.metadata, ['1', '2', '3']))

        self.assertEqual(M[0].metadata, '1')

    def test_empty(self):
        w_si = si.Window(5, 20, 250)

        emptyWindows = [db.Window.make_empty(w_si), db.Window.make_empty(w_si)]

        result2 = db.combine(*emptyWindows)

        self.assertEqual(result2, db.Window.make_empty(w_si))

    def test_window_timestamp_attribute(self):
        w_si = si.Window(3, 7, 250)

        time_a = 3

        data_a = np.arange(1, 22).reshape((7, 3))

        A = db.Window(w_si, time_a, data_a)
        B = copy.deepcopy(A)

        self.assertEqual(A, B)


