################################################
# Simple thresholding to find the approximate
# location of the edge.
# 
# Arguments: none
#
# Author:   Max Croci
# Date:     14/Nov/2019
################################################

import os
import sys
import cv2
import scipy
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np

def neighbours(X, node): #Returns list of coords of neighbours
    n_rows = len(X)
    n_cols = len(X[0])
    row = node[0]
    col = node[1]

    neigh_nodes = [(i,j) for i in range(row-1,row+2,1) for j in range(col-1,col+2,1) if i < n_rows and j < n_cols and i >= 0 and j >= 0 and (i,j) != node]
    return neigh_nodes

def update(X, node, node_visit_status, tent_dist):
    node_neighbours = neighbours(X, node)
    for n in node_neighbours:
        if node_visit_status[n] == False:
            dist = tent_dist[node] + X[n]
            if dist < tent_dist[n]:
                tent_dist[n] = dist
    
    node_visit_status[node] = True


def algo(X, initial, target, node_visit_status, tent_dist):
    print('Starting algorithm' + '#'*20)
    next_node = initial 
    while next_node != target:
        update(X, next_node, node_visit_status, tent_dist)

        next_node = ()
        min_dist = 2000
        for node, status in node_visit_status.items():
            if status == False:
                if tent_dist[node] < min_dist:
                    next_node = node
                    min_dist = tent_dist[node]
        
        if not next_node:
            return


def path(tent_dist, initial, target):
    path_nodes = [target]
    next_node = target
    while next_node != initial:
        min_val = 1000
        next_neigh = neighbours(tent_dist, next_node)
        for neigh in next_neigh:
            if tent_dist[neigh] < min_val:
                next_node = neigh
                min_val = tent_dist[neigh]
        
        path_nodes.append(next_node)

    return path_nodes


def parse_args():
    flags = {
            'plots': False,
            'display': False,
            }
    
    n_args = len(sys.argv)
    if n_args < 2:
        return flags

    for arg in sys.argv:
        if arg == 'threshold.py':
            continue
        else:
            if arg not in flags.keys():
                print('Error: argument \'' + arg + '\' is invalid!')
                print('Possible arguments are: ', list(flags.keys()))
                return {}

            flags[arg] = True
    
    if flags['display'] and not flags['plots']:
        print('Warning: argument \'display\' can not be used without argument \'plots\'!')
        flags['plots'] = True

    return flags


def main():
    flags = parse_args()
    if not flags:
        return

    data_root_dir = 'datasets/'
    if not os.path.isdir(data_root_dir):
        print('Data directory ' + data_root_dir + ' doesn\'t exist!')
        return
    
    data_dir = data_root_dir + 'Volvo_burner_OH/'
    if not os.path.isdir(data_dir):
        print('Data directory ' + data_dir + ' doesn\'t exist!')
        return
    
    edge_dir = data_root_dir + 'Volvo_burner_OH_edges/'
    if not os.path.isdir(edge_dir):
        print('Edge directory ' + edge_dir + ' doesn\'t exist!')
        return

    if flags['plots']:
        if not os.path.isdir('pictures/'):
            print('Creating pictures/ directory to save plots...')
            os.mkdir('pictures/')
            if not os.path.isdir('pictures/'):
                print('Failed to create pictures/ directory!')
                return

        picnames = ['pictures/OH0000' + str(i+1) for i in range(9)]
        picnames = picnames + ['pictures/OH000' + str(i+10) for i in range(90)]
        picnames = picnames + ['pictures/OH00' + str(i+100) for i in range(900)]

    for index in range(1,1000):
        fdata = data_dir + 'OH' + str(index) + '.dat'
        if not os.path.exists(fdata):
            print('No file with name: ' + fdata)
            return
        
        print('Opening file: {}'.format(fdata))
        raw_img = np.loadtxt(fdata) # Retrieve data
        
        #Sobel filter
        dx = ndimage.sobel(raw_img,0)
        dy = ndimage.sobel(raw_img,1)
        mag = np.hypot(dx, dy)
        f = plt.figure(1)
        plt.clf()

        #Threshold
        edge_i = []
        edge_j = []
        for i in range(len(mag)):
            for j in range(len(mag[0])):
                if mag[i][j] >= 1:
                    edge_i.append(i)
                    edge_j.append(j)
        
        fedge = edge_dir + 'OH_edge' + str(index) + '.dat'
        with open(fedge, 'w') as fe:
            for i in range(len(edge_i)):
                fe.write("{} \t {}\n".format(edge_i[i], edge_j[i]))

        if flags['plots']:
            plt.subplot(2,2,1), plt.imshow(raw_img, cmap = 'jet')
            plt.gca().set_title('Raw data')
            plt.subplot(2,2,2), plt.imshow(mag, cmap = 'jet')
            plt.gca().set_title('Sobel filtered')
            plt.subplot(2,2,3), plt.imshow(mag, cmap = 'jet')
            plt.subplot(2,2,3), plt.scatter(edge_j, edge_i, facecolors ='none', edgecolor='k')
            plt.gca().set_title('Threshold on Sobel')
            plt.subplot(2,2,4), plt.imshow(raw_img, cmap = 'jet')
            plt.subplot(2,2,4), plt.scatter(edge_j, edge_i, facecolors='none', edgecolor='k')
            plt.gca().set_title('Detected edge')
            f.savefig(picnames[index-1]+'.png', bbox_inches='tight')
            
            if flags['display']:
                plt.show()

if __name__ == '__main__':
    main()
