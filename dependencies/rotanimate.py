#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  rotanimate.py
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
#  
# 


# Imports
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d
import os
import sys
import numpy as np
 
 
# Generates a series of pictures
def make_views(fig, ax, angles, elevation=None, width=4, height = 3,
                prefix='tmprot_', **kwargs):
    """
    Makes jpeg pictures of the given 3d ax, with different angles.
    Args:
        ax (3D axis): te ax
        angles (int): the number of angles under which to take the
                      picture.
        width,height (float): size, in inches, of the output images.
        prefix (str): prefix for the files created. 
     
    Returns: the list of files created (for later removal)
    """
    
    print('*Building series, please wait...') 
    files = []
    ax.figure.set_size_inches(width,height)
    
    angles = np.linspace(0, 360, angles+1)[:-1]
     
    for i,angle in enumerate(angles):
        print('*Processing angle {} of {}...'.format(i, len(angles))) 
        ax.view_init(elev = elevation, azim=angle)
        fname = '%s%03d.jpeg'%(prefix,i)
        ax.figure.savefig(fname, facecolor=fig.get_facecolor())
        files.append(fname)
    
    print('*DONE - Finished building series.') 
    return files
 
 
# Transforms the series of pictures into a movie
def make_movie(files, output, fps=10, bitrate=1800, **kwargs):
    """
    Uses mencoder, produces a .mp4/.ogv/... movie from a list of
    picture files.
    """
    
    print('*Rendering movie, please wait...') 
    output_name, output_ext = os.path.splitext(output)
    command = { '.mp4' : 'mencoder "mf://%s" -mf fps=%d -o %s.mp4 -ovc lavc\
                         -lavcopts vcodec=msmpeg4v2:vbitrate=%d'
                         %(",".join(files),fps,output_name,bitrate)}
                          
    command['.ogv'] = command['.mp4'] + '; ffmpeg -i %s.mp4 -r %d %s'%(output_name,fps,output)
     
    print(command[output_ext])
    output_ext = os.path.splitext(output)[1]
    os.system(command[output_ext])
    print('*DONE - Finished making movie.') 
    

# Transforms the series of pictures into a GIF
def make_gif(files, output, delay=100, repeat=True, **kwargs):
    """
    Uses imageMagick to produce an animated .gif from a list of
    picture files.
    """
     
    print('*Rendering GIF, please wait...') 
    loop = -1 if repeat else 0
    os.system('convert -delay %d -loop %d %s %s'
              %(delay,loop," ".join(files),output))
    print('*DONE - Finished making GIF.') 
 

# Transforms the series of pictures into a strip
def make_strip(files, output, **kwargs):
    """
    Uses imageMagick to produce a .jpeg strip from a list of
    picture files.
    """
     
    print('*Rendering strip, please wait...') 
    os.system('montage -tile 1x -geometry +0+0 %s %s'%(" ".join(files),output))
    print('*DONE - Finished making strip.') 
     
     
# Produces an animation from a 3D plot made with matplotlib
def rotanimate(fig, ax, angles, output, **kwargs):
    """
    Produces an animation (.mp4,.ogv,.gif,.jpeg,.png) from a 3D plot on
    a 3D ax
     
    Args:
        ax (3D axis): the ax containing the plot of interest
        angles (int): the number of angles under which to show the
                      plot.
        output : name of the output file. The extension determines the
                 kind of animation used.
        **kwargs:
            - width : in inches
            - heigth: in inches
            - framerate : frames per second
            - delay : delay between frames in milliseconds
            - repeat : True or False (.gif only)
    """
         
    output_ext = os.path.splitext(output)[1]
 
    files = make_views(fig, ax, angles, **kwargs)
     
    D = { '.mp4' : make_movie,
          '.ogv' : make_movie,
          '.gif': make_gif ,
          '.jpeg': make_strip,
          '.png':make_strip}
           
    D[output_ext](files, output, **kwargs)
     
    for f in files:
        os.remove(f)


def main(args):
    return 0


# Example code
if __name__ == '__main__':
 
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X, Y, Z = axes3d.get_test_data(0.05)
    s = ax.plot_surface(X, Y, Z, cmap=cm.jet)
    plt.axis('off') # Remove axes for visual appeal
     
    angles = np.linspace(0,360,21)[:-1] # Take 20 angles between 0 and 360
 
    # Create an animated gif (20ms between frames)
    rotanimate(ax, angles,'movie.gif',delay=20) 
 
    # Create a movie with 10 frames per second and 'quality' 2000
    rotanimate(ax, angles,'movie.mp4',fps=10,bitrate=2000)
 
    # Create an ogv movie
    rotanimate(ax, angles, 'movie.ogv',fps=10) 
