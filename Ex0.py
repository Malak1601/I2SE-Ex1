                # A visible red error frame, not a black projection.
                canvas[:, :, 0] = 120
                positions = np.linspace(0, width - 1, height).astype(int)
                canvas[np.arange(height), positions] = (255, 255, 255)
                canvas[np.arange(height), width - 1 - positions] = (255, 255, 255)
            else:
                frame = make_frame(E, scale_max)
                canvas[:frame.shape[0], :frame.shape[1]] = frame[:, :, None]
            if preview:
                canvas = np.repeat(np.repeat(canvas, scale, axis=0), scale, axis=1)
            padded = np.zeros((video_height, video_width, 3), dtype=np.uint8)
            padded[:canvas.shape[0], :canvas.shape[1]] = canvas
            for _ in range(fps if preview else 1):
                writer.append_data(padded)
    print("Video saved:", filename)


def test_projection():
    M = np.zeros((3, 3, 3), dtype=np.uint8)
    for x in range(3):
        for y in range(3):
            for z in range(3):
                M[x, y, z] = 10 * x + 3 * y + z
    triangle = project_triangle(M, (0, 0, 0), (2, 0, 0), (0, 2, 0))
    np.testing.assert_array_equal(triangle, [[0, 10, 3, 0], [20, 13, 13, 6]])
    print("Triangle projection:\n", triangle)
    rectangle = project_trapezoid(M, (0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0))
    np.testing.assert_array_equal(rectangle, [[10, 13, 16], [20, 23, 26]])
    print("Rectangle projection:\n", rectangle)
    M2 = np.zeros((5, 5, 3), dtype=np.uint8)
    for x in range(5):
        for y in range(5):
            M2[x, y, 0] = 10 * x + y
    trapezoid = project_trapezoid(M2, (1, 0, 0), (0, 2, 0), (4, 2, 0), (3, 0, 0))
    assert trapezoid.ndim == 2 and trapezoid.size > 0 and trapezoid.dtype == M2.dtype
    print("Trapezoid projection:\n", trapezoid)
    # Check boundary of the permitted geometric tolerance.
    project_triangle(M, (0, 0, 0), (2, 0, 0), (0, 2.0005, 0))
    try:
        project_triangle(M, (0, 0, 0), (2, 0, 0), (0, 2.002, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid triangle was accepted")
    try:
        validate_trapezoid((0, 0, 0), (1, 2, 0), (3, 2, 0), (4, 0, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("Trapezoid with decreasing base width was accepted")
    print("All basic projection tests passed")


def test_performance():
    M = np.zeros((500, 500, 500), dtype=np.uint8)
    a, b, c = (0, 0, 0), (400, 0, 0), (0, 400, 0)
    project_triangle(M, a, b, c)
    repetitions = 10
    start = time.perf_counter()
    for _ in range(repetitions):
        project_triangle(M, a, b, c)
    elapsed = time.perf_counter() - start
    print("Volume shape:", M.shape)
    print("Number of projections:", repetitions)
    print("Average time per projection:", round(elapsed / repetitions, 5), "seconds")
    print("Projection FPS:", round(repetitions / elapsed, 2))


def main():
    if len(sys.argv) != 4:
        print("Usage: python Ex0.py file.nrrd file.csv file.mp4")
        print("       python Ex0.py --test")
        print("       python Ex0.py --performance")
        return 1
    import nrrd
    volume_filename, csv_filename, video_filename = sys.argv[1:]
    M, _ = nrrd.read(volume_filename)
    if M.ndim != 3 or M.dtype.kind != "u" or M.dtype.itemsize not in (1, 2, 4):
        raise ValueError("NRRD must contain a 3D unsigned 8/16/32-bit volume")
    if any(size < 1 or size >= 1024 for size in M.shape):
        raise ValueError("Volume dimensions must be between 1 and 1023")
    shapes = read_csv(csv_filename)
    print("Volume shape:", M.shape)
    print("Number of shapes:", len(shapes))
    projections = []
    for index, points in enumerate(shapes, start=1):
        try:
            if isinstance(points, Exception):
                raise points
            if len(points) == 3:
                E = project_triangle(M, *points)
            else:
                E = project_trapezoid(M, *points)
            print(f"Projection {index}: shape={E.shape}")
        except ValueError as exc:
            print(f"Projection {index}: ERROR: {exc}")
            E = None
        projections.append(E)
    preview = video_filename.lower().endswith("preview.mp4")
    save_video(projections, video_filename, fps=30, preview=preview)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        test_projection()
    elif len(sys.argv) == 2 and sys.argv[1] == "--performance":
        test_performance()
    else:
        sys.exit(main())
