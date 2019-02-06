import resonance.events as events
import resonance.si as si
import resonance.db as db
import resonance.state

try:
    import resonate
    resonate.register_callbacks(events.on_prepare, events.on_data_block, events.on_start, events.on_stop, si.Channels,
                                si.Event, db.Event, db.Channels)
except:
    pass


def input(id):
    raise Exception


def createOutput(name, data):
    raise Exception
