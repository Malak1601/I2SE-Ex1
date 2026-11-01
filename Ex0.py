
import csv
import math
import sys
import time
import imageio.v2 as imageio
import nrrd
import numpy as np

EPS = 1e-8
LENGTH_TOLERANCE = 0.001


def distance(p1, p2):
    return math.dist(p1, p2)


def direction(p1, p2):
    length = distance(p1, p2)

    if length <= EPS:
        raise ValueError("Points must be different")

    return np.asarray(
        [(p2[i] - p1[i]) / length for i in range(3)],
        dtype=float
    )


def read_csv(filename):
    shapes = []

    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            if not row or all(not value.strip() for value in row):
                continue

            if len(row) not in (9, 12):
                raise ValueError(
                    f"CSV line {line_number}: expected 9 or 12 numbers"
                )

            try:
                values = [float(value.strip()) for value in row]
            except ValueError as exc:
                raise ValueError(
                    f"CSV line {line_number}: invalid coordinate"
                ) from exc

            if not all(math.isfinite(v) for v in values):
                raise ValueError("Coordinates must be finite")

            points = [
                tuple(values[i:i + 3])
                for i in range(0, len(values), 3)
            ]

            shapes.append(points)

    if not shapes:
        raise ValueError("CSV file is empty")

    return shapes


def sample_nearest(M, point):
    indices = tuple(
        math.floor(float(value) + 0.5)
        for value in point
    )

    if all(0 <= indices[i] < M.shape[i] for i in range(3)):
        return M[indices]

    return 0


def render_rows(M, start1, start2, vector1, vector2,
                leg_length, max_width):

    height = max(1, math.ceil(leg_length))
    width = max(1, math.ceil(max_width) + 1)

    E = np.zeros((height, width), dtype=M.dtype)

    start1 = np.asarray(start1, dtype=float)
    start2 = np.asarray(start2, dtype=float)
    vector1 = np.asarray(vector1, dtype=float)
    vector2 = np.asarray(vector2, dtype=float)

    for y in range(height):
        step = min(y + 1, leg_length)

        p1 = start1 + step * vector1
        p2 = start2 + step * vector2

        span = float(np.linalg.norm(p2 - p1))

        if span <= EPS:
            x = round(max_width / 2)

            if 0 <= x < width:
                E[y, x] = sample_nearest(M, p1)

            continue

        unit = (p2 - p1) / span
        count = math.ceil(span)

        offsets = np.minimum(
            np.arange(count + 1, dtype=float),
            span
        )

        points = p1 + offsets[:, None] * unit

        indices = np.floor(points + 0.5).astype(np.int64)

        xs = np.rint(
            (max_width - span) / 2 + offsets
        ).astype(np.int64)

        valid = (
            (xs >= 0) &
            (xs < width) &
            (indices[:, 0] >= 0) &
            (indices[:, 0] < M.shape[0]) &
            (indices[:, 1] >= 0) &
            (indices[:, 1] < M.shape[1]) &
            (indices[:, 2] >= 0) &
            (indices[:, 2] < M.shape[2])
        )

        valid_x = xs[valid]
        valid_indices = indices[valid]

        E[y, valid_x] = M[
            valid_indices[:, 0],
            valid_indices[:, 1],
            valid_indices[:, 2]
        ]

    return E



def project_triangle(M, a, b, c):
    dab = distance(a, b)
    dac = distance(a, c)

    if (
        dab <= EPS
        or dac <= EPS
        or abs(dab - dac) >= LENGTH_TOLERANCE
    ):
        raise ValueError(
            "Triangle must have two approximately equal nonzero sides"
        )

    ab = np.subtract(b, a)
    ac = np.subtract(c, a)

    if np.linalg.norm(np.cross(ab, ac)) <= EPS * dab * dac:
        raise ValueError("Triangle points must not be collinear")

    return render_rows(
        M,
        a,
        a,
        direction(a, b),
        direction(a, c),
        dab,
        distance(b, c)
    )




def validate_trapezoid(a, b, c, d):
    a, b, c, d = [
        np.asarray(point, dtype=float)
        for point in (a, b, c, d)
    ]

    left = b - a
    right = c - d
    top = d - a
    bottom = c - b

    leg = float(np.linalg.norm(left))
    right_leg = float(np.linalg.norm(right))
    top_len = float(np.linalg.norm(top))
    bottom_len = float(np.linalg.norm(bottom))

    if min(leg, right_leg, top_len, bottom_len) <= EPS:
        raise ValueError("Trapezoid edges must be nonzero")

    if not math.isclose(
        leg, right_leg, rel_tol=1e-7, abs_tol=EPS
    ):
        raise ValueError("Trapezoid legs must be equal")

    if np.linalg.norm(np.cross(top, bottom)) > (
        1e-7 * top_len * bottom_len
    ):
        raise ValueError("Trapezoid bases must be parallel")

    normal = np.cross(top, left)
    normal_length = float(np.linalg.norm(normal))

    if normal_length <= EPS * top_len * leg:
        raise ValueError("Trapezoid is degenerate")

    if abs(float(np.dot(c - a, normal))) > (
        1e-7 * normal_length *
        max(1.0, float(np.linalg.norm(c - a)))
    ):
        raise ValueError("Trapezoid points must be coplanar")

    n = normal / normal_length

    signed_b = float(np.dot(np.cross(top, b - a), n))
    signed_c = float(np.dot(np.cross(top, c - a), n))

    if signed_b <= EPS or signed_c <= EPS:
        raise ValueError("Invalid trapezoid vertex order")

    # Check that the two legs do not cross.
    # Project the points to the trapezoid's 2D plane.
    u = top / top_len
    v = np.cross(n, u)

    def to_2d(point):
        delta = point - a
        return np.array([
            np.dot(delta, u),
            np.dot(delta, v)
        ])

    A, B, C, D = [to_2d(p) for p in (a, b, c, d)]

    def orientation(p, q, r):
        return (
            (q[0] - p[0]) * (r[1] - p[1])
            - (q[1] - p[1]) * (r[0] - p[0])
        )

    # The legs are A-B and D-C.
    o1 = orientation(A, B, D)
    o2 = orientation(A, B, C)
    o3 = orientation(D, C, A)
    o4 = orientation(D, C, B)

    if o1 * o2 < 0 and o3 * o4 < 0:
        raise ValueError("Trapezoid legs must not cross")

    # Both bases must face the same direction
    # for the required vertex ordering.
    if float(np.dot(top, bottom)) <= EPS * top_len * bottom_len:
        raise ValueError("Invalid trapezoid base direction")

    return leg, max(top_len, bottom_len)


def project_trapezoid(M, a, b, c, d):
    leg, max_width = validate_trapezoid(a, b, c, d)

    return render_rows(
        M,
        a,
        d,
        direction(a, b),
        direction(d, c),
        leg,
        max_width
    )


def make_frame(E, scale_max):
    if scale_max <= 0:
        return np.zeros(E.shape, dtype=np.uint8)

    return np.clip(
        E.astype(np.float64) / scale_max * 255,
        0,
        255
    ).astype(np.uint8)


def save_video(projections, filename, fps=30, preview=False):
    if not projections:
        raise ValueError("No projections to save")

    scale_max = max(float(np.max(E)) for E in projections)

    height = max(E.shape[0] for E in projections)
    width = max(E.shape[1] for E in projections)

    # Enlarge tiny images only for preview
    scale = max(1, math.ceil(256 / max(height, width))) if preview else 1

    video_height = height * scale
    video_width = width * scale

    # Ensure even dimensions for H.264
    video_height += video_height % 2
    video_width += video_width % 2

    with imageio.get_writer(
        filename,
        fps=fps,
        codec="libx264",
        macro_block_size=1
    ) as writer:

        for E in projections:
            frame = make_frame(E, scale_max)

            canvas = np.zeros(
                (height, width),
                dtype=np.uint8
            )

            h, w = frame.shape
            canvas[:h, :w] = frame

            if preview:
                canvas = np.repeat(
                    np.repeat(canvas, scale, axis=0),
                    scale,
                    axis=1
                )

            padded = np.zeros(
                (video_height, video_width),
                dtype=np.uint8
            )

            padded[:canvas.shape[0], :canvas.shape[1]] = canvas

            # One second per image in preview mode
            repeats = fps if preview else 1

            for _ in range(repeats):
                writer.append_data(padded)

    print("Video saved:", filename)


def test_projection():
    M = np.zeros((3, 3, 3), dtype=np.uint8)

    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10 * x + 3 * y + z

    triangle = project_triangle(
        M,
        (0, 0, 0),
        (2, 0, 0),
        (0, 2, 0)
    )

    expected_triangle = np.array([
        [0, 10, 3, 0],
        [20, 13, 13, 6]
    ], dtype=np.uint8)

    print("Triangle projection:")
    print(triangle)

    np.testing.assert_array_equal(
        triangle,
        expected_triangle
    )

    rectangle = project_trapezoid(
        M,
        (0, 0, 0),
        (2, 0, 0),
        (2, 2, 0),
        (0, 2, 0)
    )

    expected_rectangle = np.array([
        [10, 13, 16],
        [20, 23, 26]
    ], dtype=np.uint8)

    print("Rectangle projection:")
    print(rectangle)

    np.testing.assert_array_equal(
        rectangle,
        expected_rectangle
    )

    M2 = np.zeros((5, 5, 3), dtype=np.uint8)

    for x in range(5):
        for y in range(5):
            M2[x, y, 0] = 10 * x + y

    trapezoid = project_trapezoid(
        M2,
        (1, 0, 0),
        (0, 2, 0),
        (4, 2, 0),
        (3, 0, 0)
    )

    print("Trapezoid projection:")
    print(trapezoid)

    assert trapezoid.ndim == 2
    assert trapezoid.size > 0
    assert trapezoid.dtype == M2.dtype

    print("Trapezoid basic test passed")
    print("All basic projection tests passed")


def test_performance():
    print("Starting performance test...")

    # Start with a manageable volume
    size = 500
    M = np.zeros((size, size, size), dtype=np.uint8)

    a = (0, 0, 0)
    b = (400, 0, 0)
    c = (0, 400, 0)

    # Warm-up
    project_triangle(M, a, b, c)

    repetitions = 10

    start = time.perf_counter()

    for _ in range(repetitions):
        project_triangle(M, a, b, c)

    end = time.perf_counter()

    total_time = end - start
    average_time = total_time / repetitions
    fps = repetitions / total_time

    print("Volume shape:", M.shape)
    print("Number of projections:", repetitions)
    print("Average time per projection:", round(average_time, 5), "seconds")
    print("Projection FPS:", round(fps, 2))

def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("python Ex0.py file.nrrd file.csv file.mp4")
        print("python Ex0.py --test")
        return

    volume_filename, csv_filename, video_filename = sys.argv[1:]

    M, header = nrrd.read(volume_filename)

    if (
        M.ndim != 3
        or M.dtype.kind != "u"
        or M.dtype.itemsize not in (1, 2, 4)
    ):
        raise ValueError(
            "NRRD must contain a 3D unsigned 8/16/32-bit volume"
        )

    if any(size < 1 or size >= 1024 for size in M.shape):
        raise ValueError(
            "Volume dimensions must be between 1 and 1023"
        )

    shapes = read_csv(csv_filename)

    print("Volume shape:", M.shape)
    print("Number of shapes:", len(shapes))

    projections = []

    for index, points in enumerate(shapes, start=1):
        if len(points) == 3:
            E = project_triangle(M, *points)
        else:
            E = project_trapezoid(M, *points)

        print(f"Projection {index}: shape={E.shape}")
        projections.append(E)

    # Preview is only for visual inspection
    preview = video_filename.lower().endswith("preview.mp4")

    save_video(
        projections,
        video_filename,
        fps=30,
        preview=preview
    )



if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        test_projection()

    elif len(sys.argv) == 2 and sys.argv[1] == "--performance":
        test_performance()

    else:
        main()
