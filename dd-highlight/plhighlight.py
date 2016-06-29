#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plhighlight.py
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
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import rcParams
rcParams['figure.figsize'] = 12.4,12.0


# Testing
thoc = '/home/cosmo/marderlab/test/878_043_GM_scaled.hoc'


def pathplot(hoc, path = 0, fs = 20):
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
                     [b[c][1], b[c+1][1]], color='k', alpha=1, lw=1.5)

    # Create a list of indices ordered from shortest path to longest
    pord = list(pdists) # Preserve pdists
    pind = []
    for p in pord:
        maxind = pord.index(max(pord))
        pind.append(maxind)
        pord.insert(maxind, -1)
        pord.remove(pord[maxind+1])

    # Enumerate the paths leading to each tip in a dictionary
    tipDict = {}
    for d in range(len(tips)):
        tipDict[d] = pDF.pathTo(tips[d])
    
    # Overlay a tip path skeleton colored by path distance (discludes axons)
    for seg in tipDict[pind[path]]:
        plt.plot([seg.nodes[0].x, seg.nodes[1].x], 
                 [seg.nodes[0].y, seg.nodes[1].y], 
                 color='plum', alpha=1, lw=2.0)
                 
    # Plot point at the soma.
    plt.plot(geo.soma.nodes[0].x, geo.soma.nodes[0].y, 'o',
             color = 'black', alpha = 0.5, ms=10)

    # Add labels
    plt.xlabel('Micrometers', fontsize=fs)
    plt.ylabel('Micrometers', fontsize=fs)
    plt.title(hoc.split('/')[-1].split('.')[0], fontsize=fs)
       
    print('*DONE - Thank you for your patience.')

    # Display the figure in a new window
    plt.show()


def main(args):
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
