# Software Requirements Specification (SRS)

## 1. Introduction

The goal of this project is to generate 2D images from 3D medical volume data. The program uses an NRRD file containing the volume and a CSV file containing plane coordinates. The resulting images are saved as frames in an MP4 video.

## 2. Overall Description

The program is a command-line application that processes a 3D volume and a list of planes.

Each plane is defined by three or four points in 3D space. The program samples voxel values along the specified plane to create a 2D image.

The main focus is on correct results, stable execution, and efficient processing.

## 3. Functional Requirements

**FR-01: Read NRRD Files**

The program shall read a 3D volume from an NRRD file and access its voxel values.

**FR-02: Read Plane Coordinates**

The program shall read a CSV file containing a list of planes, each defined by three or four 3D points.

**FR-03: Generate 2D Images**

The program shall generate a 2D image for each plane using the projection algorithm described in the assignment.

**FR-04: Supported Plane Shapes**

The program shall support the triangle and trapezoid cases described in the assignment.

**FR-05: Handle Out-of-Bounds Points**

If a sampled point is outside the 3D volume, the program shall use a value of zero.

**FR-06: Generate MP4 Output**

The program shall save the generated images as frames in an MP4 video, following the order of the planes in the CSV file.

**FR-07: Command-Line Execution**

The program shall support the following command format:

`python Ex0.py file.nrrd file.csv file.mp4`

## 4. Non-Functional Requirements

**NFR-01: Performance**

The program must process more than 30 frames per second for a 500 × 500 × 500 byte volume. The expected performance is around 100 FPS.

**NFR-02: Correctness**

The generated images shall contain voxel values sampled according to the defined projection algorithm.

**NFR-03: Stability**

The program should handle invalid inputs and file errors by reporting an appropriate error message.

**NFR-04: Code Quality**

The code should be organized into clear functions and be easy to read and maintain.

## 5. Testing Requirements

The program will be tested using different NRRD files and plane coordinates.

The tests will cover:

- Reading valid input files.
- Generating images for different plane positions.
- Handling points outside the 3D volume.
- Supporting the triangle and trapezoid cases.
- Checking the order of frames in the output video.
- Measuring the processing speed.

## 6. Input and Output

**Input:**

- An NRRD file containing a 3D volume.
- A CSV file containing a list of plane coordinates.

**Output:**

- An MP4 video containing one frame for each plane, in the same order as the CSV file.
