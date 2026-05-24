import math
import numpy as np
import pytest
import streamstats

@pytest.mark.parametrize("dtype", [np.float64, np.float32])
def test_streamstats_basic_mean_and_variance_with_dtype(dtype):
    
    s = streamstats.StreamStats(3, dtype=dtype)

    assert s.window_size() == 3
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

    s.push(1.0)
    s.push(2.0)

    window = np.array([1.0, 2.0], dtype=dtype)
    tol = 1e-5 if dtype==np.float32 else 1e-12

    assert s.size() == 2
    assert s.mean() == pytest.approx(np.mean(window), rel=tol)
    assert s.variance() == pytest.approx(np.var(window), rel=tol)
    assert s.variance(ddof=0) == pytest.approx(np.var(window, ddof=0), rel=tol)
    assert s.variance(ddof=1) == pytest.approx(np.var(window, ddof=1), rel=tol)

    s.push(3.0)
    s.push(10.0)

    window = np.array([2.0, 3.0, 10.0], dtype=dtype)

    assert s.mean() == pytest.approx(np.mean(window), rel=tol)
    assert s.variance() == pytest.approx(np.var(window, ddof=0), rel=tol)
    assert s.variance(ddof=0) == pytest.approx(np.var(window, ddof=0), rel=tol)
    assert s.variance(ddof=1) == pytest.approx(np.var(window, ddof=1), rel=tol)

    s.reset()

    assert s.size() == 0
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

def test_streamstats_default_dtype_behavior():

    s = streamstats.StreamStats(3)

    s.push(1.0)
    s.push(2.0)

    window = np.array([1.0, 2.0], dtype=np.float64)

    assert s.mean() == pytest.approx(np.mean(window))
    assert s.variance() == pytest.approx(np.var(window, ddof=0))

def test_streamstats_invalid_dtype():
    with pytest.raises(ValueError):
        streamstats.StreamStats(3, dtype=np.int32)

def test_streamstats_variance_invalid_ddof():

    s = streamstats.StreamStats(3)
    s.push(1.0)
    s.push(2.0)

    with pytest.raises(ValueError):
        s.variance(ddof=2)