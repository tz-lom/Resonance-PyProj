import resonance
import resonance.internal as internal
import resonance.db as db


def on_data_block(block):
    plan = internal.execution_plan.get_node_by_input(block.SI)
    if plan is None:
        return

    def prepare_input(si):
        if isinstance(si, resonance.si.Base):
            if si == block.SI:
                return block
            else:
                return db.make_empty(si)
        else:
            return si

    args = list(map(prepare_input, plan.inputs))
    result = plan.call.online(*args)
    on_data_block(result)


def on_start():
    pass


def on_stop():
    pass


def on_prepare(code, descriptions):
    internal.reset()
    internal.execution_plan.inputs_data = list(map(db.make_empty, descriptions))
    internal.execution_plan.next_stream_id = len(descriptions) + 1

    def plan_input(index):
        return internal.execution_plan.inputs_data[index]

    resonance.input = plan_input
    resonance.createOutput = resonance.internal.create_output

    if callable(code):
        code()
    else:
        exec(code)

