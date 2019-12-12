import resonance.si as si
import resonance.db as db
from resonance.internal import declare_transformation, Processor
import numpy as np
import copy
import time
import math


'''
#' Split data stream to windows using event stream
#' 
#' @param data Data stream
#' @param events Events stream
#' @param windowSize Size of resulting window
#' @param backBuffer Size of buffer for data, may be increased in case of big delay in events arrival
#' @param dropLateEvents Don't expand buffer infinitely, lateTime controls buffer size and any events that arrive with timestamp earlier than last data timestamp-lateTime potentially can be dropped
#' @param lateTime - allowed delay for events (in seconds)
#' @return window
cross.windowizeByEvents <- function(data, events, windowSize, shift=0, dropLateEvents = TRUE, lateTime=10){
  processor(
    data, events,
    prepare = function(env){
      SI.is.channels(data) || stop("Data stream must be Channels")
      
      env$signal <- matrix(0.0, ncol=SI(data)$channels, nrow=2^5)
      env$pointer <- 0L
      env$si.times <- nanotime(rep(NA,nrow(env$signal)))
      env$lastTS <- NA
      env$lastSample <- 0
      env$grabSampleQueue <- list()
      env$windowSelector <- 1:windowSize-1
      env$samplingRate <- SI(data)$samplingRate
      if(dropLateEvents) {
        env$shiftBufferTo <- ceiling(lateTime*SI(data)$samplingRate)
        env$maxBufferSize <- env$shiftBufferTo*2
      } else {
        env$maxBufferSize <- Inf
      }
      
      SI.window(channels = SI(data)$channels, samples = windowSize, samplingRate = SI(data)$samplingRate)
    },
    online = function(si, events){
      # combin signal
      if(nrow(si)>0){
          
        if(nrow(si)+pointer >= nrow(signal))
        {
          tmp <- matrix(0.0, ncol=ncol(si), nrow=(nrow(signal)+nrow(si))*1.5)
          rowsCopy(tmp,0, signal, 0, -1)
          signal <<- tmp
          tmp <- vector(mode="double", length=nrow(signal))
          tmp[1:length(si.times)] <- si.times
          si.times <<- tmp
        }
        
        rowsCopy(signal, pointer, si, 0, -1)
        si.times[1:nrow(si)+pointer] <<- attr(si, 'TS')
        pointer <<- pointer+nrow(si)
        
        if(pointer > maxBufferSize){
          #diff <- pointer-shiftBufferTo
          shiftRows(signal, -shiftBufferTo)
          si.times[1:(nrow(signal)-shiftBufferTo)] <<- si.times[(shiftBufferTo+1):nrow(signal)]
          si.times[(nrow(signal)-shiftBufferTo):nrow(signal)] <<- 0
          pointer <<- pointer - shiftBufferTo
        }
      }
      
      # combine events
      if(length(events)>0){
        grabSampleQueue <<- c(grabSampleQueue, events)
      }
      
      ret <- list()
      
      while(length(grabSampleQueue)>0){
        gs <- TS(grabSampleQueue[[1]])
        
        moar <- timeInterval(gs, si.times)
        
        if(moar>0 && moar<length(si.times)){
          
          pos <- moar[1] + 1 + shift
          
          if(pos < 1) {
            # early event, drop it
            grabSampleQueue <<- grabSampleQueue[-1]
            next
          }
          
          if(pointer >= pos+windowSize){
            # get window and move on
            wnd <- signal[pos + windowSelector, , drop=F]
            TS(wnd) <- si.times[pos + windowSelector]
            # attr(wnd, 'byEvent') <- grabSampleQueue[[1]]
            
            grabSampleQueue <<- grabSampleQueue[-1]
            
            ret <- c(ret, list(wnd))
            next
          }
          break  # wait until full window arrives
          
        }else{
          break # waiting for samples
        }
      }
      ret
    })
}

'''
@declare_transformation
class WindowizeByEvents(Processor):

    def __init__(self):
        self._signal = None
        self._pointer = None
        self._si.times = None
        self._lastTS = None
        self._lastSample = None
        self._grabSampleQueue = None
        self._windowSelector = None
        self._samplingRate = None
        self._si = None
        self._maxBufferSize = None
        self._shiftBufferTo = None

    def prepare(self, input_stream, events, window_size, shift=0, drop_late_events=True, late_time=10):
        if not isinstance(input_stream, si.Channels):
            raise Exception("WindowizeByEvents processor: data stream must be Channels.")

        self._signal = np.zeros((input_stream.channels, 2 ^ 5))
        self._pointer = 0
        self._si.times = np.array(time.time_ns(), self._signal.shape[1])
        self._lastTS = None
        self._lastSample = 0
        self._grabSampleQueue = []
        self._windowSelector = np.arange(1, window_size)
        self._samplingRate = input_stream.samplingRate

        if drop_late_events:
            self._shiftBufferTo = math.ceil(late_time*input_stream.samplingRate)
            self._maxBufferSize = self._shiftBufferTo*2
        else:
            self._maxBufferSize = None

        self._si = si.Window(input_stream.channels, window_size, input_stream.samplingRate)
        return self._si

    def online(self, input_stream):
        print(input_stream.channels)


