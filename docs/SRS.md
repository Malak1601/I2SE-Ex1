# Software Requirements Specification (SRS)

## Ex1 – 3D Volume Plane Projection

### 1. Introduction

#### 1.1 Purpose

The purpose of this project is to generate 2D images from a 3D volume, such as an MRI scan.

The program receives a 3D volume in NRRD format and a CSV file containing a list of planes. Each plane is defined by three or four points in 3D space.

For each valid plane, the program calculates sampling positions, extracts voxel values from the volume, and generates a 2D image. The images are then combined into an MP4 video.

This document describes the software requirements, input constraints, geometric validation, output behavior, performance expectations, and testing strategy.

#### 1.2 Scope

The application is implemented in Python and runs from the command line.

It supports two types of regions:

- Isosceles triangles defined by three points.
- Isosceles trapezoids defined by four points.

The project focuses on correct projection, input validation, efficient processing, and reliable video generation.

A graphical user interface is not required.

### 2. Overall Description

The program receives three command-line arguments:

1. An input NRRD volume.
2. A CSV file containing plane coordinates.
3. An output MP4 filename.

Each CSV plane definition is processed in its original order.

The application uses nearest-neighbor sampling to obtain voxel values. Samples outside the volume are assigned zero.

Invalid individual plane definitions are reported and represented by error frames, allowing the program to continue with subsequent planes.

### 3. Functional Requirements

#### FR-01: Read NRRD Data

The program shall read a three-dimensional volume from an NRRD file.

The dimensions must satisfy:

`1 <= sx, sy, sz < 1024`

The required voxel types are unsigned 8-bit, 16-bit, and 32-bit integers.

The implementation also accepts signed 8-bit, 16-bit, and 32-bit integer arrays when all values are nonnegative, converting them to the corresponding unsigned type.

Volumes with unsupported dimensions or data types shall be rejected with an error message.

#### FR-02: Read Plane Coordinates

The program shall read plane definitions from a CSV file.

Each plane contains:

- Three 3D points (9 coordinates) for a triangle.
- Four 3D points (12 coordinates) for a trapezoid.

Each point consists of three coordinates: `(x, y, z)`.

The CSV reader supports:

- Rows containing only coordinates.
- Rows beginning with the number of points (`3` or `4`).
- The lecturer's CSV header format.

The program shall preserve the order of plane definitions in the CSV file.

Empty rows are ignored.

Malformed nonempty rows are reported as invalid entries.

#### FR-03: Triangle Validation

For three points `(a, b, c)`, the program shall verify that:

- The lengths `dist(a,b)` and `dist(a,c)` differ by less than `0.001`.
- Both sides have nonzero lengths.
- The three points are not collinear.

Invalid triangle definitions shall raise a `ValueError` during geometric validation.

#### FR-04: Trapezoid Validation

For four points `(a, b, c, d)`, the program shall verify that:

- The points are coplanar.
- The two bases are parallel and have the same direction.
- The two legs have approximately equal lengths.
- The region has nonzero area.
- The geometry does not produce an invalid crossing arrangement.

The point order used by the implementation is:

- First leg: `a → b`
- Second leg: `c → d`
- First base: `a → c`
- Second base: `b → d`

According to the assignment, the first base must not be longer than the second base.

**Implementation note:** This final base-length condition must also be enforced in `validate_trapezoid()` before the implementation can be considered fully compliant.

#### FR-05: Generate 2D Projections

For each valid plane, the program shall generate a two-dimensional matrix containing sampled voxel values.

The projection algorithm advances along the two equal-length legs and calculates sampling positions between the corresponding points.

Nearest-neighbor sampling is used to obtain values from the volume.

The implementation stores the resulting image as a two-dimensional NumPy array.

The detailed sampling procedure and output dimensions are described in `ALGORITHM.md`.

#### FR-06: Out-of-Bounds Sampling

When a sampled voxel index is outside the volume dimensions, the corresponding output pixel shall be assigned zero.

Out-of-bounds samples shall not terminate the projection process.

#### FR-07: Invalid Plane Handling

The program shall detect malformed CSV entries and invalid geometric definitions.

When an individual plane is invalid, the application shall:

1. Print an informative error message containing the CSV line number.
2. Generate a visible error frame.
3. Continue processing the remaining CSV entries.

This preserves the order and number of frames corresponding to nonempty CSV entries.

Unrecoverable errors, such as an unreadable NRRD file, may terminate execution.

#### FR-08: MP4 Video Generation

The program shall generate an MP4 video containing the projection results.

The video shall preserve the CSV order.

Projection matrices shall be converted to 8-bit grayscale images for encoding.

If projections have different dimensions, they shall be placed on a common canvas.

The current implementation uses H.264 encoding through ImageIO and supports an enlarged preview mode.

The normal output uses one encoded frame per CSV entry. Preview mode repeats frames to make them easier to inspect.

#### FR-09: Command-Line Interface

The main command is:

`python3 Ex0.py file.nrrd file.csv file.mp4`

The arguments represent:

- `file.nrrd`: Input 3D volume.
- `file.csv`: Plane definitions.
- `file.mp4`: Output video.

The implementation also supports:

`python3 Ex0.py --test`

Runs the built-in basic projection tests.

`python3 Ex0.py --performance`

Runs a projection performance benchmark.

#### FR-10: Input Validation

The program shall detect and report:

- Missing or unreadable input files.
- Unsupported volume dimensions or data types.
- Incorrect CSV row lengths.
- Non-numeric or non-finite coordinates.
- Invalid triangle definitions.
- Invalid trapezoid definitions.

Errors affecting individual plane definitions shall be handled using error frames when processing can continue.

### 4. Non-Functional Requirements

#### NFR-01: Performance

For a `500 × 500 × 500` volume containing unsigned 8-bit values, the assignment requires a projection computation rate greater than 30 FPS.

The expected performance target is approximately 100 FPS.

The implementation uses Numba JIT compilation to accelerate the projection loop.

Performance measurements shall exclude the initial Numba compilation warm-up and distinguish projection computation from NRRD loading and MP4 encoding.

The actual measured results must be documented separately. The presence of a benchmark does not by itself establish that the performance target has been achieved.

#### NFR-02: Correctness

The program shall generate projection matrices using the documented sampling algorithm.

Identical inputs shall produce consistent projection results.

Known voxel values and expected output matrices shall be used to test correctness.

#### NFR-03: Robustness

The program shall handle invalid individual plane definitions without terminating the entire processing sequence.

Unrecoverable errors shall be reported with meaningful messages.

#### NFR-04: Code Quality

The implementation shall keep the following responsibilities identifiable:

- CSV reading and input validation.
- Geometry calculations.
- Projection generation.
- Frame conversion.
- Video encoding.
- Testing and performance measurement.

The current implementation organizes these responsibilities into separate functions within `Ex0.py`.

#### NFR-05: Testability

The implementation shall support independent testing of the main functions.

Tests should cover valid inputs, invalid inputs, numerical boundaries, expected voxel values, and performance.

### 5. Testing Strategy

The testing strategy includes the following cases:

- Valid isosceles triangles.
- Valid trapezoids and rectangles.
- Known voxel values and expected projection matrices.
- Samples outside the volume.
- Invalid triangle definitions.
- Trapezoid geometry validation.
- Numerical tolerance conditions.
- CSV parsing and invalid-row handling.
- Error-frame generation.
- Testing with an MRI NRRD volume.
- Performance measurement using a large volume.

The built-in tests can be executed using:

`python3 Ex0.py --test`

The performance benchmark can be executed using:

`python3 Ex0.py --performance`

Additional tests are maintained separately in `test_extra.py`.

The final verification should also confirm that the generated MP4 contains the expected number of frames in the correct order.

### 6. Input and Output

#### Input

- A three-dimensional NRRD volume.
- A CSV file containing plane definitions.

#### Output

- An MP4 video containing the projection results in CSV order.
- Terminal messages describing processed projections and errors.

Invalid individual plane definitions are represented by error frames.

### 7. Completion Criteria

The project is considered complete when:

1. Supported NRRD files are read correctly.
2. CSV plane definitions are processed in order.
3. Triangle and trapezoid geometry is validated according to the assignment.
4. Projection matrices contain the expected sampled voxel values.
5. Out-of-bounds samples are handled correctly.
6. Invalid individual planes produce error frames without stopping subsequent processing.
7. The command-line interface generates an MP4 video successfully.
8. The video preserves the expected frame count and order.
9. Correctness tests pass.
10. Performance is measured and compared with the assignment requirements.
11. The GitHub repository contains the implementation, documentation, tests, and relevant experiment results.
