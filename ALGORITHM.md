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

    ## 4. Detailed Algorithm

### 4.1 Plane Definition

The plane is defined using three 3D points: a, b, and c.

For the triangle case, the distance from a to b must be equal to the distance from a to c.

We calculate:

- Dab = distance(a, b)
- Dac = distance(a, c)
- Dbc = distance(b, c)

We check that Dab and Dac are equal within a small tolerance.

### 4.2 Direction Vectors

We calculate two normalized direction vectors:

- vab = (b - a) / Dab
- vac = (c - a) / Dac

These vectors are used to move along the two sides of the triangle.

### 4.3 Output Matrix

We create a 2D matrix E.

Its height is based on Dab, and its width is based on Dbc.

Since array dimensions must be integers, we need to define a consistent rounding rule.

The output matrix is initially filled with zeros.

### 4.4 Sampling the Plane

We start with:

- a1 = a
- a2 = a

For each output row:

1. Move a1 along the direction from a to b.
2. Move a2 along the direction from a to c.
3. Calculate the distance d12 between a1 and a2.
4. Start sampling from p = a1.
5. Calculate the normalized direction from a1 to a2.
6. Move along the line and read values from M.
7. Store the sampled values in the corresponding row of E.

The horizontal position of each sample is calculated using the centering formula from the assignment.

### 4.5 Sampling Rules and Special Cases

We plan to use nearest-neighbor sampling for fractional coordinates.

If a sample is outside the 3D volume, its value will be zero.

If the distance between two sampling points is zero, the algorithm must avoid division by zero.

We also check output indices before writing to E.

The exact rounding and indexing rules will be finalized and tested during implementation.

### 4.6 Result

After processing all rows, the algorithm returns E.

The process is repeated for every plane in the CSV file. The resulting images are then converted into frames of the output MP4 video.
