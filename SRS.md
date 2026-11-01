# Software Requirements Specification (SRS)

## 1. Introduction

The goal of this project is to generate 2D images from 3D volume data, such as MRI scans. The program receives an NRRD file containing the volume and a CSV file containing plane coordinates. The resulting images are saved as frames in an MP4 video.

## 2. Overall Description

The program is a command-line application that processes a 3D volume and a list of plane regions.

Each region is defined by three points forming an isosceles triangle or four points forming an isosceles trapezoid.

The program samples voxel values from the specified regions to generate 2D images.

The main focus is on correct results, stable execution, efficient processing, and clear algorithm design.

## 3. Functional Requirements

**FR-01: Read NRRD Files**

The program shall read a 3D volume from an NRRD file.

The volume dimensions shall satisfy 1 ≤ sx, sy, sz < 1024, and voxel values shall be unsigned 8-bit, 16-bit, or 32-bit integers.

**FR-02: Read Plane Coordinates**

The program shall read a CSV file containing a list of triangle or trapezoid regions.

Each CSV row shall contain 9 numeric values for a triangle or 12 numeric values for a trapezoid, with every three values representing a 3D point.

**FR-03: Generate 2D Images**

The program shall generate a 2D image for each region by sampling values from the 3D volume according to the projection algorithm.

**FR-04: Supported Shapes**

The program shall support isosceles triangles and isosceles trapezoids as defined in the assignment.

**FR-05: Handle Out-of-Bounds Points**

If a sampled point is outside the 3D volume, the program shall use a value of zero.

**FR-06: Generate MP4 Output**

The program shall save the generated 2D images as frames in an MP4 video, preserving the order of the regions in the CSV file.

**FR-07: Command-Line Execution**

The program shall support the following command format:

`python Ex0.py file.nrrd file.csv file.mp4`

**FR-08: Input Validation**

The program shall validate the input volume, coordinate values, and supported shape conditions, and report errors for invalid inputs.

## 4. Non-Functional Requirements

**NFR-01: Performance**

For a 500 × 500 × 500 byte volume, the implementation must achieve more than 30 projection frames per second. The expected performance target is approximately 100 FPS.

**NFR-02: Correctness**

The generated images shall contain voxel values sampled according to the defined projection algorithm and documented sampling decisions.

**NFR-03: Stability**

The program should handle invalid inputs and file errors by reporting appropriate error messages.

**NFR-04: Code Quality**

The implementation should be organized into clear, reusable functions and be easy to read, test, and maintain.

## 5. Testing Requirements

The testing strategy shall cover:

- Valid triangle and trapezoid projections.
- Known voxel values and expected projection results.
- Constant-value volumes.
- Sampling outside the volume boundaries.
- Invalid triangle and trapezoid coordinates.
- Valid and invalid input files.
- Preservation of the CSV region order in the output video.
- Performance measurement using a 500 × 500 × 500 volume.

## 6. Input and Output

**Input:**

- An NRRD file containing a 3D volume.
- A CSV file containing triangle or trapezoid coordinates.

**Output:**

- An MP4 video containing one frame for each region, in the same order as the CSV file.
