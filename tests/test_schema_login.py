import pytest
from pydantic import ValidationError

from schemas import Register


def test_schema_login_register_success():
    register = Register(
        email="testcorrectemail@example.com", password="my_secret"
    )
    assert register.email == "testcorrectemail@example.com"
    assert register.password == "my_secret"


def test_schema_login_register_fail():
    with pytest.raises(ValidationError):
        Register(email="incorrect_email")
