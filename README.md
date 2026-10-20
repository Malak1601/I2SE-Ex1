## Problem Statement

The goal of this project is to extract a 2D image from a 3D volume, such as an MRI scan.

The input is a 3D matrix containing voxel values and a plane defined by three or four points. The program should calculate the values on the specified plane and generate the corresponding 2D image.

## Project Scope

The project will include:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from a CSV file.
- Generating a 2D image for each plane using the projection algorithm.
- Supporting planes defined by three or four points.
- Saving the generated images as frames in an MP4 video.
- Testing the correctness and performance of the implementation.

The project will focus on the projection algorithm and its performance, rather than building a graphical user interface.
