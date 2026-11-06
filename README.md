# I2SE Ex1 – 3D Volume Plane Projection

**Course:** Introduction to Software Engineering  
**Ariel University**

## 1. Overview

This project implements an algorithm for extracting 2D projections from a 3D volume, such as an MRI scan.

The program receives an NRRD file containing volumetric data and a CSV file containing a list of planes. Each plane is defined by three or four points in 3D space.

For every plane, the program calculates the corresponding sampling positions, retrieves voxel values from the volume, and generates a 2D image. The resulting images are combined into an MP4 video in the same order as the CSV entries.

The main challenge is to design a correct and efficient projection algorithm while handling different plane orientations, volume boundaries, and invalid inputs.

## 2. Project Scope

The implementation includes:

- Reading 3D volumetric data from NRRD files.
- Reading plane definitions from CSV files.
- Supporting isosceles triangles and isosceles trapezoids.
- Validating geometric conditions using a tolerance of 0.001.
- Generating 2D projections using nearest-neighbor sampling.
- Assigning zero to sampling positions outside the volume.
- Generating error frames for invalid plane definitions while continuing with valid entries.
- Saving the projections as an MP4 video.
- Testing correctness and measuring projection performance.

The project focuses on algorithm design, correctness, runtime efficiency, and code quality. It does not include a graphical user interface or physical-coordinate transformations.

## 3. Installation

The project is implemented in Python.

The main dependencies are:

- NumPy
- pynrrd
- Numba
- imageio
- imageio-ffmpeg

Install the required packages from the project directory:

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
| `file.mp4` | Output video containing the generated projections |

The required volume format uses unsigned 8-bit, 16-bit, or 32-bit integer values. The implementation also supports nonnegative signed integer volumes.

### CSV Format

Each plane is represented by either three or four points:

- **Triangle:** 9 coordinates defining three 3D points.
- **Trapezoid:** 12 coordinates defining four 3D points.

The implementation also supports the lecturer's CSV format, where each row begins with the number of points (3 or 4).

For triangles, the first point is the common vertex of the two equal-length sides.

For trapezoids, the points define two equal-length legs connecting the parallel bases.

Each valid CSV entry produces one projection frame.

## 5. Running the Program

Run the program from the repository's main directory.

Example using the small test dataset:

```bash
python Ex0.py data/test.nrrd data/test.csv results/output.mp4
```

Example using the MRI dataset:

```bash
python Ex0.py "MRHead_1 (6).nrrd" data/MRHead_demo.csv results/MRHead_demo.mp4
```

The MRI example assumes the NRRD file is available locally under the specified name.

The program processes the planes in CSV order and writes the resulting frames into an MP4 video.

If a plane definition is invalid, the program reports the problem and generates an error frame instead of stopping the entire process.

## 6. Projection Algorithm

The projection algorithm samples a 3D volume along a plane and produces a corresponding 2D matrix.

### Isosceles Triangle

A triangle is defined by three points `a`, `b`, and `c`, where the distances from `a` to `b` and from `a` to `c` are approximately equal.

The algorithm advances along the two equal-length sides. At each step, it samples the positions between the corresponding points and maps their voxel values into the output image.

### Isosceles Trapezoid

For a trapezoid, the algorithm advances along two equal-length legs and samples the positions between them.

### Sampling and Boundaries

Nearest-neighbor sampling is used to convert continuous 3D coordinates into voxel indices.

Positions outside the volume are assigned a value of zero.

The computationally intensive projection loop uses Numba to improve runtime performance.

The geometric validation, sampling decisions, and algorithm details are described in [ALGORITHM.md](docs/ALGORITHM.md).

## 7. Error Handling

Input validation is performed before projecting each plane.

The program checks for conditions such as:

- Invalid coordinate values.
- Degenerate triangles.
- Triangles that do not satisfy the equal-side condition.
- Invalid trapezoid geometry.
- Non-coplanar or non-parallel trapezoid configurations.

For an invalid plane, an exception is raised during validation and handled by the demo program.

An error frame is added to the output video, allowing the remaining valid planes to be processed.

This preserves the order of the CSV entries.

## 8. Testing

The project includes tests for:

- Known voxel values.
- Constant-volume projections.
- Volume boundaries.
- Valid and invalid triangles.
- Triangle tolerance.
- Valid and invalid trapezoids.
- Rectangle projections.
- CSV parsing and error handling.
- Error-frame generation.

Run the built-in tests:

```bash
python Ex0.py --test
```

Run the additional tests:

```bash
python tests/test_extra.py
```

Small test files are provided in the `data/` directory.

The testing approach and test cases are described in [TESTING.md](docs/TESTING.md).

## 9. Performance

The assignment specifies a minimum projection rate of 30 FPS for a 500 × 500 × 500 volume, with 100 FPS as the expected performance target.

The implementation uses Numba to compile the main projection loop and reduce Python-level processing overhead.

Run the benchmark using:

```bash
python Ex0.py --performance
```

The benchmark uses a 500 × 500 × 500 volume and performs ten projections after the initial Numba compilation.

In a local benchmark, the measured projection rate was approximately **443 FPS**.

This measurement covers projection computation only. It excludes NRRD loading, MP4 encoding, and the initial Numba compilation. Results may vary depending on hardware and test conditions.

## 10. Experiment and Results

The implementation was tested using an MRI volume with dimensions:

**256 × 256 × 130**

A demonstration CSV containing four valid plane definitions was used to generate different 2D views of the volume.

The program generated four projection frames and saved them as an MP4 video.

The resulting images included different MRI orientations, including sagittal, axial, and triangular views.

The lecturer's CSV file was also tested. Three plane definitions were accepted, while one triangle was rejected because its two required sides did not satisfy the equal-length condition.

These experiments demonstrate the ability to generate projections from real volumetric data using different plane orientations.

The experiment documentation is available in [results.md](results/results.md).

The final generated video is available in [output.mp4](results/output.mp4).

## 11. Repository Structure

```text
I2SE-Ex1/
├── data/
│   ├── Ex0_lecturer.csv
│   ├── MRHead_demo.csv
│   ├── test.csv
│   └── test.nrrd
│
├── docs/
│   ├── SRS.md
│   ├── ALGORITHM.md
│   └── TESTING.md
│
├── results/
│   ├── results.md
│   └── output.mp4
│
├── tests/
│   └── test_extra.py
│
├── Ex0.py
├── README.md
├── requirements.txt
└── .gitignore
```

The main files are organized as follows:

| File | Purpose |
|---|---|
| `Ex0.py` | Main implementation and command-line interface |
| `README.md` | Project overview and usage instructions |
| `docs/SRS.md` | Software requirements specification |
| `docs/ALGORITHM.md` | Algorithm design and implementation decisions |
| `docs/TESTING.md` | Testing strategy |
| `data/` | Sample CSV and NRRD inputs |
| `tests/test_extra.py` | Additional correctness tests |
| `results/results.md` | Experiment and performance results |
| `results/output.mp4` | Generated projection video |
| `requirements.txt` | Python dependencies |

## 12. Design Decisions and Limitations

Several design decisions were made to keep the implementation clear and efficient:

- Plane coordinates are interpreted as voxel coordinates rather than physical coordinates.
- Nearest-neighbor sampling is used instead of interpolation.
- Samples outside the volume receive a value of zero.
- Higher-bit-depth voxel values are normalized for grayscale video display.
- Projection computation is measured separately from video encoding.

The implementation does not include a graphical interface, GPU acceleration, or advanced interpolation.

## 13. Conclusion

The project implements a 3D-to-2D plane projection algorithm supporting isosceles triangles and trapezoids.

It includes geometric validation, boundary handling, MP4 generation, correctness tests, and performance optimization using Numba.

The implementation demonstrates how a geometric projection problem can be translated into a practical software solution with attention to design, correctness, and runtime efficiency.
