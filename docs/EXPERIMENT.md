# Performance Experiment and Results

## 1. Objective

This report evaluates the correctness, computational performance, and video-generation behavior of the 3D volume plane projection program.

The program reads an NRRD volume and CSV plane definitions, generates two-dimensional projections, and encodes them into an MP4 video.

The assignment specifies a projection rate above 30 FPS and an expected target of approximately 100 FPS for a `500 × 500 × 500` unsigned-byte volume.

The benchmark measures projection computation, not end-to-end video throughput.

## 2. Implementation and Method

The project is implemented in Python and uses:

- **NumPy:** Stores the 3D volume and projection matrices.
- **pynrrd:** Reads NRRD volume files.
- **Numba:** Accelerates the numerical sampling loop using JIT compilation.
- **imageio and imageio-ffmpeg:** Generate MP4 video files.
- **pytest:** Runs automated regression tests.

The algorithm supports isosceles triangular and trapezoidal regions.

It uses nearest-neighbor sampling, assigns zero to out-of-volume positions, and generates marked error frames for invalid individual plane definitions.

## 3. Projection Performance Benchmark

Run the benchmark from the repository root:

```bash
python Ex0.py --performance
```

The benchmark creates a synthetic `uint8` volume of dimensions:

`500 × 500 × 500`

The benchmark triangle is defined by:

```text
a = (0, 0, 0)
b = (400, 0, 0)
c = (0, 400, 0)
```

A warm-up projection is performed before measurement to exclude the initial Numba compilation.

The algorithm is then measured over ten projection executions.

### 3.1 Recorded Results

| Measurement | Result |
|---|---:|
| Volume dimensions | `500 × 500 × 500` |
| Voxel type | `uint8` |
| Measured projections | 10 |
| Average projection time | Approximately 0.00141 seconds |
| Projection computation rate | **710.91 FPS** |
| Assignment minimum | Above 30 FPS |
| Expected target | Approximately 100 FPS |

The measured projection-computation rate exceeds the assignment's minimum and expected targets for this benchmark configuration.

### 3.2 Measurement Scope

The benchmark excludes:

- NRRD file loading.
- MP4 encoding.
- Filesystem operations.
- Initial Numba JIT compilation.

Performance depends on hardware, plane geometry, projection dimensions, and runtime conditions.

Therefore, **710.91 FPS must not be interpreted as the encoded video's playback FPS or end-to-end video generation throughput**.

## 4. Automated Correctness Testing

The regression suite covers:

- Triangle and trapezoid validation.
- CSV parsing.
- Known voxel values.
- Out-of-volume behavior.
- Projection construction.
- MP4 creation.
- Error frames.
- Lecturer-specific requirements.

The test suite includes:

- `tests/test_csv.py`
- `tests/test_geometry.py`
- `tests/test_projection.py`
- `tests/test_video.py`
- `tests/test_extra.py`
- `tests/test_lecturer_requirements.py`

Run:

```bash
python -m pytest -q
```

### 4.1 Recorded Test Results

**52 tests passed** on the corrected implementation.

A recorded local run completed in 6.70 seconds.

This result demonstrates successful execution of the tested cases, but it does not prove correctness for every possible input.

Additional manual tests using selected edge cases and synthetic `uint8`, `uint16`, and `uint32` volumes were documented during development.

These earlier experiments are distinguished from the final regression suite in [Testing Strategy](TESTING.md).

## 5. Small Reproducible End-to-End Demonstration

The repository includes:

- `data/demo_small.nrrd` — a `16 × 16 × 16` synthetic volume.
- `data/demo_small.csv` — two plane definitions.

Run:

```bash
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
```

### 5.1 Recorded Results

| Measurement | Observed result |
|---|---|
| Volume shape | `(16, 16, 16)` |
| CSV entries | 2 |
| Projection 1 | Shape `(10, 16)`, 87 nonzero values |
| Projection 2 | Shape `(10, 11)`, 110 nonzero values |
| Output | `results/demo_small.mp4` |

The generated MP4 was successfully saved.

A frame extracted from the video was visually inspected and showed a nonempty grayscale triangular projection on a black background.

Because the normal output contains only two frames at 30 FPS, playback lasts approximately 0.067 seconds.

This short duration is expected and does not indicate a failed projection.

## 6. MRI Demonstration

An MRI NRRD volume was used to demonstrate projections of real volumetric data.

The main MRI video included in the repository is:

[**mri_final.mp4 — Main MRI demonstration**](../results/mri_final.mp4)

| Measurement | Result |
|---|---|
| Video | `results/mri_final.mp4` |
| Frames | 100 |
| Encoded FPS | 30 |
| Approximate duration | 3.33 seconds |

A shorter MRI example is also included:

[output (5).mp4](../results/output%20%285%29.mp4)

This short video contains four frames at 30 FPS, lasting approximately 0.13 seconds.

The source MRI NRRD may be distributed separately because of its size. Dataset acquisition instructions are provided in [Dataset Description](DATASET.md).

## 7. Additional Experiments: Croissant and Onion

Two additional NRRD datasets were used to evaluate the algorithm on different volume shapes and longer CSV sequences.

### 7.1 Reference Dataset Results

| Dataset | Volume dimensions | Voxel type | CSV entries | Generated video |
|---|---|---|---:|---|
| Croissant | `500 × 500 × 500` | `uint8` | 100 | `results/croissant_reference.mp4` |
| Onion | `256 × 256 × 130` | `uint8` | 120 | `results/onion_reference.mp4` |

The reference CSV files define successive planar regions.

### 7.2 Video Results

| Video | Frames | Playback FPS | Approximate duration |
|---|---:|---:|---:|
| [croissant_reference.mp4](../results/croissant_reference.mp4) | 100 | 30 | 3.33 seconds |
| [onion_reference.mp4](../results/onion_reference.mp4) | 120 | 30 | 4.00 seconds |

The videos demonstrate that the same implementation can process different NRRD volumes and plane sequences.

### 7.3 Additional Three-Plane Experiments

Three orthogonal rectangular planes were also used for each dataset.

| Dataset | Number of planes | Video |
|---|---:|---|
| Croissant | 3 | [croissant.mp4](../results/croissant.mp4) |
| Onion | 3 | [onion.mp4](../results/onion.mp4) |

Additional preview videos were generated by repeating frames for easier inspection.

Preview repetitions are not additional projection computations.

### 7.4 Observations

The recorded development experiments showed:

- Visible grayscale projections.
- Successful processing of different volume dimensions.
- Support for longer CSV plane sequences.
- Consistent video generation without changing the projection algorithm.

These observations describe the tested datasets and do not establish exhaustive correctness for every possible input.

## 8. Interpretation and Limitations

The experiments support the following conclusions:

1. The corrected implementation passed 52 automated tests.
2. A small end-to-end NRRD-to-MP4 workflow completed successfully.
3. The synthetic benchmark achieved 710.91 projection FPS for the measured triangle.
4. MRI, Croissant, and Onion experiments demonstrated video generation from different volume dimensions and plane sequences.
5. Invalid individual plane definitions are handled using marked error frames.

The experiments do not establish:

- Exhaustive correctness for every possible geometry.
- Uniform performance for every permitted plane.
- An end-to-end video generation rate of 710.91 FPS.

## 9. Conclusion

The implemented algorithm successfully generated two-dimensional projections from three-dimensional volumes in the recorded experiments.

The measured projection-computation performance exceeded the assignment's minimum and expected targets for the tested configuration.

The combination of automated tests, reproducible synthetic data, MRI demonstrations, and additional Croissant and Onion experiments provides evidence for the correctness, robustness, and efficiency of the implementation.

Further details are available in:

- [README](../README.md)
- [Algorithm Design](ALGORITHM.md)
- [Testing Strategy](TESTING.md)
- [Dataset Description](DATASET.md)
- [Video Results](../results/results.md)
