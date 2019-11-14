# Flame edge detection
This directory contains various algorithms for detecting a flame edge in various flame surface data sets.

- dijkstra.py : Implements Dijkstra's algorithm to find the flame surface by traversing the data matrix with a least-work cost function. Requires opencv-python and numpy.


To do:
- Improve dijkstra.py to make it more robust to noise. 
- Implement a CNN, trained on either thresholding or dijkstra results to attempt to improve edge detection. 
