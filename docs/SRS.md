# Software Requirements Specification (SRS)

## I2SE Ex1 — 3D Volume Plane Projection

### 1. Purpose and Scope

The program generates two-dimensional images by sampling planar regions of a three-dimensional volume. It reads a volume in NRRD format and a CSV file describing a sequence of planes, then writes the resulting projections to an MP4 video in CSV order.

The implementation is a command-line Python program, not a medical image viewer. It focuses on geometric correctness, predictable input handling, efficient sampling, testing, and maintainable code.

A graphical user interface and physical-space coordinate transformations are outside the scope.

### 2. Inputs and Outputs

#### 2.1 Inputs

- A three-dimensional NRRD volume with dimensions `1 <= sx, sy, sz < 1024`.
- Unsigned integer voxel types `uint8`, `uint16`, and `uint32`.
- A CSV file defining an isosceles triangle with three 3D points or an isosceles trapezoid with four 3D points.
- Coordinate-only CSV rows and count-prefixed rows (`3` or `4`), including the lecturer's header format.

The implementation additionally supports certain nonnegative signed integer volumes by converting them to an unsigned representation. This is an extension, not a required input type.

#### 2.2 Outputs

- An MP4 video containing one encoded frame per nonempty CSV plane entry in normal mode, preserving the original order.
- Diagnostic terminal output describing the input volume, processed projections, and recoverable errors.

The output video uses 8-bit grayscale frames. Higher-bit-depth projection values are mapped to 8-bit intensities for display. This does not change the source volume values used for sampling.

### 3. Functional Requirements

#### FR-01 — Volume Loading and Validation

The program shall load a three-dimensional NRRD volume, verify its dimensions and supported voxel type, and report fatal file or volume errors.

#### FR-02 — CSV Parsing

The program shall:

- Read three-point and four-point definitions in file order.
- Validate coordinate counts and finite numeric values.
- Recognize the lecturer's count-prefixed CSV format.
- Skip blank rows.
- Report malformed nonempty rows.

#### FR-03 — Triangle Geometry

For points `(a, b, c)`, the two sides originating at `a` must have nonzero lengths and satisfy:

`abs(dist(a,b) - dist(a,c)) < 0.001`

Collinear or otherwise degenerate triangles shall be rejected.

#### FR-04 — Trapezoid Geometry

For points `(a, b, c, d)`:

- The first leg is `(a,b)`.
- The second leg is `(c,d)`.
- The starting base is `(a,c)`.
- The ending base is `(b,d)`.

The program shall validate:

- Nonzero area and nonzero required edges.
- Coplanarity.
- Parallel and consistently directed bases.
- Approximately equal leg lengths.
- A non-crossing geometric arrangement.
- The assignment's base-length ordering constraint.

The implementation checks that the starting base is not longer than the ending base, allowing a small geometric tolerance. Rectangles with equal base lengths are supported.

#### FR-05 — Projection Construction

For each valid plane, the program shall advance along the relevant sides or legs, sample positions between corresponding endpoints, and store voxel values in a two-dimensional NumPy array.

The implementation follows an integer-distance row-sampling convention without adding an extra fractional endpoint sample.

#### FR-06 — Nearest-Neighbor Sampling and Boundaries

Continuous sampling positions shall be mapped to nearest-neighbor voxel indices.

Positions outside the three-dimensional volume shall produce zero-valued output pixels.

Boundary handling shall consider both the continuous position and the rounded voxel indices.

#### FR-07 — Invalid Plane Handling

A malformed or geometrically invalid individual plane shall:

1. Produce an informative diagnostic message.
2. Generate a visibly marked error frame.
3. Allow subsequent CSV entries to continue processing.

Unrecoverable input errors may terminate execution.

#### FR-08 — MP4 Encoding

Projection images of different dimensions shall be placed on a common frame canvas and encoded into an MP4 video in CSV order.

Normal output shall contain one encoded frame per processed nonempty CSV entry.

Optional preview output may enlarge or repeat frames for easier inspection.

#### FR-09 — Command-Line Interface

The standard invocation is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

Additional supported commands:

```bash
python Ex0.py --test
python Ex0.py --performance
```

#### FR-10 — Output Safety

The implementation shall:

- Avoid overwriting input files.
- Validate the output path.
- Report encoding and filesystem errors.
- Apply a protective maximum projection size of 25,000,000 pixels.

The projection-size limit is an implementation-specific safeguard rather than an explicit dimension restriction in the assignment.

### 4. Non-Functional Requirements

#### NFR-01 — Performance

The assignment requires a projection computation rate above 30 FPS, with approximately 100 FPS expected for a `500 × 500 × 500` unsigned-byte volume.

Performance measurements shall distinguish projection computation from NRRD loading, MP4 encoding, and initial Numba JIT compilation.

#### NFR-02 — Correctness

Known-value synthetic volumes, boundary cases, different plane orientations, and invalid geometry shall be used to verify projection matrices and error handling.

#### NFR-03 — Robustness

Recoverable plane-level errors shall not prevent subsequent CSV entries from being processed.

Fatal errors shall be reported clearly.

#### NFR-04 — Maintainability

The implementation separates CSV parsing, geometric validation, sampling, video generation, command-line processing, and benchmarking into identifiable functions within `Ex0.py`.

#### NFR-05 — Reproducibility

The repository shall provide:

- Installation and execution instructions.
- Reproducible sample inputs.
- Automated tests.
- Algorithm documentation.
- Dataset descriptions.
- Experiment results.
- Links to supplementary materials.

### 5. Verification and Recorded Results

Automated regression tests are maintained under `tests/`, including:

- `test_csv.py`
- `test_geometry.py`
- `test_projection.py`
- `test_video.py`
- `test_extra.py`
- `test_lecturer_requirements.py`

Run the complete suite:

```bash
python -m pytest -q
```

**Recorded result:** 52 tests passed on the corrected implementation. A local run completed in 6.70 seconds; execution time may vary between environments.

Run the benchmark:

```bash
python Ex0.py --performance
```

| Measurement | Recorded result |
|---|---:|
| Synthetic volume | `500 × 500 × 500` |
| Voxel type | `uint8` |
| Measured projections | 10 |
| Average projection time | Approximately 0.00141 s |
| Projection computation rate | 710.91 FPS |

These measurements exclude NRRD loading, MP4 encoding, and initial JIT compilation.

A small end-to-end demonstration was executed using:

```bash
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
```

The recorded run loaded a `16 × 16 × 16` volume, processed two plane entries, and generated an MP4 containing visible projection content.

### 6. Acceptance Criteria

The final submission should satisfy the following:

1. The command-line interface accepts supported NRRD and CSV files.
2. Triangle and trapezoid validation follows the lecturer's conventions.
3. Projection values and out-of-volume zeros match expected results.
4. Invalid plane entries produce error frames without disrupting later entries.
5. Normal MP4 output preserves the expected frame count and order.
6. Automated tests pass on the submitted implementation.
7. Performance measurements clearly identify their scope.
8. The README, SRS, algorithm description, and experiment report agree with the code.
9. The GitHub repository contains the required documentation, implementation, tests, and reproducible examples or dataset links.

### 7. Supporting Documentation

- [README](../README.md)
- [Algorithm Design](ALGORITHM.md)
- [Testing Strategy](TESTING.md)
- [Performance Experiment](EXPERIMENT.md)
- [Dataset Description](DATASET.md)
