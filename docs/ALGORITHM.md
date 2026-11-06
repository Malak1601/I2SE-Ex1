# Algorithm Design

## Ex1 – 3D Volume Plane Projection

### 1. Overview

This document describes the algorithm used to generate 2D projections from a 3D NRRD volume.

Each CSV entry defines either an isosceles triangle using three points or an isosceles trapezoid using four points.

The program validates the geometry, calculates sampling positions across the region, and copies voxel values into a 2D projection matrix.

The resulting projections are converted into video frames and saved as an MP4 file in CSV order.

The implementation uses NumPy for array operations and Numba JIT compilation to accelerate the main sampling loop.

### 2. Inputs and Outputs

#### Inputs

- A three-dimensional NRRD volume `M` with dimensions `(sx, sy, sz)`.
- A CSV file containing plane definitions.
- An output MP4 filename.

Each plane contains either 9 coordinates for a triangle or 12 coordinates for a trapezoid.

The CSV reader also supports the lecturer's format, where each row begins with the number of points (`3` or `4`).

Coordinates represent voxel indices. Physical coordinate transformations from NRRD metadata are not applied.

#### Outputs

- A 2D projection matrix `E` for each valid plane.
- An MP4 video containing the projections in CSV order.
- Visible error frames for invalid individual plane definitions.

### 3. Main Processing Steps

The program follows these steps:

1. Read the NRRD volume and validate its dimensions and data type.
2. Read the CSV file and preserve the order of plane definitions.
3. Validate the geometry of each triangle or trapezoid.
4. Calculate the direction vectors and output dimensions.
5. Generate each projection by sampling the volume row by row.
6. Convert projection matrices into grayscale video frames.
7. Replace invalid plane entries with visible error frames.
8. Pad frames to a common size and encode the MP4 video.

### 4. Triangle Projection

#### 4.1 Geometry

A triangle is defined by three points:

`a, b, c`

Point `a` is the common vertex of the two equal-length sides.

The side lengths are:

`Dab = ||b - a||`

`Dac = ||c - a||`

`Dbc = ||c - b||`

The triangle is valid when:

- Both sides have positive length.
- The points are not collinear.
- `|Dab - Dac| < 0.001`.

The normalized direction vectors are:

`vab = (b - a) / Dab`

`vac = (c - a) / Dac`

These vectors indicate the direction of movement along the two sides.

#### 4.2 Output Dimensions

The output matrix `E` is initialized with zeros and preserves the voxel data type of the input volume.

In the implementation described by the original algorithm document:

`height = max(1, ceil(Dab))`

`width = max(1, ceil(Dbc) + 1)`

The width is based on the triangle's base, while the height is based on its equal sides.

#### 4.3 Row Sampling

For each output row `y`, the algorithm calculates two points on the triangle's equal sides.

The step distance is:

`step = min(y + 1, Dab)`

The two endpoints are:

`p1 = a + step * vab`

`p2 = a + step * vac`

The distance between them is:

`span = ||p2 - p1||`

The segment between `p1` and `p2` represents the current row of the projection.

Sampling positions are calculated along this segment using approximately unit-distance steps.

For a nonzero span:

`count = ceil(span)`

For each integer `j` from `0` to `count`:

`offset = min(j, span)`

`point = p1 + (offset / span) * (p2 - p1)`

The calculated 3D point is sampled from the volume.

The output column is determined using the geometric offset:

`x = rint((Dbc - span) / 2 + offset)`

This places shorter rows toward the center of the output image.

If the span is approximately zero, the algorithm samples one point directly and places it near the center of the row.

### 5. Trapezoid Projection

#### 5.1 Geometry

A trapezoid is defined by four points:

`a, b, c, d`

The point order is:

- First leg: `a → b`
- Second leg: `c → d`
- Starting base: `a → c`
- Ending base: `b → d`

The program validates:

- Nonzero side and base lengths.
- Approximately equal leg lengths.
- Parallel bases pointing in the same direction.
- Coplanarity of the four points.
- Nonzero area.
- A valid, non-crossing geometric arrangement.

The assignment also requires the starting base to be no longer than the ending base:

`||c - a|| <= ||d - b||`

This requirement must be enforced by the geometry validation code.

Rectangles are accepted as a special case where both bases have equal lengths.

#### 5.2 Sampling

The trapezoid uses the same row-sampling approach as the triangle.

The starting points are:

`start1 = a`

`start2 = c`

The direction vectors are:

`vector1 = (b - a) / ||b - a||`

`vector2 = (d - c) / ||d - c||`

The row endpoints are calculated by advancing along the two legs.

The maximum row width is determined from the two base lengths:

`max_width = max(||c - a||, ||d - b||)`

The output dimensions are:

`height = max(1, ceil(||b - a||))`

`width = max(1, ceil(max_width) + 1)`

Each row is sampled between its two endpoints using nearest-neighbor voxel sampling.

Unlike the triangle, the first trapezoid row can already have a nonzero width.

### 6. Nearest-Neighbor Sampling

The algorithm uses nearest-neighbor sampling to obtain voxel values.

For a sampling position:

`p = (px, py, pz)`

The voxel indices are calculated as:

`ix = floor(px + 0.5)`

`iy = floor(py + 0.5)`

`iz = floor(pz + 0.5)`

A voxel value is copied only when all indices are inside the volume:

`0 <= ix < sx`

`0 <= iy < sy`

`0 <= iz < sz`

Otherwise, the output pixel remains zero.

Nearest-neighbor sampling is used because it is computationally inexpensive and copies existing voxel values without interpolation.

### 7. Pseudocode

The following pseudocode summarizes the projection procedure described above.

```text
PROJECT_PLANE(M, plane):

    Validate the plane geometry

    Determine the two starting points
    Determine the two leg direction vectors
    Calculate the leg length and maximum width

    H = max(1, ceil(leg_length))
    W = max(1, ceil(max_width) + 1)

    E = zero matrix of size H x W

    FOR y = 0 TO H - 1:

        step = min(y + 1, leg_length)

        p1 = start1 + step * direction1
        p2 = start2 + step * direction2

        span = distance(p1, p2)

        IF span is approximately zero:
            Sample p1
            Store the value near the center of row y
            CONTINUE

        count = ceil(span)

        FOR j = 0 TO count:

            offset = min(j, span)

            p = p1 + (offset / span) * (p2 - p1)

            x = rint((max_width - span) / 2 + offset)

            IF x is inside the output matrix:
                E[y, x] = SAMPLE_NEAREST(M, p)

    RETURN E


SAMPLE_NEAREST(M, p):

    ix = floor(p.x + 0.5)
    iy = floor(p.y + 0.5)
    iz = floor(p.z + 0.5)

    IF all indices are inside M:
        RETURN M[ix, iy, iz]

    RETURN 0
```

### 8. NRRD Handling

The program uses the `pynrrd` library to load the volume.

The volume must have exactly three dimensions, each between 1 and 1023 inclusive.

The required data types are unsigned 8-bit, 16-bit, and 32-bit integers.

The implementation described in the original algorithm document also accepts signed integer arrays of these bit depths when all voxel values are nonnegative, converting them to unsigned types.

Unsupported data types and invalid dimensions are rejected.

### 9. Video Generation

After projection, the program converts the matrices into grayscale video frames.

A common intensity scale is used across the projections to maintain consistent brightness.

The grayscale conversion described in the original algorithm document is:

`frame = clip(E / scale_max * 255, 0, 255)`

Here, `scale_max` is the largest voxel value among the generated projections.

If `scale_max` is zero, the resulting grayscale frame is black.

Because projection matrices may have different dimensions, they are placed on zero-filled canvases of a common size.

The canvas dimensions are adjusted to even numbers when necessary for H.264 video encoding.

Invalid plane definitions are represented by visible error frames with crossed diagonals.

The output video preserves the CSV entry order.

The normal output uses one encoded frame per CSV entry. The implementation also describes a preview mode that can enlarge and repeat frames for easier inspection.

### 10. Error Handling

The program distinguishes between two types of errors.

**File-level errors**

Errors such as unreadable NRRD files, unsupported volume data, or failures during video encoding terminate execution with an informative message.

**Plane-level errors**

Malformed CSV entries and invalid geometric definitions are reported individually.

For these errors, the program:

1. Reports the problem.
2. Creates an error marker.
3. Continues processing later CSV entries.
4. Converts the marker into a visible error frame during video generation.

This prevents invalid individual planes from changing the order of subsequent frames.

### 11. Complexity Analysis

Let:

- `H` be the number of rows in a projection.
- `W` be the maximum number of sampling positions per row.
- `N` be the number of plane definitions.

Each row requires at most `O(W)` sampling operations.

Therefore, the time complexity for one projection is:

`O(H * W)`

For `N` projections with dimensions bounded by `H` and `W`, the total projection time is:

`O(N * H * W)`

Each projection matrix requires:

`O(H * W)`

memory.

The implementation stores the projection matrices before video encoding, so the total projection storage depends on the sum of their dimensions.

The input volume also occupies memory proportional to:

`O(sx * sy * sz)`

### 12. Performance Optimization

The implementation uses Numba JIT compilation to accelerate the main sampling loop.

Numba converts the supported numerical Python operations into compiled machine code, reducing the overhead of Python-level iteration.

The sampling loop works directly with numerical values rather than creating large intermediate coordinate arrays for every row.

The performance requirement specified in the assignment is greater than 30 projection FPS on a `500 × 500 × 500` unsigned 8-bit volume, with approximately 100 FPS as the expected target.

The `--performance` command provides a benchmark for measuring projection computation speed.

The benchmark described in the original algorithm document:

- Creates a synthetic `500 × 500 × 500` unsigned 8-bit volume.
- Uses a triangle with vertices `(0,0,0)`, `(400,0,0)`, and `(0,400,0)`.
- Runs a warm-up projection before measurement.
- Measures ten projection executions.
- Calculates the average projection time and FPS.

NRRD loading and MP4 encoding are not included in this projection-only measurement.

Performance depends on the machine, projection dimensions, and geometry. Final FPS results should be recorded after running the submitted version of the program.

### 13. Testing and Verification

Correctness is checked using built-in and additional tests.

The basic tests are executed with:

`python3 Ex0.py --test`

The performance benchmark is executed with:

`python3 Ex0.py --performance`

The additional test file `test_extra.py` is intended to cover:

- Known voxel values.
- Volume boundaries.
- Triangle and trapezoid validation.
- Invalid geometry.
- CSV parsing and error handling.
- Error-frame generation.

Final verification should include running the complete program with an NRRD file and the lecturer's CSV file, then checking that the MP4 video contains the expected number of frames in the correct order.

The documentation and file paths should be checked against the final GitHub repository structure before submission.
