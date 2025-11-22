"""Unit tests for scripts.py"""

import sys

import pytest
from sqlmodel import Session, text

from apps.api_server.dependencies import constants, database, scripts


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param("--create", (1, 0, 0), id="only create() should be called"),
        pytest.param(
            "--seed", (0, 1, None), id="only seed() should be called, with no argument"
        ),
        pytest.param(
            "--seed --limit 7",
            (0, 1, 7),
            id="only seed() should be called, with argument of 7",
        ),
        pytest.param(
            "--limit 24 --create --seed",
            (1, 1, 24),
            id="create(), then seed() should be called, with argument of 24",
        ),
    ],
)
def test_main(mocker, test_input, expected):
    """
    Unit test for main().  Test the function on various user inputs and
    check whether the correct functions are called.
    """
    cli_input = ["scripts.py", *test_input.split(" ")]
    calls_to_create, calls_to_seed, seed_argument = expected
    mocked_create = mocker.patch("apps.api_server.dependencies.scripts.create")
    mocked_seed = mocker.patch("apps.api_server.dependencies.scripts.seed")
    mocker.patch.object(sys, "argv", cli_input)

    scripts.main()
    assert mocked_create.call_count == calls_to_create
    assert mocked_seed.call_count == calls_to_seed
    if calls_to_seed == 1:
        assert mocked_seed.called_once_with(seed_argument)


def test_seed_script():
    temp_engine = database.get_engine(
        database_uri=constants.SQLITE_URI.format(":memory:")
    )
    scripts.create(temp_engine)
    scripts.seed(temp_engine, limit=3)

    # Create a session bound to this engine
    with Session(temp_engine) as session:
        result = session.exec(text("SELECT * FROM products")).all()
        assert len(result) == 3
