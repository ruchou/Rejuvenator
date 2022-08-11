import pytest
from main import Rejuvenator


def _test_f():
    r = Rejuvenator()
    assert all([c for c in r.clean]) == True


class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

