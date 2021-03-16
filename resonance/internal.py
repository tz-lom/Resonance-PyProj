from resonance.db import Base as DataBlockBase
import resonance.si
import numpy as np
import typing


class ExecutionPlan:
    def __init__(self):
        self.plan = {}
        self.inputs_data = []
        self.next_output_id = 1
        self.next_stream_id = 1

    def __repr__(self):
        return "ExecutionPlan\nplan={}\ninputs_data={}\nnext_output_id={}\nnext_stream_id={}"\
            .format(self.plan, self.inputs_data, self.next_output_id, self.next_stream_id)

    def get_node_by_input(self, si):
        for step in self.plan.values():
            if step.has_input(si):
                return step
        return None


class ExecutionStep:
    def __init__(self, inputs, outputs, call):
        self.inputs = inputs
        self.outputs = outputs
        self.call = call

    def __repr__(self):
        return "ExecutionStep\ninputs={}\noutputs={}\ncall={}"\
            .format(self.inputs, self.outputs, self.call)

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


def declare_transformation(operator: object) -> object:
    if not issubclass(operator, Processor):
        raise Exception

    def call(*args, **kwargs):
        x = operator()
        return x.call(*args, **kwargs)

    return call


class Processor:
    def call(self, *inputs):
        outputs_si = self.prepare(*inputs)

        data_streams = list(
            filter(lambda x: isinstance(x, DataBlockBase), inputs))

        if data_streams[0].SI.online:
            # @todo: do all execution plan related stuff

            global execution_plan
            id = data_streams[0].SI.id
            input_si = list(
                map(lambda x: x.SI,
                    filter(lambda x: isinstance(x, resonance.db.Base),
                           inputs)))

            # @todo: this could be either "array" or si object
            outputs_si._id = execution_plan.next_stream_id
            execution_plan.next_stream_id += 1
            outputs_si.online = True

            execution_plan.plan[id] = ExecutionStep(input_si, outputs_si, self)

            return resonance.db.make_empty(outputs_si)
        else:
            if getattr(self, 'offline', None) is None:
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
        add_to_queue('sendBlockToStream', (self._si, data))
        return resonance.db.OutputStream(self._si)

    def _send_channels(self, data: resonance.db.Channels):
        if np.size(data, 1) > 0:
            add_to_queue('sendBlockToStream', (self._si, data))
        return resonance.db.OutputStream(self._si)

    def _send_event(self, data: resonance.db.Event):
        if len(data) > 0:
            for i in range(data.shape[0]):
                add_to_queue('sendBlockToStream', (self._si, data[i:i + 1]))
        return resonance.db.OutputStream(self._si)

    def _send_window(self, data: resonance.db.Window):
        if len(data) > 0:
            for i in range(data.shape[0]):
                add_to_queue('sendBlockToStream', (self._si, data[i:i + 1]))
        return resonance.db.OutputStream(self._si)

    def prepare(self, stream: resonance.db.Base, name: str):
        global execution_plan

        sid = execution_plan.next_output_id
        execution_plan.next_output_id += 1

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
        add_to_queue('createOutputStream', self._si)
        return self._si

    def online(self, data: resonance.db.Base):
        ret = self._callback(data)
        return ret
