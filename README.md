# 3D Medical Volume Plane Projection

## Problem Statement

The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The program receives a 3D volume stored in an NRRD file and a CSV file containing plane definitions. Each plane is defined by three or four points in 3D space.

For each plane, the program calculates sampling positions, reads the corresponding voxel values, and generates a 2D image. The images are then combined into an MP4 video.

The main challenge is to implement the projection correctly and efficiently while handling different plane orientations, volume boundaries, and invalid inputs.

## Project Scope

The project includes:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from CSV files.
- Supporting isosceles triangles and isosceles trapezoids.
- Validating geometric conditions.
- Generating 2D projections using nearest-neighbor sampling.
- Assigning zero to sampling positions outside the volume.
- Saving the generated projections as an MP4 video.
- Testing correctness and measuring projection performance.

The project focuses on the projection algorithm, its design, performance, and implementation. It is not intended to be a complete medical imaging application.

## Installation

The project was developed using Python.

Required Python packages:

- numpy
- pynrrd
- numba
- imageio
- imageio-ffmpeg

Install the dependencies using:

```bash
python3 -m pip install numpy pynrrd numba imageio imageio-ffmpeg
```

A Python virtual environment is recommended.

## Input and Output

The program accepts three command-line arguments:

1. **NRRD file:** A 3D volume containing voxel values.
2. **CSV file:** A list of planes, each defined by three or four 3D points.
3. **MP4 file:** The output video containing the generated projections in CSV order.

The program supports unsigned 8-bit, 16-bit, and 32-bit integer volumes. It also converts signed integer volumes when all voxel values are nonnegative.

### CSV Format

The program accepts CSV rows containing either nine coordinates for a triangle or twelve coordinates for a trapezoid.

It also supports the lecturer's CSV format, where each row begins with the number of points (3 or 4).

For a triangle, the first point is the common vertex of the two equal-length sides.

For a trapezoid, the points are interpreted as follows:

- The first leg connects points `a` and `b`.
- The second leg connects points `c` and `d`.
- The starting base connects `a` and `c`.
- The ending base connects `b` and `d`.

### Running the Program

Example using the included test files:

```bash
python3 Ex0.py test.nrrd test.csv output.mp4
```

Example using the MRI dataset:

```bash
python3 Ex0.py "MRHead_1 (6).nrrd" MRHead_demo.csv MRHead_demo_preview.mp4
```

The program prints information about the volume, the number of CSV entries, and the generated projections.

Invalid plane definitions are reported, and an error frame is added to preserve the order of the CSV entries.

## Projection Algorithm

The projection algorithm generates a 2D image by sampling points along a plane in the 3D volume.

For an isosceles triangle, the two sides starting from the first vertex must have approximately equal lengths.

The algorithm advances along these two sides. At each step, it calculates the positions between the corresponding points and samples the volume.

For an isosceles trapezoid, the algorithm follows the two equal-length legs and samples the points between them.

Nearest-neighbor sampling converts continuous coordinates into voxel indices. Positions outside the volume receive a value of zero.

The computationally intensive projection loop is implemented using Numba to improve performance.

More details are available in [ALGORITHM.md](ALGORITHM.md).

## Software Requirements

The functional and non-functional requirements are described in [SRS.md](SRS.md).

## Testing

The project includes basic tests and additional tests covering:

- Known voxel values.
- Constant-volume projections.
- Volume boundaries.
- Valid and invalid triangles.
- Triangle tolerance.
- Valid and invalid trapezoids.
- Rectangle projections.
- CSV parsing and error recovery.
- Error-frame generation.

Run the basic tests:

```bash
python3 Ex0.py --test
```

Run the additional tests:

```bash
python3 test_extra.py
```

The project also includes small test files, `test.nrrd` and `test.csv`.

## Performance

The assignment requires a projection rate greater than 30 frames per second for the specified benchmark.

The implementation uses Numba to compile the main projection loop.

Run the performance benchmark using:

```bash
python3 Ex0.py --performance
```

The benchmark uses a 500 × 500 × 500 volume and performs ten projections after a Numba warm-up.

In one local test, the measured projection rate was approximately **443 FPS**.

This measurement covers projection computation only. It excludes NRRD loading and MP4 encoding, and the result may vary depending on hardware and test conditions.

## Experiment and Results

The implementation was tested using an MRI volume with dimensions:

**256 × 256 × 130**

A demonstration CSV containing four valid plane definitions was used to generate different 2D views of the volume.

The program successfully generated four projections and saved them in an MP4 video.

The resulting images included sagittal, axial, and triangular views of the MRI data.

The lecturer's CSV file was also tested. Three plane definitions were accepted, while one triangle was rejected because its two required sides were not approximately equal.

The generated images demonstrate that the program can sample a real 3D volume and produce 2D projections with different orientations.

## Repository Files

- `Ex0.py` — Main implementation.
- `README.md` — Project overview and usage instructions.
- `SRS.md` — Software requirements specification.
- `ALGORITHM.md` — Algorithm description and design decisions.
- `test_extra.py` — Additional correctness tests.
- `test.nrrd` — Small test volume.
- `test.csv` — Test plane definitions.
- `MRHead_demo.csv` — MRI demonstration planes.
- `Ex0_lecturer.csv` — Lecturer CSV test cases.
- `output.mp4` — Generated projection video.
- `output_large_preview.mp4` — Enlarged preview video.
- `.gitignore` — Git ignore configuration.

Additional generated videos and MRI data files may be kept locally rather than committed to the repository.

## Limitations

The program interprets plane coordinates directly as voxel coordinates.

The MP4 output uses 8-bit grayscale frames, so higher-bit-depth voxel values are normalized for video display.

The performance benchmark measures the projection stage separately from video encoding.

## Conclusion

The project implements a 3D-to-2D plane projection algorithm supporting triangular and trapezoidal regions.

The implementation includes geometric validation, boundary handling, video generation, automated tests, and performance optimization using Numba.