#!/usr/bin/env python3
"""Create relational SQLite database for 酉阳杂俎 narrative category statistics."""

import sqlite3
import os

DB_PATH = r"C:\Users\lx\Desktop\前期准备\prepare\narrative_category_stats.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# ── 1. categories ──
cur.execute("""
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT,
    parent_id   INTEGER REFERENCES categories(id),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
)
""")

# ── 2. editions ──
cur.execute("""
CREATE TABLE editions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT    NOT NULL UNIQUE,
    description TEXT,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
)
""")

# ── 3. category_stats ──
cur.execute("""
CREATE TABLE category_stats (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id      INTEGER NOT NULL REFERENCES categories(id),
    edition_id       INTEGER NOT NULL REFERENCES editions(id),
    paragraph_count  INTEGER NOT NULL CHECK (paragraph_count >= 0),
    percentage       REAL    NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    created_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, edition_id)
)
""")

# ── 4. paragraphs ──
cur.execute("""
CREATE TABLE paragraphs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    edition_id  INTEGER NOT NULL REFERENCES editions(id),
    volume      TEXT,
    sequence_no INTEGER,
    content     TEXT,
    notes       TEXT,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
)
""")

# ── 5. annotations ──
cur.execute("""
CREATE TABLE annotations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    paragraph_id INTEGER NOT NULL REFERENCES paragraphs(id),
    annotator    TEXT,
    note         TEXT    NOT NULL,
    created_at   TEXT    DEFAULT CURRENT_TIMESTAMP
)
""")

# ── Indexes ──
cur.execute("CREATE INDEX idx_categories_name    ON categories(name)")
cur.execute("CREATE INDEX idx_categories_parent   ON categories(parent_id)")
cur.execute("CREATE INDEX idx_category_stats_cat  ON category_stats(category_id)")
cur.execute("CREATE INDEX idx_category_stats_ed   ON category_stats(edition_id)")
cur.execute("CREATE INDEX idx_paragraphs_cat      ON paragraphs(category_id)")
cur.execute("CREATE INDEX idx_paragraphs_ed       ON paragraphs(edition_id)")
cur.execute("CREATE INDEX idx_paragraphs_vol_seq  ON paragraphs(volume, sequence_no)")
cur.execute("CREATE INDEX idx_annotations_para    ON annotations(paragraph_id)")

# ── Views ──
cur.execute("""
CREATE VIEW v_category_ranking AS
    SELECT
        cs.id,
        c.name            AS category,
        e.label           AS edition,
        cs.paragraph_count,
        ROUND(cs.percentage, 2) AS percentage,
        cs.created_at
    FROM category_stats cs
    JOIN categories c ON cs.category_id = c.id
    JOIN editions   e ON cs.edition_id  = e.id
    ORDER BY cs.paragraph_count DESC
""")

cur.execute("""
CREATE VIEW v_category_hierarchy AS
    SELECT
        c.id,
        c.name       AS category,
        p.name       AS parent_category,
        c.sort_order
    FROM categories c
    LEFT JOIN categories p ON c.parent_id = p.id
    ORDER BY c.sort_order, c.id
""")

# ── Seed data ──
cur.execute(
    "INSERT INTO editions (label, description) VALUES (?, ?)",
    ("据注三次修订", "初校叙事分类统计——据注三次修订版"),
)
edition_id = cur.lastrowid

DATA = [
    ("动植物谱录", 237, 29.66,  1),
    ("异闻志怪",   151, 18.90,  2),
    ("人物轶事",    95, 11.89,  3),
    ("知识考辨",    60,  7.51,  4),
    ("神仙方术",    60,  7.51,  5),
    ("佛道异闻",    45,  5.63,  6),
    ("器艺技法",    42,  5.26,  7),
    ("异境异域",    30,  3.75,  8),
    ("征兆占验",    26,  3.25,  9),
    ("饮食医药",    19,  2.38, 10),
    ("礼俗制度",    18,  2.25, 11),
    ("器物名物",     6,  0.75, 12),
    ("冥界报应",     5,  0.63, 13),
    ("天文地理",     5,  0.63, 14),
]

for name, count, pct, sort in DATA:
    cur.execute("INSERT INTO categories (name, sort_order) VALUES (?, ?)", (name, sort))
    cat_id = cur.lastrowid
    cur.execute(
        "INSERT INTO category_stats (category_id, edition_id, paragraph_count, percentage) VALUES (?, ?, ?, ?)",
        (cat_id, edition_id, count, pct),
    )

conn.commit()

# ── Verify ──
print("=== Tables ===")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(" ", row[0])

print("\n=== Views ===")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"):
    print(" ", row[0])

print("\n=== categories (14 rows) ===")
cur.execute("SELECT id, name, sort_order FROM categories ORDER BY sort_order")
for r in cur.fetchall():
    print(f"  {r[0]:>2}  {r[1]}  (sort={r[2]})")

print("\n=== editions ===")
cur.execute("SELECT id, label, description FROM editions")
for r in cur.fetchall():
    print(f"  {r[0]}  {r[1]}  — {r[2]}")

print("\n=== v_category_ranking ===")
cur.execute("SELECT * FROM v_category_ranking")
cols = [d[0] for d in cur.description]
print("  " + " | ".join(cols))
for r in cur.fetchall():
    print("  " + " | ".join(str(x) for x in r))

print("\n=== v_category_hierarchy ===")
cur.execute("SELECT * FROM v_category_hierarchy")
cols = [d[0] for d in cur.description]
print("  " + " | ".join(cols))
for r in cur.fetchall():
    print("  " + " | ".join(str(x) for x in r))

# ── Full DDL ──
print("\n=== Full DDL ===")
for row in cur.execute(
    "SELECT name, sql FROM sqlite_master WHERE type IN ('table','view') AND sql IS NOT NULL ORDER BY name"
):
    print(f"-- {row[0]}")
    print(row[1])
    print()

conn.close()
print(f"Done: {DB_PATH}")