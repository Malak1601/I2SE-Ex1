# Performance Experiment and Results

## 1. Objective

The purpose of this experiment is to evaluate the performance of the plane projection algorithm and demonstrate its ability to generate MP4 videos from 3D NRRD volumes and CSV files containing plane coordinates.

The assignment requires a minimum projection rate of 30 FPS, with approximately 100 FPS expected for a 500 × 500 × 500 volume.

The experiments focus on computational performance, correctness, and the ability to process different datasets.

## 2. Implementation

The project is implemented in Python.

The main libraries are:

- **NumPy:** Stores the 3D volume and projection matrices.
- **pynrrd:** Reads NRRD files.
- **Numba:** Accelerates the projection loop using JIT compilation.
- **imageio and imageio-ffmpeg:** Generate MP4 video files.

The projection algorithm uses nearest-neighbor sampling. Coordinates outside the volume produce zero-valued pixels.

The implementation supports projections defined by isosceles triangles and isosceles trapezoids.

## 3. Performance Benchmark

The benchmark was executed using:

```bash
python Ex0.py --performance
```

The program creates a synthetic unsigned 8-bit volume of size 500 × 500 × 500.

It projects a triangle defined by:

- a = (0, 0, 0)
- b = (400, 0, 0)
- c = (0, 400, 0)

A warm-up projection is performed before measuring execution time to exclude the initial Numba compilation.

The algorithm is then executed 10 times.

### Measured Results

| Measurement | Result |
|---|---|
| Volume dimensions | 500 × 500 × 500 |
| Data type | uint8 |
| Number of measured projections | 10 |
| Average time per projection | 0.00189 seconds |
| Projection rate | 530.43 FPS |
| Minimum required rate | 30 FPS |
| Expected rate | Approximately 100 FPS |

The latest benchmark achieved an average projection time of 0.00189 seconds, corresponding to 530.43 projection FPS.

This exceeds both the minimum required rate of 30 FPS and the expected target of approximately 100 FPS for the tested projection.

**Important:** This benchmark measures projection computation only. It does not include NRRD file loading, MP4 encoding, or initial Numba JIT compilation. Performance may vary between runs, hardware configurations, and plane geometries.

## 4. Video Demonstration

The project generates MP4 videos from NRRD data and CSV plane definitions.

The main command is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The program processes the plane definitions in CSV order and generates the corresponding video frames.

Valid planes produce grayscale projection images. Invalid plane definitions are handled by generating marked error frames, allowing subsequent valid entries to be processed.

### Generated Video Outputs

| Dataset | Video File | Frames | FPS | Duration |
|---|---|---:|---:|---:|
| MRI | `results/output (5).mp4` | 4 | 30 | Approximately 0.13 seconds |
| Croissant | `results/croissant_reference.mp4` | 100 | 30 | 3.33 seconds |
| Onion | `results/onion_reference.mp4` | 120 | 30 | 4.00 seconds |

The Croissant and Onion videos demonstrate the processing of longer sequences of plane definitions from CSV files.

The MRI video demonstrates a shorter four-plane sequence.

The number of frames corresponds to the number of processed plane definitions for these experiments.

## 5. Automated Testing

The project includes automated tests for:

- Triangle and trapezoid geometry validation.
- CSV input parsing and invalid entries.
- Nearest-neighbor sampling and volume boundaries.
- Projection values and output data types.
- Error-frame generation.
- MP4 creation, frame order, and preview output.

The test suite was executed using:

```bash
python -m pytest -q
```

### Test Results

**45 tests passed in 14.84 seconds.**

All tests in this execution completed successfully.

Additional manual tests were performed using selected edge cases and synthetic NRRD volumes with uint8, uint16, and uint32 data types.

Detailed test descriptions and results are documented in `docs/TESTING.md`.

## 6. Additional Experiments: Croissant and Onion

Two additional NRRD datasets were used to evaluate the projection algorithm on different 3D volumes.

### Croissant Dataset

- Volume dimensions: 500 × 500 × 500
- Data type: uint8
- Reference CSV: `data/croissant_reference.csv`
- Number of plane definitions: 100
- Generated video: `results/croissant_reference.mp4`

The program processed the 100 plane definitions and generated an MP4 video showing successive views of the croissant volume.

The resulting video was visually inspected, and the projections were clearly visible.

### Onion Dataset

- Volume dimensions: 256 × 256 × 130
- Data type: uint8
- Reference CSV: `data/onion_reference.csv`
- Number of plane definitions: 120
- Generated video: `results/onion_reference.mp4`

The program processed the reference CSV and saved the resulting MP4 video.

The video was visually inspected and showed clear successive views of the onion volume.

### Additional Three-Plane Tests

For each dataset, three orthogonal rectangular planes were generated to test different orientations.

| Dataset | Number of Planes | Output |
|---|---:|---|
| Croissant | 3 | `results/croissant.mp4` |
| Onion | 3 | `results/onion.mp4` |

Separate preview videos were generated by repeating the three original frames for easier viewing.

These preview videos do not represent additional projection computations.

### Observations

The experiments demonstrate that the same implementation can generate projections from different NRRD volumes and CSV plane definitions.

The reference CSV files provide longer projection sequences than the manually created three-plane examples.

The experiments also demonstrate the ability to process volumes of different dimensions without modifying the projection algorithm.

## 7. Conclusion

The experiments demonstrate that the implemented algorithm can efficiently compute 2D projections from 3D volumes.

For the latest synthetic-volume benchmark, the implementation achieved **530.43 projection FPS**, exceeding the assignment's minimum and expected performance targets for projection computation.

Additional experiments using MRI, Croissant, and Onion datasets demonstrated video generation from different volume dimensions and plane sequences.

The project includes automated tests for correctness, geometry validation, input handling, and video generation.

The performance benchmark measures projection computation only and should not be interpreted as an end-to-end MP4 generation rate.