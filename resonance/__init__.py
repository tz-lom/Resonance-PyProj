from . import pipe
try:
    import resonate

    import resonance.events as events
    import resonance.si as si
    import resonance.db as db
    import resonance.state
    import resonance.internal

    resonate.register_callbacks(
        events.on_prepare,
        events.on_data_block,
        events.on_start,
        events.on_stop,
        si.Channels,
        si.Event,
        db.Event,
        db.Channels)

    resonance.internal.add_to_queue = resonate.add_to_queue

except:
    pass


def input(id):
    raise Exception("Can't execute directly")


def createOutput(name, data):
    raise Exception("Can't execute directly")
