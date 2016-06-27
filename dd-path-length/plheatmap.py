#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plheatmap.py
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
import matplotlib.pyplot as plt
#%matplotlib inline


# Initializing the figure
fig = plt.figure(figsize=(20,20))


# Testing
tdir = '/home/cosmo/marderlab/test/'
thoc = '/home/cosmo/marderlab/test/878_043_GM_scaled.hoc'


# Instructions
def pathhelp():
	print('\n*Use pathplot(\'hoc file\') to view the heatmap for a given hoc file.')
	print('*EXAMPLE: pathplot(\'/home/cosmo/marderlab/hocs/878_043_GM_scaled.hoc\')')
	print('\n*Use pathcompare(\'hoc folder\') to compare heatmaps for hoc files in a given folder.')
	print('*EXAMPLE: pathcompare(\'/home/cosmo/marderlab/hocs/\')')
	print('*NOTE: The folder must NOT contain anything besides hoc files.')
	print('\n*Use pathhelp() to view these instructions again.')
pathhelp()


def pathcompare(hocs):
    # Convert given directory into list of hoc files
    geo = [(hocs + g) for g in os.listdir(hocs)]
    
    # Calculate the size of the comparison chart
    lwh = int(round(sqrt(len(geo))))
    print('*Using {} by {} grid.'.format(lwh, lwh))
    
    # Calculate font size
    fs = 10
    
    # Calculate colorbar upper limit
    maxDists = []
    for g in geo:
        f = demoReadsilent(g)
        pdists = [PathDistanceFinder(f, f.soma).distanceTo(s) for s in f.getTips()[0]]
        maxDists.append(max(pdists))
        vmax = max(maxDists)

    # Create comparison chart
    for n, g in enumerate(geo, start = 1):
        plt.subplot(lwh, lwh, n)
        pathplot(g, False, fs, vmax)
    plt.suptitle('Heatmaps of Neurons Colored by Path Length', size = fs)
    plt.tight_layout()
    plt.show()


def pathplot(hoc, show = True, fs = 20, vmax = 500):
    # Convert given hoc file into a geo object
    print('*Building geo object for {}, please wait...'.format(hoc))
    geo = demoReadsilent(hoc)
    print('*Building heatmap for {}, please wait...'.format(hoc))
	
    # Find the tip segments and their end locations
    tips, ends = geo.getTips()
   
    # Calculate the path distance to each tip
    pDF = PathDistanceFinder(geo, geo.soma)
    pdists = [pDF.distanceTo(seg) for seg in tips]
   
    # Calculate the coordinate position of each tip
    coords = [tips[i].coordAt(ends[i]) for i in range(len(tips))]
   
    # Build and plot the neuron skeleton (includes axons)
    bpts = []
    for b in geo.branches:
        bpts.append([[n.x, n.y] for n in b.nodes])
    for b in bpts:
        for c in range(len(b)-1):
            plt.plot([b[c][0], b[c+1][0]], 
                     [b[c][1], b[c+1][1]], color='k', alpha=0.5)
        
    # Set up the path distance colormap with normalized values
    if show:
        vmax = max(pdists)
    tfloats = [float(i)/vmax for i in pdists]
    cmap = plt.cm.jet
    tcolors = cmap(tfloats)

    # Plot and color points at tips by path distance
    for t, pts in enumerate(coords):
        plt.plot(pts[0], pts[1], 'o', color=tcolors[t], alpha=0.1,
                 mec='none', ms=1)
                 
    # Plot point at the soma.
    plt.plot(geo.soma.nodes[0].x, geo.soma.nodes[0].y, 'o',
             color = 'black', alpha=0.9, mec='none')

    # Create a list of indices ordered from shortest path to longest
    pord = list(pdists) # Preserve pdists
    pind = []
    for p in pord:
        maxind = pord.index(max(pord))
        pind.append(maxind)
        pord.insert(maxind, -1)
        pord.remove(pord[maxind+1])
    pind.reverse()

    # Enumerate the paths leading to each tip in a dictionary
    tipDict = {}
    for d in range(len(tips)):
        tipDict[d] = pDF.pathTo(tips[d])
    
    # Overlay a tip path skeleton colored by path distance (discludes axons)
    for path in pind:
        for seg in tipDict[path]:
            plt.plot([seg.nodes[0].x, seg.nodes[1].x], 
                     [seg.nodes[0].y, seg.nodes[1].y], 
                     color=tcolors[path], alpha=1)
    
    # Add colorbar
    sc = []
    sc.append(plt.scatter([0,0], [0,0], c=[0., 1.], s=0.1,
                      vmin=0, vmax=vmax, cmap=cmap))
    cbar = plt.colorbar(sc[-1])

    # Add labels
    ax = plt.gca()
    if show:
        plt.xlabel('Micrometers', fontsize=fs)
        plt.ylabel('Micrometers', fontsize=fs)
        plt.title('Heatmap of Neuron Tips Colored by Path Length', fontsize=fs)
    else:
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
    cbar.set_label("Path Length (um)", fontsize=fs)
       
    print('*DONE - Thank you for your patience.')

    # Display the figure in a new window
    if show:
        plt.show()


def main(args):
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
