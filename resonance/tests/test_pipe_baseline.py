from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.baseline
import numpy as np
import unittest


class TestPipeBaseline(TestProcessor):
    def setUp(self):
        self.time = 3
        self.channels = 2
        self.samples = 20
        self.sampling_rate = 250
        self.first_offset = 0
        self.end_offset = 19

        self.si = resonance.si.Window(self.channels, self.samples, self.sampling_rate)

        self.src_data = np.arange(1, 41, dtype=np.float64).reshape(self.samples, self.channels)
        self.src_window = resonance.db.Window(self.si, self.time, self.src_data)

        self.expected_data = np.arange(1, 41, dtype=np.float64).reshape(self.samples, self.channels)
        self.expected_data = self.expected_data - np.mean(self.expected_data, axis=0)
        self.expected_window = resonance.db.Window(self.si, self.time, self.expected_data)

    def test_baseline_full_window_subset(self):
        self.check_processor([self.si],
                             [self.src_window],
                             {'out_0': [self.expected_window]},
                             resonance.pipe.baseline,
                             self.first_offset,
                             self.end_offset)

    def test_baseline_window_part_subset(self):
        first_offset = 2
        end_offset = 16

        averaging_window = slice(first_offset, end_offset+1)

        expected_data = self.expected_data
        expected_data = expected_data.__sub__(np.mean(expected_data[averaging_window, :], axis=0))
        expected_window = resonance.db.Window(self.si, self.time, expected_data)

        self.check_processor([self.si],
                             [self.src_window],
                             {'out_0': [expected_window]},
                             resonance.pipe.baseline,
                             first_offset,
                             end_offset)

    def test_baseline_one_channel(self):
        channels = 1

        si = resonance.si.Window(channels, self.samples, self.sampling_rate)

        src_data = np.arange(1, 21, dtype=np.float64).reshape((self.samples, channels))
        src_window = resonance.db.Window(si, self.time, src_data)

        expected_data = np.arange(1, 21, dtype=np.float64).reshape(self.samples, channels)
        expected_data = expected_data.__sub__(np.mean(expected_data, axis=0))
        expected_window = resonance.db.Window(si, self.time, expected_data)

        self.check_processor([si],
                             [src_window],
                             {'out_0': [expected_window]},
                             resonance.pipe.baseline,
                             self.first_offset,
                             self.end_offset)

    def test_baseline_multiple_channels(self):
        channels = 3

        si = resonance.si.Window(channels, self.samples, self.sampling_rate)

        src_data = np.arange(1, 61, dtype=np.float64).reshape((self.samples, channels))
        src_window = resonance.db.Window(si, self.time, src_data)

        expected_data = np.arange(1, 61, dtype=np.float64).reshape(self.samples, channels)
        expected_data = expected_data.__sub__(np.mean(expected_data, axis=0))
        expected_window = resonance.db.Window(si, self.time, expected_data)

        self.check_processor([si],
                             [src_window],
                             {'out_0': [expected_window]},
                             resonance.pipe.baseline,
                             self.first_offset,
                             self.end_offset)

    def test_baseline_parameters(self):
        first_offset = 1
        end_offset = 30

        with self.assertRaises(Exception):
            resonance.pipe.baseline(self.src_window, first_offset, end_offset)

