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


def on_prepare(code, inputs):
    internal.execution_plan.reset(inputs)

    resonance.__input = internal.execution_plan.input_by_index
    resonance.__createOutput = resonance.internal.create_output

    if callable(code):
        code()
    else:
        exec(code)
