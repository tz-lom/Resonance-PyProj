import resonance
import resonance.internal as internal
import resonance.db as db
import resonance.run


#   to_restore <- .execution_plan$processingPlanId
#   execId <- findInExectionPlan(SI(block))
#   if(length(execId)>0){
#     .execution_plan$processingPlanId <- execId
#     target <- .execution_plan$plan[[execId]]
#
#     argList <- lapply(target$inputs, function(si){
#       if(identical(si, SI(block)))
#         block
#       else
#         makeEmpty(si)
#     })
#
#     result <- do.call(target$online, argList)
#
#     if(class(result)=='multipleStreams'){
#       mapply(function(data, si){
#         SI(data) <- si
#         onDataBlock(data)
#       }, result, target$outputs)
#     } else {
#       SI(result) <- target$outputs[[1]]
#       onDataBlock(result)
#     }
#     .execution_plan$processingPlanId <- to_restore
#   }
#
def on_data_block(block):

    plan = internal.execution_plan.plan.get(block.SI.id)

    print(internal.execution_plan)

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
    result.si = plan.outputs
    on_data_block(result)


def on_start():
    pass


def on_stop():
    pass


def on_prepare(code: resonance.run.code_type, descriptions):
    internal.reset()
    internal.execution_plan.inputs_data = list(map(db.make_empty, descriptions))
    internal.execution_plan.next_stream_id = len(descriptions) + 1

    def input(id):
        return internal.execution_plan.inputs_data[id]

    resonance.input = input
    resonance.createOutput = resonance.internal.create_output

    if callable(code):
        code()
    else:
        exec(code)


