# Algorithm Design

## 1. Overview

The goal of this project is to generate 2D images from a 3D volume, such as an MRI scan.

The input consists of a 3D matrix M and a list of regions defined by three or four points in 3D space. Each region represents an isosceles triangle or an isosceles trapezoid.

The algorithm calculates sampling positions within each region, reads the corresponding voxel values from M, and stores them in a 2D matrix E.

Each valid region produces a projection image. The resulting images are converted into frames and saved as an MP4 video.

The implementation uses NumPy to process multiple sampling positions together and reduce the number of Python-level operations.

## 2. Input and Output

### Input

- An NRRD file containing a 3D volume M.
- A CSV file containing triangle or trapezoid coordinates.

Each CSV row contains either 9 values for three points or 12 values for four points.

### Output

- A 2D matrix E for each valid region.
- An MP4 video containing the generated frames in CSV order.

According to the assignment, invalid plane definitions must produce error frames while allowing subsequent valid planes to be processed.

## 3. Main Algorithm

The processing steps are:

1. Load the 3D volume from the NRRD file.
2. Validate the volume dimensions and data type.
3. Read the plane coordinates from the CSV file.
4. Identify each region as a triangle or trapezoid.
5. Validate its geometric conditions.
6. Calculate distances and normalized direction vectors.
7. Create a zero-filled output matrix E.
8. Calculate the sampling positions row by row.
9. Find the nearest voxel for each sampling position.
10. Store valid sampled values in E.
11. Convert the generated images into video frames.
12. Save the frames in an MP4 video.

The demo must also handle invalid planes by generating error frames and continuing with the remaining entries.

## 4. Triangle Projection

### 4.1 Triangle Definition

A triangle is defined by three points:

- a = (ax, ay, az)
- b = (bx, by, bz)
- c = (cx, cy, cz)

The two sides starting at a must have approximately equal lengths.

Let:

- Dab = distance(a, b)
- Dac = distance(a, c)
- Dbc = distance(b, c)

The required condition is:

`abs(Dab - Dac) < 0.001`

The triangle must also have nonzero side lengths and must not be degenerate.

A triangle with collinear points is rejected because it does not define a valid triangular region.

### 4.2 Direction Vectors

The normalized vectors along the two equal sides are:

`vab = (b - a) / Dab`

`vac = (c - a) / Dac`

These vectors have length one and define the directions used to move from a toward b and c.

### 4.3 Output Matrix

The output matrix E is initialized with zeros and uses the same data type as M.

The implementation calculates its dimensions using:

`height = max(1, ceil(Dab))`

`width = max(1, ceil(Dbc) + 1)`

The width is based on the longest sampling segment, while the height is based on the length of the equal sides.

The extra width position accounts for the sampling offsets that include both ends of a segment.

### 4.4 Row Calculation

The algorithm processes the output matrix one row at a time.

For each row index y:

`step = min(y + 1, Dab)`

The two endpoints are:

`p1 = a + step * vab`

`p2 = a + step * vac`

The distance between them is:

`span = distance(p1, p2)`

This segment represents the part of the triangle sampled for the current output row.

The implementation starts with step = 1, so the first stored row is sampled one unit away from vertex a. The vertex itself is not stored as a separate initial row.

### 4.5 Sampling Along a Row

For each row, the algorithm:

1. Calculates the distance between p1 and p2.
2. Finds the normalized direction from p1 to p2.
3. Generates sampling offsets along the segment.
4. Converts the sampled coordinates into voxel indices.
5. Calculates the horizontal positions in E.
6. Copies values from valid volume positions into E.

The number of sampling intervals is calculated using:

`count = ceil(span)`

The offsets are generated from 0 to count and limited to the segment length.

The sampled points are:

`point = p1 + offset * direction`

The horizontal output positions are calculated using:

`x = (max_width - span) / 2 + offset`

The implementation rounds these positions to integer column indices.

The centering calculation places shorter segments near the middle of the output image.

## 5. Trapezoid Projection

### 5.1 Trapezoid Definition

The implementation uses four points:

- a
- b
- c
- d

The equal legs are:

- a → b
- d → c

The bases are:

- a → d
- b → c

For the supported trapezoid definition, the two legs must have approximately equal lengths.

The required distance condition is:

`abs(distance(a,b) - distance(d,c)) < 0.001`

The starting base must not be longer than the ending base:

`distance(a,d) <= distance(b,c)`

The trapezoid must also be planar and non-degenerate.

The validation design includes checking that the bases are parallel, the vertices have a valid order, and the shape is not self-intersecting.

### 5.2 Trapezoid Sampling

The trapezoid uses the same row-sampling function as the triangle.

The parameters are:

- start1 = a
- start2 = d
- vector1 = direction(a,b)
- vector2 = direction(d,c)
- leg_length = distance(a,b)
- max_width = max(distance(a,d), distance(b,c))

For each row:

`p1 = a + step * vector1`

`p2 = d + step * vector2`

The segment between p1 and p2 is sampled using the same procedure as the triangle.

The main difference is that a trapezoid starts with a nonzero distance between its two sides.

## 6. Nearest-Neighbor Sampling

The algorithm uses nearest-neighbor sampling to obtain values from the 3D matrix.

Each coordinate is converted to an integer index using:

`index = floor(coordinate + 0.5)`

This selects the nearest integer voxel coordinate, with half-integer values rounded upward.

For each sampled point, the algorithm checks:

`0 <= x < sx`

`0 <= y < sy`

`0 <= z < sz`

If all three indices are inside the volume, the voxel value is copied into E.

If the point is outside the volume, the output position remains zero.

The output column indices are rounded separately using `np.rint`.

Since multiple sampling positions may map to the same output column, a later sample may overwrite an earlier value.

### Zero-Length Segments

If the distance between p1 and p2 is close to zero, the algorithm avoids division by zero.

It samples p1 directly and places the result near the center of the output row.

### NumPy Vectorization

Instead of using a Python loop for every pixel, the implementation generates the sampling positions of an entire row using NumPy arrays.

It then converts the positions into integer indices and reads the valid voxel values together.

This reduces Python-level loop overhead and supports more efficient processing.

## 7. NRRD Data Handling

The program uses the pynrrd library to load the volume.

After loading, it checks that:

- The matrix has exactly three dimensions.
- Each dimension is between 1 and 1023.
- The voxel values are unsigned 8-bit, 16-bit, or 32-bit integers.

The volume is stored as a NumPy array and accessed using three indices.

The current implementation uses the array indices as voxel coordinates. It does not apply additional physical-space transformations from NRRD metadata.

## 8. Video Generation

Each projection matrix is converted into an 8-bit grayscale image.

The implementation finds the maximum voxel value across the generated projections and uses it to scale the images into the range 0 to 255.

The images may have different dimensions, so they are placed on zero-filled canvases with common frame dimensions.

The video dimensions are adjusted to even numbers for H.264 encoding.

The frames are then written to an MP4 file using imageio.

The normal output writes one frame per projection.

A separate preview mode can enlarge small images and repeat frames to make them easier to inspect.

## 9. Error Handling

The geometry validation functions raise exceptions when a triangle or trapezoid is invalid.

The assignment requires the demo to catch plane-specific errors, generate a visible error frame, and continue processing the remaining planes.

This behavior still needs to be completed in the main application.

The CSV reading stage also needs improved error recovery so that an invalid row does not unnecessarily prevent valid later rows from being processed.

## 10. Complexity Analysis

Let:

- H be the number of output rows.
- W be the maximum number of sampling positions per row.

For one projection, the algorithm performs approximately O(H × W) sampling operations.

The output matrix requires O(H × W) memory.

The intermediate NumPy arrays used to process a single row require additional O(W) memory.

The complete program currently stores all generated projection matrices before video encoding.

Therefore, its total memory usage depends on the combined sizes of all projections, in addition to the input volume and video-processing buffers.

For N regions, the total projection work is approximately O(N × H × W) when H and W represent common upper bounds.

## 11. Performance Experiment

A performance benchmark was implemented using a synthetic volume of size:

`500 × 500 × 500`

The triangle vertices are:

- A = (0, 0, 0)
- B = (400, 0, 0)
- C = (0, 400, 0)

The benchmark performs one warm-up projection followed by 10 measured projections.

Execution time is measured using `time.perf_counter()`.

The latest previously reported result was 43.87 FPS, corresponding to approximately 0.0228 seconds per projection.

This reported result exceeds the minimum requirement of 30 FPS but remains below the expected target of 100 FPS.

The benchmark measures projection computation only. It does not include reading the NRRD file or encoding the video.

The result is specific to the tested triangle and execution environment and should be verified with the final implementation.

## 12. Remaining Implementation Work

Before final submission, the implementation and tests need to be updated to address the following:

1. Use the required absolute tolerance of 0.001 when validating equal side lengths.
2. Enforce the trapezoid base-length constraint.
3. Generate error frames for invalid plane definitions.
4. Continue processing valid CSV entries after plane-specific errors.
5. Add regression tests for these cases.
6. Rerun the performance benchmark and document the final results.

These changes are required to bring the implementation into agreement with the assignment requirements and the SRS.
