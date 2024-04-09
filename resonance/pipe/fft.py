import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
from scipy import signal
import scipy


@declare_transformation
class fft(Processor):
    def __init__(self):
        self._si = None
        self._channels = None
        self._window = None
        self._filter = None
        self._prealloc = None

    # array([(1, 1.1), (2, 1.2)],
    #       dtype=[('channel', 'i4'), ('frequency', 'f8')])
    def prepare(self, input: db.Window, selection, normalize=False):
        if not isinstance(input, db.Window):
            raise Exception("input must be window")

        self._channels = np.unique(selection["channel"])
        self._window = input.SI.samples

        fq_max = self._window / 2

        def select_freq(sel):
            col = np.where(self._channels == sel["channel"])[0][0]
            fq = sel["frequency"]
            if fq >= fq_max:
                raise Exception(f"Requested frequency {fq} is higher than max {fq_max}")
            return col + fq * len(self._channels)

        self._filter = np.asarray([select_freq(sel) for sel in selection], dtype="i")

        self._prealloc = np.zeros((len(self._channels), self._window))

        self._si = si.Channels(
            channels=len(self._filter), samplingRate=input.SI.samplingRate
        )

        return self._si

    def online(self, windows):
        def transform_window(wnd: db.SingleWindow):
            self._prealloc = wnd[:, self._channels]
            # spectre = np.fft.hfft(self._prealloc, n=self._prealloc.shape[0]//2, axis=0)
            spectre = 10 * np.log10(
                (np.abs(scipy.fft.fft(self._prealloc, axis=0)) ** 2)
            )
            return np.take_along_axis(spectre, self._filter, None)

        return db.Channels(
            self._si,
            [wnd.timestamps[-1] for wnd in windows],
            [transform_window(wnd) for wnd in windows],
        )
