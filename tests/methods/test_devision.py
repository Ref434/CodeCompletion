from math import sqrt
import pytest

@pytest.mark.parametrize("a, expected_result", [(4,2),(5,2)])
def test_division_good(a, expected_result):
    assert sqrt(a) == expected_result
