Algorithm Design

Overview This project generates 2D images from a 3D NRRD volume. Each CSV entry defines an isosceles triangle (three points) or an isosceles trapezoid (four points). The program validates the region, samples voxel values at points across it, and creates a 2D projection matrix. The projections are then written to an MP4 video in CSV order. Invalid entries produce visible error frames instead of stopping later entries.
The implementation uses NumPy for array storage and geometry calculations, and Numba (@njit) to compile the main row-by-row sampling loop. 2. Inputs and Outputs Inputs: a 3D NRRD volume M and a CSV file containing either 9 or 12 coordinates per row. The lecturer's format, with a leading point count (3 or 4) and a header, is also accepted.

Outputs: a 2D projection E for each valid region and an MP4 video. An invalid CSV entry or geometric region is represented by an error frame. Coordinates are interpreted as voxel indices; physical-space transformations from NRRD metadata are not applied. 3. Main Processing Steps

Read the NRRD volume and validate its dimensions and data type.
Read the CSV entries in order, recording errors for malformed rows.
For each entry, validate the triangle or trapezoid geometry.
Calculate normalized direction vectors and the output dimensions.
Sample the region row by row into a zero-initialized 2D matrix.
Keep the resulting projection, or an error marker if the entry is invalid.
Convert valid matrices to grayscale video frames, replace error markers with error frames, pad to common dimensions, and encode the MP4.
Triangle Projection 4.1 Geometry The triangle is defined by points a, b, and c. The equal sides begin at a:
Dab = ||b - a||
Dac = ||c - a||
Dbc = ||c - b|| The implementation requires Dab > EPS, Dac > EPS, and abs(Dab - Dac) < LENGTH_TOL, where EPS = 1e-8 and LENGTH_TOL = 0.001. It also rejects collinear points using the cross product of (b-a) and (c-a) and a geometric tolerance GEOM_TOL = 1e-7.
The normalized side directions are:

vab = (b-a) / Dab
vac = (c-a) / Dac 4.2 Output Dimensions The matrix E has the same voxel data type as M and is initialized with zeros:
height = max(1, ceil(Dab))
width = max(1, ceil(Dbc) + 1) 4.3 Row Sampling For each row index y from 0 to height-1:
step = min(y + 1, Dab)
p1 = a + step * vab
p2 = a + step * vac
span = ||p2 - p1|| The first stored row starts one unit from a; the vertex is not stored as a separate initial row.
For a nonzero span, the algorithm sets count = ceil(span) and visits j = 0, ..., count. Each sampling offset is offset = min(j, span) and the 3D sampling position is:

point = p1 + (offset / span) * (p2 - p1)

The corresponding output column is:

x = rint((max_width - span) / 2 + offset)

where max_width = Dbc. Centering places shorter rows toward the middle of the output image. Multiple samples can round to the same column; a later valid sample can overwrite an earlier one.

If span <= EPS, the code samples p1 directly and places it near the center of the row. 5. Trapezoid Projection 5.1 Point Order and Validation The four points must be supplied in the following order, matching the lecturer's CSV convention:

First leg: a -> b
Second leg: c -> d
Starting base: a -> c
Ending base: b -> d The implementation validates:
Nonzero lengths for both legs and both bases.
Approximately equal leg lengths: abs(||b-a|| - ||d-c||) <= 0.001.
Parallel bases using the cross product of (c-a) and (d-b).
Bases pointing in the same direction using a positive dot product.
Nonzero area and coplanarity.
A consistent non-crossing geometric arrangement using signed cross-product checks. The current code does not require the starting base to be shorter than the ending base. Rectangles are also accepted. 5.2 Sampling The trapezoid reuses the same row-rendering function as the triangle, with:
start1 = a
start2 = c
vector1 = direction(a,b)
vector2 = direction(c,d)
leg_length = ||b-a||
max_width = max(||c-a||, ||d-b||) The dimensions are:
height = max(1, ceil(leg_length))
width = max(1, ceil(max_width) + 1) For each row, the endpoints are:
p1 = a + step * vector1
p2 = c + step * vector2 The segment from p1 to p2 is sampled using the same nearest-neighbor procedure. Unlike the triangle, the trapezoid can have a nonzero segment width from the beginning.
Nearest-Neighbor Sampling and Boundaries Each 3D coordinate is converted to a voxel index using:
index = floor(coordinate + 0.5)

A sample is copied only when all indices are within the volume bounds:

0 <= ix < sx
0 <= iy < sy
0 <= iz < sz Otherwise, the output pixel remains zero. Output columns use np.rint, which is a separate rounding rule from voxel-coordinate rounding.
NRRD Handling The pynrrd library loads the volume. The code requires exactly three dimensions, each between 1 and 1023 inclusive. It accepts unsigned 8-, 16-, and 32-bit integer arrays. Signed arrays of these bit depths are converted to the corresponding unsigned type only when every voxel value is nonnegative; negative values are rejected.
Video Generation The program keeps the projection matrices until video creation. For valid projections, it finds the largest voxel value and scales each matrix to an 8-bit grayscale image using the same scale:
frame = clip(E / scale_max * 255, 0, 255)

If scale_max is zero, the image is black. Frames of different sizes are placed at the upper-left corner of zero-filled canvases with common dimensions. The video width and height are adjusted to even numbers for H.264 encoding with imageio.

Invalid entries are represented by a visible error frame with crossed diagonals and a bright top border.

Normal output: one encoded frame per CSV entry at 30 FPS.

Preview output: when the output filename ends with preview.mp4, small frames may be enlarged and each CSV entry is repeated for 30 encoded frames, making it visible for about one second at 30 FPS. 9. Error Handling The CSV reader preserves malformed nonempty data rows as entries containing an error description. Geometry validation raises ValueError for invalid regions. The main loop reports each plane-specific error, appends an error marker, and continues with later entries. During video generation, each marker becomes an error frame.

Unrecoverable errors, such as an unreadable NRRD file or unsupported volume data, stop execution with an error message. Blank CSV rows and the recognized header row are skipped. 10. Complexity Analysis Let H be the number of output rows and W the maximum number of sampled positions in a row. The projection performs O(H × W) sampling work and stores an output matrix of size O(H × W). The compiled loop uses a constant number of scalar temporary values per sample, rather than allocating full NumPy coordinate arrays for each row.

For N regions with dimensions bounded by H and W, total projection work is O(N × H × W). Because all projection matrices are stored before encoding, their combined memory use is proportional to the sum of their pixel counts, in addition to the input volume and video buffers. 11. Performance Experiment The --performance command creates a synthetic unsigned 8-bit volume of shape 500 × 500 × 500. It projects the triangle:

a = (0,0,0)
b = (400,0,0)
c = (0,400,0) The program runs one warm-up projection to compile the Numba function, then measures 10 projections using time.perf_counter(). It prints average seconds per projection and FPS = 10 / elapsed.
A previous local benchmark reported approximately 443 projection FPS. This figure should be confirmed by rerunning the final code in the submission environment. It measures projection computation only, not NRRD loading or MP4 encoding. The result depends on the machine and test geometry. 12. Testing and Verification The code includes built-in correctness tests (python3 Ex0.py --test) and a performance benchmark (python3 Ex0.py --performance). Additional tests in test_extra.py cover known voxel values, volume boundaries, geometry validation, CSV error recovery, and error-frame creation.

Before submission, run both test commands on the final code and verify that the generated video has the expected frames and order. Also confirm that all repository documentation and sample file names match the files actually committed.
