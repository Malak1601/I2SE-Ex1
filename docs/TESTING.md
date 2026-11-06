# Testing Strategy

## 1. Purpose

The purpose of testing is to verify that the plane projection program is correct, stable, and capable of processing valid and invalid inputs.

The tests focus on geometry validation, voxel sampling, CSV parsing, projection results, and MP4 video generation.

## 2. Testing Approach

The project uses automated tests with `pytest`, together with built-in tests in `Ex0.py`.

The tests are organized into the following files:

| File | Purpose |
|---|---|
| `tests/test_csv.py` | CSV parsing and invalid input handling |
| `tests/test_geometry.py` | Triangle and trapezoid validation |
| `tests/test_projection.py` | Voxel sampling and projection correctness |
| `tests/test_video.py` | Video creation, frame order, and error frames |
| `tests/test_extra.py` | Additional geometry, sampling, and input tests |

## 3. Geometry Tests

The geometry tests verify that the program:

- Accepts valid isosceles triangles.
- Rejects triangles with unequal sides.
- Rejects collinear triangle vertices.
- Accepts valid isosceles trapezoids and rectangles.
- Rejects trapezoids with unequal legs.
- Rejects non-coplanar trapezoids.
- Rejects trapezoids whose starting base is longer than the ending base.

The lecturer's tolerance of `0.001` is used for comparing the lengths of equal sides or legs.

## 4. CSV Input Tests

The CSV tests verify:

- Three-point triangle definitions.
- Four-point trapezoid definitions.
- The lecturer's CSV format with a point-count column.
- Invalid or missing coordinate values.
- Non-numeric and non-finite coordinates.
- Empty rows.
- Preservation of the original order of plane definitions.

Invalid nonempty entries are retained so that the demo can generate an error frame rather than silently skipping them.

## 5. Projection Tests

Projection tests use small 3D matrices containing known voxel values.

They verify:

- Nearest-neighbor sampling.
- Zero values for positions outside the volume.
- Correct output values for selected triangles and rectangles.
- Preservation of the volume's integer data type in the projection matrix.
- Validation of volume dimensions and supported data types.

Using known voxel values makes it possible to compare the computed image with an expected matrix.

## 6. Video Tests

Video tests verify:

- Conversion of projection matrices to grayscale frames.
- Handling of zero-intensity projections.
- Creation of MP4 files.
- Preservation of frame count and order.
- Error-frame generation for invalid planes.
- Handling of projections with different image dimensions.
- Preview video generation.

The program uses a marked error frame for invalid plane definitions, while continuing to process subsequent valid entries.

## 7. Demo Testing

The required command-line interface is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The demo is intended to verify the complete workflow:

1. Read the 3D NRRD volume.
2. Read the CSV plane definitions.
3. Validate each plane.
4. Generate the corresponding 2D projection or error frame.
5. Save the frames in CSV order to an MP4 file.

The generated demonstration video is available at:

`results/output (5).mp4`

The demo should be checked to confirm that the number and order of frames match the input CSV entries.

## 8. Automated Test Execution

Run the complete test suite from the project directory:

```bash
python -m pytest tests/ -v
```

The recorded result was:

**45 passed in 6.89 seconds**

The built-in tests can also be executed with:

```bash
python Ex0.py --test
```

## 9. Performance Testing

Run the performance benchmark using:

```bash
python Ex0.py --performance
```

The recorded benchmark used a synthetic `500 × 500 × 500` unsigned 8-bit volume and 10 measured projections after a Numba warm-up.

The measured rate was **972.22 projection FPS**.

This measurement excludes NRRD loading, MP4 encoding, and initial JIT compilation.

More details are provided in `docs/EXPERIMENT.md`.

## 10. Conclusion

The automated tests cover the main functional requirements of the project, including geometry, CSV input, projection correctness, boundary handling, and video generation.

The recorded test run completed with all 45 tests passing.

The combination of automated tests, a command-line demo, and a performance experiment provides evidence for the correctness and efficiency of the implementation.
