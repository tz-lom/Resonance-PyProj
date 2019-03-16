import unittest
import resonance.run as run


class TestPipeBaseline(unittest.TestCase):
    def check(self, si, blocks, expected):
        code = '''
from resonance import *
in = input(1)
out = pipe.baseline(in)
createOutput(out, 'out')
'''

        online = run.online([si], blocks, code)
        offline = run.offline([si], blocks, code)

        self.assertEqual(online, expected)
        self.assertEqual(online, offline)

    def test_spatial(self):
        pass
