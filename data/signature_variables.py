"""Data access layer for signature_variables table."""
from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError
from auth.db import get_connection, close


def get_by_template_id(template_id):
    """Return all variables for a given template, ordered by page and name."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM signature_variables WHERE template_id = %s ORDER BY page, name",
        (template_id,)
    )
    rows = cur.fetchall()
    close(conn, cur)
    return [dict(r) for r in rows]


def get_by_id(variable_id):
    """Return a single variable by ID or None."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM signature_variables WHERE id = %s", (variable_id,))
    row = cur.fetchone()
    close(conn, cur)
    return dict(row) if row else None


def create(template_id, name, var_type='signature', page=1, x=0, y=0,
           width=120, height=40, font_size=12, font_color='#000000', required=True, value='',
           public_variables_id=None):
    """Create a new signature_variable. Returns the created record or raises IntegrityError on duplicate name."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """INSERT INTO signature_variables 
               (template_id, name, value, var_type, page, x, y, width, height, font_size, font_color, required, public_variables_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING *""",
            (template_id, name, value, var_type, page, x, y, width, height, font_size, font_color, required, public_variables_id)
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row)
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        close(conn, cur)


def update(variable_id, **kwargs):
    """Update fields of a signature_variable. Returns the updated record or None if not found."""
    allowed_fields = ['name', 'value', 'var_type', 'page', 'x', 'y', 'width', 'height',
                      'font_size', 'font_color', 'required', 'public_variables_id']
    set_clauses = []
    values = []
    for key in allowed_fields:
        if key in kwargs:
            set_clauses.append(f"{key} = %s")
            values.append(kwargs[key])

    if not set_clauses:
        return get_by_id(variable_id)

    set_clauses.append("updated_at = NOW()")
    values.append(variable_id)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            f"UPDATE signature_variables SET {', '.join(set_clauses)} WHERE id = %s RETURNING *",
            values
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        close(conn, cur)


def delete(variable_id):
    """Delete a signature_variable by ID. Returns True if deleted, False if not found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM signature_variables WHERE id = %s", (variable_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    close(conn, cur)
    return deleted


def bulk_create(template_id, variables):
    """Bulk insert variables. Each variable is a dict with keys matching column names.
    Returns (imported_count, errors) where errors is a list of {row, message}."""
    imported = 0
    errors = []
    for idx, var in enumerate(variables):
        try:
            create(
                template_id=template_id,
                name=var.get('name', '').strip(),
                value=var.get('value', ''),
                var_type=var.get('var_type', 'signature'),
                page=int(var.get('page', 1)),
                x=float(var.get('x', 0)),
                y=float(var.get('y', 0)),
                width=float(var.get('width', 120)),
                height=float(var.get('height', 40)),
                font_size=int(var.get('font_size', 12)),
                font_color=str(var.get('font_color', '#000000')),
                required=str(var.get('required', 'true')).lower() in ('true', '1', 'yes'),
                public_variables_id=var.get('public_variables_id') or None,
            )
            imported += 1
        except IntegrityError:
            errors.append({"row": idx + 2, "message": f"Variable name '{var.get('name', '')}' already exists"})
        except (ValueError, TypeError) as e:
            errors.append({"row": idx + 2, "message": f"Invalid field value: {str(e)}"})
    return imported, errors
