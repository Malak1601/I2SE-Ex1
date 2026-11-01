# Software Requirements Specification (SRS)

## 1. Introduction

The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The program receives an NRRD file containing a 3D volume and a CSV file containing a list of plane coordinates. Each plane is used to generate a 2D image by sampling values from the volume.

The resulting images are saved as frames in an MP4 video.

This document describes the functional requirements, performance expectations, input validation, and testing requirements of the application.

## 2. Overall Description

The program is a command-line application written in Python.

It processes a 3D matrix and a sequence of plane regions defined by three or four points in 3D space.

The supported regions are:

- An isosceles triangle defined by three points.
- An isosceles trapezoid defined by four points.

The program calculates sampling positions for each region and uses the corresponding voxel values to construct a 2D image.

The main focus is on correct results, efficient processing, stable execution, and clear code structure.

A graphical user interface is not required.

## 3. Functional Requirements

### FR-01: Read NRRD Files

The program shall read a 3D volume from an NRRD file.

The volume dimensions shall satisfy:

1 ≤ sx, sy, sz < 1024

Each voxel shall contain an unsigned 8-bit, 16-bit, or 32-bit integer value.

The program shall reject unsupported volume dimensions or data types.

### FR-02: Read Plane Coordinates

The program shall read a CSV file containing a list of plane definitions.

Each CSV row shall contain:

- 9 numeric values for a triangle.
- 12 numeric values for a trapezoid.

Every three consecutive values represent a 3D point (x, y, z).

Triangle points shall be provided in the order (a, b, c).

Trapezoid points shall be provided in the order (a, b, c, d), where (a, b) and (d, c) are the two legs, and (a, d) and (b, c) are the two bases.

The program shall preserve the order of the plane definitions.

### FR-03: Validate Triangle Coordinates

For a triangle defined by points (a, b, c), the two sides starting at point a must have approximately equal lengths.

The required condition is:

|dist(a,b) - dist(a,c)| < 0.001

The triangle must also be non-degenerate, meaning that its points must not be collinear and its required sides must have nonzero lengths.

Invalid triangles shall raise an appropriate exception during validation.

### FR-04: Validate Trapezoid Coordinates

For a trapezoid defined by points (a, b, c, d), the program shall validate the following conditions:

- The two legs (a,b) and (d,c) have approximately equal lengths, with an absolute difference smaller than 0.001.
- The length of the base (a,d) is not greater than the length of the base (b,c).
- All four points lie on the same plane.
- The two bases are parallel.
- The shape is not degenerate or self-intersecting.

Invalid trapezoids shall raise an appropriate exception during validation.

### FR-05: Generate 2D Projections

The program shall generate a 2D matrix for each valid plane definition.

The projection algorithm shall calculate sampling positions in the 3D volume based on the plane coordinates.

Nearest-neighbor sampling shall be used to obtain voxel values from the volume.

The output matrix dimensions and coordinate mapping shall follow the documented projection algorithm.

### FR-06: Handle Out-of-Bounds Sampling

When a sampling position is outside the 3D volume, the corresponding output pixel shall receive a value of zero.

Out-of-bounds sampling alone shall not cause the projection process to stop.

### FR-07: Handle Invalid Planes

When a plane definition does not satisfy the required geometric conditions, the validation or projection logic shall raise an exception.

The demo application shall handle this exception and generate a visible error frame for the invalid plane.

The program shall continue processing the remaining valid planes.

An invalid plane shall not prevent the generation of the complete output video.

### FR-08: Generate MP4 Output

The program shall save the generated projections as an MP4 video.

Each plane definition shall correspond to one output frame, including an error frame when a plane is invalid.

The order of the frames shall match the order of the plane definitions in the CSV file.

The program shall convert the generated 2D matrices into video-compatible pixel values.

### FR-09: Command-Line Execution

The program shall support the following command format:

`python Ex0.py file.nrrd file.csv file.mp4`

Where:

- `file.nrrd` is the input 3D volume.
- `file.csv` contains the plane definitions.
- `file.mp4` is the output video.

### FR-10: Input and File Validation

The program shall check the validity of input files and coordinate values.

It shall detect errors such as:

- Missing or unreadable files.
- Unsupported NRRD data.
- Invalid coordinate values.
- Incorrect CSV row lengths.
- Invalid geometric plane definitions.

Errors that prevent the application from processing the input shall be reported clearly.

Plane-specific errors shall be handled according to FR-07.

## 4. Non-Functional Requirements

### NFR-01: Performance

For a 500 × 500 × 500 volume containing byte values, the implementation shall meet the assignment's minimum processing requirement of 30 projection frames per second.

The expected performance target is at least 100 projection frames per second.

Performance shall be measured using a defined benchmark and documented execution environment.

The benchmark shall distinguish projection processing time from file loading and video encoding time.

### NFR-02: Correctness

The generated 2D matrices shall contain voxel values sampled according to the documented projection algorithm.

The implementation shall produce consistent results for the same input data and plane coordinates.

### NFR-03: Stability

The application shall handle invalid plane definitions without interrupting the processing of other valid planes.

Unrecoverable input and output errors shall be reported with meaningful error messages.

### NFR-04: Code Quality

The implementation shall be organized into clear and reusable functions or components.

Input handling, geometry validation, projection calculations, and video generation should have separate responsibilities.

The code should be easy to understand, test, and maintain.

### NFR-05: Testability

The main parts of the implementation shall be testable independently.

The program shall include tests for valid inputs, invalid inputs, boundary conditions, and performance.

## 5. Testing Requirements

The testing strategy shall cover:

- Valid triangle projections.
- Valid trapezoid projections.
- Known voxel values and expected 2D outputs.
- Constant-value volumes.
- Sampling outside volume boundaries.
- Triangle coordinates within and outside the allowed tolerance.
- Degenerate and invalid triangles.
- Invalid and self-intersecting trapezoids.
- Missing or invalid input files.
- Invalid planes followed by valid planes.
- Error frame generation.
- Preservation of CSV order in the generated video.
- Performance measurements using a 500 × 500 × 500 volume.

The testing results shall be documented and compared with the expected behavior.

## 6. Input and Output

### Input

The application receives:

1. An NRRD file containing a 3D volume.
2. A CSV file containing triangle or trapezoid coordinates.

### Output

The application produces an MP4 video containing a frame for every plane definition, in CSV order.

Valid planes produce projection frames.

Invalid geometric plane definitions produce error frames.

## 7. Completion Criteria

The implementation will be considered complete when:

1. Supported NRRD files are read correctly.
2. Triangle and trapezoid coordinates are processed according to the defined geometric conditions.
3. The generated projections produce the expected 2D matrix values.
4. Invalid planes are handled without stopping the processing of valid planes.
5. The generated MP4 preserves the required frame order.
6. The test cases pass.
7. Performance is measured and compared against the assignment requirements.
8. The repository contains the source code, documentation, tests, and example output.
