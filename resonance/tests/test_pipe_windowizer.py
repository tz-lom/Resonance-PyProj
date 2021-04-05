from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.windowizer
import numpy as np


class TestPipeWindowizer(TestProcessor):
    def test_one_by_one(self):
        si = resonance.si.Channels(2, 1)
        blocks = self.generate_channels_sequence(si, [7])

        e_si = resonance.si.Window(2, 5, 1)
        e_db1 = self.generate_window(e_si, 0)
        e_db2 = self.generate_window(e_si, 1)
        e_db3 = self.generate_window(e_si, 2)

        self.check_processor([si], blocks, {'out_0': [resonance.db.combine(e_db1, e_db2, e_db3)]},
                             resonance.pipe.windowizer, 5, 1)

    def test_from_two_blocks(self):
        si = resonance.si.Channels(2, 1)
        blocks = self.generate_channels_sequence(si, [3, 4])

        e_si = resonance.si.Window(2, 5, 1)
        e_db1 = self.generate_window(e_si, 0)
        e_db2 = self.generate_window(e_si, 1)
        e_db3 = self.generate_window(e_si, 2)

        self.check_processor([si], blocks,
                             {'out_0': [resonance.db.make_empty(e_si), resonance.db.combine(e_db1, e_db2, e_db3)]},
                             resonance.pipe.windowizer, 5, 1)

    def test_big_step(self):
        # 0 1 2 3 4 5 6 7
        # .......|...|...
        # -------
        #       -------
        si = resonance.si.Channels(2, 1)
        blocks = self.generate_channels_sequence(si, [4, 2, 2])

        e_si = resonance.si.Window(2, 4, 1)
        e_db1 = self.generate_window(e_si, 0)
        e_db2 = self.generate_window(e_si, 3)

        self.check_processor([si], blocks,
                             {'out_0': [e_db1, resonance.db.make_empty(e_si), e_db2]},
                             resonance.pipe.windowizer, 4, 3)

    def test_non_overlapping_windows(self):
        # 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
        # .......|.......|............|.....
        # ---
        #           ---
        #                     -----
        si = resonance.si.Channels(2, 1)
        blocks = self.generate_channels_sequence(si, [4, 4, 5, 2])

        e_si = resonance.si.Window(2, 2, 1)
        e_db1 = self.generate_window(e_si, 0)
        e_db2 = self.generate_window(e_si, 5)
        e_db3 = self.generate_window(e_si, 10)

        self.check_processor([si], blocks,
                             {'out_0': [e_db1, e_db2, e_db3, resonance.db.make_empty(e_si)]},
                             resonance.pipe.windowizer, 2, 5)

    def test_single_channel(self):
        si = resonance.si.Channels(1, 1)
        blocks = self.generate_channels_sequence(si, [7])

        e_si = resonance.si.Window(1, 5, 1)
        e_db1 = self.generate_window(e_si, 0)
        e_db2 = self.generate_window(e_si, 1)
        e_db3 = self.generate_window(e_si, 2)

        self.check_processor([si], blocks, {'out_0': [resonance.db.combine(e_db1, e_db2, e_db3)]},
                             resonance.pipe.windowizer, 5, 1)
