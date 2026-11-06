"""Project CSV-defined isosceles triangles/trapezoids through a 3D NRRD volume.

Usage:
    python Ex0.py input.nrrd planes.csv output.mp4
    python Ex0.py --test
    python Ex0.py --performance

Triangle: a,b,c with equal sides a-b and a-c.
Trapezoid: a,b,c,d with equal legs a-b and c-d, and bases a-c and b-d.
Coordinates are voxel indices; samples outside the volume are zero.
"""

import csv
import math
import os
from pathlib import Path
import sys
import tempfile
import time

import imageio.v2 as imageio
import numpy as np

try:
    import nrrd
except ImportError:
    nrrd = None

try:
    from numba import njit
except ImportError:
    # Correct but slower fallback if Numba is not installed.
    def njit(*args, **kwargs):
        def decorate(function):
            return function
        return decorate


EPS = 1e-8
LENGTH_TOL = 1e-3
GEOM_TOL = 1e-7


def distance(p1, p2):
    return math.dist(p1, p2)


def direction(p1, p2):
    a = np.asarray(p1, dtype=np.float64)
    b = np.asarray(p2, dtype=np.float64)
    length = float(np.linalg.norm(b - a))
    if not np.isfinite(length) or length <= EPS:
        raise ValueError("Points must be distinct and finite")
    return (b - a) / length


def read_csv(filename):
    """Return (source line, points or None, error or None) for each populated row.

    Supports 9/12 raw coordinates, or a leading 3/4 point count.
    The lecturer's 13-column header and blank fourth point for triangles work.
    Bad rows are retained so they can produce error frames.
    """
    entries = []
    with open(filename, newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream)
        for line_number, original in enumerate(reader, 1):
            row = [cell.strip() for cell in original]
            if not any(row):
                continue
            first = row[0].lower()
            if first in ("number of points (3 or 4)", "number of points", "type"):
                continue
            try:
                if row[0] in ("3", "4") and len(row) >= 10:
                    count = int(row[0])
                    fields = row[1:]
                    required = 3 * count
                    if len(fields) < required or any(not v for v in fields[:required]):
                        raise ValueError("Point count does not match coordinates")
                    if any(v for v in fields[required:]):
                        raise ValueError("Unexpected coordinates after declared points")
                    fields = fields[:required]
                else:
                    # Raw 9- or 12-coordinate rows, optionally with empty trailing cells.
                    fields = list(row)
                    while fields and fields[-1] == "":
                        fields.pop()
                    if len(fields) not in (9, 12):
                        raise ValueError("Expected 9/12 coordinates or 3/4 followed by coordinates")
                    if any(not v for v in fields):
                        raise ValueError("Missing coordinate")
                values = [float(value) for value in fields]
                if not all(math.isfinite(v) for v in values):
                    raise ValueError("Coordinates must be finite")
                points = [tuple(values[i:i + 3]) for i in range(0, len(values), 3)]
                entries.append((line_number, points, None))
            except (ValueError, OverflowError) as error:
                entries.append((line_number, None, str(error)))
    if not entries:
        raise ValueError("CSV contains no plane definitions")
    return entries


def prepare_volume(volume):
    M = np.asarray(volume)
    if M.ndim != 3 or any(not 1 <= size < 1024 for size in M.shape):
        raise ValueError("Expected a 3D volume with axis sizes 1..1023")
    if M.dtype.kind == "u" and M.dtype.itemsize in (1, 2, 4):
        return M
    if M.dtype.kind == "i" and M.dtype.itemsize in (1, 2, 4):
        if np.min(M) < 0:
            raise ValueError("Signed volume contains negative values")
        return M.astype(np.dtype("u" + str(M.dtype.itemsize)))
    raise ValueError("Expected an 8/16/32-bit integer volume")


def sample_nearest(M, point):
    if len(point) != 3 or not all(math.isfinite(float(v)) for v in point):
        raise ValueError("Sample position must contain three finite coordinates")
    indices = tuple(math.floor(float(v) + 0.5) for v in point)
    if all(0 <= indices[i] < M.shape[i] for i in range(3)):
        return M[indices]
    return 0


@njit(cache=True)
def _render_rows_jit(M, start1, start2, vector1, vector2, leg_length,
                     max_width, height, width):
    """Unit-distance scanlines, retaining the original assignment convention."""
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
                if (0 <= ix < M.shape[0] and 0 <= iy < M.shape[1]
                        and 0 <= iz < M.shape[2]):
                    E[y, x] = M[ix, iy, iz]
            continue
        count = math.ceil(span)
        for j in range(count + 1):
            offset = min(float(j), span)
            # Use one consistent half-up rule for both voxel and canvas indices.
            x = math.floor((max_width - span) / 2.0 + offset + 0.5)
            if not 0 <= x < width:
                continue
            fraction = offset / span
            ix = math.floor(p1x + fraction * dx + 0.5)
            iy = math.floor(p1y + fraction * dy + 0.5)
            iz = math.floor(p1z + fraction * dz + 0.5)
            if (0 <= ix < M.shape[0] and 0 <= iy < M.shape[1]
                    and 0 <= iz < M.shape[2]):
                E[y, x] = M[ix, iy, iz]
    return E


def render_rows(M, start1, start2, vector1, vector2, leg_length, max_width):
    if not all(math.isfinite(float(v)) for v in (leg_length, max_width)):
        raise ValueError("Plane dimensions must be finite")
    if leg_length <= EPS or max_width < 0:
        raise ValueError("Invalid plane dimensions")
    height = max(1, math.ceil(leg_length))
    width = max(1, math.ceil(max_width) + 1)
    # Avoid accidental huge allocations from untrusted CSV coordinates.
    if height * width > 25_000_000:
        raise ValueError("Projection is too large (more than 25 million pixels)")
    return _render_rows_jit(
        M, np.asarray(start1, dtype=np.float64),
        np.asarray(start2, dtype=np.float64),
        np.asarray(vector1, dtype=np.float64),
        np.asarray(vector2, dtype=np.float64),
        float(leg_length), float(max_width), height, width
    )


def project_triangle(M, a, b, c):
    dab, dac = distance(a, b), distance(a, c)
    if not all(math.isfinite(v) for v in (dab, dac)):
        raise ValueError("Triangle coordinates must be finite")
    if dab <= EPS or dac <= EPS or abs(dab - dac) >= LENGTH_TOL:
        raise ValueError("Triangle requires equal nonzero sides a-b and a-c")
    ab = np.subtract(b, a)
    ac = np.subtract(c, a)
    if np.linalg.norm(np.cross(ab, ac)) <= GEOM_TOL * dab * dac:
        raise ValueError("Triangle vertices must not be collinear")
    return render_rows(M, a, a, direction(a, b), direction(a, c),
                       dab, distance(b, c))


def validate_trapezoid(a, b, c, d):
    a, b, c, d = (np.asarray(p, dtype=np.float64) for p in (a, b, c, d))
    if not all(np.all(np.isfinite(p)) for p in (a, b, c, d)):
        raise ValueError("Trapezoid coordinates must be finite")
    leg1, leg2 = b - a, d - c
    base_start, base_end = c - a, d - b
    length1, length2 = np.linalg.norm(leg1), np.linalg.norm(leg2)
    start_width, end_width = np.linalg.norm(base_start), np.linalg.norm(base_end)
    if min(length1, length2, start_width, end_width) <= EPS:
        raise ValueError("Trapezoid edges must be nonzero")
    if abs(length1 - length2) >= LENGTH_TOL:
        raise ValueError("Trapezoid legs must have equal lengths")
    if start_width > end_width + GEOM_TOL:
        raise ValueError("Trapezoid starting base must not exceed ending base")
    if np.linalg.norm(np.cross(base_start, base_end)) > GEOM_TOL * start_width * end_width:
        raise ValueError("Trapezoid bases must be parallel")
    if np.dot(base_start, base_end) <= 0:
        raise ValueError("Trapezoid bases must point in the same direction")
    normal = np.cross(base_start, leg1)
    normal_length = np.linalg.norm(normal)
    if normal_length <= GEOM_TOL * start_width * length1:
        raise ValueError("Trapezoid has zero area")
    if abs(np.dot(d - a, normal)) > GEOM_TOL * normal_length * max(1.0, np.linalg.norm(d - a)):
        raise ValueError("Trapezoid vertices must be coplanar")
    unit_normal = normal / normal_length
    side_b = np.dot(np.cross(base_start, b - a), unit_normal)
    side_d = np.dot(np.cross(base_start, d - a), unit_normal)
    if min(side_b, side_d) <= GEOM_TOL * start_width * length1:
        raise ValueError("Trapezoid vertices form an invalid or folded shape")
    return float(length1), float(max(start_width, end_width))


def project_trapezoid(M, a, b, c, d):
    leg_length, max_width = validate_trapezoid(a, b, c, d)
    return render_rows(M, a, c, direction(a, b), direction(c, d),
                       leg_length, max_width)


def make_frame(E, scale_max):
    if scale_max <= 0:
        return np.zeros(E.shape, dtype=np.uint8)
    return np.clip(E.astype(np.float64) / scale_max * 255, 0, 255).astype(np.uint8)


def make_error_frame(height, width):
    frame = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        x = round(y * (width - 1) / max(1, height - 1))
        frame[y, x] = 255
        frame[y, width - 1 - x] = 255
    frame[:min(3, height), :] = 255
    return frame


def save_video(projections, filename, fps=30, preview=False):
    if not projections:
        raise ValueError("No projections to save")
    if not isinstance(fps, int) or fps <= 0:
        raise ValueError("FPS must be a positive integer")
    valid = [E for E in projections if E is not None]
    scale_max = max((float(np.max(E)) for E in valid), default=0.0)
    height = max(32, *(E.shape[0] for E in valid))
    width = max(32, *(E.shape[1] for E in valid))
    scale = max(1, math.ceil(256 / max(height, width))) if preview else 1
    video_height = height * scale
    video_width = width * scale
    video_height += video_height % 2
    video_width += video_width % 2
    output = Path(filename)
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output must have an .mp4 extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temporary MP4 so a failed encode does not destroy a previous output.
    fd, temporary = tempfile.mkstemp(prefix=".projection-", suffix=".mp4", dir=output.parent)
    os.close(fd)
    try:
        with imageio.get_writer(temporary, fps=fps, codec="libx264",
                                pixelformat="yuv420p", macro_block_size=1) as writer:
            for E in projections:
                canvas = np.zeros((height, width), dtype=np.uint8)
                if E is None:
                    canvas = make_error_frame(height, width)
                else:
                    frame = make_frame(E, scale_max)
                    top = (height - frame.shape[0]) // 2
                    left = (width - frame.shape[1]) // 2
                    canvas[top:top + frame.shape[0], left:left + frame.shape[1]] = frame
                if preview:
                    canvas = np.repeat(np.repeat(canvas, scale, axis=0), scale, axis=1)
                padded = np.zeros((video_height, video_width), dtype=np.uint8)
                padded[:canvas.shape[0], :canvas.shape[1]] = canvas
                for _ in range(fps if preview else 1):
                    writer.append_data(padded)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Video saved:", filename)


def test_projection():
    M = np.zeros((3, 3, 3), dtype=np.uint8)
    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10 * x + 3 * y + z
    triangle = project_triangle(M, (0, 0, 0), (2, 0, 0), (0, 2, 0))
    np.testing.assert_array_equal(triangle, np.array([[0, 10, 3, 0], [20, 13, 13, 6]], dtype=np.uint8))
    rectangle = project_trapezoid(M, (0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0))
    np.testing.assert_array_equal(rectangle, np.array([[10, 13, 16], [20, 23, 26]], dtype=np.uint8))
    assert sample_nearest(M, (-1, 0, 0)) == 0
    try:
        project_triangle(M, (0, 0, 0), (2, 0, 0), (0, 1, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("Non-isosceles triangle was accepted")
    validate_trapezoid((200, 0, 0), (200, 0, 500), (200, 400, 0), (200, 400, 500))
    validate_trapezoid((200, 50, 0), (200, 0, 500), (200, 350, 0), (200, 400, 500))
    try:
        validate_trapezoid((0, 0, 0), (0, 2, 0), (4, 0, 0), (3, 2, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("Trapezoid with a longer first base was accepted")
    with tempfile.TemporaryDirectory() as folder:
        csv_path = Path(folder) / "lecturer.csv"
        csv_path.write_text(
            "Number of Points (3 or 4),x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4\n"
            "3,200,200,0,0,200,400,400,200,400\n"
            "4,200,0,0,200,0,500,200,400,0,200,400,500\n"
            "3,200,200,-30,-50,200,400,400,250,400\n"
            "4,200,50,0,200,0,500,200,350,0,200,400,500\n",
            encoding="utf-8"
        )
        entries = read_csv(csv_path)
        assert len(entries) == 4
        assert [len(points) for _, points, err in entries if err is None] == [3, 4, 3, 4]
        assert entries[2][1][0][2] == -30.0
    print("All basic projection tests passed")


def test_performance():
    M = np.zeros((500, 500, 500), dtype=np.uint8)
    a, b, c = (0, 0, 0), (400, 0, 0), (0, 400, 0)
    project_triangle(M, a, b, c)  # JIT warm-up
    repetitions = 10
    start = time.perf_counter()
    for _ in range(repetitions):
        project_triangle(M, a, b, c)
    elapsed = time.perf_counter() - start
    print("Volume shape:", M.shape)
    print("Number of projections:", repetitions)
    print("Average seconds per projection:", round(elapsed / repetitions, 5))
    print("Projection FPS:", round(repetitions / elapsed, 2))
    print("Note: excludes NRRD loading, MP4 encoding and compilation warm-up")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3:
        print("Usage: python Ex0.py file.nrrd file.csv file.mp4")
        return 2
    volume_filename, csv_filename, video_filename = args
    if Path(video_filename).resolve() in (Path(volume_filename).resolve(), Path(csv_filename).resolve()):
        raise ValueError("Output video must not overwrite an input file")
    if nrrd is None:
        raise RuntimeError("pynrrd is required: python -m pip install -r requirements.txt")
    M, _ = nrrd.read(volume_filename)
    M = prepare_volume(M)
    shapes = read_csv(csv_filename)
    print("Volume shape:", M.shape)
    print("Number of CSV entries:", len(shapes))
    projections = []
    for index, (line_number, points, error) in enumerate(shapes, 1):
        if error is not None:
            print(f"CSV line {line_number}: {error}; adding error frame")
            projections.append(None)
            continue
        try:
            E = project_triangle(M, *points) if len(points) == 3 else project_trapezoid(M, *points)
            print(f"Projection {index}: shape={E.shape}, nonzero={np.count_nonzero(E)}")
            projections.append(E)
        except (ValueError, OverflowError, MemoryError) as exc:
            print(f"CSV line {line_number}: {exc}; adding error frame")
            projections.append(None)
    preview = video_filename.lower().endswith("preview.mp4")
    save_video(projections, video_filename, fps=30, preview=preview)
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2 and sys.argv[1] == "--test":
            test_projection()
        elif len(sys.argv) == 2 and sys.argv[1] == "--performance":
            test_performance()
        else:
            sys.exit(main())
    except (OSError, ValueError, RuntimeError, MemoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
