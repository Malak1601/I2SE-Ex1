# Performance Experiment and Results

## 1. Objective

The purpose of this experiment is to evaluate the performance of the plane projection algorithm and demonstrate its ability to generate an MP4 video from a 3D NRRD volume and a CSV file containing plane coordinates.

The assignment requires a projection rate above 30 FPS, with approximately 100 FPS expected for a 500 × 500 × 500 volume.

## 2. Implementation

The project is implemented in Python.

The main libraries are:

- **NumPy:** stores the 3D volume and projection matrices.
- **pynrrd:** reads NRRD files.
- **Numba:** accelerates the projection loop using JIT compilation.
- **imageio and imageio-ffmpeg:** generate MP4 video files.

The projection uses nearest-neighbor sampling. Coordinates outside the volume produce zero-valued pixels.

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
| Average time per projection | 0.00103 seconds |
| Projection rate | 972.22 FPS |
| Minimum required rate | Above 30 FPS |
| Expected rate | Approximately 100 FPS |

The measured projection rate exceeds both the minimum requirement and the expected performance target for this benchmark.

**Important:** This benchmark measures projection computation only. It does not include NRRD file loading, MP4 encoding, or the initial Numba compilation. The result depends on the computer and the selected plane geometry.

## 4. Video Demonstration

The project also generates MP4 videos from NRRD data and CSV plane definitions.

The main command is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The program processes the plane definitions in CSV order and generates the corresponding video frames.

Valid planes produce grayscale projection images. Invalid plane definitions are handled by generating a marked error frame, allowing subsequent valid entries to be processed.

### Output File

The generated demonstration video is stored in:

`results/output (5).mp4`

This file demonstrates the output of the projection pipeline using the MRI volume.

## 5. Testing

The project includes automated tests for:

- Triangle and trapezoid geometry validation.
- CSV input parsing and invalid entries.
- Nearest-neighbor sampling and volume boundaries.
- Projection values and output data types.
- Error-frame generation.
- MP4 creation, frame order, and preview output.

The test suite was executed using:

```bash
python -m pytest tests/ -v
```

### Test Result

**45 tests passed in 6.89 seconds.**

All tests in that execution completed successfully.

## 6. Conclusion

The experiment demonstrates that the implemented algorithm can efficiently compute 2D projections from a 3D volume.

For the measured synthetic-volume benchmark, the implementation achieved **972.22 projection FPS**, exceeding the assignment's performance targets.

The project also supports video generation from CSV-defined planes and includes automated tests for correctness, validation, and error handling.

The performance result should be interpreted as a projection-only measurement rather than an end-to-end video-generation rate.

## Additional Experiments: Croissant and Onion

Two additional NRRD datasets were used to evaluate the projection algorithm on different 3D volumes.

### Croissant Dataset

- Volume dimensions: 500 × 500 × 500
- Data type: uint8
- Reference CSV: `data/croissant_reference.csv`
- Number of plane definitions: 100
- Generated video: `results/croissant_reference.mp4`

The program processed the 100 plane definitions and generated an MP4 video showing successive views of the croissant volume.

The resulting video was visually inspected and the projections were clearly visible.

### Onion Dataset

- Volume dimensions: 256 × 256 × 130
- Data type: uint8
- Reference CSV: `data/onion_reference.csv`
- Number of plane definitions: 120
- Generated video: `results/onion_reference.mp4`

The program processed the reference CSV and saved the resulting MP4 video.

The video was visually inspected and showed clear successive views of the onion volume.

### Additional Three-Plane Tests

For each dataset, three orthogonal rectangular planes were also generated to test different orientations.

| Dataset | Number of Planes | Output |
|---|---:|---|
| Croissant | 3 | `results/croissant.mp4` |
| Onion | 3 | `results/onion.mp4` |

Separate preview videos were generated by repeating the three original frames for easier viewing. These previews do not change the projection results.

### Observations

The experiments demonstrate that the same implementation can generate projections from different NRRD volumes and CSV plane definitions.

The reference CSV files provide longer projection sequences than the manually created three-plane examples.

The experiments also demonstrate the ability to process volumes of different dimensions without modifying the projection algorithm.