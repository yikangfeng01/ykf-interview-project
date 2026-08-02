"""Data access layer for public variables (template-independent variable pool)."""

from auth.db import get_connection


def get_all() -> list[dict]:
    """Return all public variables ordered by name."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public_variables ORDER BY name")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    return [dict(zip(cols, row)) for row in rows]


def get_by_id(variable_id: int) -> dict | None:
    """Return a single public variable by its ID, or None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public_variables WHERE id = %s", (variable_id,))
    row = cur.fetchone()
    if row is None:
        return None
    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))


def create(**kwargs) -> dict:
    """Insert a new public variable. Returns the created record."""
    conn = get_connection()
    cur = conn.cursor()
    fields = [k for k in kwargs if k != "id"]  # exclude id, let DB assign it
    placeholders = ["%s"] * len(fields)
    values = [kwargs[f] for f in fields]
    sql = f"INSERT INTO public_variables ({', '.join(fields)}) VALUES ({', '.join(placeholders)}) RETURNING *"
    cur.execute(sql, values)
    row = cur.fetchone()
    conn.commit()
    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))


def update(variable_id: int, **kwargs) -> dict | None:
    """Update an existing public variable by ID. Returns updated record or None.

    If name or value is changed, cascade the update to signature_variables and
    project_template_variables where public_variables_id matches.
    """
    if not kwargs:
        return get_by_id(variable_id)
    conn = get_connection()
    cur = conn.cursor()
    fields = [k for k in kwargs if k != "id"]
    set_clause = ", ".join(f"{f} = %s" for f in fields)
    values = [kwargs[f] for f in fields] + [variable_id]
    sql = f"UPDATE public_variables SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *"
    cur.execute(sql, values)
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        return None
    cols = [desc[0] for desc in cur.description]

    # Cascade name/value updates to linked child records
    cascaded_fields = {k: kwargs[k] for k in kwargs if k in ("name", "value")}
    if cascaded_fields:
        set_clause_child = ", ".join(f"{f} = %s" for f in cascaded_fields)
        child_values = [cascaded_fields[f] for f in cascaded_fields] + [variable_id]
        cur.execute(
            f"UPDATE signature_variables SET {set_clause_child}, updated_at = NOW() "
            f"WHERE public_variables_id = %s",
            child_values,
        )
        cur.execute(
            f"UPDATE project_template_variables SET {set_clause_child}, updated_at = NOW() "
            f"WHERE public_variables_id = %s",
            child_values,
        )

    conn.commit()
    return dict(zip(cols, row))


def delete(variable_id: int) -> bool:
    """Delete a public variable by ID. Returns True if deleted, False if not found.

    Cascade deletes related records in signature_variables and
    project_template_variables where public_variables_id matches.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Cascade delete from child tables first (before parent)
    cur.execute(
        "DELETE FROM signature_variables WHERE public_variables_id = %s",
        (variable_id,),
    )
    cur.execute(
        "DELETE FROM project_template_variables WHERE public_variables_id = %s",
        (variable_id,),
    )

    # Delete the public variable itself
    cur.execute("DELETE FROM public_variables WHERE id = %s", (variable_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    return deleted


def bulk_create(variables: list[dict]) -> tuple[int, list[dict]]:
    """Batch insert public variables. Returns (success_count, [errors]).

    Each variable dict must contain: name, value, var_type, page, x, y, width,
    height, font_size, font_color, required.
    """
    conn = get_connection()
    cur = conn.cursor()
    imported = 0
    errors = []
    fields = [
        "name", "value", "var_type", "page", "x", "y", "width",
        "height", "font_size", "font_color", "required",
    ]
    for i, var in enumerate(variables):
        try:
            values = [var.get(f) for f in fields]
            placeholders = ["%s"] * len(fields)
            sql = (
                f"INSERT INTO public_variables ({', '.join(fields)}) "
                f"VALUES ({', '.join(placeholders)})"
            )
            cur.execute(sql, values)
            imported += 1
        except Exception as e:
            errors.append({"row": i + 2, "name": var.get("name", ""), "error": str(e)})
            conn.rollback()
            conn = get_connection()
            cur = conn.cursor()
    conn.commit()
    return imported, errors
