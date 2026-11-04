from unittest import mock

from myrepolib import main


def test_func():
    result = main.myfunc()
    assert result == 1


def test_print_name():
    assert main.print_name("edwin") == "edwin-apple"


def test_fake_data():
    assert main.fake_data() == {"one": 1, "two": 2}


def test_call_web_service():
    fake_response = mock.Mock(content=b'{"one": 1, "two": 2}')
    with mock.patch("myrepolib.main.requests.get", return_value=fake_response) as get:
        assert main.call_web_service("http://example.test/fakedata") == {"one": 1, "two": 2}
    get.assert_called_once_with("http://example.test/fakedata", timeout=10)
