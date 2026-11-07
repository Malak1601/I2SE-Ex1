# Algorithm Design — 3D Volume Plane Projection

## 1. Purpose

This document describes the algorithm implemented in `Ex0.py` for I2SE Ex1.

The program reads a three-dimensional NRRD volume and a CSV sequence of isosceles triangles or isosceles trapezoids, constructs a two-dimensional sampled image for each valid region, and encodes the resulting images into an MP4 video in CSV order.

Invalid individual entries produce visible error frames rather than stopping the sequence.

The algorithm treats 3D coordinates as voxel coordinates, not physical-space coordinates from NRRD metadata. It uses nearest-neighbor sampling, NumPy arrays, and Numba JIT acceleration when available.

## 2. Inputs, Outputs, and Validation

### 2.1 Volume

The input volume `M` is a three-dimensional NumPy array of shape `(sx, sy, sz)`.

The required dimensions satisfy:

`1 <= sx, sy, sz < 1024`

Supported voxel types are:

- `uint8`
- `uint16`
- `uint32`

As an extension, nonnegative signed 8-, 16-, and 32-bit integer volumes can be converted to the corresponding unsigned types by `prepare_volume()`.

### 2.2 CSV Input

Each populated CSV row defines:

- A triangle using three 3D points (9 coordinates).
- A trapezoid using four 3D points (12 coordinates).

The `read_csv()` function also supports a leading point count (`3` or `4`), including the lecturer's 13-column CSV format.

Recognized headers and empty rows are skipped. Malformed populated rows are retained as error entries.

### 2.3 Output

The algorithm generates:

- A 2D projection matrix for every valid plane.
- A marked error frame for every invalid individual plane entry.
- An MP4 video preserving CSV entry order.

The standard command is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

## 3. Geometric Conventions

### 3.1 Isosceles Triangle

A triangle is defined by three points:

`(a, b, c)`

Point `a` is the common vertex of the two equal sides.

Define:

```text
Dab = ||b - a||
Dac = ||c - a||
Dbc = ||c - b||
```

The normalized direction vectors are:

```text
u = (b - a) / Dab
v = (c - a) / Dac
```

The triangle is valid when:

- All coordinates are finite.
- The required side lengths are nonzero.
- `abs(Dab - Dac) < 0.001`.
- The triangle is not degenerate or collinear.

After validation, the triangle is rendered using:

```text
render_rows(M, a, a, u, v, Dab, Dbc)
```

### 3.2 Isosceles Trapezoid

A trapezoid is defined by:

`(a, b, c, d)`

The required point ordering is:

| Element | Points |
|---|---|
| First leg | `a → b` |
| Second leg | `c → d` |
| Starting base | `a → c` |
| Ending base | `b → d` |

The `validate_trapezoid()` function checks:

- Finite coordinates.
- Nonzero required edges.
- Approximately equal leg lengths.
- Parallel and consistently directed bases.
- Coplanarity.
- Nonzero area.
- A non-crossing, non-folded arrangement.
- The starting base is not longer than the ending base, within the implementation's geometric tolerance.

Rectangles are accepted as a special case with equal base lengths.

The normalized leg directions are:

```text
u = (b - a) / ||b - a||
v = (d - c) / ||d - c||
```

The starting points are `a` and `c`.

The leg length is:

```text
L = ||b - a||
```

The maximum width is:

```text
B = max(||c - a||, ||d - b||)
```

## 4. Projection Dimensions and Row Sampling

The shared `render_rows()` function allocates a zero-filled projection matrix with the same data type as the input volume.

The dimensions are:

```text
H = max(1, ceil(leg_length))
W = max(1, ceil(max_width) + 1)
E = zeros((H, W), dtype=M.dtype)
```

The implementation rejects a projection if:

```text
H * W > 25,000,000
```

This is a protective allocation limit, not a requirement imposed by the lecturer.

### 4.1 Row Endpoints

For each output row:

```text
y = 0, 1, ..., H - 1
```

Calculate:

```text
step = min(y + 1, leg_length)

p1 = start1 + step * direction1
p2 = start2 + step * direction2

span = ||p2 - p1||
```

For a triangle, both starting points are the vertex `a`. Therefore, the first row begins one unit step away from the vertex instead of storing a separate apex row.

For a trapezoid, the starting points lie on the starting base.

### 4.2 Sampling Across a Row

When `span > EPS`, the algorithm samples at integer distances:

```text
for j = 0, 1, ..., floor(span):
    offset = j
    p = p1 + (offset / span) * (p2 - p1)
```

The output column is calculated using:

```text
x = floor((max_width - span) / 2 + offset + 0.5)
```

If `x` lies inside the output matrix, the nearest voxel value is copied to:

```text
E[y, x]
```

**Important design decision:** When the row span is nonintegral, the algorithm does not append an additional fractional endpoint sample. This follows the corrected integer-step sampling convention.

The horizontal offset centers shorter rows within the projection width.

### 4.3 Degenerate Row Span

When `span <= EPS`, the algorithm samples one point at `p1`.

The output column is:

```text
x = floor(max_width / 2 + 0.5)
```

The sample is stored only when the output column is valid.

## 5. Nearest-Neighbor Sampling and Boundaries

For a continuous 3D sampling position:

```text
p = (px, py, pz)
```

The algorithm first checks whether the continuous position lies inside the volume:

```text
0 <= px < sx
0 <= py < sy
0 <= pz < sz
```

If any condition fails, the sampled value is zero.

This prevents an outside position such as `px = -0.2` from being rounded into voxel index `0`.

For a position inside the continuous bounds, nearest-neighbor indices are calculated using half-up rounding:

```text
ix = floor(px + 0.5)
iy = floor(py + 0.5)
iz = floor(pz + 0.5)
```

The rounded indices must also satisfy:

```text
0 <= ix < sx
0 <= iy < sy
0 <= iz < sz
```

If the indices are valid:

```text
value = M[ix, iy, iz]
```

Otherwise:

```text
value = 0
```

The Numba-compiled sampling loop follows the same boundary and rounding rules as `sample_nearest()`.

## 6. End-to-End Pseudocode

```text
MAIN(volume_path, csv_path, video_path):

    Validate output path
    Prevent overwriting input files

    M = prepare_volume(read_nrrd(volume_path))
    entries = read_csv(csv_path)

    projections = []

    FOR each entry in CSV order:

        IF entry has a parsing error:
            Report error and CSV line number
            Append ERROR_MARKER
            CONTINUE

        TRY:
            IF entry contains 3 points:
                E = project_triangle(M, entry.points)

            ELSE IF entry contains 4 points:
                E = project_trapezoid(M, entry.points)

            Append E

        CATCH recoverable geometry or size error:
            Report error and CSV line number
            Append ERROR_MARKER

    save_video(projections, video_path, fps=30)
```

The row-rendering procedure is:

```text
RENDER_ROWS(M, start1, start2, dir1, dir2, L, B):

    H = max(1, ceil(L))
    W = max(1, ceil(B) + 1)

    IF H * W > MAX_PIXELS:
        RAISE error

    E = zero matrix of shape (H, W)

    FOR y = 0 TO H - 1:

        step = min(y + 1, L)

        p1 = start1 + step * dir1
        p2 = start2 + step * dir2

        span = distance(p1, p2)

        IF span <= EPS:
            x = floor(B / 2 + 0.5)

            IF x is inside E:
                E[y, x] = SAMPLE_NEAREST(M, p1)

            CONTINUE

        FOR j = 0 TO floor(span):

            offset = j

            p = p1 + (offset / span) * (p2 - p1)

            x = floor((B - span) / 2 + offset + 0.5)

            IF x is inside E:
                E[y, x] = SAMPLE_NEAREST(M, p)

    RETURN E
```

Nearest-neighbor sampling:

```text
SAMPLE_NEAREST(M, p):

    IF p is outside the continuous volume bounds:
        RETURN 0

    ix
