from resonance.db import Base as DataBlockBase
import resonance.si
import numpy as np
from functools import wraps
import typing
from collections.abc import Sequence


class ExecutionPlan:
    def __init__(self):
        self._plan = []
        self._inputs_data = []
        self._next_output_id = 0
        self._next_stream_id = 0
        self.reset([])

    def __repr__(self):
        return "ExecutionPlan\nplan={}\ninputs_data={}\nnext_output_id={}\nnext_stream_id={}".format(
            self._plan, self._inputs_data, self._next_output_id, self._next_stream_id
        )

    def steps_for_input(self, si):
        return [step for step in self._plan if step.has_input(si)]

    def reset(self, inputs):
        self._plan = []
        self._inputs_data = list(map(resonance.db.make_empty, inputs))
        self._next_output_id = 1
        self._next_stream_id = len(inputs) + 100

    def input_by_index(self, index):
        return self._inputs_data[index]

    def next_output_id(self):
        ret = self._next_output_id
        self._next_output_id += 1
        return ret

    def next_stream_id(self):
        ret = self._next_stream_id
        self._next_stream_id += 1
        return ret

    def add_step(self, input_si, output_si, callback):
        if isinstance(output_si, tuple):
            for stream in output_si:
                stream._id = self.next_stream_id()
                stream.online = True
        else:
            output_si._id = self.next_stream_id()
            output_si.online = True
        self._plan.append(ExecutionStep(input_si, output_si, callback))


class ExecutionStep:
    def __init__(self, inputs, outputs, call):
        self.inputs = inputs
        self.outputs = outputs
        self.call = call

    def __repr__(self):
        return "ExecutionStep\ninputs={}\noutputs={}\ncall={}".format(
            self.inputs, self.outputs, self.call
        )

    def has_input(self, si):
        return si in self.inputs


execution_plan = ExecutionPlan()

queue = []


def _add_to_queue(name, data):
    queue.append((name, data))


def pop_queue():
    global queue
    ret = queue
    queue = []
    return ret


add_to_queue = _add_to_queue


def reset():
    global execution_plan
    execution_plan = ExecutionPlan()


def declare_transformation(operator: type) -> object:
    if not issubclass(operator, Processor):
        raise Exception

    @wraps(operator.prepare)
    def call(*args, **kwargs):
        x = operator()
        return x.call(*args, **kwargs)

    return call


class Processor:
    def call(self, *inputs, **kwargs):
        outputs_si = self.prepare(*inputs, **kwargs)

        data_streams = list(filter(lambda x: isinstance(x, DataBlockBase), inputs))
        assert len(data_streams) > 0
        if data_streams[0].SI.online:
            assert all(map(lambda s: s.SI.online, data_streams))

            input_si = list(map(lambda s: s.SI, data_streams))

            global execution_plan

            execution_plan.add_step(input_si, outputs_si, self)
            if isinstance(outputs_si, tuple):
                return tuple(map(resonance.db.make_empty, outputs_si))
            else:
                return resonance.db.make_empty(outputs_si)
        else:
            if getattr(self, "offline", None) is None:
                return self.online(*data_streams)
            else:
                return self.offline(*data_streams)


@declare_transformation
class create_output(Processor):
    def __init__(self):
        self._si = None
        self._stream_si = None
        self._callback = None

    def _send_data(self, data):
        add_to_queue("sendBlockToStream", (self._si, data))
        return resonance.db.OutputStream(self._si)

    def _send_channels(self, data: resonance.db.Channels):
        if np.size(data, 1) > 0:
            add_to_queue("sendBlockToStream", (self._si, data))
        return resonance.db.OutputStream(self._si)

    def _send_event(self, data: resonance.db.Event):
        if len(data) > 0:
            for i in range(data.shape[0]):
                add_to_queue("sendBlockToStream", (self._si, data[i : i + 1]))
        return resonance.db.OutputStream(self._si)

    def _send_window(self, data: resonance.db.Window):
        if len(data) > 0:
            for i in range(data.shape[0]):
                add_to_queue("sendBlockToStream", (self._si, data[i : i + 1]))
        return resonance.db.OutputStream(self._si)

    def prepare(self, stream: resonance.db.Base, name: str):
        global execution_plan

        sid = execution_plan.next_output_id()

        if isinstance(stream.SI, resonance.si.Channels):
            self._callback = self._send_data
        elif isinstance(stream.SI, resonance.si.Event):
            self._callback = self._send_data
        elif isinstance(stream.SI, resonance.si.Window):
            self._callback = self._send_data
        else:
            raise Exception("Unsupported stream type")
        self._si = resonance.si.OutputStream(sid, name, stream.SI)
        self._stream_si = stream.SI
        add_to_queue("createOutputStream", self._si)
        return self._si

    def online(self, data: resonance.db.Base):
        ret = self._callback(data)
        return ret
