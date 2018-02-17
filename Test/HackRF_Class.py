from pylibhackrf import hackrfCtrl
import time
import timeit 
import numpy as np

def timesTorun(minTime, maxTime, sampleRate):
    minTime *= 1.0
    maxTime *= 1.0
    numTimes = np.ceil((maxTime - minTime) / sampleRate)
    return numTimes

if __name__ == '__main__':
    hackrf = hackrfCtrl()
    Startf = 104e6
    Finishf = 107e6
    center_frequency = int(106e6)
    sample_rate = 2.048e6
    timesRan = 0
        
    #center_frequency = int(Startf + (sample_rate/2))
    #print(center_frequency)
    
    data_pts = hackrf.setParameters(center_frequency, sample_rate)
    
    start1 = timeit.default_timer()
    iq = hackrf.hackrf_run(5)
    stop1 = timeit.default_timer()
    
    #print(iq)
    print stop1 - start1 
    
    strname = str(center_frequency/1e6) + 'e6' #+ str(time.strftime('%m_%d_%H_%M', time.localtime()))
    print(strname)
    #np.savez(strname, data_pts = data_pts, iq = iq)