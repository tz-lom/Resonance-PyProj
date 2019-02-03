import unittest
import resonance.pipe as pipe
import resonance.si as si
import resonance.db as db
import resonance.run as run
import numpy as np


class TestSimpleTransformation(unittest.TestCase):
    def test_transformation_is_callable(self):
        t = pipe.spatial
        self.assertTrue(callable(t))

    def test_transformation_calls_something(self):
        s = si.Channels(2, 20)
        d = db.Channels(s, 300, np.arange(1, 27))
        t = pipe.spatial(d, np.array([[1, 0], [0, -1]]))

        self.assertIsInstance(t, db.Channels)
        self.assertEqual(t.shape, (13, 2))

    def test_run_offline(self):
        code = '''
from resonance import *
createOutput('foo', input(0))
'''

        s = si.Channels(2, 20)
        d = db.Channels(s, 300, np.arange(1, 27))

        results = run.offline([s], [d], code)

        self.assertEqual(results, {'foo': d})


