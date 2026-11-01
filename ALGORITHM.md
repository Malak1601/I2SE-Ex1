# Algorithm Design

## 1. Overview

The goal of this project is to extract 2D images from a 3D volume.

The input consists of a 3D matrix M and a list of regions defined by three or four 3D points. Each region represents an isosceles triangle or an isosceles trapezoid.

The algorithm calculates sampling positions within each region, reads the corresponding voxel values from M, and stores them in a 2D matrix E.

Each region produces one image. The images are then saved as frames in an MP4 video.

## 2. Input and Output

**Input:**
- A 3D volume stored in an NRRD file.
- A CSV file containing the coordinates of the triangle or trapezoid regions.

**Output:**
- A 2D matrix E for each region.
- An MP4 video containing one frame per region, in the same order as the CSV file.

## 3. Main Steps

1. Load the 3D volume from the NRRD file.
2. Validate the volume dimensions and data type.
3. Read the region coordinates from the CSV file.
4. Validate each triangle or trapezoid.
5. Calculate the distances and normalized direction vectors.
6. Create an initially zero-filled 2D output matrix E.
7. Move along the region row by row and sample values from M.
8. Store the sampled values in E.
9. Repeat for all regions.
10. Convert the resulting images into MP4 frames and save the video.

## 4. Detailed Algorithm

### 4.1 Triangle Definition

A triangle is defined by three 3D points: a, b, and c.

The triangle must satisfy:

- Dab = distance(a, b)
- Dac = distance(a, c)
- Dbc = distance(b, c)
- Dab ≈ Dac

The implementation checks that the two equal sides have nonzero lengths and are equal within a small numerical tolerance. Collinear points are rejected.

### 4.2 Direction Vectors

The normalized direction vectors are:

- vab = (b - a) / Dab
- vac = (c - a) / Dac

These vectors define unit-length directions along the two equal sides of the triangle.

### 4.3 Output Matrix

The implementation creates an initially zero-filled 2D matrix E with the same data type as the input volume.

The output dimensions are:

- height = max(1, ceil(leg_length))
- width = max(1, ceil(max_width) + 1)

For each row y, the sampling step is:

`step = min(y + 1, leg_length)`

The two endpoints of the row are calculated as:

- p1 = start1 + step × vector1
- p2 = start2 + step × vector2

### 4.4 Triangle Sampling

For a triangle:

- start1 = a
- start2 = a
- vector1 = vab
- vector2 = vac
- leg_length = Dab
- max_width = Dbc

For each output row:

1. Calculate the two endpoints p1 and p2 along the equal sides.
2. Calculate `span`, the distance between p1 and p2.
3. Determine the sampling direction from p1 to p2.
4. Generate sampling positions along the segment.
5. Convert the positions to voxel indices.
6. Calculate the centered horizontal output positions.
7. Copy valid voxel values into E.

### 4.5 Trapezoid Sampling

The algorithm also supports isosceles trapezoids defined by four 3D points.

For the implemented vertex ordering a, b, c, d, the equal legs are a→b and d→c.

The validation checks include:

- Nonzero edge lengths.
- Equal leg lengths.
- Parallel bases.
- Coplanarity of the four vertices.
- Valid vertex ordering.

The algorithm advances along the two equal legs and samples each segment connecting their current positions.

Unlike the triangle case, the starting segment of a trapezoid may have a nonzero width.

### 4.6 Sampling Rules and Special Cases

The implementation generates sampling positions along each row using NumPy arrays.

For a row of length `span`, it calculates:

`count = ceil(span)`

Sampling offsets are generated from zero to `count` and limited to the segment length.

Fractional 3D coordinates are converted to voxel indices using nearest-neighbor sampling:

`index = floor(coordinate + 0.5)`

Horizontal output positions are calculated using the centering formula from the assignment:

`x = (max_width - span) / 2 + offset`

The resulting positions are rounded using `np.rint`.

Samples outside the input volume are excluded from indexed reads. Their output positions remain zero unless another valid sample writes to the same output position.

Zero-length sampling segments are handled separately to avoid division by zero.

NumPy vectorization is used to process the sampling positions of each row without a Python loop over individual samples.

### 4.7 Result

After processing all rows, the algorithm returns E.

The process is repeated for every region in the CSV file.

## 5. NRRD Data

The implementation uses Python and the pynrrd library to load the input volume.

After loading the data, the program checks:

- The volume has exactly three dimensions.
- Each dimension is between 1 and 1023.
- The voxel data type is an unsigned 8-bit, 16-bit, or 32-bit integer.

The loaded volume is stored in M and accessed using its three array indices.

The program has been tested using a small synthetic NRRD volume. A separate performance benchmark was conducted using a 500 × 500 × 500 volume.

## 6. Video Generation

Each generated 2D matrix is converted into an 8-bit grayscale image for MP4 output.

The implementation scales the values for display and pads the images to consistent frame dimensions when necessary.

The frames are saved in the same order as the regions in the CSV file.

## 7. Complexity and Performance

Let H be the number of output rows and W the maximum number of sampling positions in a row.

The projection requires O(H × W) sampling work for one region.

The output image requires O(H × W) memory.

A performance benchmark was conducted using a 500 × 500 × 500 volume and 10 measured triangle projections after one warm-up run.

The measured average processing time was approximately 0.0223 seconds per projection, corresponding to 44.84 FPS.

This result exceeds the minimum requirement of 30 FPS but remains below the expected target of 100 FPS.

The measurement applies to the tested configuration and execution environment. It does not include the full cost of loading the input file and encoding the MP4 video.