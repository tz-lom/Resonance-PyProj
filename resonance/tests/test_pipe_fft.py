from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.filters
import numpy as np
import os


class TestFFTFilter(TestProcessor):
    def setUp(self):
        self.time = 1E9

        self.select = np.array([(0, 5), (2, 12), (1, 4), (0, 7)], [('channel', 'i4'), ('frequency', 'f8')])

        self.si = resonance.si.Window(channels=5, sampling_rate=2, samples=100)
        self.db = self.generate_window(self.si, 0)

        self.e_si = resonance.si.Channels(channels=4, samplingRate=2)
        self.expected = resonance.db.Channels(self.e_si,49.5e9, [
            -52.36067977499794,
            -2.4404254292287783e-14,
            -5.4346102019248406e-14,
            -27.5804237380977])

    def test_single_channel(self):
        self.check_processor([self.si], [self.db], {'out_0': [self.expected]}, resonance.pipe.fft, self.select)

