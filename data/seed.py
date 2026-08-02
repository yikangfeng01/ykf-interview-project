"""Seed sample users into ykf-interview-project-db."""
import bcrypt
import psycopg2
import os

DB_NAME = os.environ.get("PG_DB", "ykf-interview-project-db")
DB_USER = os.environ.get("PG_USER", "yikangfeng")
DB_HOST = os.environ.get("PG_HOST", "localhost")

PASSWORD = "password123"
USERS = ["admin", "lawyer01"]


def main():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST)
    cur = conn.cursor()

    for username in USERS:
        password_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
            (username, password_hash),
        )
        print(f"Seeded user: {username}")

    conn.commit()
    cur.close()
    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
