#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dddheatmap.py
#  
#  Copyright 2016 Cosmo <cosmo@CosmoSpectre>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA. Also, see <http://www.gnu.org/licenses/>.


# Imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), 'dependencies'))
from neuron_readExportedGeometry import *
from rotanimate import *
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
#%matplotlib inline # For use with Jupyter Notebooks.


# Testing
thoc = '/home/cosmo/marderlab/test/878_043_GM_scaled.hoc'


# Instructions
def pathhelp():
	print('\n*Use pathplot(\'hoc file\') to view the heatmap for a given hoc file.')
	print('*EXAMPLE: pathplot(\'/home/cosmo/marderlab/hocs/878_043_GM_scaled.hoc\')')
	print('*NOTE: The folder must NOT contain anything besides hoc files.')
	print('\n*Use pathhelp() to view these instructions again.')
pathhelp()


# Plots the path heat map in 3D.
def pathplot(hoc, movie='', ms=15, fs=30, lw=2, res=30, invert=True, pkl=''):

    # Initialize figure.
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Convert given hoc file into a geo object.
    print('*Building geo object for {}, please wait...'.format(hoc))
    geo = demoReadsilent(hoc)
    print('*Building heatmap for {}, please wait...'.format(hoc))

    # Find the tip segments and their end locations.
    tips, ends = geo.getTips()
   
    # Calculate the path distance to each tip.
    pDF = PathDistanceFinder(geo, geo.soma)
    pdists = [pDF.distanceTo(seg) for seg in tips]
   
    # Calculate the coordinate position of each tip.
    coords = [tips[i].coordAt(ends[i]) for i in range(len(tips))]
    
    # Establish color scheme.
    ic = 'black'
    if invert:
        ax.set_axis_bgcolor('black')
        ax.patch.set_facecolor('black')
        fig.patch.set_facecolor('black')
        ic = 'white'
        for spine in ax.spines: ax.spines[spine].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

    # Build and plot the neuron skeleton (includes axons).
    bpts = []
    for b in geo.branches:
        bpts.append([[n.x, n.y, n.z] for n in b.nodes])
    for b in bpts:
        for c in range(len(b)-1):
            ax.plot([b[c][0], b[c+1][0]], 
                    [b[c][1], b[c+1][1]],
                    [b[c][2], b[c+1][2]], 
                    color=ic, alpha=0.5, linewidth=lw)
        
    # Set up the path distance color map with normalized values.
    vmax = max(pdists)
    tfloats = [float(i)/vmax for i in pdists]
    cmap = plt.cm.viridis # viridis > inferno >> jet
    tcolors = cmap(tfloats)

    # Plot points at tips and color by path distance
    for t, pts in enumerate(coords):
        ax.scatter(pts[0], pts[1], pts[2], c=tcolors[t],
                   edgecolors='face', alpha=0.9)
    
    # Plot point at the soma.
    ax.scatter(geo.soma.nodes[0].x, geo.soma.nodes[0].y, geo.soma.nodes[0].z,
               c = ic, s = 100, edgecolors='face')

    # Create a list of indices ordered from shortest path to longest.
    pord = list(pdists) # Preserve pdists.
    pind = []
    for p in pord:
        maxind = pord.index(max(pord))
        pind.append(maxind)
        pord.insert(maxind, -1)
        pord.remove(pord[maxind+1])
    pind.reverse()

    # Enumerate the paths leading to each tip in a dictionary.
    tipDict = {}
    for d in range(len(tips)):
        tipDict[d] = pDF.pathTo(tips[d])
    
    # Overlay a tip path skeleton colored by path distance (discludes axons).
    for path in pind:
        if path==pind[0]: lw+=0.1
        else:lw+=0.001
        for seg in tipDict[path]:
            ax.plot([seg.nodes[0].x, seg.nodes[1].x], 
                    [seg.nodes[0].y, seg.nodes[1].y],
                    [seg.nodes[0].z, seg.nodes[1].z], 
                    color=tcolors[path], alpha=1, linewidth=lw)
    print('*The maximum linewidth is {}'.format(round(lw, 4)))
    print(lw)
    
    # Add colorbar.
    sc = []
    sc.append(plt.scatter([0,0], [0,0], c=[0., 1.], s=0.1,
                          vmin=0, vmax=vmax, cmap=cmap))
    cbar = plt.colorbar(sc[-1])
    cbar.ax.yaxis.set_tick_params(color=ic)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

    # Add labels.
    ax.set_xlabel('Micrometers', fontsize = fs, color = ic)
    ax.set_ylabel('Micrometers', fontsize = fs, color = ic)
    ax.set_zlabel('Micrometers', fontsize = fs, color = ic)
    ax.set_title('Heat Map of Neuron Tips Colored by Path Length',
                 fontsize = fs, color = ic)
    cbar.set_label("Path Length (um)", fontsize = fs, color = ic)
       
    print('*HEATMAP COMPLETE - Thank you for your patience.')
    
    # Save the figure as a .pickle
    if pkl != '':
        import pickle
        output = open(pkl + '.pickle', 'wb')
        pickle.dump(fig, output)
        output.close()
        
    # Save the figure as a movie.
    if movie != '':
		
		# Remove whitespace around skeleton for visual appeal.
        xpts = []
        ypts = []
        zpts = []
        for b in bpts:
            for c in range(len(b)-1):
                xpts.append(b[c][0])
                ypts.append(b[c][1])
                zpts.append(b[c][2])
        ax.set_xlim(min(xpts),max(xpts))
        ax.set_ylim(min(ypts),max(ypts))
        ax.set_zlim(min(zpts),max(zpts))
        
        # Remove axes for visual appeal.
        plt.axis('off')
        
        print('*Creating movie for {}, please wait...'.format(hoc))
 
        # Create an animated gif (delay ms between frames).
        if os.path.splitext(movie)[1] == '.gif':
            rotanimate(fig, ax, res, movie, delay=20,
                       width = ms, height = ms)
        
        # Create a movie with fps frames per second and bitrate 'quality'
        if os.path.splitext(movie)[1] == '.mp4':
            rotanimate(fig, ax, res, movie, fps=8, bitrate=2000,
                       width = ms, height = ms)
 
        # Create an ogv movie with fps frames per second.
        if os.path.splitext(movie)[1] == '.ogv':
            rotanimate(fig, ax, res, movie, fps=8,
                       width = ms, height = ms)
        print('*MOVIE COMPLETE - Thank you for your patience.')

    # Display the figure in a new window.
    fig.show()
    

# Load a saved pickle figure.
def pathload(pkl):
    import pickle
    figx = pickle.load(open(pkl + '.pickle', 'rb'))
    figx.show()


def main(args):
    return 0
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
