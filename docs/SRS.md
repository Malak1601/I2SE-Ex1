Software Requirements Specification (SRS)
I2SE Ex1 — 3D Volume Plane Projection
1. Purpose and scope
The program generates two-dimensional images by sampling planar regions of a three-dimensional volume. It reads a volume in NRRD format and a CSV file describing a sequence of planes, then writes the resulting projections to an MP4 video in CSV order.

The implementation is a command-line Python program, not a medical image viewer. It focuses on geometric correctness, predictable input handling, efficient sampling, testing, and maintainable code. A graphical user interface and physical-space coordinate transformations are outside the scope.
2. Inputs and outputs
Inputs
- A three-dimensional NRRD volume with dimensions 1 <= sx, sy, sz < 1024.
- Unsigned integer voxel types uint8, uint16, and uint32.
- A CSV file defining an isosceles triangle with three 3D points or an isosceles trapezoid with four 3D points. The parser accepts coordinate-only rows and count-prefixed rows (3 or 4), including the lecturer's header layout.
The implementation additionally supports certain nonnegative signed integer volumes by converting them to an unsigned representation. This is an extension, not a required input type.

Output
- An MP4 video with one encoded frame per nonempty CSV plane entry in normal mode, preserving entry order.
- Diagnostic terminal output describing the input volume, projections, and recoverable errors.
The output video uses 8-bit grayscale frames. Higher-bit-depth projection values are mapped to 8-bit intensities for display; this does not change the source volume values used for sampling.
3. Functional requirements
FR-01 — Volume loading and validation. The program shall load a 3D NRRD volume, check its dimensions and supported voxel type, and report fatal file or volume errors without producing misleading output.

FR-02 — CSV parsing. The program shall read three- and four-point definitions in file order, validate coordinate counts and finite numeric values, and recognize the lecturer's count-prefixed CSV format. Blank rows may be skipped; malformed nonempty rows shall be reported.

FR-03 — Triangle geometry. For points (a, b, c), the two sides originating at a must be nonzero and satisfy abs(dist(a,b) - dist(a,c)) < 0.001. Collinear or otherwise degenerate triangles shall be rejected.

FR-04 — Trapezoid geometry. For points (a, b, c, d), the legs are (a,b) and (c,d) and the bases are (a,c) and (b,d). The program shall validate nonzero area, coplanarity, parallel bases, approximately equal legs, and a non-crossing arrangement. The assignment's base-length ordering constraint must also be checked against the final implementation before submission; passing the current tests alone does not prove every geometric restriction is enforced.

FR-05 — Projection construction. For each valid plane, the program shall advance along the relevant sides/legs, sample positions between corresponding endpoints, and store sampled voxel values in a two-dimensional NumPy array. The final implementation follows the assignment's integer-step row-sampling convention rather than adding an extra fractional endpoint sample.

FR-06 — Nearest-neighbor and boundaries. Continuous positions shall be sampled using nearest-neighbor voxel indices. Positions outside the 3D volume shall yield zero. The boundary decision must be made consistently with the documented sampling rule, including near-boundary fractional coordinates.

FR-07 — Invalid entries. A malformed or geometrically invalid individual plane shall produce an informative diagnostic and a visibly marked error frame, while later CSV entries continue processing. Unrecoverable input errors may terminate the run.

FR-08 — MP4 encoding. Projection images of different sizes shall be placed on a common frame canvas and encoded into MP4 in input order. Normal output preserves one frame per processed nonempty CSV entry. Optional preview output may repeat or enlarge frames for inspection and is not used to verify normal-mode frame counts.

FR-09 — Command-line interface. The standard invocation shall be:
python Ex0.py file.nrrd file.csv file.mp4
The implementation also provides:
python Ex0.py --test
python Ex0.py --performance
FR-10 — Output safety. The implementation shall avoid overwriting its input files, validate the output path, and report encoding or filesystem errors. The implementation includes a protective upper bound on projection image size; this implementation-specific limitation must be disclosed and evaluated against the assignment's permitted inputs.
4. Non-functional requirements
NFR-01 — Performance. The assignment requires a projection rate above 30 frames per second and gives approximately 100 FPS as the expected target for a 500 × 500 × 500 unsigned-byte volume. Performance is measured for projection computation separately from NRRD loading, MP4 encoding, and initial Numba JIT compilation.

NFR-02 — Correctness. Known-value synthetic volumes, boundary cases, different plane orientations, and invalid geometry shall be used to verify output matrices and error handling.

NFR-03 — Robustness. Recoverable plane-level errors shall not prevent subsequent entries from being processed. Fatal errors shall be reported clearly.

NFR-04 — Maintainability. The implementation separates CSV parsing, geometric validation, sampling, video creation, command-line processing, and benchmarking into identifiable functions in Ex0.py.

NFR-05 — Reproducibility. The repository shall contain installation instructions, a runnable small example, automated tests, algorithm documentation, and an experiment report. Larger source volumes may be distributed separately with clear acquisition instructions.
5. Verification and recorded results
Automated regression tests are maintained under tests/, including test_csv.py, test_geometry.py, test_projection.py, test_video.py, test_extra.py, and test_lecturer_requirements.py.

Run the suite with:
python -m pytest -q
Latest user-reported run: 52 tests passed in 6.70 seconds on the corrected Ex0.py version. This is a recorded result, not a guarantee for other environments.

Run the projection benchmark with:
python Ex0.py --performance
Latest user-reported benchmark: synthetic 500 × 500 × 500 volume, 10 measured projections, approximately 0.00141 s per projection and 710.91 projection FPS. These figures exclude file loading, video encoding, and JIT warm-up and should not be described as end-to-end video throughput.

A small end-to-end demonstration was run using:
python Ex0.py data/demo_small.nrrd data/demo_small.csv results/demo_small.mp4
The reported run loaded a 16 × 16 × 16 volume, processed two CSV entries, saved the MP4, and allowed a visible nonempty projection frame to be extracted for inspection.
6. Acceptance checklist
The final submission should be checked for all of the following:
1. The command-line interface works with supported NRRD and CSV files.
2. Triangle and trapezoid geometry follows the lecturer's required conventions.
3. Sample values and out-of-volume zeros match independently calculated expected results.
4. Invalid plane entries produce error frames without changing the order of later entries.
5. The normal MP4 contains the expected number of frames in CSV order.
6. The documented tests pass on the submitted version.
7. The performance experiment reports its exact measurement scope.
8. The README, algorithm description, SRS, and experiment report agree with the submitted code.
9. The GitHub repository contains the required documentation, code, tests, and reproducible sample data or documented dataset links.
See [README](../README.md), [Algorithm](ALGORITHM.md), [Testing](TESTING.md), and [Experiment](EXPERIMENT.md) for supporting details.