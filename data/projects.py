"""PostgreSQL-backed project data access layer."""
from typing import Optional, List
from auth.db import get_connection


def list_by_user(username: str) -> List[dict]:
    """List all projects owned by a given username."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT p.id, p.name, p.description, p.status, p.template_id, p.created_by, 
                   p.created_at, p.updated_at, t.name AS template_name
            FROM projects p
            LEFT JOIN templates t ON p.template_id = t.id
            WHERE p.created_by = %s
            ORDER BY p.updated_at DESC
            """,
            (username,),
        )
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()
        conn.close()


def get_by_id(project_id: int) -> Optional[dict]:
    """Get a single project by ID, including its template name if any."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT p.id, p.name, p.description, p.status, p.template_id, p.created_by,
                   p.created_at, p.updated_at, t.name AS template_name
            FROM projects p
            LEFT JOIN templates t ON p.template_id = t.id
            WHERE p.id = %s
            """,
            (project_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        cur.close()
        conn.close()


def create(name: str, username: str, description: Optional[str] = None) -> dict:
    """Create a new project and return it."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO projects (name, description, created_by) VALUES (%s, %s, %s) RETURNING id;",
            (name, description, username),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return get_by_id(new_id)


def update(project_id: int, **kwargs) -> Optional[dict]:
    """Update project fields. Returns the updated project or None if not found."""
    allowed = {"name", "description", "status", "template_id"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_by_id(project_id)

    conn = get_connection()
    cur = conn.cursor()
    try:
        set_clauses = [f"{k} = %s" for k in updates.keys()]
        values = list(updates.values())
        # Also touch updated_at
        set_clauses.append("updated_at = NOW()")
        values.append(project_id)

        cur.execute(
            f"UPDATE projects SET {', '.join(set_clauses)} WHERE id = %s;",
            values,
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return get_by_id(project_id)


def delete(project_id: int) -> bool:
    """Delete a project by ID. Returns True if deleted, False if not found."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM projects WHERE id = %s;", (project_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        cur.close()
        conn.close()
