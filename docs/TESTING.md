# Testing Strategy

## 1. Purpose

Testing evaluates the correctness, robustness, and reproducibility of the 3D-to-2D plane projection program.

The tests cover geometric validation, CSV parsing, voxel sampling, projection values, supported volume data types, MP4 generation, and error recovery.

Performance is evaluated separately from functional correctness.

## 2. Automated Testing

The project uses `pytest` and a built-in test mode in `Ex0.py`.

| Test file | Main coverage |
|---|---|
| `tests/test_csv.py` | CSV parsing and malformed entries |
| `tests/test_geometry.py` | Triangle and trapezoid geometry |
| `tests/test_projection.py` | Known-value projections and voxel sampling |
| `tests/test_video.py` | Video generation, frame order, and error frames |
| `tests/test_extra.py` | Additional geometry, boundary, and input cases |
| `tests/test_lecturer_requirements.py` | Additional checks based on lecturer requirements |

Run the complete suite from the project root:

```bash
python -m pytest -q
```

**Recorded result:** 52 tests passed on the corrected implementation. One local run completed in 6.70 seconds; execution time may vary by environment.

Built-in tests can also be executed:

```bash
python Ex0.py --test
```

### 2.1 Geometry Tests

The geometry tests cover:

- Valid isosceles triangles.
- Triangles with unequal required sides.
- Collinear or degenerate triangles.
- Valid isosceles trapezoids.
- Rectangles.
- Trapezoids with unequal legs.
- Invalid trapezoid configurations.
- Geometric tolerance conditions.

The required length-comparison tolerance is `0.001`.

Passing the automated tests demonstrates correctness for the tested cases, not exhaustive verification of every possible geometry.

### 2.2 CSV Input Tests

The CSV tests cover:

- Coordinate-only triangle rows.
- Coordinate-only trapezoid rows.
- Count-prefixed entries in the lecturer's CSV format.
- Invalid coordinate counts.
- Missing or nonnumeric values.
- Non-finite coordinates.
- Empty rows.
- Error handling and preservation of CSV entry order.

Malformed populated rows are retained as error entries so the demo can generate error frames rather than silently removing their positions.

### 2.3 Projection and Boundary Tests

Small synthetic 3D arrays with known voxel values are used to compare computed projection matrices with expected results.

The tests cover:

- Nearest-neighbor sampling.
- Out-of-volume positions producing zero.
- Expected values for selected triangles and trapezoids.
- Different plane orientations.
- Preservation of integer data types.
- Supported volume dimensions and data types.

After the correction to integer-step row sampling, two expected-value tests were updated to match the corrected convention.

In both cases, the final pixel of the second row changed from `6` to `0`, while the remaining values were unchanged.

These expectations should be evaluated against the documented sampling rule rather than considered correct solely because the tests pass.

### 2.4 Video Tests

Video tests cover:

- MP4 generation.
- Grayscale conversion.
- Handling zero-intensity projections.
- Error-frame generation.
- Frame order and placement.
- Different projection dimensions.
- Preview output.

Normal mode is intended to produce one frame per processed nonempty CSV entry.

Preview mode may enlarge or repeat frames for visual inspection.

## 3. Small End-to-End Demonstration

The reproducible demonstration uses:

```bash
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
```

The recorded execution produced:

| Measurement | Result |
|---|---|
| Volume dimensions | `16 × 16 × 16` |
| CSV plane entries | 2 |
| Projection 1 shape | `(10, 16)` |
| Projection 1 nonzero values | 87 |
| Projection 2 shape | `(10, 11)` |
| Projection 2 nonzero values | 110 |
| Output | `results/demo_small.mp4` |

The first video frame was extracted into `results/demo_check.png` and visually inspected.

It contained a visible grayscale projection on a black background.

This verifies a complete local NRRD-to-CSV-to-MP4 workflow on a small example. It does not replace testing on larger datasets.

## 4. Supplementary Edge-Case Experiments

Earlier development experiments used selected cases from `edge_cases.csv` and a constant-valued `uint8` volume of dimensions `200 × 180 × 160`, with voxel value `100`.

These observations were recorded for an earlier implementation and have not been independently rerun against the corrected final `Ex0.py`.

They are therefore presented as historical development observations, not final-version regression results.

### 4.1 Recorded Triangle Observations

| Case | Earlier observed result | Description |
|---|---|---|
| 4 | Accepted | Nonempty projection |
| 5 | Accepted | Nonempty projection |
| 6 | Accepted | Equal required side lengths; some coordinates outside the test volume |
| 7 | Rejected | Invalid triangle geometry |
| 12 | Rejected | Collinear vertices |
| 13 | Rejected | Invalid triangle geometry |

For case 6, geometric validity and volume boundaries are separate considerations. A geometrically valid plane may contain sampling positions outside the volume, which must produce zero.

### 4.2 Recorded Trapezoid Observations

| Case | Earlier observed result | Description |
|---|---|---|
| 1 | Accepted | Projection generated |
| 2 | Accepted | Projection generated |
| 3 | Accepted | Projection generated |
| 14 | Rejected | Unequal leg lengths |
| 15 | Rejected | Invalid base configuration |

### 4.3 Recorded Integer Data Type Experiments

| Voxel type | Earlier observed result |
|---|---|
| `uint8` | Projection generated |
| `uint16` | Projection generated |
| `uint32` | Projection generated |

The earlier experiments recorded 72 nonzero pixels for each type using a valid triangle.

These experiments tested projection functions directly rather than the complete CSV-to-MP4 workflow.

## 5. Performance Testing

Run:

```bash
python Ex0.py --performance
```

The latest recorded benchmark on the corrected implementation was:

| Measurement | Recorded value |
|---|---:|
| Volume dimensions | `500 × 500 × 500` |
| Voxel type | `uint8` |
| Measured projections | 10, after warm-up |
| Average projection time | Approximately 0.00141 s |
| Projection computation rate | 710.91 FPS |
| Lecturer's minimum | Above 30 FPS |
| Lecturer's expected target | Approximately 100 FPS |

This measurement covers projection computation only.

It excludes NRRD loading, MP4 encoding, and initial Numba JIT compilation. It is not a measurement of end-to-end video throughput.

Results depend on hardware and plane geometry.

See [Performance Experiment](EXPERIMENT.md) for details.

## 6. Final Submission Verification

Before submission, confirm that:

1. `python -m pytest -q` passes on the submitted version.
2. `python Ex0.py --test` completes successfully.
3. The small NRRD/CSV example generates a readable MP4.
4. Normal-mode MP4 frame counts and order match the processed CSV entries.
5. The lecturer's geometric requirements are implemented, including trapezoid base ordering.
6. The documented image-size safeguard does not unintentionally reject required assignment inputs.
7. The README, SRS, algorithm description, experiment report, and repository paths agree with the submitted files.

## 7. Conclusion

The recorded corrected implementation passed 52 automated tests.

The small end-to-end demonstration generated a visible projection, and the computation-only benchmark exceeded the assignment's stated FPS targets for the tested configuration.

Supplementary edge-case observations from earlier development remain useful historical evidence but require rerunning before being claimed as final-version results.
