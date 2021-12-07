from resonance.tests.TestProcessor import TestProcessor
import resonance.cross.combine_sequential_events


class TestPipeFilter(TestProcessor):
    def setUp(self):
        self.time = 1E9
        self.si1 = resonance.si.Event(id=1, name='first')
        self.si2 = resonance.si.Event(id=2, name='second')
        self.esi = resonance.si.Event()
        self.empty = resonance.db.make_empty(self.esi)
        self.si = [self.si1, self.si2]

    def test_first_then_second(self):
        data = [
            resonance.db.Event(self.si1, 1e9, 1),
            resonance.db.Event(self.si1, 2e9, 2),
            resonance.db.Event(self.si1, 3e9, 3),
            resonance.db.Event(self.si2, 1.1e9, 'a'),
            resonance.db.Event(self.si2, 2.1e9, 'b'),
            resonance.db.Event(self.si2, 3.1e9, 'c'),
        ]
        expected = [
            self.empty,
            self.empty,
            self.empty,
            resonance.db.Event(self.esi, 1.1e9, (1, 'a')),
            resonance.db.Event(self.esi, 2.1e9, (2, 'b')),
            resonance.db.Event(self.esi, 3.1e9, (3, 'c')),
        ]
        self.check_processor(self.si, data, {'out_0': expected}, resonance.cross.combine_sequential_events)

    def test_interleaved(self):
        data = [
            resonance.db.Event(self.si1, 1e9, 1),
            resonance.db.Event(self.si2, 1.1e9, 'a'),
            resonance.db.Event(self.si1, 2e9, 2),
            resonance.db.Event(self.si2, 2.1e9, 'b'),
            resonance.db.Event(self.si1, 3e9, 3),
            resonance.db.Event(self.si2, 3.1e9, 'c'),
        ]
        expected = [
            self.empty,
            resonance.db.Event(self.esi, 1.1e9, (1, 'a')),
            self.empty,
            resonance.db.Event(self.esi, 2.1e9, (2, 'b')),
            self.empty,
            resonance.db.Event(self.esi, 3.1e9, (3, 'c')),
        ]
        self.check_processor(self.si, data, {'out_0': expected}, resonance.cross.combine_sequential_events)

    def test_double_second_event(self):
        data = [
            resonance.db.Event(self.si1, 1e9, 1),
            resonance.db.Event(self.si2, 1.1e9, 'a'),
            resonance.db.Event(self.si2, 2.1e9, 'b'),
            resonance.db.Event(self.si1, 3e9, 3),
            resonance.db.Event(self.si2, 3.1e9, 'c'),
        ]
        expected = [
            self.empty,
            resonance.db.Event(self.esi, 1.1e9, (1, 'a')),
            self.empty,
            self.empty,
            resonance.db.Event(self.esi, 3.1e9, (3, 'c')),
        ]
        self.check_processor(self.si, data, {'out_0': expected}, resonance.cross.combine_sequential_events)


    def test_wait_for_first(self):
        data = [
            resonance.db.Event(self.si2, 1.1e9, 'a'),
            resonance.db.Event(self.si2, 2.1e9, 'b'),
            resonance.db.Event(self.si2, 3.1e9, 'c'),
            resonance.db.Event(self.si1, 1e9, 1),
            resonance.db.Event(self.si1, 2e9, 2),
            resonance.db.Event(self.si1, 3e9, 3),
        ]
        expected = [
            self.empty,
            self.empty,
            self.empty,
            resonance.db.Event(self.esi, 1.1e9, (1, 'a')),
            resonance.db.Event(self.esi, 2.1e9, (2, 'b')),
            resonance.db.Event(self.esi, 3.1e9, (3, 'c')),
        ]
        self.check_processor(self.si, data, {'out_0': expected}, resonance.cross.combine_sequential_events)
