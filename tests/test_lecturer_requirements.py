"""Focused regression tests for requirements clarified in the lectures.

Run: python test_lecturer_requirements.py
Does not alter Ex0.py or the existing test_extra.py.
"""

import math
import numpy as np
from Ex0 import (
    sample_nearest,
    project_triangle,
    project_trapezoid,
    validate_trapezoid,
    prepare_volume,
)


def check(name, action):
    try:
        action()
    except Exception as exc:
        print(f"FAIL: {name}: {type(exc).__name__}: {exc}")
        raise
    print(f"PASS: {name}")


def raises_value_error(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError("Expected ValueError, but none was raised")


def test_nearest_half_up():
    vol = np.arange(27, dtype=np.uint8).reshape((3, 3, 3))
    assert int(sample_nearest(vol, (0.5, 0.5, 0.5))) == int(vol[1, 1, 1])
    assert int(sample_nearest(vol, (0.4, 0.4, 0.4))) == int(vol[0, 0, 0])
    assert int(sample_nearest(vol, (1.5, 1.5, 1.5))) == int(vol[2, 2, 2])


def test_collinear_triangle():
    vol = np.zeros((5, 5, 5), dtype=np.uint8)
    raises_value_error(project_triangle, vol, (2, 2, 2), (3, 2, 2), (1, 2, 2))


def test_outside_valid_plane_zero():
    vol = np.full((5, 5, 5), 77, dtype=np.uint8)
    plane = project_triangle(vol, (20, 20, 20), (24, 20, 20), (20, 24, 20))
    assert plane.size > 0
    assert np.count_nonzero(plane) == 0


def test_exact_rectangle_pixels():
    vol = np.zeros((5, 5, 5), dtype=np.uint16)
    for x in range(5):
        for y in range(5):
            vol[x, y, :] = 100*x + 10*y
    image = project_trapezoid(vol, (0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0))
    expected = np.array([[100, 110, 120], [200, 210, 220]], dtype=np.uint16)
    np.testing.assert_array_equal(image, expected)


def test_oblique_rectangle_values():
    vol = np.zeros((6, 6, 6), dtype=np.uint16)
    for x in range(6):
        for y in range(6):
            for z in range(6):
                vol[x, y, z] = 100*x + 10*y + z
    # a->b and c->d are equal, tilted legs (both x and z change).
    image = project_trapezoid(vol, (0, 0, 0), (2, 0, 2), (0, 2, 0), (2, 2, 2))
    assert image.ndim == 2 and image.size > 0
    # Test each generated row against independent calculation of row endpoints.
    leg_length = math.sqrt(8)
    for row in range(image.shape[0]):
        step = min(row + 1, leg_length)
        x = step / math.sqrt(2)
        ix = math.floor(x + 0.5)
        iz = ix
        for column in range(3):
            expected = vol[ix, column, iz]
            assert image[row, column] == expected, (row, column, image[row, column], expected)


def test_reject_non_coplanar_trapezoid():
    raises_value_error(validate_trapezoid, (0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 1))


def test_volume_uint_types():
    for dtype in (np.uint8, np.uint16, np.uint32):
        vol = np.zeros((2, 2, 2), dtype=dtype)
        result = prepare_volume(vol)
        assert result.dtype == dtype


if __name__ == "__main__":
    tests = [
        ("rounding of half values", test_nearest_half_up),
        ("collinear triangle rejected", test_collinear_triangle),
        ("valid plane outside volume gives zeros", test_outside_valid_plane_zero),
        ("exact rectangle pixel values", test_exact_rectangle_pixels),
        ("oblique rectangle pixel values", test_oblique_rectangle_values),
        ("non-coplanar trapezoid rejected", test_reject_non_coplanar_trapezoid),
        ("unsigned volume types", test_volume_uint_types),
    ]
    for name, test in tests:
        check(name, test)
    print("\nAll lecturer-focused regression tests passed!")