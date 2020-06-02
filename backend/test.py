import pytest

class test_class1:
    def test_pass01(self):
        x = "this"
        assert "h" in x

    def test_fail(self):
        x = "hello"
        assert hasattr(x, "check")
