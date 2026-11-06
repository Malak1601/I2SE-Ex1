# I2SE Ex1 – 3D Volume Plane Projection

**Course:** Introduction to Software Engineering  
**University:** Ariel University

## 1. Overview

This project implements an algorithm for generating 2D projections from a 3D volume, such as an MRI scan.

The program receives two input files:

- An NRRD file containing a 3D volume.
- A CSV file containing plane definitions using three or four points in 3D space.

For each plane, the program calculates the sampling positions, retrieves voxel values from the volume, and generates a 2D image.

The generated images are combined into an MP4 video in the same order as the CSV entries.

The main goal is to implement a correct and efficient projection algorithm while handling different plane orientations, volume boundaries, and invalid inputs.

## 2. Project Scope

The implementation includes:

- Reading 3D volumes from NRRD files.
- Reading plane definitions from CSV files.
- Supporting isosceles triangles and isosceles trapezoids.
- Validating geometric conditions using the required tolerance.
- Generating 2D projections using nearest-neighbor sampling.
- Assigning zero to sampling positions outside the volume.
- Generating marked error frames for invalid plane definitions.
- Continuing to process subsequent planes after an invalid entry.
- Saving the resulting frames as an MP4 video.
- Automated correctness testing.
- Performance measurement using a 500 × 500 × 500 volume.

The project focuses on algorithm design, correctness, runtime efficiency, robustness, and code quality.

It does not include a graphical user interface or physical-coordinate transformations.

## 3. Installation

The project is implemented in Python.

### Requirements

The main dependencies are:

- NumPy
- pynrrd
- Numba
- imageio
- imageio-ffmpeg
- pytest (for automated testing)

Install the dependencies from the project directory:

```bash
python -m pip install -r requirements.txt
```

Using a Python virtual environment is recommended.

## 4. Input and Output

The program accepts three command-line arguments:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

| Argument | Description |
|---|---|
| `file.nrrd` | Input 3D volume |
| `file.csv` | CSV file containing plane definitions |
| `file.mp4` | Output MP4 video |

### NRRD Volume

The required input format is a 3D volume with dimensions:

- 1 ≤ sx, sy, sz < 1024

Supported unsigned integer types:

- uint8
- uint16
- uint32

The implementation also accepts nonnegative signed integer volumes by converting them to an appropriate unsigned type.

### CSV Format

Each plane is defined using three or four points in 3D space.

**Triangle:** Three points, represented by nine coordinate values.

**Trapezoid:** Four points, represented by twelve coordinate values.

The program also supports the lecturer's CSV format, where each row starts with the number of points (`3` or `4`).

For a triangle, the first point is the common vertex of the two equal-length sides.

For a trapezoid, the points describe two parallel bases connected by two equal-length legs.

Each valid plane produces one projection frame. An invalid nonempty plane entry produces a marked error frame.

## 5. Running the Program

Run the program from the repository's main directory.

### Example 1: Small Test Dataset

```bash
python Ex0.py data/test.nrrd data/test.csv results/output.mp4
```

### Example 2: MRI Dataset

```bash
python Ex0.py "MRHead_1 (6).nrrd" data/MRHead_demo.csv results/MRHead_demo.mp4
```

The MRI example assumes the NRRD file is available locally under the specified name.

The program reads the plane definitions in CSV order and generates the corresponding projections.

If a plane is invalid, the program handles the validation error and generates a marked error frame without stopping the remaining processing.

## 6. Projection Algorithm

The projection algorithm converts a plane defined in 3D space into a 2D matrix of sampled voxel values.

### Isosceles Triangle

A triangle is defined by three points `a`, `b`, and `c`.

The two sides starting from `a` must have approximately equal lengths:

`|dist(a,b) - dist(a,c)| < 0.001`

The algorithm advances along the two equal-length sides.

At each step, it samples the positions between the corresponding points and stores the voxel values in the output image.

### Isosceles Trapezoid

A trapezoid is defined by four points forming two parallel bases and two equal-length legs.

The algorithm validates the geometric conditions, advances along the legs, and samples the positions between them.

The implementation also checks coplanarity and the required base-length relationship.

### Nearest-Neighbor Sampling

Continuous coordinates are mapped to the nearest voxel indices.

This method was selected because it is simple, efficient, and suitable for the assignment.

### Volume Boundaries

If a sampling position is outside the volume, the corresponding output pixel receives a value of zero.

### Performance Optimization

The computationally intensive sampling loop is accelerated using Numba JIT compilation.

Detailed explanations of the geometry, sampling method, and algorithm are available in:

[Algorithm Documentation](docs/ALGORITHM.md)

## 7. Error Handling

The program validates input data and plane geometry before generating each projection.

Examples of invalid inputs include:

- Missing or invalid coordinate values.
- Non-finite coordinate values.
- Degenerate triangles.
- Triangles with unequal required sides.
- Trapezoids with unequal legs.
- Non-parallel trapezoid bases.
- Non-coplanar trapezoid vertices.
- Invalid volume dimensions or unsupported data types.

Invalid plane geometry raises an exception.

The main demo handles plane errors by generating a visibly marked error frame.

This allows subsequent plane definitions to be processed while preserving their order.

Fatal input errors, such as an unreadable NRRD file, are reported rather than converted into individual plane frames.

## 8. Testing

The project includes automated tests for geometry, input parsing, sampling, projection correctness, and video generation.

### Test Files

| File | Purpose |
|---|---|
| `tests/test_csv.py` | CSV parsing and invalid entries |
| `tests/test_geometry.py` | Triangle and trapezoid validation |
| `tests/test_projection.py` | Voxel sampling and projection correctness |
| `tests/test_video.py` | Video creation, frame order, and error frames |
| `tests/test_extra.py` | Additional correctness and boundary tests |

### Run Automated Tests

```bash
python -m pytest tests/ -v
```

Latest recorded result:

**45 tests passed in 6.89 seconds.**

### Run Built-in Tests

```bash
python Ex0.py --test
```

The automated tests use small volumes with known values to verify projection results.

The testing strategy also addresses invalid inputs, boundary conditions, and the command-line demo.

Full testing documentation:

[Testing Strategy](docs/TESTING.md)

## 9. Performance

The assignment requires a projection rate above 30 FPS for a 500 × 500 × 500 volume, with approximately 100 FPS as the expected performance target.

The implementation uses Numba to accelerate the projection loop.

### Run the Benchmark

```bash
python Ex0.py --performance
```

The benchmark uses a synthetic unsigned 8-bit volume with dimensions:

`500 × 500 × 500`

It performs an initial warm-up projection and then measures ten projection executions.

### Recorded Results

| Measurement | Result |
|---|---|
| Volume dimensions | 500 × 500 × 500 |
| Data type | uint8 |
| Number of measured projections | 10 |
| Average time per projection | 0.00103 seconds |
| Projection rate | 972.22 FPS |
| Minimum required rate | Above 30 FPS |
| Expected target | Approximately 100 FPS |

The measured projection rate exceeds the assignment's performance targets for this benchmark.

**Important:** The benchmark measures projection computation only. It excludes NRRD loading, MP4 encoding, and initial Numba compilation.

Results may vary depending on the computer, input data, and plane geometry.

More details:

[Performance Experiment](docs/EXPERIMENT.md)

## 10. Experiment and Results

The project was tested using synthetic volumes and an MRI volume.

### Synthetic Volume Testing

Small volumes with known voxel values were used to verify:

- Correct voxel sampling.
- Projection output values.
- Handling of positions outside the volume.
- Geometry validation.
- Error handling.

### MRI Demonstration

An MRHead MRI volume was used to demonstrate projections from real 3D data.

The demonstration uses CSV plane definitions to generate 2D images from different positions and orientations.

The resulting frames are saved as an MP4 video.

### Demonstration Output

[View Generated MP4 Video](results/output%20%285%29.mp4)

### Experiment Documentation

[Experiment and Results](docs/EXPERIMENT.md)

The experiment documentation includes the benchmark configuration, recorded performance results, testing information, and output description.

## 11. Dataset

The project uses two main types of data:

### Synthetic Data

Small synthetic volumes are used for correctness testing because their voxel values are known.

A synthetic 500 × 500 × 500 unsigned 8-bit volume is generated in memory for the performance benchmark.

### MRI Data

An MRHead MRI dataset is used for the video demonstration.

CSV files contain plane definitions for extracting 2D projections from the volume.

The sample input files are organized in the `data/` directory.

The MRI volume must be provided locally when running the MRI example.

For further details:

[Dataset Documentation](docs/DATASET.md)

## 12. Repository Structure

```text
I2SE-Ex1/
├── data/
│   ├── Ex0_lecturer.csv
│   ├── MRHead_demo.csv
│   ├── test.csv
│   └── test.nrrd
│
├── docs/
│   ├── ALGORITHM.md
│   ├── DATASET.md
│   ├── EXPERIMENT.md
│   ├── SRS.md
│   └── TESTING.md
│
├── results/
│   └── output (5).mp4
│
├── tests/
│   ├── test_csv.py
│   ├── test_extra.py
│   ├── test_geometry.py
│   ├── test_projection.py
│   └── test_video.py
│
├── Ex0.py
├── README.md
├── requirements.txt
└── .gitignore
```

This structure shows the main project files. Local datasets, generated videos, temporary files, and other working files may also be present.

### Main Files

| File | Purpose |
|---|---|
| `Ex0.py` | Main implementation and command-line interface |
| `README.md` | Project overview, setup, and usage |
| `docs/SRS.md` | Software requirements specification |
| `docs/ALGORITHM.md` | Algorithm design and implementation details |
| `docs/DATASET.md` | Description of the datasets |
| `docs/TESTING.md` | Testing strategy and test coverage |
| `docs/EXPERIMENT.md` | Performance experiment and results |
| `data/` | Sample NRRD and CSV input files |
| `tests/` | Automated tests |
| `results/` | Generated demonstration output |
| `requirements.txt` | Python dependencies |

## 13. Design Decisions and Limitations

The following design decisions were made:

- Plane coordinates are interpreted as voxel coordinates rather than physical coordinates.
- Nearest-neighbor sampling is used instead of interpolation.
- Positions outside the volume are assigned zero.
- Higher-bit-depth voxel values are normalized for grayscale video display.
- Invalid plane definitions generate marked error frames.
- Numba is used to improve projection performance.
- Projection performance is measured separately from video encoding.

The implementation does not include:

- A graphical user interface.
- GPU acceleration.
- Advanced interpolation methods.
- Physical-coordinate transformations based on NRRD spatial metadata.

## 14. Conclusion

This project implements a 3D-to-2D plane projection algorithm supporting isosceles triangles and trapezoids.

It includes geometric validation, nearest-neighbor sampling, volume boundary handling, error-frame generation, MP4 output, automated tests, and performance optimization using Numba.

The automated test suite completed with 45 passing tests.

In the recorded synthetic-volume benchmark, the algorithm achieved 972.22 projection FPS, exceeding the specified performance targets for projection computation.

The project demonstrates how a geometric projection problem can be implemented as a practical software solution with attention to correctness, design, robustness, and runtime efficiency.