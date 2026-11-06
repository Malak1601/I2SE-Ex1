
import pytest

from Ex0 import read_csv


def write_csv(tmp_path, content):
    path = tmp_path / "planes.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_triangle_csv(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,2,0,0,0,2,0\n"
    )

    entries = read_csv(path)

    assert len(entries) == 1
    assert len(entries[0][1]) == 3
    assert entries[0][2] is None


def test_trapezoid_csv(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,2,0,0,0,2,0,2,2,0\n"
    )

    entries = read_csv(path)

    assert len(entries) == 1
    assert len(entries[0][1]) == 4


def test_lecturer_csv_format(tmp_path):
    path = write_csv(
        tmp_path,
        "Number of Points (3 or 4),x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4\n"
        "3,0,0,0,2,0,0,0,2,0,,,\n"
        "4,0,0,0,2,0,0,0,2,0,2,2,0\n"
    )

    entries = read_csv(path)

    assert len(entries) == 2
    assert len(entries[0][1]) == 3
    assert len(entries[1][1]) == 4


def test_invalid_csv_row(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,2,0,0,0,2,0\n"
        "invalid,row\n"
        "0,0,0,2,0,0,0,2,0\n"
    )

    entries = read_csv(path)

    assert len(entries) == 3
    assert entries[1][1] is None
    assert entries[1][2] is not None


def test_non_numeric_coordinates(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,abc,0,0,0,2,0\n"
    )

    entries = read_csv(path)

    assert entries[0][1] is None
    assert entries[0][2] is not None


def test_nan_coordinates(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,nan,0,0,0,2,0\n"
    )

    entries = read_csv(path)

    assert entries[0][1] is None
    assert entries[0][2] is not None


def test_blank_lines_are_ignored(tmp_path):
    path = write_csv(
        tmp_path,
        "\n"
        "0,0,0,2,0,0,0,2,0\n"
        "\n"
    )

    entries = read_csv(path)

    assert len(entries) == 1
    assert entries[0][0] == 2


def test_empty_csv_rejected(tmp_path):
    path = write_csv(tmp_path, "")

    with pytest.raises(ValueError):
        read_csv(path)


def test_csv_preserves_order(tmp_path):
    path = write_csv(
        tmp_path,
        "0,0,0,2,0,0,0,2,0\n"
        "invalid,row\n"
        "0,0,0,3,0,0,0,3,0\n"
    )

    entries = read_csv(path)

    assert [entry[0] for entry in entries] == [1, 2, 3]
    assert entries[0][1] is not None
    assert entries[1][1] is None
    assert entries[2][1] is not None
