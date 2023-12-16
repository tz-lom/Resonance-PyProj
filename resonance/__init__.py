import resonance.db as db

try:
    import resonate

    import resonance.events as events
    import resonance.si as si
    import resonance.internal

    resonate.register_callbacks(
        events.on_prepare,
        events.on_data_block,
        events.on_start,
        events.on_stop,
        si.Channels,
        si.Event,
        db.Event,
        db.Channels,
    )

    resonance.internal.add_to_queue = resonate.add_to_queue
    resonance.running_in_speed = True

except:
    pass

from .split import split
from .simulation import playback


def __input(idx: int):
    raise Exception("Can't execute directly")


def input(idx: int):
    return __input(idx)


def __createOutput(name: str, data: db.Base):
    raise Exception("Can't execute directly")


def createOutput(data: db.Base, name: str):
    return __createOutput(data, name)
