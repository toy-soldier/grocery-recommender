"""This module defines the application's constants."""

SQLITE_DB_PATH = "dependencies/inventory.sqlite3"
SQLITE_URI = "sqlite:///{}"
SQLITE_CREATE_SCRIPT = "assets/create.sql"
SQLITE_SEED_SCRIPT = "assets/seed.sql"

# allow FastAPI to use the same SQLite database in different threads
SQLITE_CONNECT_ARGS = {"check_same_thread": False}
