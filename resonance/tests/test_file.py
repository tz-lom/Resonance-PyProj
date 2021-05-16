import unittest
import resonance.file
import numpy as np


class TestHdf5(unittest.TestCase):
    # def test_channels(self):
    #     sis, blocks = resonance.file.hdf5('test_eeg.h5')
    #     self.assertEqual(1, len(sis))
    #     self.assertEqual(329, len(blocks))
    #
    # def test_events(self):
    #     si, blocks = resonance.file.hdf5('test_events.h5')
    #     self.assertEqual(1, len(si))
    #     self.assertEqual(12, len(blocks))

    def test_channels_and_events(self):
        sis, blocks = resonance.file.hdf5('test_eeg_events.h5')
        self.assertEqual(2, len(sis))
        self.assertEqual(115, len(blocks))

        self.assertEqual(sis[0], resonance.si.Channels(3, 250, name='EEG'))
        self.assertEqual(sis[1], resonance.si.Event(name='events'))

        ts = np.asarray([block.TS[0] for block in blocks])
        events = [block for block in blocks if isinstance(block, resonance.db.Event)]
        eeg = [block for block in blocks if isinstance(block, resonance.db.Channels)]
        self.assertEqual(5, len(events))
        self.assertEqual(110, len(eeg))
        self.assertTrue(np.all(np.diff(ts) >= 0))


if __name__ == '__main__':
    unittest.main()
