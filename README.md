# I2SE Ex1 — 3D Volume Plane Projection

**Course:** Introduction to Software Engineering (I2SE)  
**University:** Ariel University

## Problem statement and scope

Given a three-dimensional raster volume `M` and a planar region specified by three or four points, compute a two-dimensional image by sampling the volume along that region. The assignment deliberately leaves implementation details open; this project documents the chosen sampling, validation, and output conventions.

The implementation is a Python command-line application supporting **isosceles triangles** and **isosceles trapezoids**. It emphasizes geometry validation, stable handling of invalid plane definitions, reproducible tests, and efficient projection computation. A GUI and transformations from NRRD physical-space metadata are outside the project scope.

## Installation

From the repository root, use Python 3 and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Dependencies include NumPy, pynrrd, imageio, imageio-ffmpeg, Numba, and pytest.

## Usage

```bash
python Ex0.py file.nrrd file.csv file.mp4
```

- **NRRD input:** a three-dimensional volume with `1 <= sx, sy, sz < 1024`, supporting `uint8`, `uint16`, and `uint32` voxel values. Nonnegative signed integer data of supported widths can also be converted as an extension.
- **CSV input:** each nonempty row specifies a three-point triangle or four-point trapezoid. Both coordinate-only rows and the lecturer's point-count-prefixed format (`3` or `4`) are accepted.
- **MP4 output:** one encoded grayscale frame per nonempty plane entry in normal mode, in CSV order. Invalid plane entries produce visibly marked error frames; subsequent entries are still processed.

**Point ordering:** for a triangle `(a, b, c)`, `a` is the common vertex of the equal sides. For a trapezoid `(a, b, c, d)`, the equal legs are `a → b` and `c → d`; the bases are `a → c` and `b → d`.

## Reproducible small demo

Both demo input files are included in the repository:

```bash
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
```

The `16 × 16 × 16` example has two plane entries. The recorded run produced projection shapes `(10, 16)` and `(10, 11)`, with 87 and 110 nonzero pixels, respectively. At 30 encoded FPS, the two-frame video lasts only about 0.067 seconds. To inspect its first frame:

```bash
python -c "import imageio.v2 as i; i.imwrite('results/demo_check.png', i.get_reader('results/demo_small.mp4').get_data(0))"
```

The demo MP4 and extracted PNG are generated locally; the source demo inputs are tracked in Git.

## Projection algorithm

1. Load and validate the NRRD volume and parse the CSV entries in order.
2. Validate isosceles triangle or trapezoid geometry using the specified length tolerance (`0.001`), with checks for degeneracy and trapezoid constraints.
3. Move in integer-distance row steps along the two equal sides or legs, sampling across each row.
4. Use nearest-neighbor voxel sampling; positions outside the volume contribute zero.
5. Preserve the sampled projection as a 2D matrix, then map it to 8-bit grayscale and pad frames to a common canvas for MP4 encoding.
6. Convert invalid individual plane entries to marked error frames without stopping the remaining sequence.

The sampling loop uses Numba JIT acceleration. See [Algorithm design](docs/ALGORITHM.md) for formulas, pseudocode, and complexity analysis.

## Testing

```bash
python -m pytest -q
python Ex0.py --test
```

**Recorded result for the corrected version (7 November 2026): 52 tests passed in 6.70 seconds** on the developer's machine. The suite covers CSV parsing, geometry, voxel sampling, boundary cases, video output, and lecturer-specific requirements. See [Testing strategy](docs/TESTING.md).

## Performance experiment

```bash
python Ex0.py --performance
```

| Measurement | Recorded result |
|---|---:|
| Synthetic volume | `500 × 500 × 500`, `uint8` |
| Timed projections | 10 |
| Average computation time | `0.00141 s` per projection |
| Projection computation rate | **710.91 FPS** |
| Assignment minimum | Above 30 FPS |
| Assignment expected target | Approximately 100 FPS |

**Measurement scope:** the benchmark excludes NRRD loading, MP4 encoding, and initial JIT compilation. It does **not** measure end-to-end video generation throughput. See [Experiment report](docs/EXPERIMENT.md).

## Demonstration videos

The repository includes a principal MRI video and additional Croissant and Onion reference sequences:

| Video | Frames | Encoded FPS | Purpose |
|---|---:|---:|---|
| [MRI main demonstration](results/mri_final.mp4) | 100 | 30 | Main video example |
| [Croissant reference](results/croissant_reference.mp4) | 100 | 30 | Additional dataset |
| [Onion reference](results/onion_reference.mp4) | 120 | 30 | Additional dataset |
| [Short four-plane example](results/output.mp4) | 4 | 30 | Short demonstration |

See [Video results index](results/results.md) for details. Encoded playback FPS should not be confused with measured projection computation FPS.

## Dataset availability

The small demo files and sample CSVs are tracked in the repository. Larger MRI, Croissant, and Onion NRRD volumes are distributed separately; see [Dataset documentation](docs/DATASET.md) and the [assignment supplementary dataset folder](https://drive.google.com/drive/folders/1koJ83uaeMYdJt6AwvVlmMJk_wzczvmmG).

For a larger local MRI run, after obtaining the matching NRRD file:

```bash
python Ex0.py data/mri_uint16.nrrd data/mri_full.csv results/mri_full.mp4
```

This command requires `data/mri_uint16.nrrd` to be available locally; it is not included in the Git repository.

## Repository structure

```text
I2SE-Ex1/
├── Ex0.py
├── README.md
├── requirements.txt
├── data/                 # Demo NRRD and CSV definitions
├── docs/
│   ├── SRS.md
│   ├── ALGORITHM.md
│   ├── DATASET.md
│   ├── TESTING.md
│   └── EXPERIMENT.md
├── tests/                # pytest suite, including lecturer requirements
└── results/              # MP4 examples and results.md
```

**Documentation:** [SRS](docs/SRS.md) · [Algorithm](docs/ALGORITHM.md) · [Datasets](docs/DATASET.md) · [Testing](docs/TESTING.md) · [Experiments](docs/EXPERIMENT.md).

## Design decisions and limitations

- Nearest-neighbor sampling is used rather than interpolation or super-resolution.
- CSV coordinates are interpreted in voxel-index space, without physical-coordinate metadata transformations.
- Output MP4 frames are 8-bit grayscale; original 16-/32-bit sampled values are scaled for display.
- A filename ending in `preview.mp4` triggers enlarged/repeated frames for inspection; ordinary output keeps one frame per CSV entry.
- A protective limit of **25,000,000 pixels per projection** prevents excessive allocations. Extremely large plane definitions may be rejected.
- The application does not include a GUI or GPU acceleration.

The repository contains the design, implementation, tests, reproducible small inputs, documented larger datasets, and experiment results required for the assignment.
