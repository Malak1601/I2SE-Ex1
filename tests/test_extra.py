
import csv
import os
import tempfile

import numpy as np

from Ex0 import (
    project_triangle,
    project_trapezoid,
    validate_trapezoid,
    sample_nearest,
    read_csv,
    make_error_frame,
)


def expect_value_error(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError("Expected ValueError was not raised")


def test_constant_volume():
    M = np.full((5, 5, 5), 100, dtype=np.uint8)

    E = project_triangle(
        M, (0, 0, 0), (4, 0, 0), (0, 4, 0)
    )

    assert E.ndim == 2
    assert E.dtype == np.uint8
    assert np.any(E == 100)
    assert np.all((E == 0) | (E == 100))

    print("Constant volume test passed")


def test_known_values():
    M = np.zeros((3, 3, 3), dtype=np.uint8)

    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10*x + 3*y + z

    E = project_triangle(
        M, (0, 0, 0), (2, 0, 0), (0, 2, 0)
    )

    expected = np.array([
        [0, 10, 3, 0],
        [20, 13, 13, 6]
    ], dtype=np.uint8)

    np.testing.assert_array_equal(E, expected)
    print("Known voxel values test passed")


def test_outside_volume():
    M = np.full((5, 5, 5), 100, dtype=np.uint8)

    assert sample_nearest(M, (-2, 0, 0)) == 0
    assert sample_nearest(M, (5, 0, 0)) == 0
    assert sample_nearest(M, (0, 0, 0)) == 100
    assert sample_nearest(M, (4, 4, 4)) == 100

    print("Volume boundaries test passed")


def test_invalid_triangles():
    M = np.zeros((5, 5, 5), dtype=np.uint8)

    expect_value_error(
        project_triangle,
        M, (0, 0, 0), (4, 0, 0), (0, 2, 0)
    )

    expect_value_error(
        project_triangle,
        M, (0, 0, 0), (2, 0, 0), (-2, 0, 0)
    )

    expect_value_error(
        project_triangle,
        M, (0, 0, 0), (0, 0, 0), (0, 0, 0)
    )

    print("Invalid triangles test passed")


def test_triangle_tolerance():
    M = np.zeros((5, 5, 5), dtype=np.uint8)

    E = project_triangle(
        M, (0, 0, 0), (2, 0, 0), (0, 2.0005, 0)
    )

    assert E.ndim == 2

    expect_value_error(
        project_triangle,
        M, (0, 0, 0), (2, 0, 0), (0, 2.002, 0)
    )

    print("Triangle tolerance test passed")


def test_valid_trapezoid():
    M = np.full((5, 5, 5), 100, dtype=np.uint8)

    # Lecturer order: a,b and c,d are the legs.
    E = project_trapezoid(
        M,
        (1, 0, 0),
        (0, 2, 0),
        (3, 0, 0),
        (4, 2, 0)
    )

    assert E.ndim == 2
    assert E.size > 0
    assert E.dtype == M.dtype
    assert np.any(E == 100)

    print("Valid trapezoid test passed")


def test_rectangle():
    M = np.full((5, 5, 5), 100, dtype=np.uint8)

    E = project_trapezoid(
        M,
        (0, 0, 0),
        (2, 0, 0),
        (0, 2, 0),
        (2, 2, 0)
    )

    assert E.shape == (2, 3)
    assert np.all(E == 100)

    print("Rectangle test passed")


def test_lecturer_trapezoids():
    leg, width = validate_trapezoid(
        (200, 0, 0),
        (200, 0, 500),
        (200, 400, 0),
        (200, 400, 500)
    )

    assert abs(leg - 500) < 1e-8
    assert abs(width - 400) < 1e-8

    leg, width = validate_trapezoid(
        (200, 50, 0),
        (200, 0, 500),
        (200, 350, 0),
        (200, 400, 500)
    )

    assert abs(width - 400) < 1e-8
    assert leg > 500

    print("Lecturer trapezoids test passed")


def test_invalid_trapezoids():
    # Unequal legs
    expect_value_error(
        validate_trapezoid,
        (0, 0, 0),
        (4, 0, 0),
        (0, 3, 0),
        (2, 3, 0)
    )

    # Crossing legs
    expect_value_error(
        validate_trapezoid,
        (0, 0, 0),
        (2, 2, 0),
        (2, 0, 0),
        (0, 2, 0)
    )

    # Non-coplanar points
    expect_value_error(
        validate_trapezoid,
        (0, 0, 0),
        (2, 0, 0),
        (0, 2, 0),
        (2, 2, 1)
    )

    # Zero-length base
    expect_value_error(
        validate_trapezoid,
        (0, 0, 0),
        (2, 0, 0),
        (0, 0, 0),
        (2, 0, 0)
    )

    print("Invalid trapezoids test passed")


def test_csv_recovery():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "planes.csv")

        rows = [
            [0, 0, 0, 2, 0, 0, 0, 2, 0],
            ["invalid", 1, 2],
            [0, 0, 0, 2, 0, 0, 0, 2, 0, 2, 2, 0],
        ]

        with open(filename, "w", newline="") as file:
            csv.writer(file).writerows(rows)

        shapes = read_csv(filename)

        assert len(shapes) == 3
        assert shapes[0][1] is not None
        assert shapes[0][2] is None
        assert shapes[1][1] is None
        assert shapes[1][2] is not None
        assert shapes[2][1] is not None
        assert shapes[2][2] is None

    print("CSV error recovery test passed")


def test_lecturer_csv_format():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "lecturer.csv")

        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Number of Points (3 or 4)",
                "x1", "y1", "z1",
                "x2", "y2", "z2",
                "x3", "y3", "z3",
                "x4", "y4", "z4"
            ])

            writer.writerow([
                3, 0, 0, 0, 2, 0, 0, 0, 2, 0,
                "", "", ""
            ])

            writer.writerow([
                4, 0, 0, 0, 2, 0, 0,
                0, 2, 0, 2, 2, 0
            ])

        shapes = read_csv(filename)

        assert len(shapes) == 2
        assert len(shapes[0][1]) == 3
        assert len(shapes[1][1]) == 4
        assert all(error is None for _, _, error in shapes)

    print("Lecturer CSV format test passed")


def test_error_frame():
    frame = make_error_frame(64, 64)

    assert frame.ndim == 2
    assert frame.dtype == np.uint8
    assert frame.shape == (64, 64)
    assert np.any(frame == 255)
    assert np.any(frame == 0)

    print("Error frame test passed")


def run_all_tests():
    test_constant_volume()
    test_known_values()
    test_outside_volume()
    test_invalid_triangles()
    test_triangle_tolerance()
    test_valid_trapezoid()
    test_rectangle()
    test_lecturer_trapezoids()
    test_invalid_trapezoids()
    test_csv_recovery()
    test_lecturer_csv_format()
    test_error_frame()

    print("\nAll extra tests passed!")


if __name__ == "__main__":
    run_all_tests()
