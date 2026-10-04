from blasto.utils import capitalize_name


def test_capitalize_name() -> None:
    assert capitalize_name("hello") == "Hello"
    assert capitalize_name("Hello") == "Hello"
    assert capitalize_name("") == ""
