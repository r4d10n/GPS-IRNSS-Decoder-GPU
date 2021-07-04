import pickle
from collections import defaultdict
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab

def NestedDictValues(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from NestedDictValues(v)
        else:
           yield v

def load(file):
    f = open(file, 'rb')
    svdata = pickle.load(f)
    f.close()
    return svdata

def mayaviplot(resultant):
    x = np.arange(-10000, 10500, 500)
    y = np.arange(1, 16369, 1)
    X,Y = np.meshgrid(y,x)

    #fig.set_size_inches((15, 15), forward=True)
    #cmap = plt.cm.get_cmap("hsv", 38)

    for svid in range(1,2):
        mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
        Z = np.array(list(resultant[svid].values()))

        # Visualize the points
        pts = mlab.points3d(X, Y, Z, Z, scale_mode='none', scale_factor=0.05)

        # Create and visualize the mesh
        #mesh = mlab.pipeline.delaunay2d(pts)
        #surf = mlab.pipeline.surface(mesh)
        #mlab.surf(X,Y,Z)
        #surf.scene.anti_aliasing_frames = 0
        mlab.view(47, 57, 8.2, (0.1, 0.15, 0.14))
        mlab.show()

def plot(resultant):
    x = np.arange(-10000, 10500, 500)
    y = np.arange(1, 16369, 1)
    X,Y = np.meshgrid(y,x)

    #fig.set_size_inches((15, 15), forward=True)
    #cmap = plt.cm.get_cmap("hsv", 38)

    for svid in range(1,33):
        fig = plt.figure(figsize=plt.figaspect(0.5))

        Z = np.array(list(resultant[svid].values()))
        ax = plt.axes(projection='3d')

        surf = ax.plot_surface(X, Y, Z, cstride=1, cmap='viridis', edgecolor='none', linewidth=0, antialiased=False)
        #fig.colorbar(surf, shrink=0.5, aspect=10)

        ax.set_xlabel('Doppler KHz')
        ax.set_ylabel('PRN Code Phase')
        ax.set_title('SV ID#' + str(svid))

        plt.show(block = False)
        plt.pause(0.0001)

        #fig.savefig('sv' + svid +'.png', bbdpi=600)

svdata = load("svdata.dat")
mayaviplot(svdata)
#plt.show()

""""
#x = np.array(list(svdata.keys()))
x = np.arange(-10000, 10500, 500)
print(x)
y = np.arange(1, 16369, 1)
#y = np.array(list(svdata[0].keys()))
print(y)
X,Y = np.meshgrid(y,x)
Z = np.array(svdata)
print(X.shape, Y.shape, Z.shape)

#Z = np.array(list(NestedDictValues(svdata)))
#Z = np.array(svdata)
#print(len(Z))

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
plt.show(block = True)
"""