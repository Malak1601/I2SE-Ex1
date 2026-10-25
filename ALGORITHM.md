# Algorithm Design

## 1. Overview

The goal of the algorithm is to extract a 2D image from a 3D volume.

The input is a 3D matrix M and a set of points that define a plane inside the volume.

The algorithm calculates the positions of the points on the plane, reads the corresponding values from M, and stores them in a new 2D matrix E.

Each plane produces one 2D image. The images are later combined into an MP4 video.

## 2. Input and Output

**Input:**
- A 3D volume stored in an NRRD file.
- A CSV file containing the points that define each plane.

**Output:**
- A 2D matrix E for each plane.
- An MP4 video containing the resulting images in the order given in the CSV file.

## 3. Main Steps

1. Load the 3D volume from the NRRD file.
2. Read the plane points from the CSV file.
3. Calculate the distances between the points.
4. Calculate the direction vectors.
5. Create an empty 2D output matrix E.
6. Move along the plane and sample values from the 3D matrix M.
7. Store the sampled values in E.
8. Repeat for all planes.
9. Save the resulting images as an MP4 video.
