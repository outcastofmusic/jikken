import pytest
from jikken.database.query import valid_list

values = [
    # value, expected_return
    (None, []),
    ((1,), [1]),
    ([1, 2], [1, 2]),
    (["hello world"], ["hello world"]),
    (["hello", "world"], ["hello", "world"])
]


@pytest.mark.parametrize("value, expected", values)
def test_valid_list(value, expected):
    assert expected == valid_list(value)

invalid_values = [
    # value
    ("hello"),
    (1),
    ({"hello":"key"})
]
@pytest.mark.parametrize("value", invalid_values)
def test_valid_list_raises_error(value):
    with pytest.raises(AssertionError):
        valid_list(value)
