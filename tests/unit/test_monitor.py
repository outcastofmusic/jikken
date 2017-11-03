import pytest
from jikken.monitor import log_value, capture_value

testdata = [
    # name, value
    ("test", "seen"),
    ("loss", 0.5),
    ("finished", True),
    ("listings", [0.1, 0.2])
]


@pytest.mark.parametrize("name,value", testdata)
def test_logging_and_capturing_value(name, value, capsys):
    """Check that a value gets captured when it gets logged"""
    log_value(name=name, value=value)
    out, err = capsys.readouterr()
    for line in err:
        result = capture_value(line)
        assert result[0] == name
        assert result[1] == value
