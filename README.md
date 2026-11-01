# I2SE-Ex1

## 3D Medical Volume Plane Projection

### Problem Statement

This project focuses on extracting 2D images from 3D volumetric data, such as MRI scans.

The input consists of a 3D matrix containing voxel values and a set of planes defined by three or four points. For each plane, the program calculates the corresponding positions in the volume, samples the voxel values, and creates a 2D image.

The main goal is to implement a correct and efficient projection algorithm that can handle different plane orientations and input conditions.

### Project Scope

The project includes:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from a CSV file.
- Supporting triangle and trapezoid plane definitions.
- Checking the validity of the input plane coordinates.
- Generating 2D images using the projection algorithm.
- Using zero for sampling positions outside the volume.
- Handling invalid plane definitions without interrupting the processing of valid planes.
- Combining the generated frames into an MP4 video.
- Testing the correctness and performance of the implementation.

The main focus is on the projection algorithm, its efficiency, and the reliability of the implementation. A graphical user interface is not part of this project.

### Requirements

The project uses Python 3 and the following libraries:

- NumPy
- pynrrd
- imageio
- imageio-ffmpeg

Install the required libraries using:

```bash
python3 -m pip install numpy pynrrd imageio imageio-ffmpeg
```

### How to Run

Run the program from the command line:

```bash
python3 Ex0.py file.nrrd file.csv file.mp4
```

The arguments are:

- `file.nrrd` - The input 3D volume.
- `file.csv` - A CSV file containing the plane coordinates.
- `file.mp4` - The output video file.

Each CSV row contains either 9 values for a triangle or 12 values for a trapezoid. Every three consecutive values represent a point in 3D space.

To run the included example:

```bash
python3 Ex0.py test.nrrd test.csv output.mp4
```

The program processes the plane definitions in CSV order and generates a corresponding video frame for each one.

### Testing

The project contains basic projection tests and additional tests for different input conditions.

Run the basic tests:

```bash
python3 Ex0.py --test
```

Run the additional tests:

```bash
python3 test_extra.py
```

The tests cover:

- Triangle and trapezoid projections.
- Expected output values.
- Constant volume data.
- Sampling outside the volume boundaries.
- Invalid triangle definitions.
- Invalid trapezoid definitions.
- Crossed-trapezoid regression cases.

The tests are intended to verify the correctness of the calculations and the handling of invalid inputs.

### Performance Experiment

A performance benchmark was used to measure the processing speed of the triangle projection algorithm.

The experiment used a synthetic 3D volume with dimensions of 500 × 500 × 500.

The triangle was defined by the following points:

- A = (0, 0, 0)
- B = (400, 0, 0)
- C = (0, 400, 0)

The algorithm was executed once as a warm-up, followed by 10 measured runs. Execution time was measured using `time.perf_counter()`.

Run the benchmark using:

```bash
python3 Ex0.py --performance
```

#### Results

| Metric | Result |
|---|---|
| Volume dimensions | 500 × 500 × 500 |
| Measured runs | 10 |
| Latest reported processing speed | 43.87 FPS |
| Minimum required speed | 30 FPS |
| Expected performance target | 100 FPS |

The reported speed exceeds the minimum requirement of 30 FPS but remains below the expected target of 100 FPS.

The benchmark measures projection processing time, excluding file loading and video encoding.

These results are specific to the tested triangle and execution environment. Other plane configurations may produce different processing times.

### Dataset

The repository includes `test.nrrd`, a small synthetic volume used for testing the projection algorithm.

The `test.csv` file contains sample triangle and trapezoid coordinates.

A separate synthetic volume of size 500 × 500 × 500 was used for performance measurements.

### Demo and Output

The demo can be executed using:

```bash
python3 Ex0.py test.nrrd test.csv output.mp4
```

The program reads the volume and plane coordinates, computes the projections, and saves them as video frames in the same order as the CSV entries.

The repository contains:

- `output.mp4` - The generated projection video.
- `output_large_preview.mp4` - An enlarged version for easier viewing.

### Project Files

- `Ex0.py` - Main Python implementation.
- `test_extra.py` - Additional tests.
- `test.nrrd` - Sample volume data.
- `test.csv` - Sample plane definitions.
- `SRS.md` - Software requirements specification.
- `ALGORITHM.md` - Algorithm design and explanation.
- `README.md` - Project overview and instructions.
