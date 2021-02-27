from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.filter
import numpy as np


class TestPipeFilter(TestProcessor):
    def setUp(self):
        self.time = 1E9
        self.si = resonance.si.Channels(1, 26)
        self.db = resonance.db.Channels(self.si, self.time, [
            9.35016242685414833e-01
            ,- 6.63122658240795304e-01
            ,- 4.64723172043768396e-01
            , 9.92708874098053973e-01
            ,- 2.39315664287558072e-01
            ,- 8.22983865893656130e-01
            , 8.22983865893655575e-01
            , 2.39315664287557295e-01
            ,- 9.92708874098054195e-01
            ,  4.64723172043769062e-01
            ,  6.63122658240796081e-01
            , - 9.35016242685415055e-01
            , - 9.79717439317882566e-16
            ,  9.35016242685415833e-01
            , - 6.63122658240791862e-01
            , - 4.64723172043767674e-01
            ,  9.92708874098053862e-01
            , - 2.39315664287555380e-01
            , - 8.22983865893658795e-01
            ,  8.22983865893657129e-01
            ,  2.39315664287558238e-01
            , - 9.92708874098054306e-01
            ,  4.64723172043765065e-01
            ,  6.63122658240794083e-01
            , - 9.35016242685414722e-01
            , - 1.95943487863576513e-15
        ])
        self.ba = (
            [0.0465829066364436689, 0.1863316265457746757, 0.2794974398186620412, 0.1863316265457746757, 0.0465829066364436689],
            [1.0000000000000000000, -0.7820951980233376011,  0.6799785269162993417, -0.1826756977530322179,  0.0301188750431692284])

        self.expected = resonance.db.Channels(self.si, self.time, [
            4.355577433657303182e-02
            , 1.773976784237727145e-01
            , 2.252506475386053808e-01
            , 1.203007154782509414e-02
            , - 1.487313945820971373e-01
            , - 1.164977332361991774e-02
            , 6.886207424754971218e-02
            , - 2.962840432194260853e-02
            , - 3.770718619071654343e-03
            , 4.870207750908683852e-02
            , - 4.388049480176299533e-02
            , - 3.116268960854329251e-02
            , 6.594320776813765439e-02
            , - 9.288917918409606012e-03
            , - 5.647581830546984094e-02
            , 4.770159710550052334e-02
            , 2.055919131626844643e-02
            , - 6.246265071717359979e-02
            , 2.463108864724521119e-02
            , 4.548190937186858546e-02
            , - 5.708181059114052214e-02
            , - 5.314571501358562877e-03
            , 6.079863765675493081e-02
            , - 3.768093227054283845e-02
            , - 3.399460136256619858e-02
            , 6.176906046401800521e-02

        ])

        self.expected_2nd_block = resonance.db.Channels(self.si, self.time * 2, [
            -9.859684670332456713e-03
            , - 5.478792701119510056e-02
            , 4.873257664167104930e-02
            , 2.023924103129345897e-02
            , - 6.308839867255294775e-02
            , 2.449675101879355416e-02
            , 4.571284064528602364e-02
            , - 5.691452605013672117e-02
            , - 5.346460767788822899e-03
            , 6.070617894859293984e-02
            , - 3.770795633571592809e-02
            , - 3.396373063417428700e-02
            , 6.179565060628578604e-02
            , - 9.862031967849994862e-03
            , - 5.480139028078973018e-02
            , 4.872757077626192757e-02
            , 2.024325104283859755e-02
            , - 6.308424729499828576e-02
            , 2.449676211807962078e-02
            , 4.571090978108215824e-02
            , - 5.691540613827990314e-02
            , - 5.345959141554147698e-03
            , 6.070681665283795408e-02
            , - 3.770790130061484058e-02
            , - 3.396400307449330691e-02
            , 6.179550149398233688e-02

        ])

    def test_single_channel(self):
        self.check_processor([self.si], [self.db], {'out_0': [self.expected]}, resonance.pipe.filter, self.ba)

    def test_multiple_channels(self):
        channels = 2

        si = resonance.si.Channels(channels, self.si.samplingRate)
        data = np.zeros((self.db.shape[0], channels))
        data[:, 0] = self.db[:, 0]
        data[:, 1] = self.db[:, 0]
        data = resonance.db.Channels(si, 1E9, data)

        expected = np.zeros_like(data)
        expected[:, 0] = self.expected[:, 0]
        expected[:, 1] = self.expected[:, 0]
        expected = resonance.db.Channels(si, 1E9, expected)

        self.check_processor([si], [data], {'out_0': [expected]}, resonance.pipe.filter, self.ba)

    def test_non_ba_input(self):
        with self.assertRaises(Exception):
            resonance.pipe.filter(self.db, [1, 2, 3])


    def test_multiple_blocks(self):
        data = resonance.db.Channels(self.si, self.time*2, self.db)
        self.check_processor([self.si], [self.db, data], {'out_0': [self.expected, self.expected_2nd_block]}, resonance.pipe.filter, self.ba)




