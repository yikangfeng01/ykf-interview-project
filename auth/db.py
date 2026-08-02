"""PostgreSQL connection management for ykf-interview-project-db."""
import os
import sys
import psycopg2
import psycopg2.extras


DB_NAME = os.environ.get("PG_DB", "ykf-interview-project-db")
DB_USER = os.environ.get("PG_USER", "yikangfeng")
DB_HOST = os.environ.get("PG_HOST", "localhost")
DB_PORT = os.environ.get("PG_PORT", "5432")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_database():
    """Read data/init.sql and execute all DDL statements against the database.

    Uses CREATE TABLE IF NOT EXISTS / ALTER TABLE ADD COLUMN IF NOT EXISTS
    so it is safe to call multiple times (idempotent).

    Raises RuntimeError if the SQL file cannot be read or any statement fails.
    """
    sql_path = os.path.join(PROJECT_ROOT, "data", "init.sql")

    # Read the SQL file
    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"[init_database] ERROR: SQL file not found: {sql_path}", file=sys.stderr)
        raise RuntimeError(f"Database initialization file not found: {sql_path}")

    # Strip SQL comment lines (--) before splitting into statements
    sql_content = "\n".join(
        line for line in sql_content.splitlines()
        if not line.strip().startswith("--")
    )

    # Split into individual statements, filtering out empty/whitespace-only ones
    statements = [
        s.strip() for s in sql_content.split(";")
        if s.strip()
    ]

    conn = None
    errors = []

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            for stmt in statements:
                try:
                    cur.execute(stmt)
                except Exception as e:
                    preview = stmt[:80].replace("\n", " ")
                    errors.append(f"Statement failed: {preview}... | Error: {e}")
                    print(f"[init_database] ERROR: {preview}... | {e}", file=sys.stderr)

        if errors:
            conn.rollback()
            raise RuntimeError(
                f"Database initialization failed with {len(errors)} error(s):\n" +
                "\n".join(errors)
            )

        conn.commit()
        print(f"[init_database] OK - executed {len(statements)} statements from {sql_path}")

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"[init_database] ERROR: Database connection failed: {e}", file=sys.stderr)
        raise RuntimeError(f"Database connection failed during initialization: {e}")
    finally:
        if conn:
            conn.close()


def get_connection():
    """Return a new psycopg2 connection to the application database."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT,
    )


def get_cursor(conn=None):
    """Return a (cursor, connection) tuple. Creates a new connection if none provided.

    The caller is responsible for closing the connection after use.
    """
    if conn is None:
        conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return cur, conn


def close(conn, cur=None):
    """Safely close cursor and connection."""
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
