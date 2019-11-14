################################################
# Dijkstra algorithm implementation to find the
# quickest path through a matrix (with strictly
# non-negative entries). 
#
# Arguments: none
#
# Author:   Max Croci
# Date:     14/Nov/2019
################################################

import os
import sys
import cv2
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
    print("Starting algorithm" + "#"*20)
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


def main():
    data_root_dir = 'datasets/'
    data_dir = 'Volvo_burner_OH/'
    if not os.path.isdir(data_root_dir + data_dir):
        print("Data directory " + data_root_dir + data_dir + " doesn't exist!")
        return

    fnames = [data_root_dir + data_dir + 'OH' + str(i+1) for i in range(100)]

    if not os.path.isdir('pictures/'):
        print("Creating pictures/ directory to save plots...")
        os.mkdir('pictures/')
        if not os.path.isdir('pictures/'):
            print("Failed to create pictures/ directory!")
            return

    vidnames = ['pictures/OH0000' + str(i+1) for i in range(9)]
    vidnames = vidnames + ['pictures/OH000' + str(i+10) for i in range(90)]
    vid = 0
    for fname in fnames:
        print("Opening file: {}".format(fname))

        raw_img = np.loadtxt(fname+'.dat') # Retrieve data
        pre_filtered = cv2.GaussianBlur(raw_img,(5,5),0) # Apply Gaussian filter
        laplacian = cv2.Laplacian(pre_filtered,cv2.CV_64F) # Calculate Laplacian
        post_filtered = cv2.GaussianBlur(laplacian,(5,5),0) # Apply Gaussian filter
        #post_filtered = laplacian

        abs_data = np.abs(post_filtered) 
        #abs_data = post_filtered+1 
        
        #Plots
        f = plt.figure(1)
        plt.clf()
        plt.subplot(2,4,1), plt.imshow(raw_img,cmap = 'jet')
        plt.gca().set_title('Raw data')

        plt.subplot(2,4,2), plt.imshow(pre_filtered,cmap = 'jet')
        plt.gca().set_title('Pre-filtered')

        plt.subplot(2,4,3), plt.imshow(laplacian,cmap = 'jet')
        plt.gca().set_title('Laplacian')

        plt.subplot(2,4,4), plt.imshow(post_filtered,cmap = 'jet')
        plt.gca().set_title('Post-filtered')
        
        plt.subplot(2,4,5), plt.imshow(abs_data,cmap = 'jet')
        plt.gca().set_title('Absolute values')

        abs_data2 = [[0 for i in range(len(laplacian[0]))] for j in range(len(laplacian))]
        for i in range(1,len(laplacian)-1):
            for j in range(1,len(laplacian[0])-1):
                if sum(abs_data[i-1][j-1:j+2])+sum(abs_data[i][j-1:j+2])+sum(abs_data[i+1][j-1:j+2]) < 0.04*3:
                    abs_data2[i][j] = 0.04
             
        for i in range(len(laplacian)):
            for j in range(len(laplacian[0])):
                if i == 0:
                    abs_data[i][j] = 0.04
                if abs_data[i][j] != abs_data2[i][j] and abs_data2[i][j] != 0:
                    abs_data[i][j] = abs_data2[i][j]

        plt.subplot(2,4,6), plt.imshow(abs_data,cmap = 'jet')
        plt.gca().set_title('Block fill out-of-tube')
        
        #lap = np.power(1+laplacian[0:30,:],19) # Select top half and ensure all entries > 0
        #lap = np.abs(laplacian[0:30,:]) # Select top half and ensure all entries > 0
        lap = abs_data[0:30,:] # Select top half

        ### Find starting point
        min_val = 1000
        min_i = 0
        for i in range(len(lap)-10):
            if lap[(i, len(lap[0])-1)] < min_val:
                min_i = i
                min_val = lap[(i, len(lap[0])-1)]

        start = (min_i, len(lap[0])-1)
        #print("Starting point: {}".format(start))

        #### Set up dictionaries and matrices
        tent_dist = np.ndarray(shape = (len(lap),len(lap[0])), dtype = float)
        node_visit_status = {}
        node_list = [(i, j) for i in range(len(lap)) for j in range(len(lap[0]))]

        for node in node_list:
            tent_dist[node] = 1000
            node_visit_status[node] = False


        #### Run algo
        initial = start
        target = (19, 0)
        tent_dist[initial] = lap[initial]
        node_visit_status[initial] = True
        X = lap
        algo(X, initial, target, node_visit_status, tent_dist)
        path_list = path(tent_dist, initial, target)

        path_i = []
        path_j = []
        for node in path_list:
            path_i.append(node[0])
            path_j.append(node[1])

        #Plots

        
        plt.subplot(2,4,7), plt.imshow(abs_data,cmap = 'jet')
        plt.subplot(2,4,7), plt.scatter(path_j, path_i, facecolors='k', edgecolor='none')
        plt.gca().set_title('Block fill: valley detected')
        plt.xlim([0,68])
        plt.ylim([57,0])
        plt.subplot(2,4,8), plt.imshow(raw_img,cmap = 'jet')
        plt.subplot(2,4,8), plt.scatter(path_j, path_i, facecolors='none', edgecolor='k')
        plt.gca().set_title('Raw data: edge detected')
        plt.xlim([0,68])
        plt.ylim([57,0])
        f.savefig(vidnames[vid]+'.png', bbox_inches='tight')
        plt.show()

        vid += 1

if __name__ == "__main__":
    main()
