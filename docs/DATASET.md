Dataset Description
1. Overview
This project uses three-dimensional NRRD volumes and CSV files containing geometric plane definitions. Small synthetic data supports reproducible demonstrations and exact-value tests; MRI, Croissant, and Onion volumes support experiments on larger datasets. The projection benchmark creates its own synthetic volume in memory.

The program interprets CSV coordinates as voxel-index coordinates. It does not apply physical-space transformations from NRRD metadata.
2. Reproducible small demonstration
The small demonstration uses the following files:
File	Purpose
data/demo_small.nrrd	Small synthetic 3D volume, shape 16 × 16 × 16
data/demo_small.csv	Two plane definitions for a complete command-line demonstration


Run from the project root:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
In the recorded run, the program processed two entries and saved results/demo_small.mp4. The projection shapes were (10, 16) and (10, 11), with 87 and 110 nonzero pixels respectively. A nonempty first frame was also extracted and inspected. At 30 encoded frames per second, a two-frame video lasts approximately 0.067 seconds; extracting a frame is more useful than watching such a short video.

The demo files were added after the earlier project archive was prepared. Confirm that both files are present in the final GitHub repository before describing this command as reproducible from a fresh clone.
3. MRI dataset
An MRHead MRI volume associated with 3D Slicer sample data is used for visual projection experiments. The project includes MRI-related CSV definitions, including:
- data/MRHead_demo.csv — a small MRI demonstration sequence.
- data/mri_full.csv — a longer MRI projection sequence.
The large MRI NRRD file is not assumed to be included in Git. One documented local example is:
python Ex0.py data/mri_uint16.nrrd data/mri_full.csv results/mri_full.mp4
This command requires the corresponding NRRD file to be placed at data/mri_uint16.nrrd locally. File names and coordinates should be checked against the actual downloaded dataset before running the command.
4. Croissant and Onion datasets
Additional datasets used in the experiments are:
Dataset	Reported volume dimensions	Reported data type	Reference CSV	Plane definitions
Croissant	500 × 500 × 500	uint8	data/croissant_reference.csv	100
Onion	256 × 256 × 130	uint8	data/onion_reference.csv	120


The reference CSVs were obtained from the supplementary assignment dataset. The project also includes data/croissant.csv and data/onion.csv, each defining three manually selected orthogonal rectangular planes.

The earlier experiment report records reference videos named results/croissant_reference.mp4 and results/onion_reference.mp4, plus three-plane videos. These are recorded experiment outputs, not guaranteed repository downloads. Confirm that the videos actually exist in the submitted repository before adding clickable links to them.
5. Other CSV and test data
File or source	Purpose
data/Ex0_lecturer.csv	Plane definitions based on lecturer examples
data/test.csv	Small CSV input for development/testing
tests/	Automated tests that construct known-value synthetic arrays and exercise validation and projection behavior


Each valid plane is defined by either three points (an isosceles triangle) or four points (an isosceles trapezoid). The parser supports the lecturer's point-count-prefixed CSV format (3 or 4) and coordinate-only rows.

Do not refer to data/test.nrrd as a bundled file: it was not present in the project archive reviewed for this documentation update. Use data/demo_small.nrrd for the small end-to-end example, once its presence in the final repository has been confirmed.
6. Performance dataset
The benchmark command is:
python Ex0.py --performance
It creates an in-memory 500 × 500 × 500 uint8 volume, performs a compilation warm-up, and times ten projection computations. No separate benchmark NRRD file is required.

The latest recorded run reported approximately 0.00141 seconds per projection, or 710.91 projection FPS. This measures projection computation only; it excludes NRRD loading, MP4 encoding, and the initial Numba compilation.
7. Dataset availability and reproduction
The large MRI, Croissant, and Onion NRRD volumes are kept separately from the source repository because of their size. The supplementary dataset folder provided for the assignment is:

https://drive.google.com/drive/folders/1koJ83uaeMYdJt6AwvVlmMJk_wzczvmmG

To reproduce a larger experiment, obtain the corresponding NRRD volume, place it in the local data/ directory, select its matching CSV, and run:
python Ex0.py <volume.nrrd> <planes.csv> <output.mp4>
Generated MP4 files belong in results/. Their existence in a local workspace does not establish that they are tracked in Git. The final submission should contain the required source files, relevant small reproducible data, and documented access to external large datasets.
8. Limitations
- Synthetic known-value arrays are useful for exact numerical assertions but do not replace experiments on real volumes.
- Some larger dataset dimensions and outputs above are recorded from previous experiment runs; they should be rechecked against the actual files if experiments are repeated.
- Coordinates are interpreted in voxel-index space rather than physical-space units.
- Projection-only FPS is not the same as complete NRRD-to-MP4 throughput.
See [README](../README.md), [Testing](TESTING.md), and [Experiment](EXPERIMENT.md) for commands, verification details, and measured results.