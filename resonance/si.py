import resonance.db as db


class Base:
    def __init__(self, id=None, name=None):
        self._id = id
        self._name = name
        self.online = False

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Channels(Base):
    def __init__(self, channels, samplingRate, id=None, name=None):
        Base.__init__(self, id, name)
        self._channels = channels
        self._samplingRate = samplingRate
        self.db_type = db.Channels

    @property
    def channels(self):
        return self._channels

    @property
    def samplingRate(self):
        return self._samplingRate


class Event(Base):
    def __init__(self, id=None, name=None):
        Base.__init__(self, id, name)


class Window(Base):
    def __init__(self, channels, samples, samplingRate, id=None, name=None):
        Base.__init__(self, id, name)
        self._channels = channels
        self._samples = samples
        self._samplingRate = samplingRate
        self.db_type = db.Window

    @property
    def channels(self):
        return self._channels

    @property
    def samples(self):
        return self._samples

    @property
    def samplingRate(self):
        return self._samplingRate



class OutputStream(Base):
    def __init__(self, id, name, source):
        Base.__init__(self, id, name)
        self._source = source
