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


class ExecutionStep:
    def __init__(self, inputs, outputs, call):
        self.inputs = inputs
        self.outputs = outputs
        self.call = call

    def __repr__(self):
        return "ExecutionStep\ninputs={}\noutputs={}\ncall={}"\
            .format(self.inputs, self.outputs, self.call)


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


def declare_transformation(operator):
    if not issubclass(operator, Processor):
        raise Exception

    def call(*inputs):
        x = operator()
        return x.call(*inputs)

    return call


class Processor:

    def call(self, *inputs):
        outputs_si = self.prepare(*inputs)

        data_streams = list(filter(lambda x: isinstance(x, DataBlockBase), inputs))

        if data_streams[0].SI.online:
            # @todo: do all execution plan related stuff

            global execution_plan
            id = data_streams[0].SI.id
            input_si = list(
                map(
                    lambda x: x.SI,
                    filter(
                        lambda x: isinstance(x, resonance.db.Base),
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

#   processor(
#     data,
#     prepare = function(env){
#
#       id <- .execution_plan$nextOutputId
#       .execution_plan$nextOutputId <- .execution_plan$nextOutputId+1
#
#       args <- SI(data)
#       args$id <- id
#       args$name <- name
#
#       do.call(addToQueue, c(list("createOutputStream"), args))
#
#       env$id <- id
#
#       if(SI.is.channels(data))
#       {
#         env$cb <- function(data){
#           if(length(data)>0){
#             addToQueue(
#               "sendBlockToStream",
#               id = id,
#               data= data
#             )
#           }
#           list()
#         }
#       }
#       else if(SI.is.event(data))
#         {
#         env$cb <- function(data){
#           for(d in data){
#             addToQueue(
#               "sendBlockToStream",
#               id = id,
#               data= d
#             )
#           }
#           list()
#         }
#       }
#       else if(SI.is.window(data))
#       {
#         env$cb <- function(data){
#           for(d in data){
#             addToQueue(
#               "sendBlockToStream",
#               id = id,
#               data= d
#             )
#           }
#           list()
#         }
#       }
#       else if(SI.is.epoch(data))
#       {
#         env$cb <- function(data){
#           for(d in data){
#             addToQueue(
#               "sendBlockToStream",
#               id=id,
#               data=d
#             )
#           }
#           list()
#         }
#       }
#       else
#       {
#         stop("[createOutput] Unsupported stream type=",SI(data)$type, call.=F)
#       }
#
#       SI.outputStream(name, id)
#
#     },
#     online = function(data){
#       cb(data)
#     }
#   )
@declare_transformation
class create_output(Processor):
    def __init__(self):
        self._si = None
        self._callback = None

    def _send_np_based(self, data: resonance.db.Channels):
        if np.size(data, 0) > 0:
            add_to_queue('sendBlockToStream', (self._si, data))
        return resonance.db.OutputStream(self._si)

    def prepare(self, stream: resonance.db.Base, name: str):
        global execution_plan

        id = execution_plan.next_output_id

        execution_plan.next_output_id += 1

        if isinstance(stream.SI, resonance.si.Channels) or isinstance(stream.SI, resonance.si.Event) or isinstance(stream.SI, resonance.si.Window):
            self._callback = self._send_np_based
            self._si = resonance.si.OutputStream(id, name, stream.SI)
            add_to_queue('createOutputStream', self._si)
        else:
            raise Exception("Unsupported stream type")
    #       {
    #         env$cb <- function(data){
    #           if(length(data)>0){
    #             addToQueue(
    #               "sendBlockToStream",
    #               id = id,
    #               data= data
    #             )
    #           }
    #           list()
    #         }
    #       }
    #       else if(SI.is.event(data))
    #         {
    #         env$cb <- function(data){
    #           for(d in data){
    #             addToQueue(
    #               "sendBlockToStream",
    #               id = id,
    #               data= d
    #             )
    #           }
    #           list()
    #         }
    #       }
    #       else if(SI.is.window(data))
    #       {
    #         env$cb <- function(data){
    #           for(d in data){
    #             addToQueue(
    #               "sendBlockToStream",
    #               id = id,
    #               data= d
    #             )
    #           }
    #           list()
    #         }
    #       }
    #       else if(SI.is.epoch(data))
    #       {
    #         env$cb <- function(data){
    #           for(d in data){
    #             addToQueue(
    #               "sendBlockToStream",
    #               id=id,
    #               data=d
    #             )
    #           }
    #           list()
    #         }
    #       }
    #       else
    #       {
    #         stop("[createOutput] Unsupported stream type=",SI(data)$type, call.=F)
    #       }
    #
        return self._si

    def online(self, data: resonance.db.Base):
        ret = self._callback(data)
        return ret
