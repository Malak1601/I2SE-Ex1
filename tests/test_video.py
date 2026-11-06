
import numpy as np
import imageio.v2 as imageio

from Ex0 import make_frame, make_error_frame, save_video


def test_grayscale_conversion():
    E = np.array([[0, 50, 100]], dtype=np.uint16)

    frame = make_frame(E, 100)

    expected = np.array([[0, 127, 255]], dtype=np.uint8)

    np.testing.assert_array_equal(frame, expected)


def test_zero_intensity():
    E = np.zeros((4, 4), dtype=np.uint8)

    frame = make_frame(E, 0)

    assert frame.dtype == np.uint8
    assert np.all(frame == 0)


def test_error_frame():
    frame = make_error_frame(64, 64)

    assert frame.shape == (64, 64)
    assert frame.dtype == np.uint8
    assert frame[0, 0] == 255
    assert frame[0, 63] == 255
    assert frame[32, 32] == 255 or frame[32, 31] == 255


def test_mp4_creation(tmp_path):
    output = tmp_path / "output.mp4"

    projections = [
        np.full((32, 32), 100, dtype=np.uint8),
        np.full((32, 32), 200, dtype=np.uint8),
    ]

    save_video(projections, str(output))

    assert output.exists()
    assert output.stat().st_size > 0


def test_video_frame_count_and_order(tmp_path):
    output = tmp_path / "ordered.mp4"

    projections = [
        np.full((32, 32), 50, dtype=np.uint8),
        np.full((32, 32), 200, dtype=np.uint8),
    ]

    save_video(projections, str(output))

    reader = imageio.get_reader(str(output))

    try:
        frames = [reader.get_data(i) for i in range(2)]
        assert reader.count_frames() == 2
    finally:
        reader.close()

    first_mean = np.mean(frames[0])
    second_mean = np.mean(frames[1])

    assert first_mean < second_mean


def test_invalid_plane_error_frame_in_video(tmp_path):
    output = tmp_path / "with_error.mp4"

    projections = [
        np.full((32, 32), 100, dtype=np.uint8),
        None,
        np.full((32, 32), 200, dtype=np.uint8),
    ]

    save_video(projections, str(output))

    reader = imageio.get_reader(str(output))

    try:
        error_frame = reader.get_data(1)
        assert reader.count_frames() == 3
    finally:
        reader.close()

    assert np.mean(error_frame[0]) > 100
    assert np.max(error_frame) > 200


def test_different_projection_sizes(tmp_path):
    output = tmp_path / "different_sizes.mp4"

    projections = [
        np.ones((20, 30), dtype=np.uint8) * 100,
        np.ones((40, 50), dtype=np.uint8) * 200,
    ]

    save_video(projections, str(output))

    reader = imageio.get_reader(str(output))

    try:
        frame = reader.get_data(0)
    finally:
        reader.close()

    assert frame.shape[0] == 40
    assert frame.shape[1] == 50


def test_preview_video(tmp_path):
    output = tmp_path / "preview.mp4"

    projections = [
        np.ones((16, 16), dtype=np.uint8) * 100
    ]

    save_video(
        projections,
        str(output),
        fps=30,
        preview=True
    )

    reader = imageio.get_reader(str(output))

    try:
        first_frame = reader.get_data(0)
        assert reader.count_frames() == 30
    finally:
        reader.close()

    assert first_frame.shape[0] >= 256
    assert first_frame.shape[1] >= 256