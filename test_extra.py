
import numpy as np

from Ex0 import (
    project_triangle,
    project_trapezoid,
    sample_nearest
)


def test_extra():
    M = np.full((5, 5, 5), 100, dtype=np.uint8)

    # Test 1: Constant volume
    E = project_triangle(
        M,
        (0, 0, 0),
        (4, 0, 0),
        (0, 4, 0)
    )

    assert E.ndim == 2
    assert np.all((E == 0) | (E == 100))
    print("Constant volume test passed")

    # Test 2: Outside volume
    assert sample_nearest(M, (-2, 0, 0)) == 0
    print("Outside volume test passed")

    # Test 3: Invalid triangle
    try:
        project_triangle(
            M,
            (0, 0, 0),
            (4, 0, 0),
            (0, 2, 0)
        )
    except ValueError:
        print("Invalid triangle test passed")
    else:
        raise AssertionError("Invalid triangle was accepted")

    # Test 4: Invalid trapezoid
    try:
        project_trapezoid(
            M,
            (0, 0, 0),
            (4, 0, 0),
            (4, 3, 0),
            (0, 2, 0)
        )
    except ValueError:
        print("Invalid trapezoid test passed")
    else:
        raise AssertionError("Invalid trapezoid was accepted")

    print("All extra tests passed")

def test_crossed_trapezoid():
    from Ex0 import validate_trapezoid

    try:
        validate_trapezoid(
            (0, 0, 0),
            (2, 2, 0),
            (0, 2, 0),
            (2, 0, 0)
        )
    except ValueError:
        print("Crossed trapezoid test passed")
    else:
        raise AssertionError(
            "Crossed trapezoid should be rejected"
        )

if __name__ == "__main__":
    test_extra()

if __name__ == "__main__":
    test_extra()
    test_crossed_trapezoid()