import streamstats

def test_addition():
    # test if add function of streamstats returns 8
    assert streamstats.add() == 8
    print("Test passed!")

if __name__ == "__main__":
    test_addition()