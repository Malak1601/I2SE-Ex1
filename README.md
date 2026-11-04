# 3D Medical Volume Plane Projection

## Problem Statement

The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The input consists of a 3D matrix containing voxel values and a CSV file defining planes using three or four 3D points. For each plane, the program calculates sampling positions inside the volume and uses the sampled values to generate a 2D image.

The main challenge is to design and implement the projection algorithm correctly and efficiently, while handling different plane orientations, volume boundaries, and invalid inputs.

## Project Scope

The project includes:

- Reading 3D volume data from NRRD files.
- Reading plane coordinates from a CSV file.
- Supporting valid isosceles triangles and isosceles trapezoids.
- Validating plane coordinates and geometric conditions.
- Generating 2D projections using nearest-neighbor sampling.
- Assigning zero to sampling positions outside the volume.
- Combining the generated images into an MP4 video.
- Testing the correctness and performance of the projection algorithm.

The project focuses on the projection algorithm, its design, performance, and code quality. It does not aim to develop a complete medical imaging application.

## Input and Output

The program uses three command-line arguments:

1. **NRRD file:** Contains the 3D volumetric data.
2. **CSV file:** Contains plane coordinates. Each row defines a plane using three or four 3D points.
3. **MP4 file:** The output video containing one frame for each plane, following the order of the CSV rows.

Example:

```bash
python Ex0.py test.nrrd test.csv output.mp4
```

## Projection Algorithm

The projection algorithm generates a 2D image by sampling points along a plane inside the 3D volume.

For a triangular plane, the three points must form an isosceles triangle, where the distances from the first point to the other two points are equal.

The algorithm moves along the two sides of the triangle. At each step, it samples the points between the corresponding positions on these sides and stores their values in the output image.

A similar approach is used for a valid isosceles trapezoid.

Nearest-neighbor sampling is used to convert continuous 3D coordinates into voxel indices. Sampling positions outside the volume are assigned a value of zero.

The detailed algorithm and its design decisions are described in [ALGORITHM.md](ALGORITHM.md).

## Software Requirements

The functional and non-functional requirements are described in [SRS.md](SRS.md).

## Testing

The project includes tests for:

- Valid and invalid plane definitions.
- Triangle and trapezoid geometry.
- Sampling positions inside and outside the volume.
- Projection output dimensions and values.
- Handling invalid inputs.

The repository includes `test_extra.py` for additional tests, along with `test.nrrd` and `test.csv` as test inputs.

## Performance

The assignment requires efficient projection of large 3D volumes, with a minimum target of more than 30 frames per second.

Performance should be evaluated by measuring the time required to generate projection frames, separately from MP4 encoding.

The measured results depend on the input volume, plane dimensions, and hardware used.

## Repository Files

- `Ex0.py` – Main Python implementation.
- `README.md` – Project description and instructions.
- `SRS.md` – Software requirements specification.
- `ALGORITHM.md` – Detailed projection algorithm.
- `test_extra.py` – Additional tests.
- `test.nrrd` – Test volume.
- `test.csv` – Test plane coordinates.
- `output.mp4` – Generated projection video.
- `output_large_preview.mp4` – Additional projection preview.
- `.gitignore` – Git ignore rules.

## Experiment and Results

The project includes generated MP4 files to demonstrate the projection process.

The experiment should evaluate projection correctness, output dimensions, and execution time using the selected NRRD dataset and plane coordinates.

The final experimental results should include the tested volume dimensions, number of generated frames, measured projection time, calculated FPS, and a short description of the output.
