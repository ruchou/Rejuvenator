import pytest

from main import Rejuvenator


def test_f():
    r = Rejuvenator()
    assert all([c for c in r.clean]) == True


class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")