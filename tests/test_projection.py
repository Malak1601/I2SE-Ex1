
import numpy as np
import pytest

from Ex0 import (
    project_triangle,
    project_trapezoid,
    sample_nearest,
    prepare_volume,
)


def test_nearest_neighbor():
    M = np.arange(27, dtype=np.uint8).reshape(3, 3, 3)

    assert sample_nearest(M, (1.2, 1, 1)) == M[1, 1, 1]
    assert sample_nearest(M, (1.6, 1, 1)) == M[2, 1, 1]


def test_outside_volume():
    M = np.ones((3, 3, 3), dtype=np.uint8)

    assert sample_nearest(M, (-1, 0, 0)) == 0
    assert sample_nearest(M, (3, 0, 0)) == 0


def test_triangle_expected_values():
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
        [20, 13, 13, 0]
    ], dtype=np.uint8)

    np.testing.assert_array_equal(E, expected)


def test_rectangle_expected_values():
    M = np.zeros((3, 3, 3), dtype=np.uint8)

    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10*x + 3*y + z

    E = project_trapezoid(
        M,
        (0, 0, 0), (2, 0, 0),
        (0, 2, 0), (2, 2, 0)
    )

    expected = np.array([
        [10, 13, 16],
        [20, 23, 26]
    ], dtype=np.uint8)

    np.testing.assert_array_equal(E, expected)


def test_output_dtype():
    M = np.ones((5, 5, 5), dtype=np.uint16)

    E = project_triangle(
        M, (0, 0, 0), (4, 0, 0), (0, 4, 0)
    )

    assert E.dtype == np.uint16


def test_outside_projection_is_zero():
    M = np.ones((3, 3, 3), dtype=np.uint8)

    E = project_triangle(
        M, (10, 10, 10), (12, 10, 10), (10, 12, 10)
    )

    assert np.all(E == 0)


def test_invalid_volume_dimensions():
    with pytest.raises(ValueError):
        prepare_volume(np.zeros((3, 3), dtype=np.uint8))


def test_signed_volume_with_negative_values():
    M = np.array([[[-1, 2]]], dtype=np.int16)

    with pytest.raises(ValueError):
        prepare_volume(M)
