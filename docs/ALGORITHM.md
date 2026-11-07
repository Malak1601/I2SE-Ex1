Algorithm Design — 3D Volume Plane Projection
1. Purpose
This document describes the algorithm implemented in Ex0.py for I2SE Ex1. The program reads a 3D NRRD volume and a CSV sequence of isosceles triangles or isosceles trapezoids, constructs a 2D sampled image for each valid region, and encodes the images into an MP4 in CSV order. Invalid individual entries produce visible error frames rather than stopping the sequence.

The algorithm treats 3D coordinates as voxel coordinates, not physical-space coordinates from NRRD metadata. It uses nearest-neighbor sampling, NumPy arrays, and an optionally Numba-compiled inner loop.
2. Inputs, outputs, and validation
- Volume: a three-dimensional NumPy array M of shape (sx, sy, sz), with 1 <= sx, sy, sz < 1024. Required voxel types are uint8, uint16, and uint32. As an extension, nonnegative signed 8/16/32-bit volumes are converted to the corresponding unsigned type by prepare_volume.
- CSV: one plane per populated row: nine coordinates for a triangle or twelve for a trapezoid. read_csv also accepts a leading point count (3 or 4), including the lecturer's 13-column header and blank unused fourth point for triangles. Empty rows and the recognized header are skipped. Malformed populated rows are retained as error entries.
- Output: one 2D projection matrix per valid plane, and an MP4 containing one encoded frame per populated CSV entry in normal mode. Errors are represented by marked frames.
Standard invocation:
python Ex0.py file.nrrd file.csv file.mp4
3. Geometric conventions
3.1 Isosceles triangle
Input points are (a, b, c). Point a is the common vertex of the equal sides (a,b) and (a,c).

Define:
- Dab = ||b-a||, Dac = ||c-a||, Dbc = ||c-b||.
- u = (b-a)/Dab, v = (c-a)/Dac.
project_triangle rejects non-finite coordinates, zero-length sides, sides with abs(Dab-Dac) >= 0.001, and degenerate/collinear triangles (using the implementation's geometry tolerance). It then calls render_rows(M, a, a, u, v, Dab, Dbc).
3.2 Isosceles trapezoid
Input points are (a, b, c, d) in this specific order:
- First leg: a -> b; second leg: c -> d.
- Starting base: a -> c; ending base: b -> d.
validate_trapezoid checks finite coordinates, nonzero edges, equal leg lengths within 0.001, parallel and consistently directed bases, coplanarity, nonzero area, and a non-crossing/non-folded arrangement. It also checks that the starting base is not longer than the ending base, allowing the implementation's small geometric tolerance. Equal bases (rectangles) are accepted.

The projection uses starting points a and c, unit directions (b-a)/||b-a|| and (d-c)/||d-c||, leg length ||b-a||, and maximum width max(||c-a||, ||d-b||).
4. Projection dimensions and row sampling
The shared function render_rows allocates a zero-filled matrix E with the same data type as M:
H = max(1, ceil(leg_length))
W = max(1, ceil(max_width) + 1)
E = zeros((H, W), dtype=M.dtype)
The implementation rejects a projection when H * W > 25,000,000 pixels. This is a software protection limit, not a dimension restriction stated by the lecturer; it should be considered when evaluating very large coordinate inputs.

For each output row y = 0, ..., H-1:
step = min(y + 1, leg_length)
p1 = start1 + step * direction1
p2 = start2 + step * direction2
span = ||p2 - p1||
The triangle therefore starts at the first unit step away from vertex a, rather than storing a separate apex row. For a trapezoid, the two starting points lie on its first base.

When span > EPS, sample at integer distances along the row:
for j = 0, 1, ..., floor(span):
    offset = j
    p = p1 + (offset / span) * (p2 - p1)
    x = floor((max_width - span)/2 + offset + 0.5)
    if 0 <= x < W:
        E[y, x] = sample_nearest(M, p)
In particular, if span is nonintegral, the algorithm does not append an extra fractional sample at the endpoint. This is the corrected integer-step convention used by the submitted Ex0.py. The horizontal offset centers shorter rows within the width based on the maximum base length.

If span <= EPS, a single sample at p1 is placed at floor(max_width/2 + 0.5) when that output column is valid.
5. Nearest-neighbor sampling and boundaries
For a 3D sample position p = (px, py, pz), the corrected implementation first checks whether the continuous position itself lies inside the volume:
0 <= px < sx
0 <= py < sy
0 <= pz < sz
If not, the sample is zero. This prevents a position such as px = -0.2 from being rounded into voxel 0 and incorrectly treated as an in-volume sample.

For an in-volume position, voxel indices are obtained using the consistent half-up rule:
ix = floor(px + 0.5)
iy = floor(py + 0.5)
iz = floor(pz + 0.5)
The rounded indices must also lie inside the volume; otherwise the value is zero. When both checks pass, the sample is M[ix, iy, iz]. The compiled _render_rows_jit applies the same boundary and rounding rules as sample_nearest.
6. End-to-end pseudocode
MAIN(volume_path, csv_path, video_path):
    reject an output path that overwrites either input
    M = prepare_volume(read_nrrd(volume_path))
    entries = read_csv(csv_path)
    projections = []

    for each (source_line, points, parse_error) in entries, in order:
        if parse_error:
            report the source line and append ERROR_MARKER
            continue
        try:
            if points has 3 vertices:
                E = project_triangle(M, points)
            else:
                E = project_trapezoid(M, points)
            append E
        except recoverable geometry/size error:
            report the source line and append ERROR_MARKER

    save_video(projections, video_path, fps=30, preview=preview_mode)
read_csv preserves invalid populated entries so that an error frame occupies the corresponding position. Fatal NRRD, output-path, and video-encoding errors are reported instead of being silently converted into plane-level errors.
7. Video generation
save_video calculates a shared grayscale scale from the maximum sampled value across valid projection matrices. For a valid projection E, the conversion is:
frame = clip(E / scale_max * 255, 0, 255).astype(uint8)
If the scale maximum is zero, the output is black. This grayscale conversion is for video display; it does not change the unsigned values held in the projection matrices.

Each image is centered on a zero-filled common canvas whose height and width are at least 32 pixels and at least as large as the valid projections. Error entries become high-contrast frames with crossed diagonals and a top marker. Final video dimensions are padded to even numbers for H.264 (libx264, yuv420p) encoding.

Normal mode writes one frame per populated CSV entry at 30 FPS. If the output filename ends with preview.mp4, the code enlarges small images and repeats each frame for easier viewing; preview frame counts must not be used to check the normal one-entry/one-frame requirement.

The encoder first writes a temporary MP4 in the destination directory and replaces the destination only after successful encoding. The program also checks that the output ends in .mp4 and prevents direct overwriting of input paths.
8. Complexity and memory
Let H be the number of output rows, W the maximum output width, and N the number of CSV entries. The worst-case sampling time for one projection is O(HW); for N similarly bounded projections it is O(NHW). One projection matrix occupies O(HW) space. The implementation keeps all projection matrices until video encoding, so projection storage is proportional to their combined sizes. The NRRD volume requires O(sx * sy * sz) memory. Video encoding introduces additional time and memory costs not captured by the projection-only bound.
9. Performance and verification
Numba JIT accelerates the row-sampling loop; a pure-Python fallback is available when Numba is absent, but the benchmarked performance should not be assumed for that fallback.
python Ex0.py --test
python -m pytest -q
python Ex0.py --performance
The --performance benchmark creates a synthetic 500 x 500 x 500 uint8 volume, warms up the projection once, and times ten triangle projections with vertices (0,0,0), (400,0,0), and (0,400,0). It excludes NRRD loading, video encoding, and initial JIT compilation.

The latest user-reported run of the corrected code passed 52 automated tests and measured approximately 0.00141 seconds per projection (710.91 projection FPS). This is a machine- and workload-specific computation benchmark, not end-to-end MP4 throughput.

A small CLI demonstration was also run with:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
It loaded a 16 x 16 x 16 volume, processed two planes, and produced an MP4 from which a visible projection frame was extracted. The demo video is very short because normal mode encodes only two frames.