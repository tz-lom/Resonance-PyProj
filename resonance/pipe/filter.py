import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
from scipy import signal


@declare_transformation
class filter(Processor):
    def __init__(self):
        self._si = None
        self._b = None
        self._a = None
        self._zi = None

    def prepare(self, channels: db.Channels, ba_filter):
        if not isinstance(channels, db.Channels):
            raise Exception("input must be channels")

        self._si = si.Channels(channels=channels.SI.channels, samplingRate=channels.SI.samplingRate)
        self._b, self._a = ba_filter
        z = signal.lfilter_zi(self._b, self._a)
        channels = channels.SI.channels
        self._zi = np.repeat(z, channels).reshape((len(z), channels))

        return self._si

    def online(self, channels):
        ret, zo = signal.lfilter(self._b, self._a, channels, 0, self._zi)
        self._zi = zo

        return db.Channels(self._si, channels.TS, ret)
