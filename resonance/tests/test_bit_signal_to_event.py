from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.bit_signal_to_event


class TestPipeFilter(TestProcessor):
    def setUp(self):
        self.time = 1e9
        self.si = resonance.si.Channels(1, 25)
        self.esi = resonance.si.Event()
        self.db = resonance.db.Channels(self.si, self.time, [1, 0, 0, 1, 1])

    def test_trivial(self):
        db = resonance.db.Channels(self.si, self.time, [1, 0, 0, 1, 1])
        expected = [
            resonance.db.combine(
                resonance.db.Event(self.esi, self.time - 4 / 25 * 1e9, True),
                resonance.db.Event(self.esi, self.time - 1 / 25 * 1e9, True),
            )
        ]
        self.check_processor(
            [self.si],
            [db],
            {"out_0": expected},
            resonance.pipe.bit_signal_to_event,
            bit=0,
        )

    def test_carry_front_across_blocks(self):
        data = [
            resonance.db.Channels(self.si, self.time + 0 / 25 * 1e9, [1, 0]),
            resonance.db.Channels(self.si, self.time + 2 / 25 * 1e9, [0, 1]),
            resonance.db.Channels(self.si, self.time + 4 / 25 * 1e9, [1, 0]),
            resonance.db.Channels(self.si, self.time + 6 / 25 * 1e9, [0, 1]),
        ]
        expected = [
            resonance.db.combine(
                resonance.db.Event(self.esi, self.time - 1 / 25 * 1e9, "Rise"),
                resonance.db.Event(self.esi, self.time + 0 / 25 * 1e9, "Fall"),
            ),
            resonance.db.Event(self.esi, self.time + 2 / 25 * 1e9, "Rise"),
            resonance.db.Event(self.esi, self.time + 4 / 25 * 1e9, "Fall"),
            resonance.db.Event(self.esi, self.time + 6 / 25 * 1e9, "Rise"),
        ]
        self.check_processor(
            [self.si],
            data,
            {"out_0": expected},
            resonance.pipe.bit_signal_to_event,
            bit=0,
            rising_edge="Rise",
            falling_edge="Fall",
        )
