from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe
import numpy as np


class TestPipeFilterEvent(TestProcessor):
    def setUp(self):
        self.si = resonance.si.Event()
        self.blocks = [
            resonance.db.Event(self.si, 1, '1'),
            resonance.db.Event(self.si, 2, '2'),
            resonance.db.Event(self.si, 3, '3')
        ]
        self.empty = resonance.db.Event.make_empty(self.si)

    def test_empty(self):
        rule = lambda x: True
        self.check_processor_only_offline(
            [self.si], [], {'out_0': [resonance.db.Event.make_empty(self.si)]},
            resonance.pipe.filter_event,
            rule)

    def test_filter(self):
        def rule(x):
            return int(x) <= 2

        self.check_processor(
            [self.si], self.blocks,
            {'out_0': [self.blocks[0], self.blocks[1], self.empty]},
            resonance.pipe.filter_event, rule)
