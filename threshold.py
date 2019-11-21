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
import scipy
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np

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
    
    data_dir = data_root_dir + 'OH_double_cycle/'
    #data_dir = data_root_dir + 'Volvo_burner_OH/'
    if not os.path.isdir(data_dir):
        print('Data directory ' + data_dir + ' doesn\'t exist!')
        return
    
    edge_dir = data_root_dir + 'OH_double_cycle_edges/'
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
    

    #Thresholding algorithm
    n_pic = 0
    for index in range(2200,2401):
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
        thresh = 1
        edge_i = []
        edge_j = []
        for i in range(len(mag)):
            for j in range(len(mag[0])):
                if mag[i][j] >= thresh:
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
            f.savefig(picnames[n_pic]+'.png', bbox_inches='tight')
            n_pic += 1

            if flags['display']:
                plt.show()

if __name__ == '__main__':
    main()
