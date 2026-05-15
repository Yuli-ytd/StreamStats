import streamstats
import math

def test_streamstats_basic_mean():

    s = streamstats.StreamStats(3)

    assert s.window_size() == 3
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

    s.push(1.0)
    s.push(2.0)

    assert s.size() == 2
    assert s.mean() == 1.5
    assert s.variance() == 0.5

    s.push(3.0)
    s.push(10.0)

    assert s.mean() == 5.0
    assert s.variance() == 19.0

    s.reset()
    assert s.size() == 0
    assert math.isnan(s.mean())
    assert math.isnan(s.variance())

# if __name__ == "__main__":
#     test_streamstats_basic_mean()