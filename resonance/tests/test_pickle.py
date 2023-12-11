import unittest

import resonance.si
import resonance.db
import pickle


class MyTestCase(unittest.TestCase):
    def test_pickle(self):
        si = resonance.si.Channels(3, 12)
        db = resonance.db.Channels(si, [], [1, 2, 3])

        serialized = pickle.dumps(db)

        unserialized = pickle.loads(serialized)

        self.assertEqual(unserialized, db)


if __name__ == "__main__":
    unittest.main()
