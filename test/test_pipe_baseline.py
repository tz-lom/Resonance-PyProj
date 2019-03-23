import unittest
import resonance.pipe as pipe
import resonance.si as si
import resonance.db as db
import resonance.run as run
import numpy as np


class TestPipeBaseline(unittest.TestCase):
    def check(self, si, blocks, expected, beginOffset, endOffset):

        code = "from resonance import *"\
               "inputData = input(0)"\
               "out = pipe.baseline(inputData, {0}, {1})"\
               "createOutput(out, 'out')"\
               .format(beginOffset, endOffset)

        online = run.online([si], blocks, code)
        offline = run.offline([si], blocks, code)

        self.assertEqual(online, expected)
        self.assertEqual(online, offline)

    def test_baseline(self):
        channels = 2
        samples = 20
        time = 3

        w_si = si.Window(channels, samples, 250)
        data = np.arange(1, 41).reshape((samples, channels))

        srcWindow = db.Window(w_si, time, data)

        expectedData = np.array([-8.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5,
                                 6.5, 7.5, 8.5, 9.5, 10.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5,
                                 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5], dtype=np.float64)

        expectedWindow = db.Window(w_si, time, expectedData)

        self.check([w_si], srcWindow, expectedWindow, 1, 20)

    def test_baseline_channels(self):
        time = 3
        samples = 20
        samplingRate = 250

        # one channel window
        channels = 1
        data = np.arange(1, 21).reshape((samples, channels))
        w_si = si.Window(channels, samples, samplingRate)
        oneChWindow = db.Window(w_si, time, data)

        expectedData = np.arange(1, 21)
        expectedWindow = db.Window(w_si, time, expectedData)

        self.check([w_si], oneChWindow, expectedWindow, 1, samples)

        # two channel window
        channels = 2
        data = np.arange(1, 41).reshape((samples, channels))
        w_si = si.Window(channels, samples, samplingRate)
        twoChWindow = db.Window(w_si, time, data)

        expectedData = np.arange(1, 41)
        expectedWindow = db.Window(w_si, time, expectedData)

        self.check([w_si], twoChWindow, expectedWindow, 1, samples)

        # check 1 and 2 channel window
        # if begin > end ->  error
        # if end < -1 -> end index = last - 1...
        # if end < 0 -> end index = last...

