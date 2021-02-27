import unittest
import resonance
import resonance.pipe as pipe
import resonance.si as si
import resonance.db as db
import resonance.run as run
import numpy as np


class TestSimpleTransformation(unittest.TestCase):
    def setUp(self):
        self._si = si.Channels(2, 20)
        self._db = db.Channels(self._si, 300, np.arange(1, 27))
        self._code = '''
from resonance import *
createOutput(input(0), 'foo')
'''


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
        results = run.offline([self._si], [self._db], self._code)
        self.assertEqual(results, {'foo': self._db})

    def test_run_online(self):
        results = run.online([self._si], [self._db], self._code)
        self.assertEqual(results, {'foo': self._db})

    def test_run_function(self):
        def call():
            resonance.createOutput(resonance.input(0), 'func')

        results = run.offline([self._si], [self._db], call)
        self.assertEqual(results, {'func': self._db})

