# Dataset Description

## 1. Overview

This project uses 3D NRRD volumes and CSV files containing plane coordinates to test and demonstrate the projection algorithm.

The datasets are used to verify projection correctness, geometry validation, boundary handling, and performance.

## 2. NRRD Data

### MRI Volume

The project uses an MRHead MRI volume associated with the 3D Slicer sample data.

This dataset provides real volumetric data for demonstrating projections on different planes.

The MRI data is used for the video demonstration.

### Synthetic Test Volume

A small synthetic NRRD volume is included in the project:

`data/test.nrrd`

Synthetic volumes with known voxel values are also created during automated testing. These allow the expected projection values to be checked directly.

### Performance Dataset

The performance benchmark generates a synthetic unsigned 8-bit volume with dimensions:

`500 × 500 × 500`

This volume is created in memory by the benchmark and is not stored as a separate NRRD file.

## 3. CSV Plane Definitions

The `data/` directory contains CSV files used to define projection regions.

| File | Purpose |
|---|---|
| `Ex0_lecturer.csv` | Plane definitions based on the lecturer's examples |
| `MRHead_demo.csv` | Plane definitions used for the MRI demonstration |
| `test.csv` | Small sample input for testing |
| `test.nrrd` | Small synthetic volume |

Each CSV entry describes either an isosceles triangle using three 3D points or an isosceles trapezoid using four 3D points.

The lecturer's CSV format includes a leading point count of `3` or `4`.

## 4. Input Validation

The program validates the NRRD volume dimensions and data type before processing.

For each CSV entry, it checks the number of coordinates, numerical values, and geometric validity of the region.

Invalid plane definitions are handled by generating marked error frames in the demonstration video.

## 5. Reproducibility

The repository contains the program, sample CSV files, automated tests, and generated demonstration output.

The main execution command is:

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

The performance experiment can be repeated using:

```bash
python Ex0.py --performance
```

The results and benchmark measurements are documented in `docs/EXPERIMENT.md`.

## 6. Dataset Limitations

The MRI volume is used for visual demonstration, while small synthetic volumes are used for exact numerical correctness tests.

The synthetic performance benchmark measures projection computation separately from file loading and video encoding.

The performance results therefore do not represent the complete time required to generate a video from an MRI file.