
"""Plane projection of a 3D NRRD volume - Ex1.

Usage:
    python Ex0.py input.nrrd planes.csv output.mp4
    python Ex0.py --test
    python Ex0.py --performance

Triangle points: a, b, c
    Equal sides: a->b and a->c

Trapezoid points: a, b, c, d
    Equal legs: a->b and c->d
    Parallel bases: a->c and b->d

Coordinates are interpreted as voxel indices.
"""

import csv
import math
import sys
import time

import imageio.v2 as imageio
import numpy as np
import nrrd
from numba import njit


EPS = 1e-8
LENGTH_TOL = 1e-3
GEOM_TOL = 1e-7


# ---------------------------------
# Geometry helpers
# ---------------------------------

def distance(p1, p2):
    return math.dist(p1, p2)


def direction(p1, p2):
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)

    length = float(np.linalg.norm(p2 - p1))

    if length <= EPS:
        raise ValueError("Points must be different")

    return (p2 - p1) / length


# ---------------------------------
# CSV reader
# ---------------------------------

def read_csv(filename):
    """Read simple CSV or lecturer count-prefixed CSV."""

    shapes = []

    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, 1):
            row = [cell.strip() for cell in row]

            while row and not row[-1]:
                row.pop()

            if not row or not any(row):
                continue

            if row[0].lower().startswith("number of points"):
                continue

            try:
                if len(row) in (10, 13) and row[0] in ("3", "4"):
                    number = int(row[0])

                    if len(row) != 1 + 3 * number:
                        raise ValueError(
                            "Point count does not match coordinates"
                        )

                    row = row[1:]

                if len(row) not in (9, 12):
                    raise ValueError(
                        "Expected 9/12 coordinates "
                        "or count + coordinates"
                    )

                values = [float(cell) for cell in row]

                if not all(math.isfinite(v) for v in values):
                    raise ValueError("Coordinates must be finite")

                points = [
                    tuple(values[i:i + 3])
                    for i in range(0, len(values), 3)
                ]

                shapes.append((line_number, points, None))

            except ValueError as exc:
                shapes.append((line_number, None, str(exc)))

    if not shapes:
        raise ValueError("CSV contains no plane definitions")

    return shapes


# ---------------------------------
# Volume validation
# ---------------------------------

def prepare_volume(M):
    if M.ndim != 3 or any(
        not 1 <= size < 1024 for size in M.shape
    ):
        raise ValueError(
            "Expected a 3D volume with dimensions 1..1023"
        )

    if M.dtype.kind == "u" and M.dtype.itemsize in (1, 2, 4):
        return M

    if M.dtype.kind == "i" and M.dtype.itemsize in (1, 2, 4):
        if M.min() < 0:
            raise ValueError(
                "Signed NRRD contains negative values"
            )

        unsigned_dtype = np.dtype(
            "u" + str(M.dtype.itemsize)
        )

        print(
            "Converting nonnegative signed volume to",
            unsigned_dtype
        )

        return M.astype(unsigned_dtype)

    raise ValueError("Expected 8/16/32-bit integer volume")


def sample_nearest(M, point):
    indices = tuple(
        math.floor(float(v) + 0.5)
        for v in point
    )

    if all(
        0 <= indices[i] < M.shape[i]
        for i in range(3)
    ):
        return M[indices]

    return 0


# ---------------------------------
# Fast projection with Numba
# ---------------------------------

@njit(cache=True)
def _render_rows_jit(
    M,
    start1,
    start2,
    vector1,
    vector2,
    leg_length,
    max_width,
    height,
    width
):
    E = np.zeros((height, width), dtype=M.dtype)

    for y in range(height):
        step = min(float(y + 1), leg_length)

        p1x = start1[0] + step * vector1[0]
        p1y = start1[1] + step * vector1[1]
        p1z = start1[2] + step * vector1[2]

        dx = start2[0] + step * vector2[0] - p1x
        dy = start2[1] + step * vector2[1] - p1y
        dz = start2[2] + step * vector2[2] - p1z

        span = math.sqrt(dx * dx + dy * dy + dz * dz)

        if span <= EPS:
            x = math.floor(max_width / 2.0 + 0.5)

            if 0 <= x < width:
                ix = math.floor(p1x + 0.5)
                iy = math.floor(p1y + 0.5)
                iz = math.floor(p1z + 0.5)

                if (
                    0 <= ix < M.shape[0]
                    and 0 <= iy < M.shape[1]
                    and 0 <= iz < M.shape[2]
                ):
                    E[y, x] = M[ix, iy, iz]

            continue

        count = math.ceil(span)

        for j in range(count + 1):
            offset = min(float(j), span)

            x = int(
                np.rint(
                    (max_width - span) / 2.0 + offset
                )
            )

            if x < 0 or x >= width:
                continue

            fraction = offset / span

            ix = math.floor(p1x + fraction * dx + 0.5)
            iy = math.floor(p1y + fraction * dy + 0.5)
            iz = math.floor(p1z + fraction * dz + 0.5)

            if (
                0 <= ix < M.shape[0]
                and 0 <= iy < M.shape[1]
                and 0 <= iz < M.shape[2]
            ):
                E[y, x] = M[ix, iy, iz]

    return E


def render_rows(
    M,
    start1,
    start2,
    vector1,
    vector2,
    leg_length,
    max_width
):
    height = max(1, math.ceil(leg_length))
    width = max(1, math.ceil(max_width) + 1)

    return _render_rows_jit(
        M,
        np.asarray(start1, dtype=np.float64),
        np.asarray(start2, dtype=np.float64),
        np.asarray(vector1, dtype=np.float64),
        np.asarray(vector2, dtype=np.float64),
        float(leg_length),
        float(max_width),
        height,
        width
    )


# ---------------------------------
# Triangle projection
# ---------------------------------

def project_triangle(M, a, b, c):
    dab = distance(a, b)
    dac = distance(a, c)

    if (
        dab <= EPS
        or dac <= EPS
        or abs(dab - dac) >= LENGTH_TOL
    ):
        raise ValueError(
            "Triangle requires two approximately "
            "equal nonzero sides from a"
        )

    ab = np.subtract(b, a)
    ac = np.subtract(c, a)

    if np.linalg.norm(np.cross(ab, ac)) <= (
        GEOM_TOL * dab * dac
    ):
        raise ValueError(
            "Triangle points must not be collinear"
        )

    return render_rows(
        M,
        a,
        a,
        direction(a, b),
        direction(a, c),
        dab,
        distance(b, c)
    )


# ---------------------------------
# Trapezoid validation
# Corrected lecturer point order
# ---------------------------------

def validate_trapezoid(a, b, c, d):
    a, b, c, d = (
        np.asarray(p, dtype=np.float64)
        for p in (a, b, c, d)
    )

    leg1 = b - a
    leg2 = d - c

    base_start = c - a
    base_end = d - b

    length1 = np.linalg.norm(leg1)
    length2 = np.linalg.norm(leg2)

    start_width = np.linalg.norm(base_start)
    end_width = np.linalg.norm(base_end)

    if min(
        length1, length2, start_width, end_width
    ) <= EPS:
        raise ValueError("Trapezoid edges must be nonzero")

    if abs(length1 - length2) > LENGTH_TOL:
        raise ValueError(
            "Trapezoid legs must have equal lengths"
        )

    if np.linalg.norm(
        np.cross(base_start, base_end)
    ) > GEOM_TOL * start_width * end_width:
        raise ValueError(
            "Trapezoid bases must be parallel"
        )

    if np.dot(base_start, base_end) <= 0:
        raise ValueError(
            "Trapezoid bases have opposite directions"
        )

    normal = np.cross(base_start, leg1)
    normal_length = np.linalg.norm(normal)

    if normal_length <= GEOM_TOL * start_width * length1:
        raise ValueError("Trapezoid has zero area")

    if abs(np.dot(d - a, normal)) > (
        GEOM_TOL
        * normal_length
        * max(1.0, np.linalg.norm(d - a))
    ):
        raise ValueError(
            "Trapezoid points are not coplanar"
        )

    unit_normal = normal / normal_length

    side_b = np.dot(
        np.cross(base_start, b - a),
        unit_normal
    )

    side_d = np.dot(
        np.cross(base_start, d - a),
        unit_normal
    )

    if min(side_b, side_d) <= (
        GEOM_TOL * start_width * length1
    ):
        raise ValueError(
            "Invalid trapezoid geometry"
        )

    return float(length1), float(max(start_width, end_width))


# ---------------------------------
# Trapezoid projection
# ---------------------------------

def project_trapezoid(M, a, b, c, d):
    leg_length, max_width = validate_trapezoid(
        a, b, c, d
    )

    return render_rows(
        M,
        a,
        c,
        direction(a, b),
        direction(c, d),
        leg_length,
        max_width
    )


# ---------------------------------
# Frame conversion
# ---------------------------------

def make_frame(E, scale_max):
    if scale_max <= 0:
        return np.zeros(E.shape, dtype=np.uint8)

    return np.clip(
        E.astype(np.float64) / scale_max * 255,
        0,
        255
    ).astype(np.uint8)


def make_error_frame(height, width):
    frame = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    for y in range(height):
        x = round(
            y * (width - 1) / max(1, height - 1)
        )

        frame[y, x] = 255
        frame[y, width - 1 - x] = 255

    frame[:min(3, height), :] = 255

    return frame


# ---------------------------------
# MP4 generation
# ---------------------------------

def save_video(
    projections,
    filename,
    fps=30,
    preview=False
):
    if not projections:
        raise ValueError("No projections to save")

    valid = [
        E for E in projections
        if E is not None
    ]

    scale_max = max(
        (float(np.max(E)) for E in valid),
        default=0.0
    )

    height = max(
        (E.shape[0] for E in valid),
        default=64
    )

    width = max(
        (E.shape[1] for E in valid),
        default=64
    )

    height = max(height, 32)
    width = max(width, 32)

    scale = (
        max(1, math.ceil(256 / max(height, width)))
        if preview else 1
    )

    video_height = height * scale
    video_width = width * scale

    video_height += video_height % 2
    video_width += video_width % 2

    with imageio.get_writer(
        filename,
        fps=fps,
        codec="libx264",
        macro_block_size=1
    ) as writer:

        for E in projections:
            if E is None:
                canvas = make_error_frame(
                    height, width
                )
            else:
                canvas = np.zeros(
                    (height, width),
                    dtype=np.uint8
                )

                frame = make_frame(E, scale_max)

                canvas[
                    :frame.shape[0],
                    :frame.shape[1]
                ] = frame

            if preview:
                canvas = np.repeat(
                    np.repeat(
                        canvas,
                        scale,
                        axis=0
                    ),
                    scale,
                    axis=1
                )

            padded = np.zeros(
                (video_height, video_width),
                dtype=np.uint8
            )

            padded[
                :canvas.shape[0],
                :canvas.shape[1]
            ] = canvas

            for _ in range(fps if preview else 1):
                writer.append_data(padded)

    print("Video saved:", filename)


# ---------------------------------
# Basic tests
# ---------------------------------

def test_projection():
    M = np.zeros((3, 3, 3), dtype=np.uint8)

    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10*x + 3*y + z

    triangle = project_triangle(
        M,
        (0, 0, 0),
        (2, 0, 0),
        (0, 2, 0)
    )

    np.testing.assert_array_equal(
        triangle,
        np.array([
            [0, 10, 3, 0],
            [20, 13, 13, 6]
        ], dtype=np.uint8)
    )

    # Rectangle with corrected point order
    rectangle = project_trapezoid(
        M,
        (0, 0, 0),
        (2, 0, 0),
        (0, 2, 0),
        (2, 2, 0)
    )

    np.testing.assert_array_equal(
        rectangle,
        np.array([
            [10, 13, 16],
            [20, 23, 26]
        ], dtype=np.uint8)
    )

    M2 = np.zeros((5, 5, 3), dtype=np.uint8)

    for x in range(5):
        for y in range(5):
            M2[x, y, 0] = 10*x + y

    trapezoid = project_trapezoid(
        M2,
        (1, 0, 0),
        (0, 2, 0),
        (3, 0, 0),
        (4, 2, 0)
    )

    assert trapezoid.ndim == 2
    assert trapezoid.size > 0
    assert trapezoid.dtype == M2.dtype

    assert sample_nearest(M, (-1, 0, 0)) == 0

    try:
        project_triangle(
            M,
            (0, 0, 0),
            (2, 0, 0),
            (0, 1, 0)
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid triangle was accepted"
        )

    # Lecturer rectangle
    leg, width = validate_trapezoid(
        (200, 0, 0),
        (200, 0, 500),
        (200, 400, 0),
        (200, 400, 500)
    )

    assert abs(leg - 500) < EPS
    assert abs(width - 400) < EPS

    # Lecturer isosceles trapezoid
    validate_trapezoid(
        (200, 50, 0),
        (200, 0, 500),
        (200, 350, 0),
        (200, 400, 500)
    )

    print("All basic projection tests passed")


# ---------------------------------
# Performance test
# ---------------------------------

def test_performance():
    M = np.zeros(
        (500, 500, 500),
        dtype=np.uint8
    )

    a = (0, 0, 0)
    b = (400, 0, 0)
    c = (0, 400, 0)

    # Numba warm-up
    project_triangle(M, a, b, c)

    repetitions = 10

    start = time.perf_counter()

    for _ in range(repetitions):
        project_triangle(M, a, b, c)

    elapsed = time.perf_counter() - start

    print("Volume shape:", M.shape)
    print("Number of projections:", repetitions)

    print(
        "Average seconds per projection:",
        round(elapsed / repetitions, 5)
    )

    print(
        "Projection FPS:",
        round(repetitions / elapsed, 2)
    )

    print(
        "Note: excludes NRRD loading and MP4 encoding"
    )


# ---------------------------------
# Main application
# ---------------------------------

def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python Ex0.py "
            "file.nrrd file.csv file.mp4"
        )
        return 2

    volume_filename = sys.argv[1]
    csv_filename = sys.argv[2]
    video_filename = sys.argv[3]

    M, header = nrrd.read(volume_filename)
    M = prepare_volume(M)

    shapes = read_csv(csv_filename)

    print("Volume shape:", M.shape)
    print("Number of CSV entries:", len(shapes))

    projections = []

    for index, (
        line_number,
        points,
        error
    ) in enumerate(shapes, 1):

        if error is not None:
            print(
                f"CSV line {line_number}: "
                f"{error}; adding error frame"
            )
            projections.append(None)
            continue

        try:
            if len(points) == 3:
                E = project_triangle(M, *points)
            else:
                E = project_trapezoid(M, *points)

            print(
                f"Projection {index}: "
                f"shape={E.shape}, "
                f"nonzero={np.count_nonzero(E)}"
            )

            projections.append(E)

        except (ValueError, OverflowError) as exc:
            print(
                f"CSV line {line_number}: "
                f"{exc}; adding error frame"
            )
            projections.append(None)

    preview = video_filename.lower().endswith(
        "preview.mp4"
    )

    save_video(
        projections,
        video_filename,
        fps=30,
        preview=preview
    )

    return 0


# ---------------------------------
# Entry point
# ---------------------------------

if __name__ == "__main__":
    try:
        if (
            len(sys.argv) == 2
            and sys.argv[1] == "--test"
        ):
            test_projection()

        elif (
            len(sys.argv) == 2
            and sys.argv[1] == "--performance"
        ):
            test_performance()

        else:
            sys.exit(main())

    except (OSError, ValueError, RuntimeError) as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr
        )
        sys.exit(1)
