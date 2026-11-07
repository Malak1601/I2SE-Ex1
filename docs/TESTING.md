Testing Strategy
1. Purpose
Testing evaluates the correctness, robustness, and reproducibility of the 3D-to-2D plane projection program. The tests cover geometric validation, CSV parsing, voxel sampling, projection values, volume data types, MP4 generation, and error recovery. Performance is evaluated separately from functional correctness.
2. Automated testing
The project uses pytest and a built-in test mode in Ex0.py.
Test file	Main coverage
tests/test_csv.py	CSV parsing and malformed entries
tests/test_geometry.py	Triangle and trapezoid geometry
tests/test_projection.py	Known-value projections and voxel sampling
tests/test_video.py	Video generation, frame order, and error frames
tests/test_extra.py	Additional geometry, boundary, and input cases
tests/test_lecturer_requirements.py	Additional checks based on the lecturer's requirements


From the project root, run:
python -m pytest -q
Latest reported result on the corrected Ex0.py: 52 tests passed. This is the result reported during final local verification; execution time and results may vary by environment.

Built-in tests can be run separately:
python Ex0.py --test
2.1 Geometry tests
The tests exercise valid isosceles triangles, degenerate or collinear triangles, unequal required sides, valid trapezoids and rectangles, unequal trapezoid legs, and invalid plane configurations. The specified length-comparison tolerance is 0.001.

Automated success demonstrates coverage of the tested examples; it is not a mathematical proof that all possible input geometries are handled correctly.
2.2 CSV tests
The tests exercise coordinate-only triangle and trapezoid rows, count-prefixed entries in the lecturer's CSV format, invalid coordinate counts, nonnumeric or nonfinite coordinates, and error handling. The program preserves the order of processed nonempty plane entries.
2.3 Projection and boundary tests
Small synthetic 3D arrays with known voxel values are used to compare actual projection matrices against independently specified expected matrices. Tests also cover nearest-neighbor sampling, out-of-volume zeros, and supported integer data types.

After the final correction to integer-step row sampling, two expected-value tests were updated to match the corrected sampling convention. In both, the final pixel of the second row changed from 6 to 0; the remaining values were unchanged. These updated expectations should be checked against the algorithm specification rather than treated as correct merely because the tests pass.
2.4 Video tests
The tests cover MP4 creation, grayscale conversion, error-frame behavior, and the ordering and placement of projections. In normal mode, the intended mapping is one output frame per processed nonempty CSV entry. Preview output, when used, is intended for inspection and may repeat or enlarge frames.
3. Small end-to-end demonstration
A reproducible small-volume demonstration was run with:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
The reported run loaded a 16 × 16 × 16 volume, processed two plane definitions, and wrote the MP4 output. The first video frame was extracted to results/demo_check.png and inspected visually; it contained a nonempty projected region.

This verifies a complete local NRRD-to-CSV-to-MP4 workflow on a small example. It does not replace testing on the larger datasets.
4. Supplementary edge-case experiments
The earlier project documentation records experiments using selected cases from edge_cases.csv and a constant-valued uint8 volume of dimensions 200 × 180 × 160 (voxel value 100). These observations were recorded for an earlier implementation; they have not been independently rerun against the corrected final Ex0.py and should not be presented as final-version regression results.
4.1 Recorded triangle observations
Case	Earlier observed result	Description
4	Accepted	Nonempty projection
5	Accepted	Nonempty projection
6	Accepted	Equal required side lengths; some coordinates outside the test volume
7	Rejected	Invalid triangle geometry
12	Rejected	Collinear vertices
13	Rejected	Invalid triangle geometry


For case 6, geometric validity and whether sampled points lie inside the volume are separate questions: an otherwise valid plane may have out-of-volume samples that must yield zero.
4.2 Recorded trapezoid observations
Case	Earlier observed result	Description
1	Accepted	Projection generated
2	Accepted	Projection generated
3	Accepted	Projection generated
14	Rejected	Unequal leg lengths
15	Rejected	Invalid base configuration


4.3 Recorded unsigned integer experiments
Voxel type	Earlier observed result
uint8	Projection generated
uint16	Projection generated
uint32	Projection generated


The earlier report recorded 72 nonzero pixels for each type using a valid triangle. These experiments tested projection functions directly rather than the complete CSV-to-MP4 workflow.
5. Performance experiment
Run:
python Ex0.py --performance
Latest reported benchmark on the corrected implementation:
Metric	Recorded value
Volume	500 × 500 × 500
Voxel type	uint8
Measured projections	10, after warm-up
Average projection time	Approximately 0.00141 s
Projection computation rate	710.91 FPS
Lecturer's minimum	More than 30 FPS
Lecturer's expected target	Approximately 100 FPS


This is a projection-computation-only measurement. It excludes NRRD loading, MP4 encoding, and initial Numba JIT compilation. It is not a measurement of end-to-end video throughput. Results depend on hardware and plane geometry.

See [Experiment](EXPERIMENT.md) for the detailed benchmark description.
6. Final submission verification
Before submission, confirm that:
1. python -m pytest -q passes on the exact version being submitted.
2. python Ex0.py --test completes successfully.
3. The small NRRD/CSV example produces a readable MP4 with visible projection content.
4. The normal-mode MP4 frame count and order match the processed CSV entries.
5. The lecturer's geometric requirements, including trapezoid base ordering, are checked against the submitted implementation.
6. The documented image-size safeguard does not unintentionally reject required assignment inputs.
7. The README, SRS, algorithm description, experiment report, and repository file paths agree with the submitted files.
7. Conclusion
The recorded final local test suite passed 52 tests, and the small end-to-end demonstration produced a visible projection. The measured computation-only benchmark exceeded the assignment's stated FPS targets for the tested configuration. Supplementary edge-case observations from an earlier code version remain useful historical evidence but require rerunning before being claimed as final-version results.