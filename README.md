# I2SE-Ex1

3D Medical Volume Plane Projection

## Problem Statement

The goal of this project is to extract a 2D image from a 3D volume, such as an MRI scan.

The input is a 3D matrix containing voxel values and a plane defined by three or four points. The program uses these points to sample values from the volume and generate the corresponding 2D image.

## Project Scope

The project includes:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from a CSV file.
- Generating a 2D image for each plane using the projection algorithm.
- Supporting the triangle and trapezoid cases described in the assignment.
- Saving the generated images as frames in an MP4 video.
- Testing the correctness and performance of the implementation.

The project focuses on the projection algorithm and its performance rather than building a graphical user interface.

## Requirements

- Python 3
- NumPy
- pynrrd
- imageio
- imageio-ffmpeg

Install the required libraries using:

```bash
python3 -m pip install numpy pynrrd imageio imageio-ffmpeg
```

## How to Run

Run the program using:

```bash
python3 Ex0.py file.nrrd file.csv file.mp4
```

The arguments are:

- `file.nrrd`: Input 3D volume.
- `file.csv`: CSV file containing the triangle or trapezoid coordinates.
- `file.mp4`: Output video file.

Each CSV row contains 9 values for a triangle or 12 values for a trapezoid. Each group of three values represents a 3D point.

To run the included example:

```bash
python3 Ex0.py test.nrrd test.csv output.mp4
```

## Testing

The project includes basic projection tests and additional tests for valid and invalid inputs.

Run the basic tests:

```bash
python3 Ex0.py --test
```

Run the additional tests:

```bash
python3 test_extra.py
```

The additional tests cover constant volume data, sampling outside the volume, invalid triangles, and invalid trapezoids.

## Performance Benchmark

Run the performance test:

```bash
python3 Ex0.py --performance
```

The benchmark measures the processing speed of the triangle projection algorithm on a 500 × 500 × 500 volume.

## Performance Experiment

The performance of the triangle projection algorithm was measured using a 3D volume of size 500 × 500 × 500.

The benchmark used an isosceles triangle with the following vertices:

- A = (0, 0, 0)
- B = (400, 0, 0)
- C = (0, 400, 0)

The projection was executed 10 times, after one warm-up run. Execution time was measured using `time.perf_counter()`.

### Results

| Metric | Result |
|---|---|
| Volume dimensions | 500 × 500 × 500 |
| Number of measured projections | 10 |
| Average processing time per projection | 0.0223 seconds |
| Projection processing speed | 44.84 FPS |
| Minimum required speed | 30 FPS |
| Expected performance target | 100 FPS |

### Conclusion

The measured processing speed was 44.84 FPS, exceeding the minimum requirement of 30 FPS but remaining below the expected target of 100 FPS.

These results apply to the tested triangle configuration and execution environment. They do not guarantee the same performance for every possible input.

## Dataset

The repository includes `test.nrrd`, a small synthetic 3D volume used to verify the projection algorithm.

The file `test.csv` contains example triangle and trapezoid coordinates used to generate the output frames.

A separate synthetic volume of size 500 × 500 × 500 was used for the performance benchmark.

## Testing Strategy

The implementation was tested using:

- Basic triangle and trapezoid projection tests with expected output values.
- A constant-volume test.
- Sampling outside the volume boundaries.
- Invalid triangle and trapezoid inputs.
- A crossed-trapezoid regression test.
- A performance benchmark using 10 measured projections after one warm-up run.

The basic and additional tests passed.

To run the tests:

```bash
python3 Ex0.py --test
python3 test_extra.py
```

## Demo and Experiment Output

To reproduce the example:

```bash
python3 Ex0.py test.nrrd test.csv output.mp4
```

The program reads the 3D volume and the coordinates from the CSV file, generates one projection per region, and saves the resulting frames in CSV order.

The repository includes:

- `output.mp4` — the generated projection video.
- `output_large_preview.mp4` — an enlarged preview for easier viewing.

The latest performance measurement was 43.87 FPS on a 500 × 500 × 500 synthetic volume, exceeding the minimum requirement of 30 FPS. The earlier measurement was 44.84 FPS.

The performance results measure projection processing rather than total file-loading and video-encoding time.
