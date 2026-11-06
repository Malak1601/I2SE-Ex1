
import pytest
import numpy as np

from Ex0 import project_triangle, validate_trapezoid, project_trapezoid


def test_valid_triangle():
    M = np.ones((5, 5, 5), dtype=np.uint8)
    E = project_triangle(
        M, (0, 0, 0), (4, 0, 0), (0, 4, 0)
    )
    assert E.ndim == 2
    assert E.dtype == M.dtype
    assert np.count_nonzero(E) > 0


def test_invalid_triangle_unequal_sides():
    M = np.ones((5, 5, 5), dtype=np.uint8)
    with pytest.raises(ValueError):
        project_triangle(
            M, (0, 0, 0), (4, 0, 0), (0, 3, 0)
        )


def test_invalid_triangle_collinear():
    M = np.ones((5, 5, 5), dtype=np.uint8)
    with pytest.raises(ValueError):
        project_triangle(
            M, (0, 0, 0), (2, 0, 0), (-2, 0, 0)
        )


def test_valid_rectangle():
    M = np.ones((5, 5, 5), dtype=np.uint8)
    E = project_trapezoid(
        M,
        (0, 0, 0), (4, 0, 0),
        (0, 3, 0), (4, 3, 0)
    )
    assert E.ndim == 2
    assert np.count_nonzero(E) > 0


def test_valid_isosceles_trapezoid():
    leg, width = validate_trapezoid(
        (1, 0, 0), (0, 3, 0),
        (3, 0, 0), (4, 3, 0)
    )
    assert leg > 0
    assert width == pytest.approx(4)


def test_invalid_trapezoid_longer_first_base():
    with pytest.raises(ValueError):
        validate_trapezoid(
            (0, 0, 0), (1, 3, 0),
            (4, 0, 0), (3, 3, 0)
        )


def test_invalid_trapezoid_unequal_legs():
    with pytest.raises(ValueError):
        validate_trapezoid(
            (0, 0, 0), (0, 3, 0),
            (3, 0, 0), (4, 3, 0)
        )


def test_invalid_trapezoid_non_coplanar():
    with pytest.raises(ValueError):
        validate_trapezoid(
            (0, 0, 0), (0, 3, 0),
            (3, 0, 0), (3, 3, 1)
        )
