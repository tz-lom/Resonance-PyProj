from resonance.tests.TestProcessor import TestProcessor
import resonance.pipe.filters
import numpy as np
from scipy import signal


class TestPipeFilter(TestProcessor):
    def setUp(self):
        self.time = 1E9
        self.si = resonance.si.Channels(1, 26)
        self.db = resonance.db.Channels(self.si, self.time, [
            9.35016242685414833e-01
            , - 6.63122658240795304e-01
            , - 4.64723172043768396e-01
            , 9.92708874098053973e-01
            , - 2.39315664287558072e-01
            , - 8.22983865893656130e-01
            , 8.22983865893655575e-01
            , 2.39315664287557295e-01
            , - 9.92708874098054195e-01
            , 4.64723172043769062e-01
            , 6.63122658240796081e-01
            , - 9.35016242685415055e-01
            , - 9.79717439317882566e-16
            , 9.35016242685415833e-01
            , - 6.63122658240791862e-01
            , - 4.64723172043767674e-01
            , 9.92708874098053862e-01
            , - 2.39315664287555380e-01
            , - 8.22983865893658795e-01
            , 8.22983865893657129e-01
            , 2.39315664287558238e-01
            , - 9.92708874098054306e-01
            , 4.64723172043765065e-01
            , 6.63122658240794083e-01
            , - 9.35016242685414722e-01
            , - 1.95943487863576513e-15
        ])
        self.ba = (
            [0.0465829066364436689, 0.1863316265457746757, 0.2794974398186620412, 0.1863316265457746757,
             0.0465829066364436689],
            [1.0000000000000000000, -0.7820951980233376011, 0.6799785269162993417, -0.1826756977530322179,
             0.0301188750431692284])

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
        data = resonance.db.Channels(self.si, self.time * 2, self.db)
        self.check_processor([self.si], [self.db, data], {'out_0': [self.expected, self.expected_2nd_block]},
                             resonance.pipe.filter, self.ba)


class TestPipeSOSFilter(TestPipeFilter):
    def setUp(self):
        TestPipeFilter.setUp(self)
        self.sos = np.asarray([
            [6.37835424e-05, 6.37835424e-05, 0.00000000e+00,
             1.00000000e+00, -9.27054679e-01, 0.00000000e+00],
            [1.00000000e+00, -1.78848938e+00, 1.00000000e+00,
             1.00000000e+00, -1.87008942e+00, 8.78235919e-01],
            [1.00000000e+00, -1.93118487e+00, 1.00000000e+00,
             1.00000000e+00, -1.90342568e+00, 9.17455718e-01],
            [1.00000000e+00, -1.95799864e+00, 1.00000000e+00,
             1.00000000e+00, -1.93318668e+00, 9.52433552e-01],
            [1.00000000e+00, -1.96671846e+00, 1.00000000e+00,
             1.00000000e+00, -1.95271141e+00, 9.75295685e-01],
            [1.00000000e+00, -1.97011885e+00, 1.00000000e+00,
             1.00000000e+00, -1.96423610e+00, 9.88608056e-01],
            [1.00000000e+00, -1.97135784e+00, 1.00000000e+00,
             1.00000000e+00, -1.97157693e+00, 9.96727086e-01]])

        self.expected = resonance.db.Channels(self.si, self.time, [
            [0.9999956457728433],
            [0.9998856845859893],
            [0.9996922260810792],
            [0.9995835104416045],
            [0.9994098250284393],
            [0.9990290084376168],
            [0.9986227124833456],
            [0.9981390093158422],
            [0.9973658219507469],
            [0.9964321938525657],
            [0.9953765403726055],
            [0.9939497244203208],
            [0.9921853483758439],
            [0.9901916705931763],
            [0.9877287730669466],
            [0.984716747347062],
            [0.9812986167220171],
            [0.9772882572298898],
            [0.9724999539302204],
            [0.9670678889858701],
            [0.9608913273476745],
            [0.9537101297613396],
            [0.9456077345179766],
            [0.9365808526356946],
            [0.9263437988327515],
            [0.9148999105054919]

        ])

        self.expected_2nd_block = resonance.db.Channels(self.si, self.time * 2, [
            [0.9023345056978992],
            [0.8883930339363232],
            [0.8729902011855225],
            [0.8562737901354261],
            [0.8380734326355362],
            [0.8182309579728637],
            [0.7969205956112334],
            [0.7740947767150088],
            [0.7495601406713566],
            [0.7234808638393732],
            [0.6959485315261033],
            [0.6667864534104619],
            [0.6361208549327353],
            [0.6041733791409701],
            [0.5708385401953315],
            [0.5361919014341386],
            [0.5005526955565384],
            [0.46393114504771965],
            [0.426357112973833],
            [0.388198374375762],
            [0.349604269337496],
            [0.31057936570650957],
            [0.27148427524928387],
            [0.23260287528465506],
            [0.19394387116185466],
            [0.15580917088829724]
        ])

    def test_single_channel(self):
        self.check_processor([self.si], [self.db], {'out_0': [self.expected]}, resonance.pipe.sosfilt, self.sos)

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

        self.check_processor([si], [data], {'out_0': [expected]}, resonance.pipe.sosfilt, self.sos)

    def test_multiple_blocks(self):
        data = resonance.db.Channels(self.si, self.time * 2, self.db)
        self.check_processor([self.si], [self.db, data], {'out_0': [self.expected, self.expected_2nd_block]},
                             resonance.pipe.sosfilt, self.sos)
