I2SE Ex1 — 3D Volume Plane Projection
Course: Introduction to Software Engineering (I2SE)
University: Ariel University
Overview
This project implements a command-line program that samples two-dimensional regions from a three-dimensional NRRD volume and writes the resulting frames to an MP4 video. Each nonempty CSV plane entry corresponds to one video frame, in input order. The supported regions are isosceles triangles and isosceles trapezoids.

The implementation emphasizes geometric correctness, explicit boundary handling, recoverable per-plane errors, reproducible testing, and efficient projection computation.
Requirements and installation
Use Python 3 and install the project dependencies from the repository root:
python -m pip install -r requirements.txt
The main dependencies are NumPy, pynrrd, imageio, and imageio-ffmpeg. Numba accelerates the projection loop when available; pytest is used for automated testing.
Input and output
python Ex0.py <volume.nrrd> <planes.csv> <output.mp4>
- NRRD: a three-dimensional array with dimensions 1 <= sx, sy, sz < 1024. Supported volume types are unsigned 8-, 16-, and 32-bit integers. Nonnegative signed integer data may also be converted to an unsigned representation.
- CSV: one triangle (three 3D points) or trapezoid (four 3D points) per populated row. The parser supports 9 or 12 coordinate values, as well as the lecturer's count-prefixed format (3 or 4) with its header and optional empty trailing cells.
- MP4: grayscale video at 30 FPS. A valid plane produces a projection; an invalid populated row produces a visibly marked error frame, allowing later rows to be processed.
Point order matters. For a triangle (a, b, c), a is the shared vertex of the two equal-length sides. For a trapezoid (a, b, c, d), the equal legs are a→b and c→d, and the bases are a→c and b→d.
Reproducible small example
The repository includes a small 16 × 16 × 16 demonstration volume and a two-plane CSV:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
This example was run locally: the program reported two nonempty projections and saved the MP4. The output has only two frames (approximately 0.067 seconds at 30 FPS), so it can appear to finish immediately in a video player. For visual inspection, the first frame can be extracted with:
python -c "import imageio.v2 as i; i.imwrite('results/demo_check.png', i.get_reader('results/demo_small.mp4').get_data(0))"
The extracted image shows a nonempty triangular projection.
Other datasets
Additional CSV definitions are provided under data/, including MRI, Croissant, and Onion examples. The corresponding large NRRD files may need to be supplied separately. To reproduce a larger experiment, use the appropriate local NRRD file and matching CSV:
python Ex0.py data/mri_uint16.nrrd data/mri_full.csv results/mri_full.mp4
This MRI command assumes that data/mri_uint16.nrrd is present locally. Do not expect it to work on a fresh clone unless that dataset has been provided.
Projection algorithm
1. Read and validate the NRRD volume and CSV rows.
2. Validate the geometric constraints: nondegenerate isosceles triangles, or coplanar trapezoids with parallel bases and equal-length legs. Length comparisons use a tolerance of 0.001.
3. Advance along the two equal-length sides or legs and sample positions across each row of the region.
4. For every sampled 3D position, check the volume boundaries and use nearest-neighbor voxel sampling. Positions outside the volume contribute zero.
5. Store each projection as a 2D matrix; for MP4 output, scale higher-bit-depth intensities into 8-bit grayscale and pad frames to a common video size.
6. For invalid CSV entries or plane geometry, create a marked error frame without discarding subsequent entries.
The projection loop uses Numba JIT acceleration when installed. The implementation interprets coordinates as voxel coordinates, not NRRD physical-space coordinates. See [Algorithm documentation](docs/ALGORITHM.md) for the implementation details.
Testing
Run the full test suite from the project root:
python -m pytest -q
Latest local result (7 November 2026): 52 passed in 6.70 seconds. This includes the lecturer-requirements tests in tests/test_lecturer_requirements.py, alongside the CSV, geometry, projection, video, and extra tests.

The built-in checks can also be run with:
python Ex0.py --test
Testing covers known voxel values, geometric validity, CSV parsing, boundaries, error handling, and video output. See [Testing documentation](docs/TESTING.md).
Performance experiment
Run the computation-only benchmark:
python Ex0.py --performance
The benchmark allocates a synthetic 500 × 500 × 500 uint8 volume, warms up the projection function, and times ten triangle projections.
Measurement	Latest local result
Volume	500 × 500 × 500, uint8
Measured projections	10
Average computation time per projection	0.00141 s
Projection computation rate	710.91 FPS
Assignment minimum	Above 30 FPS
Assignment expected target	Approximately 100 FPS


Measurement scope: these numbers exclude NRRD file loading, MP4 encoding, and the initial Numba compilation. They are not the end-to-end video export FPS. Performance varies with hardware and projection geometry. See [Experiment documentation](docs/EXPERIMENT.md).
Project organization
I2SE-Ex1/
├── Ex0.py
├── README.md
├── requirements.txt
├── data/
│   ├── demo_small.nrrd
│   ├── demo_small.csv
│   └── ... other CSV definitions and local datasets
├── docs/
│   ├── SRS.md
│   ├── ALGORITHM.md
│   ├── DATASET.md
│   ├── TESTING.md
│   └── EXPERIMENT.md
├── tests/
│   ├── test_csv.py
│   ├── test_geometry.py
│   ├── test_projection.py
│   ├── test_video.py
│   ├── test_extra.py
│   └── test_lecturer_requirements.py
└── results/
    └── ... generated MP4 files and optional inspection images
Documentation: [Software requirements](docs/SRS.md) · [Algorithm](docs/ALGORITHM.md) · [Datasets](docs/DATASET.md) · [Testing](docs/TESTING.md) · [Experiments](docs/EXPERIMENT.md).
Design decisions and limitations
- Nearest-neighbor sampling is used instead of interpolation.
- Samples outside the volume are zero; invalid plane definitions are represented by marked error frames.
- MP4 output is 8-bit grayscale, so original 16-/32-bit voxel intensities are scaled for display.
- The video uses one frame per CSV entry; an output name ending with preview.mp4 enables an enlarged preview for inspecting small projections.
- A safety limit on the number of projection pixels protects against excessive memory use; very large plane definitions may be rejected.
- No GUI, GPU acceleration, or physical-coordinate transformation based on NRRD metadata is included.
- The measured benchmark reports projection computation only, not full file-to-video throughput.
Conclusion
The project provides a tested implementation of 3D-volume plane sampling for isosceles triangles and trapezoids, including geometry validation, recoverable input errors, MP4 output, and an accelerated projection loop. The local benchmark exceeded the assignment's projection-computation target under the reported test conditions.