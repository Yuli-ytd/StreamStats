import math
import pytest
import streamstats

def test_golden_reference():
    cases = [
        # inserted_value, expected_size, expected_mean, expected_pop_var, expected_sample_var
        ( 1.0, 1,    1.0,     0.0, math.nan),
        ( 2.0, 2,    1.5,    0.25,      0.5),
        ( 3.0, 3,    2.0,   2.0/3,        1),
        (10.0, 3,    5.0,  38.0/3,       19),
        (-2.0, 3, 11.0/3, 218.0/9,  218.0/6)
    ]

    s = streamstats.StreamStats(3)

    for inserted_value, expected_size, expected_mean, expected_pop_var, expected_sample_var in cases:
        
        s.push(inserted_value)

        assert s.size() == expected_size
        assert s.mean() == pytest.approx(expected_mean)
        assert s.variance(ddof = 0) == pytest.approx(expected_pop_var)
        
        if math.isnan(expected_sample_var):
            assert math.isnan(s.variance(ddof = 1))
        else:
            assert s.variance(ddof = 1) == pytest.approx(expected_sample_var)

def test_golden_reference_empty_stream():
    
    s = streamstats.StreamStats(3)

    assert s.size() == 0
    assert math.isnan(s.mean())
    assert math.isnan(s.variance(ddof=0))
    assert math.isnan(s.variance(ddof=1))

def test_golden_reference_window_size_one():

    s = streamstats.StreamStats(1)

    s.push(5.0)

    assert s.size() == 1
    assert s.mean() == pytest.approx(5.0)
    assert s.variance(ddof=0) == pytest.approx(0.0)
    assert math.isnan(s.variance(ddof=1))

    s.push(8.0)

    assert s.size() == 1
    assert s.mean() == pytest.approx(8.0)
    assert s.variance(ddof=0) == pytest.approx(0.0)
    assert math.isnan(s.variance(ddof=1))

def test_golden_reference_reset_behavior():

    s = streamstats.StreamStats(3)

    s.push(1.0)
    s.push(2.0)
    s.push(3.0)

    assert s.size() == 3
    assert s.mean() == pytest.approx(2.0)

    s.reset()

    assert s.size() == 0
    assert math.isnan(s.mean())
    assert math.isnan(s.variance(ddof=0))
    assert math.isnan(s.variance(ddof=1))

    s.push(10.0)
    s.push(20.0)

    assert s.size() == 2
    assert s.mean() == pytest.approx(15.0)
    assert s.variance(ddof=0) == pytest.approx(25.0)
    assert s.variance(ddof=1) == pytest.approx(50.0)

def test_golden_reference_invalid_window_size():
    with pytest.raises(ValueError):
        streamstats.StreamStats(0)