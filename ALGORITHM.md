# Main Algorithm Design

## 1. Overview

The algorithm receives a 3D volume and a plane defined by three or four points.

The goal is to generate a 2D image by sampling voxel values from the given plane.

The algorithm processes the plane row by row and stores the sampled values in a 2D matrix.

If a sampled point is outside the 3D volume, its value is set to zero.

## 2. Input and Output

**Input:**
- A 3D matrix M containing voxel values.
- Three or four 3D points defining the plane.

**Output:**
- A 2D matrix E containing the sampled values from the plane.
