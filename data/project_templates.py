"""Data access layer for project-scoped signature page templates."""

from typing import Optional, List
from auth.db import get_connection


def _row_to_dict(cur, row):
    """Convert a psycopg2 result row (tuple) into a dict keyed by column name."""
    if row is None:
        return None
    columns = [desc[0] for desc in cur.description]
    return dict(zip(columns, row))


def _rows_to_dicts(cur, rows):
    """Convert a list of psycopg2 result rows (tuples) into dicts."""
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in rows]


def list_all(project_id: int, category: Optional[str] = None) -> List[dict]:
    """List all templates for a project, optionally filtered by category."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if category:
            cur.execute(
                "SELECT * FROM project_templates WHERE project_id = %s AND category = %s ORDER BY id",
                (project_id, category))
        else:
            cur.execute(
                "SELECT * FROM project_templates WHERE project_id = %s ORDER BY id",
                (project_id,))
        return _rows_to_dicts(cur, cur.fetchall())
    finally:
        cur.close()
        conn.close()


def get_by_id(template_id: int) -> Optional[dict]:
    """Get a single project template by its id."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM project_templates WHERE id = %s", (template_id,))
        return _row_to_dict(cur, cur.fetchone())
    finally:
        cur.close()
        conn.close()


def create(project_id: int, name: str, category: str, description: str, file_path: str,
           public_template_id: int = None) -> dict:
    """Insert a new project template record and return it."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO project_templates (project_id, name, category, file_path, description, public_template_id) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (project_id, name, category, file_path, description, public_template_id))
        row = cur.fetchone()
        conn.commit()
        return _row_to_dict(cur, row)
    finally:
        cur.close()
        conn.close()


def update(template_id: int, name: Optional[str] = None, category: Optional[str] = None,
           description: Optional[str] = None, file_path: Optional[str] = None) -> Optional[dict]:
    """Update a project template's metadata and return the updated record."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        fields = []
        values = []
        if name is not None:
            fields.append("name = %s")
            values.append(name)
        if category is not None:
            fields.append("category = %s")
            values.append(category)
        if description is not None:
            fields.append("description = %s")
            values.append(description)
        if file_path is not None:
            fields.append("file_path = %s")
            values.append(file_path)
        if not fields:
            cur.execute("SELECT * FROM project_templates WHERE id = %s", (template_id,))
            return _row_to_dict(cur, cur.fetchone())
        values.append(template_id)
        cur.execute(
            f"UPDATE project_templates SET {', '.join(fields)} WHERE id = %s RETURNING *",
            tuple(values))
        row = cur.fetchone()
        conn.commit()
        return _row_to_dict(cur, row)
    finally:
        cur.close()
        conn.close()


def delete(template_id: int) -> Optional[dict]:
    """Delete a project template by id. Returns the row before deletion (for file cleanup)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM project_templates WHERE id = %s", (template_id,))
        row = _row_to_dict(cur, cur.fetchone())
        if row:
            cur.execute("DELETE FROM project_templates WHERE id = %s", (template_id,))
            conn.commit()
        return row
    finally:
        cur.close()
        conn.close()
