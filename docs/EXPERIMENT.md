Performance Experiment and Results
1. Objective
This report evaluates the correctness, computational performance, and video-generation behavior of the 3D volume plane projection program. The program reads an NRRD volume and CSV plane definitions, produces two-dimensional projections, and encodes them as an MP4 video.

The assignment specifies a projection rate above 30 FPS and an expected target of approximately 100 FPS for a 500 × 500 × 500 unsigned-byte volume. The reported benchmark measures projection computation, not end-to-end video throughput.
2. Implementation and method
The program is written in Python and uses:
- NumPy for volume and projection arrays.
- pynrrd for reading NRRD volumes.
- Numba for JIT acceleration of the numerical sampling loop.
- imageio and imageio-ffmpeg for MP4 encoding.
- pytest for automated regression tests.
The algorithm supports isosceles triangular and trapezoidal regions. It samples nearest-neighbor voxel values, assigns zero to out-of-volume positions, and produces marked error frames for invalid individual plane definitions.
3. Projection performance benchmark
Run from the repository root:
python Ex0.py --performance
The built-in benchmark creates a synthetic uint8 volume of dimensions 500 × 500 × 500 and measures ten projections after a warm-up run. The benchmark triangle is defined by a = (0, 0, 0), b = (400, 0, 0), and c = (0, 400, 0).
Latest recorded results
Measurement	Result
Volume dimensions	500 × 500 × 500
Voxel type	uint8
Measured projections	10
Average projection time	approximately 0.00141 seconds
Projection computation rate	710.91 FPS
Assignment minimum	Above 30 FPS
Expected target	Approximately 100 FPS


These are the results reported from the corrected Ex0.py run. The measured projection-computation rate exceeds the stated minimum and expected target for this benchmark configuration.

Measurement scope: NRRD file loading, MP4 encoding, filesystem operations, and the initial Numba compilation are excluded. Results depend on the machine, geometry, output dimensions, and runtime conditions. Therefore, the measured 710.91 FPS must not be presented as the final video's playback frame rate or end-to-end encoding throughput.
4. Automated correctness testing
The regression tests cover geometry, CSV parsing, known voxel values, out-of-volume behavior, projection construction, video creation, error frames, and lecturer-specific requirements.

The suite includes:
- tests/test_csv.py
- tests/test_geometry.py
- tests/test_projection.py
- tests/test_video.py
- tests/test_extra.py
- tests/test_lecturer_requirements.py
Run:
python -m pytest tests/ -q
Latest recorded result on the corrected implementation: 52 passed in 6.70 seconds. This is a record of one successful local run, not proof that every possible input has been tested.

Selected manual edge cases and uint8, uint16, and uint32 synthetic-volume checks were also documented during development. Those earlier checks should be distinguished from the latest 52-test regression run; see [Testing Strategy](TESTING.md).
5. Small reproducible end-to-end demonstration
The repository's small synthetic example uses:
- data/demo_small.nrrd — a 16 × 16 × 16 volume.
- data/demo_small.csv — two plane definitions.
- results/demo_small.mp4 — the generated video.
Run:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
The recorded successful run reported:
Item	Observed result
Volume shape	(16, 16, 16)
CSV entries	2
Projection 1	Shape (10, 16), 87 nonzero values
Projection 2	Shape (10, 11), 110 nonzero values
Output	results/demo_small.mp4 saved


A frame extracted from the video was visually inspected and showed a nonempty grayscale triangular projection on a black background. Because the normal output has only two frames, playback at 30 FPS is very brief; this is expected and does not indicate a failed projection.
6. MRI demonstration
An MRI NRRD volume was used to demonstrate projection of real volumetric data. A previously generated four-plane video is documented as results/output (5).mp4 (four frames at 30 FPS, approximately 0.13 seconds).

Additional MRI slice sequences were generated during development. Their exact filenames, frame counts, and availability in the submitted repository should be checked before citing them as final deliverables. The source MRI NRRD may be kept separately because of its size; dataset acquisition instructions belong in [Dataset Documentation](DATASET.md).
7. Additional experiments: Croissant and Onion
Two further NRRD datasets were used to test the same projection implementation with different volume shapes and CSV plane sequences.
Dataset	Volume dimensions	Voxel type	Reference CSV entries	Recorded video
Croissant	500 × 500 × 500	uint8	100	results/croissant_reference.mp4
Onion	256 × 256 × 130	uint8	120	results/onion_reference.mp4


The reference CSV runs generated successive cross-sectional views. The previously recorded videos had the following playback properties:
Video	Frames	Playback FPS	Approximate duration
results/croissant_reference.mp4	100	30	3.33 seconds
results/onion_reference.mp4	120	30	4.00 seconds


Three-plane experiments using orthogonal rectangular regions were also performed, producing results/croissant.mp4 and results/onion.mp4. Separate preview files repeated frames to make short sequences easier to inspect. Repeated preview frames are not additional projection computations.

The earlier videos were visually inspected and showed visible projections. These observations describe development experiments; verify that each linked or named output is actually included in the final GitHub repository before submission.
8. Interpretation and limitations
The experiments support the following conclusions:
1. The corrected implementation passed the latest recorded 52 automated tests.
2. A small NRRD-to-MP4 workflow completed successfully, with two nonempty projections.
3. The synthetic benchmark achieved 710.91 projection FPS for the measured triangle, exceeding the assignment's stated performance thresholds for that configuration.
4. Earlier MRI, Croissant, and Onion experiments demonstrated processing of different volume sizes and longer CSV sequences.
The experiments do not establish exhaustive geometric correctness, uniform performance for every permitted plane, or 710.91 FPS end-to-end video production. Final verification should compare the submitted code and test outputs, confirm the presence of referenced artifacts, and check MP4 frame counts and CSV order.