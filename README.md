# I2SE-Ex1

## 3D Medical Volume Plane Projection

### Problem Statement

The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The input consists of a 3D matrix containing voxel values and a set of planes defined by three or four points. For each plane, the program calculates positions in the 3D volume, samples the corresponding values, and arranges them into a 2D image.

The main challenge is to implement this process correctly and efficiently while supporting different plane orientations and handling invalid inputs.

### Project Scope

The project includes:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from a CSV file.
- Supporting triangle and trapezoid plane definitions.
- Checking the geometric validity of the planes.
- Generating 2D projections using nearest-neighbor sampling.
- Using zero for sampling positions outside the volume.
- Combining the generated images into an MP4 video.
- Testing the correctness and performance of the projection algorithm.

The project focuses on the projection algorithm, its performance, and the quality of the implementation rather than developing a
