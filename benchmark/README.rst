=================
Runtime Benchmark
=================

This directory contains the runtime benchmark for StreamStats. The benchmark
evaluates the cost of updating rolling mean and variance over a scalar data
stream.

The purpose of this benchmark is to compare the current StreamStats
implementation against recomputation-based Python and NumPy baselines. It
focuses on rolling-statistics update performance, not on general-purpose array
processing performance.

Goal
====

The benchmark answers the following question:

Given a stream of scalar values and a fixed window size, how much runtime is
needed to update and query rolling mean and population variance as each new
sample arrives?

StreamStats maintains the rolling statistics incrementally. The Python and
NumPy baselines recompute the statistics from the active window at every step.
This comparison is intended to show the difference between incremental update
and repeated full-window recomputation.

How to Run
==========

From the project root directory, run:

.. code-block:: bash

   make benchmark

The Makefile builds the Python extension module first and then runs:

.. code-block:: bash

   PYTHONPATH=. python3 benchmark/benchmark_runtime.py

The benchmark results are written to:

.. code-block:: text

   benchmark/results_runtime.csv

Benchmark Design
================

The benchmark uses deterministic input data generated from NumPy's random
number generator with a fixed seed. This makes the input data reproducible
across benchmark runs.

The benchmark evaluates the following stream lengths:

- ``1_000``
- ``10_000``
- ``100_000``

For each stream length, the benchmark evaluates the following window sizes:

- ``16``
- ``64``
- ``256``
- ``1024``

For every pair of stream length and window size, the benchmark runs three
methods:

1. StreamStats incremental update.
2. Python recomputation.
3. NumPy recomputation.

Each method is executed once as a warmup run and then measured five times. The
reported runtime is the median of the measured runs. The benchmark also records
the standard deviation of the measured runtimes.

Compared Methods
================

StreamStats Incremental Update
------------------------------

The StreamStats benchmark creates a ``streamstats.StreamStats`` object with
``dtype=np.float64``. For each incoming value, it performs the following steps:

1. Push the new value into the stream.
2. Query the current rolling mean.
3. Query the current rolling population variance with ``variance(ddof=0)``.

The key characteristic of this method is that the statistics are maintained
incrementally by the C++ implementation. The active window is not recomputed
from scratch at every step.

Python Recomputation
--------------------

The Python baseline stores the input data as a Python list. For each incoming
position, it reconstructs the active window and recomputes:

1. the mean using Python ``sum()``;
2. the population variance by iterating over the active window.

This baseline represents a straightforward pure-Python implementation. It is
simple and readable, but its cost increases with the window size because the
active window is revisited at every step.

NumPy Recomputation
-------------------

The NumPy baseline stores the input data as a NumPy array. For each incoming
position, it slices the active window and recomputes:

1. the mean using ``np.mean``;
2. the population variance using ``np.var(..., ddof=0)``.

This baseline uses optimized NumPy operations for each window. However, it
still recomputes the statistics from the current window at every step.

Correctness Check
=================

Before recording the benchmark result for each case, the script checks that the
final mean and variance from StreamStats are close to the Python and NumPy
baseline results.

The benchmark compares the final mean and final population variance using
``np.isclose``. If the results are not close enough, the script raises an
``AssertionError`` instead of reporting a misleading speedup.

This check does not prove that every intermediate value is identical, but it
provides a useful consistency check for the final state of each benchmark case.

Evaluation Metrics
==================

The benchmark records the following runtime metrics:

- ``streamstats_sec``: median runtime of StreamStats.
- ``python_recompute_sec``: median runtime of the Python recomputation baseline.
- ``numpy_recompute_sec``: median runtime of the NumPy recomputation baseline.
- ``streamstats_std_sec``: runtime standard deviation for StreamStats.
- ``python_recompute_std_sec``: runtime standard deviation for Python
  recomputation.
- ``numpy_recompute_std_sec``: runtime standard deviation for NumPy
  recomputation.
- ``streamstats_ns_per_update``: StreamStats runtime per input sample.
- ``python_recompute_ns_per_update``: Python recomputation runtime per input
  sample.
- ``numpy_recompute_ns_per_update``: NumPy recomputation runtime per input
  sample.
- ``speedup_vs_python``: Python recomputation runtime divided by StreamStats
  runtime.
- ``speedup_vs_numpy``: NumPy recomputation runtime divided by StreamStats
  runtime.

The output file also records the final mean and variance values from all three
methods for reference.

How to Interpret the Results
============================

Lower runtime means that a method finished the full stream-processing workload
more quickly.

Lower nanoseconds per update means that the average cost of processing one
input sample is smaller.

Higher speedup means that StreamStats is faster than the corresponding
baseline. For example, ``speedup_vs_python = 10`` means that StreamStats was
approximately ten times faster than the Python recomputation baseline for that
case.

The most important trend to observe is how runtime changes as the window size
increases. Recompute-based methods usually become more expensive for larger
windows because they revisit the active window at every update step.
StreamStats is expected to be less sensitive to the window size because it
updates maintained statistics incrementally.

Benchmark Scope
===============

This benchmark focuses on the following operation sequence:

1. receive one scalar value;
2. push the value into the rolling stream;
3. update rolling statistics;
4. query rolling mean and population variance.

The benchmark is designed to evaluate scalar rolling mean and variance update
performance. It is not intended to evaluate every possible use case of NumPy,
Python, or rolling-window analysis libraries.

Limitations
===========

The benchmark has several limitations:

1. It measures only scalar rolling mean and population variance.
2. It does not benchmark sample variance separately.
3. It does not benchmark batch input, because the current implementation only
   supports single-value ``push()`` updates.
4. It does not benchmark zero-copy NumPy window access, because the current
   Python binding does not expose the underlying C++ ring buffer through the
   Python buffer protocol.
5. It does not compare against pandas or other optimized rolling-window
   libraries.
6. The benchmark is executed from Python, so the measured StreamStats runtime
   includes Python-to-C++ binding overhead.
7. Runtime results may vary depending on CPU, compiler, Python version, NumPy
   version, and system load.

Notes for Presentation
======================

When presenting the benchmark, the main point is not simply that one method is
faster than another. The main point is the algorithmic difference:

- StreamStats uses incremental updates.
- Python and NumPy baselines recompute statistics from the active window.

Therefore, the benchmark should be interpreted as evidence that maintaining
rolling statistics incrementally can reduce repeated computation for streaming
data.