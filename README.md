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