"""Pytest configuration - ensure database initialization is skipped during tests."""
import os
os.environ["SKIP_DB_INIT"] = "1"
