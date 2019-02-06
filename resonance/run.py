import resonance
import resonance.db as db
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

def offline(input, blocks, code):

    def combine_blocks(si):
        data = list(filter(lambda x: x.SI == si, blocks))
        if len(data):
            return db.combine(*data)
        else:
            return db.make_empty(si)

    input_list = list(map(combine_blocks, input))
    results = {}

    def input(id):
        return input_list[id]

    def create_output(name, data):
        results[name] = data

    resonance.input = input
    resonance.createOutput = create_output

    exec(code)

    return results
