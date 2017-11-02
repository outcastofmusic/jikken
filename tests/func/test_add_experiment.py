import jikken
import pytest


def test_add_raises():
    """add should raise an error if object is not Experiment"""
    with pytest.raises(TypeError):
        jikken.add('hello world')
