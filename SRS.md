# Software Requirements Specification (SRS)

## 1. Introduction

This project aims to generate 2D images from 3D medical volume data. The program receives an NRRD file and a CSV file containing plane coordinates, then generates an MP4 video with the resulting images.

## 2. Functional Requirements

**FR-01: Read NRRD Files**

The program shall read a 3D volume from an NRRD file and access its voxel values.

**FR-02: Read Plane Coordinates**

The program shall read a CSV file containing a list of planes, each defined by three or four 3D points.

**FR-03: Generate 2D Images**

The program shall generate a 2D image for each plane using the projection algorithm described in the assignment.

**FR-04: Support Different Plane Shapes**

The program shall support the isosceles triangle and trapezoid cases described in the assignment.

**FR-05: Handle Out-of-Bounds Points**

If a sampled point is outside the 3D volume, the program shall use a value of zero.

**FR-06: Generate MP4 Output**

The program shall save the generated images as frames in an MP4 video, following the order of the planes in the CSV file.

**FR-07: Command-Line Execution**

The program shall support the following command format:

`python Ex0.py file.nrrd file.csv file.mp4`

## 3. Non-Functional Requirements

**NFR-01: Performance**

The implementation must achieve more than 30 frames per second when processing a 500 × 500 × 500 byte volume. The expected performance is approximately 100 FPS.

**NFR-02: Correctness**

The generated images shall represent the sampled voxel values according to the defined projection algorithm.

**NFR-03: Stability**

The program should handle invalid inputs and unexpected errors
