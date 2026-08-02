"""PostgreSQL-backed template data access layer."""
import os
from typing import List, Optional
from auth.db import get_connection


def list_all(category: Optional[str] = None) -> List[dict]:
    """List all templates, optionally filtered by category."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if category:
            cur.execute(
                "SELECT id, name, category, file_path, description FROM templates WHERE category = %s ORDER BY name;",
                (category,),
            )
        else:
            cur.execute(
                "SELECT id, name, category, file_path, description FROM templates ORDER BY category, name;"
            )
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()
        conn.close()


def get_by_id(template_id: int) -> Optional[dict]:
    """Get a single template by ID."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, name, category, file_path, description FROM templates WHERE id = %s;",
            (template_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        cur.close()
        conn.close()


def create(name: str, category: str = '', description: str = '', file_path: str = '') -> dict:
    """Insert a new template record and return it."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO templates (name, category, description, file_path) "
            "VALUES (%s, %s, %s, %s) RETURNING id, name, category, file_path, description;",
            (name, category, description, file_path),
        )
        row = cur.fetchone()
        conn.commit()
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        cur.close()
        conn.close()


def update(template_id: int, name: str = None, category: str = None, description: str = None, file_path: str = None) -> Optional[dict]:
    """Update template metadata. Returns updated dict or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        set_clauses = []
        values = []
        if name is not None:
            set_clauses.append("name = %s")
            values.append(name)
        if category is not None:
            set_clauses.append("category = %s")
            values.append(category)
        if description is not None:
            set_clauses.append("description = %s")
            values.append(description)
        if file_path is not None:
            set_clauses.append("file_path = %s")
            values.append(file_path)
        if not set_clauses:
            return get_by_id(template_id)
        values.append(template_id)
        cur.execute(
            f"UPDATE templates SET {', '.join(set_clauses)} "
            "WHERE id = %s RETURNING id, name, category, file_path, description;",
            values,
        )
        row = cur.fetchone()
        conn.commit()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        cur.close()
        conn.close()


def delete(template_id: int) -> bool:
    """Delete a template by ID.

    Cascade deletes project_templates records where public_template_id matches,
    then cascade deletes signature_variables.
    Returns True if deleted.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Cascade delete project_templates first
        cur.execute(
            "DELETE FROM project_templates WHERE public_template_id = %s",
            (template_id,),
        )
        # Cascade delete signature_variables (via DB ON DELETE CASCADE)
        cur.execute("DELETE FROM templates WHERE id = %s;", (template_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        cur.close()
        conn.close()
