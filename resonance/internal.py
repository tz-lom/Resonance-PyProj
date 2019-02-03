from resonance.db import Base as DataBlockBase


def declare_transformation(operator):
    if not issubclass(operator, Processor):
        raise Exception

    def call(*inputs):
        x = operator()
        return x.call(*inputs)

    return call


class Processor:
    def __init__(self):
        pass

    def call(self, *inputs):
        self.prepare(*inputs)

        data_streams = list(filter(lambda x: isinstance(x, DataBlockBase), inputs))

        if data_streams[0].SI.online:
            # @todo: do all execution plan related stuff
            return self.online(*data_streams)
        else:
            if getattr(self, 'offline', None) is None:
                return self.online(*data_streams)
            else:
                return self.offline(*data_streams)
