import resonance.si


def timeoption2ts(si: resonance.si.Channels, x):
    return x * 1E9 / si.samplingRate
