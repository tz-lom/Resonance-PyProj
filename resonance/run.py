import resonance
import resonance.db as db
from resonance.si import Base as StreamInfo
import resonance.events as events
from typing import Sequence, Callable, Union


code_type = Union[Callable[[], None], str]  # @todo: add code object type to this list


def offline(stream_info: Sequence[StreamInfo], blocks: Sequence[db.Base], code: code_type):

    def combine_blocks(si):
        data = list(filter(lambda x: x.SI == si, blocks))
        if len(data):
            return db.combine(*data)
        else:
            return db.make_empty(si)

    input_list = list(map(combine_blocks, stream_info))
    results = {}

    def input_handler(id):
        return input_list[id]

    def create_output(data, name):
        results[name] = data

    resonance.input = input_handler
    resonance.createOutput = create_output

    if callable(code):
        code()
    else:
        exec(code)

    return results


def online(stream_info: Sequence[StreamInfo], blocks: Sequence[db.Base], code: code_type, return_blocks: bool = False):
    outputs = {}

    id = 100
    for i_si in stream_info:
        i_si.online = True
        if i_si.id is None:
            i_si._id = id
            id += 1

    def process_queue():
        queue = resonance.internal.pop_queue()
        if len(queue) > 0:
            for cmd, data in queue:
                if cmd == 'createOutputStream':
                    outputs[data.name] = []
                    pass
                if cmd == 'sendBlockToStream':
                    si, block = data
                    outputs[si.name].append(block)
                    pass

    events.on_prepare(code, stream_info)
    process_queue()

    events.on_start()
    process_queue()

    for block in blocks:
        events.on_data_block(block)
        process_queue()

    events.on_stop()
    process_queue()

    if return_blocks:
        return outputs
    else:
        return {name: db.combine(*values) for name, values in outputs.items()}
