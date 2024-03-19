import time


# @pytest.mark.skip
def test_runtime():
    time.sleep(2.5)


def test_pass():
    pass


def test_fali():
    assert False
