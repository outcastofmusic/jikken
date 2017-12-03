import pytest
from jikken.database.db_mongo import add_mongo

keys_to_add = (
    # key, value, expected
    ("key1", "hi", {"$push": {"key1": "hi"}}),
    (["key1", "key2"], "hi", {"$push": {"key1.key2": "hi"}}),
    ("key1", 1, {"$inc": {"key1": 1}}),
    ("key1", ["hello"], {"$addToSet": {"key1": "hello"}}),
    ("key1", {"hello", "bye"}, {"$addToSet": {"key1": {"hello", "bye"}}})
)


@pytest.mark.parametrize("key,value,expected", keys_to_add)
def test_add_mongo(key, value, expected):
    query = add_mongo(value, key=key)
    assert query == expected
