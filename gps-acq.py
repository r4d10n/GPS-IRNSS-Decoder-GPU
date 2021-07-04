from os import write
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from mayavi import mlab
import numpy as np
import scipy.signal as signal
import math, sys
from collections import defaultdict, deque
from timeit import default_timer as timer
import pickle
import genCAcode
import ThrustRTC as trtc
import csv

def p(*args):
    namespace = globals()
    for arg in args:
        name = [name for name in namespace if namespace[name] is arg]
        #if (hasattr(arg, 'len')):
        print(name,'[',len(arg),']=>', arg)
        #else: print (name, '-', arg)

def dump(result, file):
    f = open(file, 'wb')
    pickle.dump(result,f)
    f.close()

def writecsv(result, file):
    x = np.arange(-10000, 10500, 500)
    y = np.arange(1, 16369, 1)
    with open(file, mode='w') as result_file:
        result_writer = csv.writer(result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE, escapechar='\\')

        result_writer.writerow([0] + y)
        for i in range(41):
            result_writer.writerow(x[i]+ result[i])

def matplot(svid, resultant):
    x = np.arange(-10000, 10500, 500)
    y = np.arange(1, 16369, 1)
    X,Y = np.meshgrid(y,x)
    Z = np.array(resultant)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, cstride=1, cmap='viridis', edgecolor='none', linewidth=0, antialiased=False)
    ax.set_ylabel('Doppler KHz')
    ax.set_xlabel('PRN Code Phase')
    ax.set_title('SV ID#' + str(svid))

    plt.show(block = False)
    #fig.savefig('sv_'+str(svid)+'.png', bbdpi=600)

def mayaviplot(svid, resultant):
    x = np.arange(-10000, 10500, 500)
    y = np.arange(1, 16369, 1)
    X,Y = np.meshgrid(y,x)
    Z = np.array(resultant)

    mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))

    # Visualize the points
    pts = mlab.points3d(X, Y, Z, Z, scale_mode='none', scale_factor=0.05)

    # Create and visualize the mesh
    mesh = mlab.pipeline.delaunay2d(pts)
    surf = mlab.pipeline.surface(mesh)

    surf.scene.anti_aliasing_frames = 0
    #mlab.view(47, 57, 8.2, (0.1, 0.15, 0.14))
    mlab.show()

    #ax.set_ylabel('Doppler KHz')
    #ax.set_xlabel('PRN Code Phase')
    #ax.set_title('SV ID#' + str(svid))


np.set_printoptions(threshold=sys.maxsize)

sv = defaultdict(np.array)
dopplerSet = []

sampleRateFs = 16368000
sampsPerChip = 16                               # No of samples for 1 chip - 1ms [16368000/1023*1000]
chiplen = 1023 * sampsPerChip                   # Total Chip Length [16368]

cmacKernel = trtc.Kernel(['rDopplerVec','iDopplerVec','rCodePhaseVec','iCodePhaseVec', 'resultant'],
                        '''
                        size_t idx = blockIdx.x * blockDim.x * blockDim.y  + threadIdx.y * blockDim.x + threadIdx.x;
                        size_t len = rDopplerVec.size();
                        if (idx > len) return;
                        float iSum, qSum;

                        for(int i=0, j=0; i < len; i++)
                        {
                            j = (i+idx) % len;
                            iSum = iSum + ((rDopplerVec[i] * rCodePhaseVec[j]) - (iDopplerVec[i] * iCodePhaseVec[j]));
                            qSum = qSum + ((rDopplerVec[i] * iCodePhaseVec[j]) + (iDopplerVec[i] * rCodePhaseVec[j]));
                        }
                        resultant[idx] = (iSum * iSum) + (qSum * qSum);
                        ''')

def computeSumVectorGPU(sv, freqSweep):

    N = 16368
    T = 1024
    B = 16

    rCodePhase = trtc.device_vector_from_numpy(np.array([np.real(codePhase) for codePhase in sv], dtype='float32'))
    iCodePhase = trtc.device_vector_from_numpy(np.array([np.imag(codePhase) for codePhase in sv], dtype='float32'))
    rDoppler = trtc.device_vector_from_numpy(np.array([np.real(doppler) for doppler in freqSweep], dtype='float32'))
    iDoppler = trtc.device_vector_from_numpy(np.array([np.imag(doppler) for doppler in freqSweep], dtype='float32'))

    resultant = trtc.device_vector('float', N)

    #start = timer()
    cmacKernel.launch(B,T, [rDoppler, iDoppler, rCodePhase, iCodePhase, resultant])
    res = resultant.to_host()
    #end = timer()
    #print("GPU Time:", end-start)
    return res

def computeSumVectorCPU(sv, freqSweep):
    codePhase = deque(sv)
    res = []
    #print(len(freqSweep * codePhase))

    start = timer()
    for i in range(len(freqSweep)):
        doppler_codePhase_mix = freqSweep * codePhase
        iSum = sum([phase.real for phase in doppler_codePhase_mix])
        qSum = sum([phase.imag for phase in doppler_codePhase_mix])
        res.append((iSum * iSum) + (qSum * qSum))
        codePhase.rotate(1)
    end = timer()

    print("Res:", res)
    print("CPU Time:", end-start)
    return res


if __name__ == '__main__':

    dat = np.fromfile("gps-16368-1s-16b-i.iq",dtype="int16")    # Read signed 16bit integers from file

    dat = dat[0::2] + 1j*dat[1::2]                  # Convert interleaved IQ to complex

    dat = dat * 2**-11                              # Division by 2^-11 to normalize in (0.5,-0.5) interval
    iq_data = dat[2*chiplen:(3*chiplen)]

    iqMax = np.amax(dat)
    iqMin = np.amin(dat)
    print("IQ max:" + str(iqMax) + " | min:" + str(iqMin))
    print("Sample size: ", len(iq_data))

    for id in range(1,38):
        sv[id] = genCAcode.genCA(id, nrz = True, sampsPerChip = sampsPerChip)           # Generate CA code for all satellite ids
        sv[id] = np.array(sv[id], dtype="int16").astype('complex')                      # Convert to complex array

    dopplerCoefficient = 1j * 2 * math.pi / sampleRateFs
    for fc in range(-10000, 10500, 500):
            dopplerSet.append([np.exp(dopplerCoefficient * fc * phase) for phase in range(1, chiplen+1)])
    dopplerSet = np.asarray(dopplerSet)

    freqSweep = dopplerSet * iq_data

    print("Freq Sweep Size: ", freqSweep.shape)
    for svid in range(1,2):
        resultant = [] # defaultdict(dict)
        start = timer()
        for fc in range(len(dopplerSet)):
            #resultant[svid][fc] = computeSumVectorGPU(sv[svid], freqSweep[fc])
            resultant.append(computeSumVectorGPU(sv[svid], freqSweep[fc]))
            #print(svid, fc)
        end = timer()
        #print("\n\n\n\nResultant:",len(resultant[svid]),len(resultant[svid][0]))
        print(svid, end-start)
        mayaviplot(svid, resultant)
        #writecsv(resultant,'sv_' + str(svid) + '.csv')

    #plt.show(block = True)

    #dump(resultant, "svdata.dat")

    #plot(resultant)

    #resCPU = computeSumVectorCPU(sv[1], freqSweep[1])
    #print("\n\n\n\n\n************\n\n\n\n\n")
    #print("Diff:", np.array(resCPU) - np.array(resGPU))
