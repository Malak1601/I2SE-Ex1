Software Requirements Specification (SRS)
1. Introduction
The goal of this project is to generate 2D images from 3D volumetric data, such as MRI scans.

The application receives a 3D volume in NRRD format and a CSV file containing plane definitions. Each plane is defined by three or four points in 3D space.

For each plane, the application calculates sampling positions and generates a 2D projection using voxel values from the volume. The resulting images are combined into an MP4 video.

This document describes the functional requirements, input constraints, performance expectations, and testing strategy.

2. Overall Description
The application is implemented in Python and runs from the command line.

It supports two types of plane regions:

Isosceles triangles defined by three points.
Isosceles trapezoids defined by four points.
The application focuses on projection correctness, efficient processing, geometric validation, and code quality.

A graphical user interface is outside the scope of this project.

3. Functional Requirements
FR-01: Read NRRD Data
The application shall read a 3D volume from an NRRD file.

The volume dimensions shall satisfy:

1 ≤ sx, sy, sz < 1024

Supported voxel data types are unsigned 8-bit, 16-bit, and 32-bit integers.

The implementation also supports signed integer volumes of these bit depths when all values are nonnegative, by converting them to the corresponding unsigned type.

Unsupported dimensions or data types shall be rejected with an error message.

FR-02: Read Plane Coordinates
The application shall read plane definitions from a CSV file.

Each plane shall contain:

Three 3D points (9 coordinates) for a triangle.
Four 3D points (12 coordinates) for a trapezoid.
Each point consists of three coordinates (x, y, z).

The application supports two CSV formats:

Rows containing only the coordinates.
Rows beginning with the number of points (3 or 4), followed by the coordinates.
A header row in the lecturer's CSV format is supported.

Plane definitions shall be processed in their original CSV order.

FR-03: Triangle Validation
For three points (a, b, c), the application shall verify that:

The distances dist(a,b) and dist(a,c) are approximately equal.
The two sides have nonzero lengths.
The three points are not collinear.
A numerical tolerance is used to handle small floating-point differences.

Invalid triangle definitions shall be reported.

FR-04: Trapezoid Validation
For four points (a, b, c, d), the application shall verify that:

The points are coplanar.
The two bases are parallel and point in the same direction.
The two legs have approximately equal lengths.
The region has nonzero area.
The geometric arrangement is valid and does not produce crossing sides.
The point ordering used by the implementation is:

First leg: a → b
Second leg: c → d
Starting base: a → c
Ending base: b → d
Invalid trapezoid definitions shall be reported.

FR-05: Generate 2D Projections
For each valid plane definition, the application shall generate a 2D matrix.

The algorithm advances along the two equal-length sides and samples points between their corresponding positions.

Nearest-neighbor sampling shall be used to obtain voxel values.

The output dimensions and sampling positions shall follow the algorithm described in ALGORITHM.md.

FR-06: Out-of-Bounds Sampling
When a calculated voxel index falls outside the 3D volume, the corresponding output pixel shall be assigned zero.

Out-of-bounds sampling shall not terminate the projection process.

FR-07: Invalid Plane Handling
The application shall detect invalid geometric plane definitions and malformed CSV entries.

When an invalid plane is encountered, the implementation shall:

Report the error in the terminal.
Generate a visible error frame.
Continue processing the remaining CSV entries.
This preserves the number and order of output frames corresponding to the CSV entries.

FR-08: MP4 Video Generation
The application shall generate an MP4 video containing the projection results.

Frames shall follow the order of the CSV entries.

Projection matrices shall be converted into 8-bit grayscale images for video encoding.

When projection matrices have different dimensions, they shall be placed on a common canvas.

The implementation also supports an enlarged preview mode for easier visualization.

FR-09: Command-Line Interface
The application shall support the following command:

python3 Ex0.py file.nrrd file.csv file.mp4

The arguments represent:

file.nrrd: Input volume.
file.csv: Plane definitions.
file.mp4: Output video.
The application shall also provide commands for running basic tests and measuring projection performance.

FR-10: Input Validation
The application shall detect and report:

Missing or unreadable input files.
Unsupported volume dimensions or data types.
Incorrect CSV row lengths.
Non-numeric or non-finite coordinates.
Invalid triangle definitions.
Invalid trapezoid definitions.
Unrecoverable input errors shall terminate the program with an error message.

Invalid individual plane definitions shall be handled using error frames when processing can continue.

4. Non-Functional Requirements
NFR-01: Performance
For a 500 × 500 × 500 volume containing unsigned byte values, the assignment requires a projection rate greater than 30 frames per second.

The expected performance target is approximately 100 FPS.

The implementation uses Numba to accelerate the main projection loop.

Performance shall be measured using a documented benchmark after an initial compilation warm-up.

Projection computation time shall be measured separately from NRRD loading and MP4 encoding.

NFR-02: Correctness
The application shall produce projection matrices containing voxel values sampled according to the documented algorithm.

Identical inputs shall produce consistent results.

NFR-03: Stability
The application shall handle invalid plane definitions without terminating the entire processing sequence.

Unrecoverable errors shall be reported using meaningful messages.

NFR-04: Code Quality
The implementation shall separate the responsibilities of:

Input reading and validation.
Geometry calculations.
Projection generation.
Frame conversion.
Video encoding.
Testing and benchmarking.
The code should remain readable, maintainable, and testable.

NFR-05: Testability
The main components shall support independent testing.

Tests should cover valid inputs, invalid inputs, boundary conditions, known output values, and performance.

5. Testing Strategy
The testing strategy includes:

Valid triangle projections.
Valid trapezoid projections.
Rectangle projections.
Known voxel values and expected output matrices.
Constant-value volumes.
Sampling positions outside the volume.
Degenerate or invalid plane definitions.
Numerical tolerance checks.
CSV parsing and recovery from invalid rows.
Error-frame generation.
Testing with real MRI volume data.
Performance measurements on a large volume.
Additional verification should include checking the output video's frame count and order against the CSV entries.

The basic tests are available through Ex0.py --test, and additional tests are implemented in test_extra.py.

6. Input and Output
Input
A 3D volumetric NRRD file.
A CSV file containing plane coordinates.
Output
An MP4 video containing the projection results in CSV order.

Invalid plane definitions are represented by error frames.

7. Completion Criteria
The project is considered complete when:

Supported NRRD files are processed correctly.
Triangle and trapezoid definitions are validated.
Generated projections match expected sampled values.
The command-line interface works as specified.
The MP4 output preserves the intended frame order.
Invalid inputs are handled as documented.
Correctness tests are executed successfully.
Performance is measured against the assignment requirements.
The repository contains the implementation, documentation, tests, and required submission materials
