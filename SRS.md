# Software Requirements Specification (SRS)

## 1. Introduction

The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The application receives a 3D volume in NRRD format and a CSV file containing plane definitions. Each plane is represented by three or four points in 3D space.

For each plane, the application generates a 2D projection by sampling voxel values from the volume. The resulting images are combined into an MP4 video.

This document describes the functional requirements, input constraints, performance expectations, and testing strategy.

## 2. Overall Description

The application is implemented in Python and runs from the command line.

It supports two types of plane regions:

- Isosceles triangles defined by three points.
- Isosceles trapezoids defined by four points.

The application focuses on projection correctness, efficient processing, input validation, and code quality.

A graphical user interface is outside the scope of this project.

## 3. Functional Requirements

### FR-01: Read NRRD Data

The application shall read a 3D volume from an NRRD file.

The volume dimensions shall satisfy:

1 ≤ sx, sy, sz < 1024

Supported voxel data types are unsigned 8-bit, 16-bit, and 32-bit integers.

Unsupported dimensions or data types shall be rejected with a clear error message.

### FR-02: Read Plane Coordinates

The application shall read plane definitions from a CSV file.

Each row shall contain:

- 9 numeric values representing three 3D points.
- 12 numeric values representing four 3D points.

Each point consists of three coordinates (x, y, z).

The application shall process the plane definitions in their original CSV order.

### FR-03: Triangle Validation

For three points (a, b, c), the application shall verify that:

- The distances dist(a,b) and dist(a,c) are approximately equal.
- The triangle has nonzero side lengths.
- The three points are not collinear.

A numerical tolerance may be used to account for floating-point calculations.

Invalid triangle definitions shall be reported.

### FR-04: Trapezoid Validation

For four points defining a trapezoid, the application shall verify that:

- The points are coplanar.
- The two bases are parallel.
- The two legs have approximately equal lengths.
- The region is non-degenerate and does not self-intersect.

The point ordering and geometric conventions shall be defined in the algorithm documentation.

Invalid trapezoid definitions shall be reported.

### FR-05: Generate 2D Projections

For each valid plane definition, the application shall generate a 2D matrix.

Sampling positions shall be calculated using the projection algorithm described in `ALGORITHM.md`.

Nearest-neighbor sampling shall be used to obtain voxel values at the calculated positions.

The output dimensions and pixel positions shall follow the documented algorithm.

### FR-06: Out-of-Bounds Sampling

When a sampling position falls outside the 3D volume, the corresponding output pixel shall be assigned zero.

Out-of-bounds sampling shall not terminate the projection process.

### FR-07: Invalid Plane Handling

The application shall detect invalid geometric plane definitions.

The implementation may use an error frame to represent an invalid plane while continuing to process the remaining valid planes.

The selected behavior shall be documented and tested.

### FR-08: MP4 Video Generation

The application shall generate an MP4 video containing the projection results.

Frames shall follow the order of the plane definitions in the CSV file.

The generated images shall be converted into a format suitable for video encoding.

### FR-09: Command-Line Interface

The application shall support the following command:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The arguments represent:

- `file.nrrd`: Input volumetric data.
- `file.csv`: Plane coordinates.
- `file.mp4`: Output video.

### FR-10: Input Validation

The application shall detect and report:

- Missing or unreadable input files.
- Unsupported NRRD data.
- Incorrect CSV row lengths.
- Non-numeric or invalid coordinate values.
- Invalid geometric plane definitions.

Errors shall be reported clearly, according to the application's documented error-handling strategy.

## 4. Non-Functional Requirements

### NFR-01: Performance

For a 500 × 500 × 500 volume containing byte values, the assignment requires a processing rate above 30 projection frames per second.

The expected performance target is approximately 100 FPS or higher.

Performance shall be measured using a documented benchmark.

Projection processing time should be distinguished from file loading and video encoding time.

### NFR-02: Correctness

The application shall produce projection matrices containing voxel values sampled according to the documented algorithm.

Identical inputs shall produce consistent projection results.

### NFR-03: Stability

The application shall handle invalid inputs without unexpected failures.

Unrecoverable errors shall be reported with meaningful messages.

### NFR-04: Code Quality

The implementation should separate the responsibilities of:

- Input reading.
- Geometry validation.
- Projection calculations.
- Video generation.

The code should be readable, maintainable, and testable.

### NFR-05: Testability

The main components shall support independent testing.

Tests should cover valid inputs, invalid inputs, boundary conditions, and performance.

## 5. Testing Strategy

The testing strategy includes:

- Valid triangle projections.
- Valid trapezoid projections.
- Known voxel values and expected output matrices.
- Constant-value volumes.
- Sampling positions outside the volume.
- Degenerate or invalid plane definitions.
- Incorrect or missing input files.
- Verification of video frame ordering.
- Verification of the selected invalid-plane handling behavior.
- Performance measurements on a large volume.

The results shall be documented and compared with the expected behavior.

## 6. Input and Output

### Input

- A 3D volumetric NRRD file.
- A CSV file containing plane coordinates.

### Output

An MP4 video containing projection frames in the order specified by the CSV file.

Invalid planes shall be handled according to the documented error-handling strategy.

## 7. Completion Criteria

The project is considered complete when:

- Supported NRRD files are processed correctly.
- Triangle and trapezoid definitions are validated correctly.
- Generated projections match the expected sampled values.
- The command-line interface works as specified.
- MP4 frames follow the CSV order.
- The implemented error-handling behavior is tested.
- Tests are executed and their results documented.
- Performance is measured against the assignment requirements.
- The repository contains the implementation, documentation, tests, and example output.
