class Base:
    def __init__(self, id=None, name=None):
        self._id = id
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name


class Channels(Base):
    def __init__(self, channels, samplingRate, id=None, name=None):
        Base.__init__(self, id, name)
        self._channels = channels
        self._samplingRate = samplingRate

    @property
    def channels(self):
        return self._channels

    @property
    def samplingRate(self):
        return self._samplingRate


class Event(Base):
    pass