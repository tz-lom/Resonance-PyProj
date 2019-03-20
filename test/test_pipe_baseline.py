import unittest
import resonance.pipe as pipe
import resonance.si as si
import resonance.db as db
import resonance.run as run
import numpy as np


class TestPipeBaseline(unittest.TestCase):
    def check(self, si, blocks, expected, beginOffset, endOffset):
#        code = '''
# from resonance import *
# inputData = input(0)
# out = pipe.baseline(inputData, beginOffset, endOffset)
# createOutput(out, 'out')
# '''
        code = "from resonance import *\n"\
               "inputData = input(0)\n"\
               "out = pipe.baseline(inputData, %f, %f)\n"\
               "createOutput(out, 'out')"\
               % (beginOffset, endOffset)

        online = run.online([si], blocks, code)
        offline = run.offline([si], blocks, code)

        self.assertEqual(online, expected)
        self.assertEqual(online, offline)

    def test_baseline(self):
        w_si = si.Window(2, 20, 250)
        data = np.arange(1, 41).reshape((20, 2))
        time = 3

        srcWindow = db.Window(w_si, time, data)

        expectedData = np.array([-8.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5,
                                 6.5, 7.5, 8.5, 9.5, 10.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5,
                                 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5], dtype=np.float64)

        expectedWindow = db.Window(w_si, time, expectedData)

        self.check(w_si, srcWindow, expectedWindow, 1, 20)
        # win generate
        # expected gen
        # check

    def test_baseline_subset(self):
        pass
        # check 1 and 2 channel window
        # if begin > end ->  error
        # if end < -1 -> end index = last - 1...
        # if end < 0 -> end index = last...

