import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor


@declare_transformation
class transform_to_event(Processor):
    def __init__(self):
        self._si = None
        self._transform = None

    def prepare(self, input: db.Base, transform):
        self._si = si.Event()
        self._transform = transform
        return self._si

    def online(self, input):
        return db.combine(
            db.make_empty(self._si),
            *[
                db.Event(self._si, block.TS[0:1], self._transform(block))
                for block in input
            ]
        )