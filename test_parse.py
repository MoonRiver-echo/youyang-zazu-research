import re

def parse_filename(basename):
    name, ext = os.path.splitext(basename)
    name = re.sub(r'\s*\((?:z-library\.sk|1lib\.sk|z-lib\.sk)[^)]*\)', '', name)
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    name = name.strip()
    
    author = None
    title = None
    doc_type = 'article'
    
    if '_' in name:
        parts_r = name.rsplit('_', 1)
        cand_author = parts_r[1].strip()
        cand_title = parts_r[0].strip()
        
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', cand_author))
        title_like = bool(re.search(r'(研究|探析|初探|论|分析|考察|叙事|小说|文化)', cand_author))
        too_long = len(cand_author) > 20
        
        if has_cn and not title_like and not too_long:
            author = cand_author
            title = cand_title
        else:
            parts_f = name.split('_', 1)
            title = parts_f[0].strip()
            author = parts_f[1].strip()
    else:
        m = re.search(r'[（(]([^（()]+?)(?:著|编|译)?[）)]$', name)
        if m:
            author = m.group(1).strip()
            title = name[:m.start()].strip()
            doc_type = 'book'
        else:
            title = name.strip()
    
    title = re.sub(r'^\[.*?\]\s*', '', title).strip()
    if author:
        author = re.sub(r'[（(].*?[）)]', '', author).strip()
    
    return title, author, doc_type

if __name__ == '__main__':
    import os
    test_files = [
        '《酉阳杂俎·_尸穸_》中的“盗墓与反盗墓”现象探析_许关喜.pdf',
        '唐代小说的传播与接受_陈依雯（Tang_Yee_Woon）.caj',
        '“异—常”相对结构_《阅微草堂笔记》等清代志怪小说的叙事方式_吴卉.caj',
        '从死亡的归回_解读段成式《酉阳杂俎》故事中的话语——由顾非熊形象看由阴返阳故事的叙事传统与艺术创造_赖春桃.pdf',
        '《酉阳杂俎》中游仙故事的传承与变异_赖春桃.pdf'
    ]
    with open('test_parse_result.txt', 'w', encoding='utf-8') as out:
        for fname in test_files:
            t, a, d = parse_filename(fname)
            out.write(f'fname={fname}\n')
            out.write(f't={t}\n')
            out.write(f'a={a}\n')
            out.write('---\n')
