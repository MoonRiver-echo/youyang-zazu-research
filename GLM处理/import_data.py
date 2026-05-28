#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《酉阳杂俎》数据库数据导入脚本
"""

import sqlite3
import re
from pathlib import Path

DATA_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")
DB_PATH = DATA_DIR / "youyang_zazu.db"

# 叙事结构定义
NARRATIVE_CATEGORIES = {
    'A': ('历史纪事', '记载帝王将相事迹、朝政制度、正史性质的叙述'),
    'B': ('志怪故事', '含鬼神妖怪、异变怪异、因果报应的叙事故事'),
    'C': ('方术异闻', '描述方术、道法、幻术、祈雨驱邪等术数技艺'),
    'D': ('博物考证', '描述动植物、矿物、地理、自然现象的分类知识'),
    'E': ('礼仪制度', '记载礼仪、官制、婚俗、丧制等制度性内容'),
    'F': ('轶事传闻', '关于名人的轶事趣闻、传说故事'),
    'G': ('佛道典籍', '引述佛道经典、宗教义理、修行体系'),
    'H': ('技艺杂录', '记载手工技艺、奇术表演等'),
    'I': ('掌故杂识', '杂录医药、民俗、占卜、饮食等实用知识'),
    'J': ('注释考证', '文字考证、典籍引述、异说校勘'),
}

# 描写对象定义
SUBJECT_CATEGORIES = {
    'a': ('帝王将相', '关于帝王、后妃、将相、官员的段落'),
    'b': ('动物', '描述或涉及各种动物的段落'),
    'c': ('植物', '描述或涉及各种植物的段落'),
    'd': ('鬼神妖怪', '涉及鬼、神、妖怪作祟的段落'),
    'e': ('仙术道法', '涉及修道成仙、方术、道法的段落'),
    'f': ('佛事僧徒', '涉及佛教、僧人、佛事的段落'),
    'g': ('异域风俗', '描述外国异邦风土人情的段落'),
    'h': ('天文地理', '涉及天象、地理、自然奇观的段落'),
    'i': ('器物宝物', '涉及珍奇器物、宝物、武器的段落'),
    'j': ('医术药理', '涉及医药、药理、治病的段落'),
    'k': ('军事武艺', '涉及军事、战争、武艺的段落'),
    'l': ('婚丧礼俗', '涉及婚嫁、丧葬、典礼的段落'),
    'm': ('奇人异事', '描述个人奇异经历、怪事的段落'),
    'n': ('梦兆预言', '涉及梦境、占卜、预言的段落'),
    'o': ('书法文辞', '涉及书法、诗文、文辞的段落'),
    'p': ('音乐百戏', '涉及音乐、乐器、百戏的段落'),
    'q': ('饮食烹饪', '涉及食物、烹饪、饮馔的段落'),
    'r': ('盗贼侠客', '涉及盗贼、刺客、侠客的段落'),
    's': ('建筑交通', '涉及建筑、道路、桥梁的段落'),
    't': ('刑法纹身', '涉及刑法、刑罚、纹身的段落'),
}

def insert_categories():
    """插入分类数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute('DELETE FROM narrative_categories')
    cursor.execute('DELETE FROM subject_categories')
    
    # 插入叙事结构类别
    for code, (name, definition) in NARRATIVE_CATEGORIES.items():
        cursor.execute(
            'INSERT INTO narrative_categories VALUES (?, ?, ?)',
            (code, name, definition)
        )
    
    # 插入描写对象类别
    for code, (name, definition) in SUBJECT_CATEGORIES.items():
        cursor.execute(
            'INSERT INTO subject_categories VALUES (?, ?, ?)',
            (code, name, definition)
        )
    
    conn.commit()
    conn.close()
    print('Categories inserted')

def parse_paragraphs():
    """解析01-卷目分段.md提取段落数据"""
    paragraphs = []
    
    with open(DATA_DIR / '01-卷目分段.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取段落表格数据
    # 匹配: | 忠志-1 | 12-12 | A(历史纪事) | 帝王将相 | 内容摘要 |
    pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([A-J])\s*\([^)]+\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
    matches = re.findall(pattern, content)
    
    # 构建卷名映射
    chapter_to_volume = {}
    volume_pattern = r'###\s+(卷[一二三四五六七八九十]+)·([^\n]+)'
    for match in re.finditer(volume_pattern, content):
        volume = match.group(1)
        chapter = match.group(2).strip().replace('（', '(').replace('）', ')')
        # 提取篇名（去掉括号内容）
        chapter_clean = re.sub(r'\s*[（(].*?[）)]', '', chapter).strip()
        chapter_to_volume[chapter_clean] = volume
    
    for match in matches:
        para_id, line_range, nar_type, subjects, summary = match
        para_id = para_id.strip()
        
        # 解析卷·篇
        parts = para_id.split('-')
        chapter = parts[0] if parts else '未知'
        
        # 从映射获取卷名
        volume = chapter_to_volume.get(chapter, '未知')
        if volume == '未知' and chapter == '序':
            volume = '序'
        
        volume_chapter = f'{volume}·{chapter}' if volume != '序' else '序·序'
        
        # 解析行号
        line_match = re.match(r'(\d+)-(\d+)', line_range.strip())
        start_line = int(line_match.group(1)) if line_match else 0
        end_line = int(line_match.group(2)) if line_match else 0
        
        # 获取叙事结构名称
        narrative_name = NARRATIVE_CATEGORIES.get(nar_type, ('未知', ''))[0]
        
        paragraphs.append({
            'id': para_id,
            'volume': volume,
            'chapter': chapter,
            'volume_chapter': volume_chapter,
            'narrative_type': nar_type,
            'narrative_name': narrative_name,
            'content_summary': summary.strip(),
            'start_line': start_line,
            'end_line': end_line,
            'subjects': [s.strip() for s in subjects.split('、') if s.strip()]
        })
    
    print(f'Parsed {len(paragraphs)} paragraphs')
    return paragraphs

def insert_paragraphs(paragraphs):
    """插入段落数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute('DELETE FROM paragraphs')
    cursor.execute('DELETE FROM paragraph_subjects')
    
    # 创建名称到代码的映射
    subject_name_to_code = {name: code for code, (name, _) in SUBJECT_CATEGORIES.items()}
    
    for para in paragraphs:
        # 插入段落
        cursor.execute('''
        INSERT INTO paragraphs 
        (id, volume, chapter, volume_chapter, narrative_type, narrative_name, 
         content_summary, start_line, end_line)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            para['id'], para['volume'], para['chapter'], para['volume_chapter'],
            para['narrative_type'], para['narrative_name'],
            para['content_summary'], para['start_line'], para['end_line']
        ))
        
        # 插入段落-对象关系
        for subject_name in para['subjects']:
            subject_code = subject_name_to_code.get(subject_name)
            if subject_code:
                cursor.execute('''
                INSERT INTO paragraph_subjects VALUES (?, ?)
                ''', (para['id'], subject_code))
    
    conn.commit()
    conn.close()
    print(f'Inserted {len(paragraphs)} paragraphs')

def verify_data():
    """验证数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM paragraphs')
    para_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM narrative_categories')
    nar_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM subject_categories')
    sub_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM paragraph_subjects')
    rel_count = cursor.fetchone()[0]
    
    conn.close()
    
    print('\nData verification:')
    print(f'  Paragraphs: {para_count}')
    print(f'  Narrative categories: {nar_count}')
    print(f'  Subject categories: {sub_count}')
    print(f'  Relations: {rel_count}')

def main():
    print('='*50)
    print('Importing data into database')
    print('='*50)
    
    # 插入分类
    insert_categories()
    
    # 解析并插入段落
    paragraphs = parse_paragraphs()
    insert_paragraphs(paragraphs)
    
    # 验证数据
    verify_data()
    
    print('\nDone!')

if __name__ == '__main__':
    main()
