import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor


@declare_transformation
class transform_channels(Processor):
    def __init__(self):
        self._si = None
        self._transform = None

    def prepare(self, input: db.Channels, outputChannels, transform):
        if not isinstance(input, db.Channels):
            raise Exception("input must be channels")

        self._si = si.Channels(channels=outputChannels, samplingRate=input.SI.samplingRate)
        self._transform = transform
        return self._si

    def online(self, channels):
        ret = self._transform(channels)
        return db.Channels(self._si, channels.TS, ret)
