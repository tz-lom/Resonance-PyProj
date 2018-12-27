import events
import si
import db

try:
    import resonate
    resonate.register_callbacks(events.on_prepare, events.on_data_block, events.on_start, events.on_stop, si.Channels,
                                si.Event, db.event, db.channels)
except:
    pass

print "Resonance loaded"