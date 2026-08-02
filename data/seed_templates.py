"""Seed sample DOCX signature page templates into ykf-interview-project-db."""
import psycopg2
import os

DB_NAME = os.environ.get("PG_DB", "ykf-interview-project-db")
DB_USER = os.environ.get("PG_USER", "yikangfeng")
DB_HOST = os.environ.get("PG_HOST", "localhost")

TEMPLATES = [
    {
        "name": "股权转让签字页",
        "category": "share_transfer",
        "file_path": "templates/share_transfer_standard.docx",
        "description": "标准股权转让协议签字页模板，含转让方、受让方、目标公司三方签字区域",
    },
    {
        "name": "增资协议签字页",
        "category": "capital_increase",
        "file_path": "templates/capital_increase_standard.docx",
        "description": "增资扩股协议签字页模板，含增资方、原股东、目标公司签字区域",
    },
    {
        "name": "股权转让签字页（简化版）",
        "category": "share_transfer",
        "file_path": "templates/share_transfer_simple.docx",
        "description": "简化版股权转让签字页，仅含转让方与受让方签字区域",
    },
    {
        "name": "股东会决议签字页",
        "category": "resolution",
        "file_path": "templates/resolution_standard.docx",
        "description": "股东会决议签字页模板，适用于公司重大事项决议签署",
    },
    {
        "name": "董事会决议签字页",
        "category": "resolution",
        "file_path": "templates/board_resolution.docx",
        "description": "董事会决议签字页模板，含全体董事签字区域",
    },
    {
        "name": "增资协议签字页（多投资方）",
        "category": "capital_increase",
        "file_path": "templates/capital_increase_multi.docx",
        "description": "多投资方增资协议签字页，支持多个增资方同时签署",
    },
]


def main():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST)
    cur = conn.cursor()

    for t in TEMPLATES:
        cur.execute(
            "INSERT INTO templates (name, category, file_path, description) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;",
            (t["name"], t["category"], t["file_path"], t["description"]),
        )
        print(f"Seeded template: {t['name']} [{t['category']}]")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Seed complete. {len(TEMPLATES)} templates inserted.")


if __name__ == "__main__":
    main()
