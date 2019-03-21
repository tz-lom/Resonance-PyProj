import resonance
import resonance.db as db
from resonance.si import Base as StreamInfo
import resonance.events as events
from typing import Sequence, Callable, Union


code_type = Union[Callable[[], None], str] # @todo: add code object type to this list


#
#  run.offline <- function(inputs, blocks, code, env=new.env()) {
#
#   data <- lapply(inputs, function(si){
#     F <- Filter(function(x){
#       identical(SI(x), si)
#     }, blocks)
#
#     if(length(F)){
#       do.call(DBcombine, F)
#     }else{
#       makeEmpty(si)
#     }
#   })
#
#
#   env$input <- function(index){
#     if(index>0 && index<=length(data)){
#       data[[index]]
#     } else {
#       stop('Unknown input required')
#     }
#   }
#
#   results <- list()
#
#   env$createOutput <- function(out, name){
#     results[[name]] <<- out
#   }
#
#   if(!is.language(code)) code <- parse(text=code)
#
#   eval(code, env)
#   env$process()
#
#   results
# }
#
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


#
# old_inputs <- inputs
##
#   inputs <- mapply(FUN=function(x, id){
#     x$online <- T
#     if(is.null(x$id) || x$id == -1){
#       x$id = id
#     }
#     x
#   }, inputs, seq_len(length(inputs)), SIMPLIFY = FALSE)
#
#   blocks <- lapply(blocks, function(x){
#     SI(x) <- inputs[sapply(old_inputs, identical, SI(x))][[1]]
#     x
#   })
#
#   sis <- list()
#   datas <- list()
#   siNames <- list()
#   timers <- data.frame(id=integer(), time=bit64::integer64(), timeout=numeric(), singleShot=logical())
#   currentTime <- nanotime(0)
#
#   processQueue <- function(){
#     Q <- popQueue()
#     lapply(Q, function(x){
#       if(x$cmd == 'createOutputStream'){
#         L <- x$args
#         sis[[L$id]] <<- L[!(names(L) %in% c('id', 'name', 'online'))]
#         siNames[[L$id]] <<- L$name
#         datas[[L$name]] <<- list(makeEmpty(sis[[L$id]]))
#       }
#       if(x$cmd == 'sendBlockToStream'){
#         si <- sis[[x$args$id]]
#
#         data <- x$args$data
#
#         datas[[siNames[[x$args$id]]]] <<- c(
#           datas[[siNames[[x$args$id]]]],
#           list(
#             DB.something(
#               si,
#               TS(x$args$data),
#               data
#             )
#           )
#         )
#       }
#       if(x$cmd == 'startTimer'){
#         timers <<- rbind(
#           timers,
#           data.frame(
#             id = x$args$id,
#             time = currentTime + x$args$timeout*1E6,
#             timeout = x$args$timeout*1E6,
#             singleShot = x$args$singleShot
#           ))
#       }
#       if(x$cmd == 'stopTimer'){
#         timers <<- timers[timers$id != x$args$id, ]
#       }
#     })
#   }
#
#   # actual execution
#
#   onPrepare(inputs, code, env)
#   processQueue()
#
#   onStart()
#   processQueue()
#
#   lapply(blocks, function(x){
#     currentTime <<- lastTS(x)
#     # maybe some timers will trigger before this data block
#     while(nrow(timers)>0 && length(toProcess <- which(timers$time<currentTime))>0){
#       toProcess <- toProcess[order(timers$time[toProcess])[1]]
#
#       timer <- timers[toProcess, ]
#       currentTime <<- timer$time
#       onTimer(timer$id, timer$time)
#       processQueue()
#       if(!timer$singleShot){
#         timers[toProcess, 'time'] <<- currentTime + timer$timeout
#       } else {offline
#

def online(stream_info: Sequence[StreamInfo], blocks: Sequence[db.Base], code: code_type):
    outputs = {}

    id = 100
    for si in stream_info:
        si.online = True
        if si.id is None:
            si._id = id
            id += 1

    def process_queue():
        queue = resonance.internal.pop_queue()
        if len(queue) > 0:
            for cmd, data in queue:
                if cmd == 'createOutputStream':
                    outputs[data.name] = [db.make_empty(data._source)]
                    pass
                if cmd == 'sendBlockToStream':
                    si, block = data
                    outputs[si.name].append(block)
                    pass
            #       if(x$cmd == 'createOutputStream'){
            #         L <- x$args
            #         sis[[L$id]] <<- L[!(names(L) %in% c('id', 'name', 'online'))]
            #         siNames[[L$id]] <<- L$name
            #         datas[[L$name]] <<- list(makeEmpty(sis[[L$id]]))
            #       }
            #       if(x$cmd == 'sendBlockToStream'){
            #         si <- sis[[x$args$id]]
            #
            #         data <- x$args$data
            #
            #         datas[[siNames[[x$args$id]]]] <<- c(
            #           datas[[siNames[[x$args$id]]]],
            #           list(
            #             DB.something(
            #               si,
            #               TS(x$args$data),
            #               data
            #             )
            #           )
            #         )
            #       }
            #       if(x$cmd == 'startTimer'){
            #         timers <<- rbind(
            #           timers,
            #           data.frame(
            #             id = x$args$id,
            #             time = currentTime + x$args$timeout*1E6,
            #             timeout = x$args$timeout*1E6,
            #             singleShot = x$args$singleShot
            #           ))
            #       }
            #       if(x$cmd == 'stopTimer'){
            #         timers <<- timers[timers$id != x$args$id, ]
            #       }
            #     })

    events.on_prepare(code, stream_info)
    process_queue()

    events.on_start()
    process_queue()

    for block in blocks:
        events.on_data_block(block)
        process_queue()

    events.on_stop()
    process_queue()

    return {name: db.combine(*values) for name, values in outputs.items()}
