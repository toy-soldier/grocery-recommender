"""This module contains database creation and seed scripts."""

import argparse
import pathlib

from sqlalchemy import Engine

from apps.api_server.dependencies import constants, database


def execute_script_against_db(
    engine: Engine, script_filename: str, limit: int | None
) -> None:
    """Execute the script against the database."""
    basedir = pathlib.Path(__file__).parent.parent.resolve()
    with (
        engine.connect() as conn,
        open(basedir / script_filename, "r") as f,
    ):
        if not limit:
            sql = f.read()
        else:
            lines = []
            for _ in range(limit):
                lines.append(f.readline())
            sql = "".join(lines)

        # for databases such as PostgreSQL, running scripts using the Connection object is fine
        # since the database is SQLite, we need to work directly with the driver to run scripts
        raw_connection = conn.connection
        raw_connection.executescript(sql)


def create(engine: Engine) -> None:
    """Create database and table."""
    print("create called")
    execute_script_against_db(engine, constants.SQLITE_CREATE_SCRIPT, None)
    print("database created!")


def seed(engine: Engine, limit: int | None) -> None:
    """Run the first `limit` INSERT queries from seed file to populate table."""
    print("seed called")
    execute_script_against_db(engine, constants.SQLITE_SEED_SCRIPT, limit)
    print("database populated!")


def main() -> None:
    """Script entrypoint."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--create", action="store_true", help="create database and table"
    )
    parser.add_argument(
        "--seed", action="store_true", help="populate table with initial data"
    )
    parser.add_argument(
        "--limit", type=int, help="limit on the number of records to load"
    )
    args = parser.parse_args()

    engine = database.get_engine(None)

    if args.create:
        create(engine)
    if args.seed:
        seed(engine, args.limit)


if __name__ == "__main__":
    main()
