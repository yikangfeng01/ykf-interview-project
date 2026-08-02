"""Data access layer for project template signature variables."""

from typing import List, Optional
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


def get_by_template_id(template_id: int) -> List[dict]:
    """Get all variables for a project template, ordered by page and name."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM project_template_variables WHERE template_id = %s ORDER BY page, name",
            (template_id,))
        return _rows_to_dicts(cur, cur.fetchall())
    finally:
        cur.close()
        conn.close()


def get_by_id(variable_id: int) -> Optional[dict]:
    """Get a single variable by its id."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM project_template_variables WHERE id = %s", (variable_id,))
        return _row_to_dict(cur, cur.fetchone())
    finally:
        cur.close()
        conn.close()


def create(template_id: int, name: str, var_type: str = 'signature', page: int = 1,
           x: float = 0, y: float = 0, width: float = 120, height: float = 40,
           font_size: int = 12, font_color: str = '#000000', required: bool = True,
           value: str = '', public_variables_id: int = None) -> dict:
    """Create a new variable for a project template and return it."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO project_template_variables "
            "(template_id, name, value, var_type, page, x, y, width, height, font_size, font_color, required, public_variables_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (template_id, name, value, var_type, page, x, y, width, height, font_size, font_color, required, public_variables_id))
        row = cur.fetchone()
        conn.commit()
        return _row_to_dict(cur, row)
    finally:
        cur.close()
        conn.close()


def update(variable_id: int, **kwargs) -> Optional[dict]:
    """Update fields of a project template variable and return the updated record."""
    allowed_fields = {'name', 'value', 'var_type', 'page', 'x', 'y', 'width', 'height',
                      'font_size', 'font_color', 'required', 'public_variables_id'}
    conn = get_connection()
    cur = conn.cursor()
    try:
        fields = []
        values = []
        for key, val in kwargs.items():
            if key in allowed_fields:
                fields.append(f"{key} = %s")
                values.append(val)
        if not fields:
            cur.execute("SELECT * FROM project_template_variables WHERE id = %s", (variable_id,))
            return _row_to_dict(cur, cur.fetchone())
        values.append(variable_id)
        cur.execute(
            f"UPDATE project_template_variables SET {', '.join(fields)}, updated_at = NOW() "
            f"WHERE id = %s RETURNING *",
            tuple(values))
        row = cur.fetchone()
        conn.commit()
        return _row_to_dict(cur, row)
    finally:
        cur.close()
        conn.close()


def delete(variable_id: int) -> None:
    """Delete a project template variable by id."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM project_template_variables WHERE id = %s", (variable_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def bulk_create(template_id: int, variables: List[dict]) -> tuple:
    """Bulk insert variables for a project template.

    Args:
        template_id: The project template id.
        variables: List of dicts with keys matching create() parameters.

    Returns:
        (imported_count, error_details): Count of successfully imported rows and list of error dicts.
    """
    errors = []
    imported = 0
    conn = get_connection()
    cur = conn.cursor()
    try:
        for var in variables:
            try:
                cur.execute(
                    "INSERT INTO project_template_variables "
                    "(template_id, name, value, var_type, page, x, y, width, height, font_size, font_color, required, public_variables_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                    (template_id,
                     var.get('name'),
                     var.get('value', ''),
                     var.get('var_type', 'signature'),
                     var.get('page', 1),
                     var.get('x', 0),
                     var.get('y', 0),
                     var.get('width', 120),
                     var.get('height', 40),
                     var.get('font_size', 12),
                     var.get('font_color', '#000000'),
                     var.get('required', True),
                     var.get('public_variables_id', None)))
                imported += 1
            except Exception as e:
                errors.append({'row': var.get('name', 'unknown'), 'error': str(e)})
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return imported, errors
