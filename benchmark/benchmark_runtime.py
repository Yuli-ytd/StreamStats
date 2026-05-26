import time
import statistics
import csv
from pathlib import Path

import numpy as np
import streamstats


def measure_runtime(func, repeat=5, warmup=1):
    """Measure median runtime after optional warmup runs."""

    for _ in range(warmup):
        func()

    times = []
    result = None

    for _ in range(repeat):
        t0 = time.perf_counter()
        result = func()
        t1 = time.perf_counter()
        times.append(t1 - t0)

    median_time = statistics.median(times)

    if len(times) > 1:
        std_time = statistics.stdev(times)
    else:
        std_time = 0.0

    return median_time, std_time, result


def generate_data(n, seed=123):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float64)


def assert_close_results(stream_result, python_result, numpy_result,
                         rtol=1e-10, atol=1e-12):
    """Check that StreamStats, Python, and NumPy produce similar results."""

    baseline_results = [
        ("Python", python_result),
        ("NumPy", numpy_result),
    ]

    for name, result in baseline_results:
        mean_close = np.isclose(stream_result[0], result[0],
                                rtol=rtol, atol=atol)
        var_close = np.isclose(stream_result[1], result[1],
                               rtol=rtol, atol=atol)

        if not mean_close:
            raise AssertionError(
                f"Mean mismatch between StreamStats and {name}: "
                f"StreamStats={stream_result[0]}, {name}={result[0]}"
            )

        if not var_close:
            raise AssertionError(
                f"Variance mismatch between StreamStats and {name}: "
                f"StreamStats={stream_result[1]}, {name}={result[1]}"
            )


def bench_streamstats(data, window_size):
    s = streamstats.StreamStats(window_size, dtype=np.float64)

    last_mean = 0.0
    last_var = 0.0

    for x in data:
        s.push(float(x))
        last_mean = s.mean()
        last_var = s.variance(ddof=0)

    return last_mean, last_var


def bench_python_recompute(data, window_size):
    last_mean = 0.0
    last_var = 0.0

    for i in range(len(data)):
        start = max(0, i + 1 - window_size)
        window = data[start:i + 1]

        last_mean = sum(window) / len(window)
        ss = sum((x - last_mean) ** 2 for x in window)
        last_var = ss / len(window)

    return last_mean, last_var


def bench_numpy_recompute(data, window_size):
    last_mean = 0.0
    last_var = 0.0

    for i in range(len(data)):
        start = max(0, i + 1 - window_size)
        window = data[start:i + 1]

        last_mean = np.mean(window)
        last_var = np.var(window, ddof=0)

    return float(last_mean), float(last_var)


def main():
    cases = [1_000, 10_000, 100_000]
    window_sizes = [16, 64, 256, 1024]

    rows = []

    for n in cases:
        data_np = generate_data(n)
        data_list = data_np.tolist()

        for w in window_sizes:
            stream_time, stream_std, stream_result = measure_runtime(
                lambda: bench_streamstats(data_np, w)
            )
            python_time, python_std, python_result = measure_runtime(
                lambda: bench_python_recompute(data_list, w)
            )
            numpy_time, numpy_std, numpy_result = measure_runtime(
                lambda: bench_numpy_recompute(data_np, w)
            )

            assert_close_results(stream_result, python_result, numpy_result)

            speedup_vs_python = python_time / stream_time
            speedup_vs_numpy = numpy_time / stream_time

            stream_ns_per_update = stream_time / n * 1e9
            python_ns_per_update = python_time / n * 1e9
            numpy_ns_per_update = numpy_time / n * 1e9

            row = {
                "n": n,
                "window_size": w,

                "streamstats_sec": stream_time,
                "python_recompute_sec": python_time,
                "numpy_recompute_sec": numpy_time,

                "streamstats_std_sec": stream_std,
                "python_recompute_std_sec": python_std,
                "numpy_recompute_std_sec": numpy_std,

                "streamstats_ns_per_update": stream_ns_per_update,
                "python_recompute_ns_per_update": python_ns_per_update,
                "numpy_recompute_ns_per_update": numpy_ns_per_update,

                "speedup_vs_python": speedup_vs_python,
                "speedup_vs_numpy": speedup_vs_numpy,

                "streamstats_last_mean": stream_result[0],
                "streamstats_last_var": stream_result[1],
                "python_last_mean": python_result[0],
                "python_last_var": python_result[1],
                "numpy_last_mean": numpy_result[0],
                "numpy_last_var": numpy_result[1],
            }

            rows.append(row)

            print(
                f"n={n:>7}, w={w:>4} | "
                f"StreamStats={stream_time:.6f}s "
                f"({stream_ns_per_update:.2f} ns/update), "
                f"Python={python_time:.6f}s "
                f"({python_ns_per_update:.2f} ns/update), "
                f"NumPy={numpy_time:.6f}s "
                f"({numpy_ns_per_update:.2f} ns/update) | "
                f"speedup_py={speedup_vs_python:.2f}x, "
                f"speedup_np={speedup_vs_numpy:.2f}x"
            )

    output_path = Path("benchmark/results_runtime.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nBenchmark results written to {output_path}")


if __name__ == "__main__":
    main()