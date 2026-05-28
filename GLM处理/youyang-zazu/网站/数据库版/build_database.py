#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
构建酉阳杂俎（Youyang Zazu）数据库
1) 删除已存在的数据库文件
2) 创建所需表结构
3) 将6个 CSV 文件导入对应表
4) 打印导入统计摘要
"""
import csv
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")
DB_PATH = BASE_DIR / "youyang_zazu.db"

NARRATIVE_DETAIL_CSV = BASE_DIR / "叙事分类明细.csv"
NARRATIVE_STATS_CSV = BASE_DIR / "叙事分类统计.csv"
THEME_DETAIL_CSV = BASE_DIR / "主题分类明细.csv"
THEME_STATS_CSV = BASE_DIR / "主题分类统计.csv"
THEME_FREQUENCY_CSV = BASE_DIR / "主题频次统计.csv"
DUPLICATE_THEMES_CSV = BASE_DIR / "重复主题分类.csv"


def ensure_dir(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def create_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE narrative_detail (
        narrative_category TEXT,
        volume_index INTEGER,
        volume_title TEXT,
        source TEXT,
        paragraph_id TEXT,
        text TEXT
    )
    """ )

    cur.execute("""
    CREATE TABLE narrative_stats (
        narrative_category TEXT,
        paragraph_count INTEGER,
        absolute_percentage TEXT
    )
    """ )

    cur.execute("""
    CREATE TABLE theme_detail (
        broad_category TEXT,
        level1_subject TEXT,
        level2_subject TEXT,
        specific_subject TEXT,
        volume_index INTEGER,
        volume_title TEXT,
        source TEXT,
        paragraph_id TEXT,
        primary_subject TEXT,
        annotation_supported TEXT,
        original_subject TEXT,
        text TEXT
    )
    """ )

    cur.execute("""
    CREATE TABLE theme_stats (
        broad_category TEXT,
        paragraph_count INTEGER,
        absolute_percentage TEXT
    )
    """ )

    cur.execute("""
    CREATE TABLE theme_frequency (
        level1_subject TEXT,
        level2_subject TEXT,
        appearance_count INTEGER
    )
    """ )

    cur.execute("""
    CREATE TABLE duplicate_themes (
        volume_index INTEGER,
        volume_title TEXT,
        source TEXT,
        paragraph_id TEXT,
        duplicate_broad_categories TEXT,
        duplicate_specific_subjects TEXT,
        text TEXT
    )
    """ )
    conn.commit()


def insert_narrative_detail(conn: sqlite3.Connection, row: dict):
    sql = """
    INSERT INTO narrative_detail
    (narrative_category, volume_index, volume_title, source, paragraph_id, text)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (
        row.get("narrative_category"),
        int(row["volume_index"]) if row.get("volume_index") not in (None, "") else None,
        row.get("volume_title"),
        row.get("source"),
        row.get("paragraph_id"),
        row.get("text"),
    ))


def import_narrative_detail(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            insert_narrative_detail(conn, row)
            count += 1
    return count


def insert_narrative_stat(row: dict):
    return (
        row.get("narrative_category"),
        int(row.get("paragraph_count", 0)),
        row.get("absolute_percentage"),
    )


def import_narrative_stats(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO narrative_stats (narrative_category, paragraph_count, absolute_percentage) VALUES (?, ?, ?)",
                insert_narrative_stat(row),
            )
            count += 1
    return count


def insert_theme_detail(row: dict):
    return (
        row.get("broad_category"),
        row.get("level1_subject"),
        row.get("level2_subject"),
        row.get("specific_subject"),
        int(row["volume_index"]) if row.get("volume_index") not in (None, "") else None,
        row.get("volume_title"),
        row.get("source"),
        row.get("paragraph_id"),
        row.get("primary_subject"),
        row.get("annotation_supported"),
        row.get("original_subject"),
        row.get("text"),
    )


def import_theme_detail(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO theme_detail (broad_category, level1_subject, level2_subject, specific_subject, volume_index, volume_title, source, paragraph_id, primary_subject, annotation_supported, original_subject, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                insert_theme_detail(row),
            )
            count += 1
    return count


def insert_theme_stat(row: dict):
    return (
        row.get("broad_category"),
        int(row.get("paragraph_count", 0)),
        row.get("absolute_percentage"),
    )


def import_theme_stats(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO theme_stats (broad_category, paragraph_count, absolute_percentage) VALUES (?, ?, ?)",
                insert_theme_stat(row),
            )
            count += 1
    return count


def insert_theme_frequency(row: dict):
    return (
        row.get("level1_subject"),
        row.get("level2_subject"),
        int(row.get("appearance_count", 0)),
    )


def import_theme_frequency(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO theme_frequency (level1_subject, level2_subject, appearance_count) VALUES (?, ?, ?)",
                insert_theme_frequency(row),
            )
            count += 1
    return count


def insert_duplicate_themes(row: dict):
    return (
        int(row.get("volume_index")) if row.get("volume_index") not in (None, "") else None,
        row.get("volume_title"),
        row.get("source"),
        row.get("paragraph_id"),
        row.get("duplicate_broad_categories"),
        row.get("duplicate_specific_subjects"),
        row.get("text"),
    )


def import_duplicate_themes(csv_path: Path, conn: sqlite3.Connection) -> int:
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO duplicate_themes (volume_index, volume_title, source, paragraph_id, duplicate_broad_categories, duplicate_specific_subjects, text) VALUES (?, ?, ?, ?, ?, ?, ?)",
                insert_duplicate_themes(row),
            )
            count += 1
    return count


def main():
    ensure_dir(BASE_DIR)
    # 删除已存在的数据库
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        create_tables(conn)

        counts = {}

        # 1) narrative_detail
        counts['narrative_detail'] = import_narrative_detail(NARRATIVE_DETAIL_CSV, conn)
        # 2) narrative_stats
        counts['narrative_stats'] = import_narrative_stats(NARRATIVE_STATS_CSV, conn)
        # 3) theme_detail
        counts['theme_detail'] = import_theme_detail(THEME_DETAIL_CSV, conn)
        # 4) theme_stats
        counts['theme_stats'] = import_theme_stats(THEME_STATS_CSV, conn)
        # 5) theme_frequency
        counts['theme_frequency'] = import_theme_frequency(THEME_FREQUENCY_CSV, conn)
        # 6) duplicate_themes
        counts['duplicate_themes'] = import_duplicate_themes(DUPLICATE_THEMES_CSV, conn)

        conn.commit()
        print("数据导入完成：")
        for k, v in counts.items():
            print(f" - {k}: {v} 条记录")
        # 打印简单统计摘要
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM narrative_detail")
        nd = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM narrative_stats")
        ns = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM theme_detail")
        td = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM theme_stats")
        ts = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM theme_frequency")
        tf = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM duplicate_themes")
        dt = cur.fetchone()[0]
        print("摘要：")
        print(f" 叙事_detail 行数: {nd}")
        print(f" 叙事_stats 行数: {ns}")
        print(f" 主题_detail 行数: {td}")
        print(f" 主题_stats 行数: {ts}")
        print(f" 主题_frequency 行数: {tf}")
        print(f" duplicate_themes 行数: {dt}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
