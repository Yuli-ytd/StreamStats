import math
import numpy as np
import pytest
import streamstats


def test_streamstats_basic_mean_and_variance():

    s = streamstats.StreamStats(3)

    assert s.window_size() == 3
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

    s.push(1.0)
    s.push(2.0)

    window = np.array([1.0, 2.0])

    assert s.size() == 2
    assert s.mean() == pytest.approx(np.mean(window))
    assert s.variance() == pytest.approx(np.var(window, ddof=0))
    assert s.variance(ddof=0) == pytest.approx(np.var(window, ddof=0))
    assert s.variance(ddof=1) == pytest.approx(np.var(window, ddof=1))

    s.push(3.0)
    s.push(10.0)

    window = np.array([2.0, 3.0, 10.0])

    assert s.mean() == pytest.approx(np.mean(window))
    assert s.variance() == pytest.approx(np.var(window, ddof=0))
    assert s.variance(ddof=0) == pytest.approx(np.var(window, ddof=0))
    assert s.variance(ddof=1) == pytest.approx(np.var(window, ddof=1))

    s.reset()

    assert s.size() == 0
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

def test_streamstats_variance_invalid_ddof():

    s = streamstats.StreamStats(3)
    s.push(1.0)
    s.push(2.0)

    with pytest.raises(ValueError):
        s.variance(ddof=2)