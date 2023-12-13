from .file import hdf5
import resonance.run
from cache_to_disk import cache_to_disk


def playback(file: str, code, online=False, cache=3):
    @cache_to_disk(cache)
    def load(fname):
        return hdf5(fname)

    (si, data) = load(file)

    if online:
        return resonance.run.online(si, data, code)
    else:
        return resonance.run.offline(si, data, code)
