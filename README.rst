======================================
Stream Statistics for Real-time Data
======================================

**StreamStats**:
A C++11 library with Python bindings for real-time streaming
numerical statistics.

Numerical analysis often involves continuous data streams, such as
high-frequency financial ticks, sensor telemetry, and real-time experimental
signals. Unlike static datasets, streaming data must be processed as data
points arrive sequentially. In many applications, the complete stream may be
too large to store entirely in memory.

Efficiently computing statistics over a sliding window, defined as the most
recent ``W`` elements, is a common operation in these domains. StreamStats
provides a C++ implementation for maintaining rolling statistics with fixed
window storage, while exposing a Python interface for easier experimentation
and integration into data analysis workflows.

The current implementation focuses on rolling scalar mean and variance over a
fixed-size sliding window.

Problem to Solve
================

The primary challenge in streaming statistics is the trade-off between
computational latency, memory overhead, and numerical stability in
high-frequency environments.

1. **Redundant Computation:** A naive implementation recomputes statistics
   from scratch each time the window advances. For a stream of length ``N`` and
   a window size ``W``, this requires ``O(NW)`` operations. As ``W`` grows,
   this repeated computation becomes a bottleneck in real-time systems.
   StreamStats avoids full-window recomputation by updating maintained summary
   values as new samples arrive.

2. **Memory Overhead and Jitter:** In Python-based pipelines, repeatedly
   slicing arrays, such as ``data[-W:]``, may create temporary objects and
   increase allocation overhead. Frequent allocation may also introduce
   unpredictable runtime behavior. StreamStats uses a fixed-size C++
   ``RingBuffer<T>`` to store the active window and avoid resizing the storage
   during streaming.

3. **Numerical Stability:** Naive variance formulas can suffer from
   floating-point cancellation, especially when the stream is long or the data
   has large offsets. StreamStats maintains the rolling mean and the second
   central moment ``m2`` incrementally, using a Welford-style update strategy
   for improved numerical behavior compared with direct sum-of-squares
   recomputation.

The current implementation focuses on scalar rolling mean and variance. It
does not attempt to be a full replacement for NumPy or pandas rolling-window
operations.

Prospective Users
=================

StreamStats is intended for students, researchers, and developers who need to
compute basic streaming statistics with low latency while still working from
Python.

Potential users include:

- **Quantitative Finance Learners and Practitioners:** Users working with
  market time-series data who need rolling statistics, such as moving average
  or volatility, updated as new ticks arrive.

- **IoT and Monitoring Developers:** Users building sensor-data pipelines that
  require real-time statistical summaries for simple anomaly detection.

- **Signal Processing and Experimental Research Students:** Users handling
  continuous measurement data, such as laboratory instrument signals, and
  applying window-based statistics for preprocessing.

Overall, StreamStats separates the performance-critical update logic into C++
while keeping the user-facing interface accessible from Python.

System Architecture
===================

StreamStats follows a two-layer architecture: a C++ core for streaming
computation and a Python binding layer for user-facing workflows.

1. C++ Core Layer
-----------------

The core layer is implemented in C++11 and focuses on fixed-size storage and
incremental statistic updates.

- ``RingBuffer<T>`` is the primary data container. It stores the most recent
  ``W`` samples in a fixed-size buffer. Once the buffer is created, its
  capacity remains fixed, which avoids repeated memory reallocation during
  streaming.

- ``ScalarStream<T>`` is the main streaming-statistics class. It is built on
  top of ``RingBuffer<T>`` and maintains the rolling mean and ``m2`` value.
  When a new sample is pushed, the class updates the maintained statistics
  according to whether the window is still growing or already full.

- ``ScalarStream<T>`` currently requires ``T`` to be a floating-point type.
  This design avoids integer-division behavior and allows undefined numerical
  results to be represented as NaN.

This layer is designed to minimize repeated computation and avoid frequent
memory allocation during streaming.

2. Python Binding Layer
-----------------------

The Python layer is built with pybind11 and provides Python bindings for data
analysis workflows.

- Python users can push new scalar samples and query the current statistics
  directly.

- The current implementation exposes two concrete internal classes,
  ``_StreamStatsF64`` and ``_StreamStatsF32``, and a factory function
  ``StreamStats(window_size, dtype=None)``.

- The factory function returns a float64-backed stream by default. Users may
  also request ``np.float64`` or ``np.float32`` explicitly through the
  ``dtype`` argument.

The current Python binding exposes scalar update and query methods. It does
not currently expose the underlying C++ ring buffer through the Python buffer
protocol.

3. Data Flow and Scope
----------------------

At each update step, a new sample is inserted into the ring buffer. If the
window is already full, the oldest sample is replaced. ``ScalarStream<T>``
then updates the maintained mean and variance-related state.

The current version focuses on correctness, numerical behavior, and predictable
single-threaded runtime performance for rolling scalar statistics.

API Description
===============

StreamStats provides a minimal API in both C++ and Python for rolling
statistics on streaming scalar data. The current version focuses on essential
operations and keeps advanced features as future work.

1. C++ API
----------

The main C++ class is ``ScalarStream<T>``. The template parameter ``T`` must be
a floating-point type.

Main methods:

- ``ScalarStream<T>(std::size_t window_size)``
- ``void push(T value)``
- ``std::size_t size() const``
- ``std::size_t window_size() const``
- ``T mean() const``
- ``T variance() const``
- ``T sample_variance() const``
- ``T population_variance() const``
- ``void reset()``

The constructor takes the window size. A window size of zero is invalid and
raises an exception.

In the C++ API, ``variance()`` is equivalent to ``sample_variance()``.
``population_variance()`` is provided separately for population variance.

2. Python API
-------------

The Python interface provides a factory function:

- ``streamstats.StreamStats(window_size)``
- ``streamstats.StreamStats(window_size, dtype=np.float64)``
- ``streamstats.StreamStats(window_size, dtype=np.float32)``

Example usage:

.. code-block:: python

   import numpy as np
   import streamstats

   s = streamstats.StreamStats(4, dtype=np.float64)

   s.push(1.0)
   s.push(2.0)
   s.push(3.0)

   print(s.mean())
   print(s.variance(ddof=0))  # population variance
   print(s.variance(ddof=1))  # sample variance

Main Python methods:

- ``s.push(value)``
- ``s.size()``
- ``s.window_size()``
- ``s.mean()``
- ``s.variance(ddof=0)``
- ``s.variance(ddof=1)``
- ``s.reset()``

In Python, ``variance(ddof=0)`` returns the population variance, and
``variance(ddof=1)`` returns the sample variance. This follows the common
``ddof`` convention used by NumPy.

Only ``ddof=0`` and ``ddof=1`` are currently supported. Other ``ddof`` values
raise ``ValueError``.

The current version supports single-value updates through ``push()`` only.
Batch input support is considered future work.

Numerical Behavior
==================

The numerical behavior depends on the number of samples currently stored in the
window.

1. Empty Stream
---------------

When the stream contains no samples:

- ``mean()`` returns NaN.
- ``population_variance()`` returns NaN.
- ``sample_variance()`` returns NaN.
- In Python, both ``variance(ddof=0)`` and ``variance(ddof=1)`` return NaN.

2. One Sample
-------------

When the stream contains exactly one sample:

- ``mean()`` returns the sample value.
- ``population_variance()`` returns ``0``.
- ``sample_variance()`` returns NaN.
- In Python, ``variance(ddof=0)`` returns ``0`` and ``variance(ddof=1)``
  returns NaN.

3. Two or More Samples
----------------------

When the stream contains two or more samples:

- ``mean()`` is defined.
- ``population_variance()`` is defined.
- ``sample_variance()`` is defined.
- In Python, both ``variance(ddof=0)`` and ``variance(ddof=1)`` are defined.

Build and Test
==============

The project uses a Makefile-based build flow. The Python extension module is
built from the C++ source code through pybind11.

Before building, initialize the vendored pybind11 submodule if necessary:

.. code-block:: bash

   git submodule update --init --recursive

Install Python dependencies used by the tests:

.. code-block:: bash

   python -m pip install pytest numpy

Build and run all tests:

.. code-block:: bash

   make clean
   make test

The test target runs both C++ unit tests and Python integration tests.

Benchmark
=========

StreamStats includes a runtime benchmark for comparing rolling-statistics
update performance.

Run the benchmark with:

.. code-block:: bash

   make benchmark

The benchmark compares three approaches:

- StreamStats incremental update.
- Naive Python recomputation.
- NumPy recomputation.

The benchmark evaluates multiple stream lengths and window sizes. It reports
median runtime, runtime standard deviation, nanoseconds per update, and speedup
against the Python and NumPy recomputation baselines.

Benchmark results are written to:

.. code-block:: text

   benchmark/results_runtime.csv

This benchmark focuses on scalar rolling mean and variance update performance.
It does not benchmark zero-copy NumPy access, batch input, or full-array
rolling-window APIs.

For details about the benchmark methodology, compared methods, evaluation
metrics, and result interpretation, see ``benchmark/README.rst``.

Development Summary
===================

The project started as a proposal for a C++/Python streaming-statistics
library and was gradually refined into a focused implementation of rolling
mean and variance.

The final version includes:

- a fixed-size C++ ``RingBuffer<T>``;
- a floating-point ``ScalarStream<T>`` class;
- pybind11 bindings for Python;
- support for float64 and float32 streams from Python;
- C++ unit tests;
- Python integration tests;
- GitHub Actions CI;
- runtime benchmark support.

The implementation emphasizes correctness, clear API behavior, and measurable
runtime performance for scalar streaming statistics.

Limitations and Future Work
===========================

The following features are left as future work:

1. **Zero-copy NumPy window access:** The current Python binding does not expose
   the underlying C++ ring buffer through the Python buffer protocol.

2. **Batch input API:** The current implementation supports single-value
   updates through ``push()`` only. A future version may support batch input,
   such as ``push_batch()``.

3. **Additional statistics:** The current implementation supports rolling mean
   and variance. Future versions may add rolling median, minimum, maximum, or
   other statistics.

4. **Integer input support:** ``ScalarStream<T>`` currently requires a
   floating-point stream type. Supporting integer input with floating-point
   accumulation is future work.

5. **Thread safety:** The current implementation is intended for single-threaded
  use. Thread-safety guarantees are not currently provided.
