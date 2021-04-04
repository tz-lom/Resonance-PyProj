from resonance.tests.TestProcessor import TestProcessor
import resonance
import numpy as np


class TestSplitEvent(TestProcessor):
    def setUp(self):
        self.si = resonance.si.Event()
        self.blocks = [
            resonance.db.Event(self.si, 1, (0,)),
            resonance.db.Event(self.si, 2, (1, 2)),
            resonance.db.Event(self.si, 3, (0, 2))
        ]
        self.empty = resonance.db.Event.make_empty(self.si)

    def test_split(self):
        def rule(x):
            return x

        self.check_processor(
            [self.si], self.blocks, {
                'out_0': [self.blocks[0], self.empty, self.blocks[2]],
                'out_1': [self.empty, self.blocks[1], self.empty],
                'out_2': [self.empty, self.blocks[1], self.blocks[2]]
            },
            resonance.split,
            3,
            rule)
    #
    # def test_filter(self):
    #     def rule(x):
    #         return int(x) <= 2
    #
    #     self.check_processor(
    #         [self.si], self.blocks,
    #         {'out_0': [self.blocks[0], self.blocks[1], self.empty]},
    #         resonance.pipe.filter_event, rule)
