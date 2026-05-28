import fitz
import os
import glob
import re
import json
import unicodedata
from collections import Counter

ref_dir = r'C:\Users\lx\Desktop\前期准备\references'

def parse_filename(basename):
    """Extract title and author from filename with robust underscore handling."""
    name, ext = os.path.splitext(basename)
    name = re.sub(r'\s*\((?:z-library\.sk|1lib\.sk|z-lib\.sk)[^)]*\)', '', name)
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    name = name.strip()
    
    author = None
    title = None
    doc_type = 'article'
    
    if '_' in name:
        # Try rsplit first (author usually last)
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
    title = title.replace('_', ' ')
    if author:
        author = re.sub(r'[（(].*?[）)]', '', author).strip()
    
    return title, author, doc_type

def extract_hf_lines(doc):
    lines = []
    for i in range(min(4, len(doc))):
        page = doc[i]
        h = page.rect.height
        w = page.rect.width
        top_rect = fitz.Rect(0, 0, w, h * 0.18)
        bot_rect = fitz.Rect(0, h * 0.82, w, h)
        for l in (page.get_textbox(top_rect) + '\n' + page.get_textbox(bot_rect)).splitlines():
            l = l.strip()
            if l and 3 < len(l) < 35:
                lines.append(l)
    return lines

def parse_gb_t_citation(cf):
    """Parse GB/T 7714 citation format line."""
    result = {}
    cf_norm = unicodedata.normalize('NFKC', cf)
    
    if '[J]' in cf_norm:
        parts = cf_norm.split('[J]')
        result['type'] = 'article'
    elif '[M]' in cf_norm:
        parts = cf_norm.split('[M]')
        result['type'] = 'book'
    else:
        return None
    
    prefix = parts[0].strip()
    suffix = parts[1].strip()
    
    dot_idx = prefix.find('.')
    if dot_idx > 0:
        result['author'] = prefix[:dot_idx].strip()
        result['title'] = prefix[dot_idx+1:].strip()
    else:
        return None
    
    suffix = suffix.lstrip('.').rstrip('.').strip()
    colon_idx = suffix.rfind(':')
    if colon_idx > 0:
        page_part = suffix[colon_idx+1:].strip()
        body = suffix[:colon_idx].strip()
        if '-' in page_part:
            p1, p2 = page_part.split('-', 1)
            result['start_page'] = p1.strip()
            result['end_page'] = p2.strip()
        else:
            result['start_page'] = page_part.strip()
    else:
        body = suffix
    
    comma_parts = [p.strip() for p in body.split(',') if p.strip()]
    if len(comma_parts) >= 2:
        result['journal'] = comma_parts[0]
        result['year'] = comma_parts[1]
    if len(comma_parts) >= 3:
        m = re.match(r'(\d+)\s*\((\d+)\)', comma_parts[2])
        if m:
            result['volume'] = m.group(1)
            result['issue'] = m.group(2)
    
    return result

def is_valid_journal_name(line, title=''):
    bad = ['摘要', '关键词', '作者简介', '中图分类号', '文献标识码', '文章编号', 
           '收稿日期', '基金项目', '博士论坛', '工作研究', '学术探讨', '文艺与文化',
           '研究方向', '研究者', '研究生学位论文', '通讯作者', '论文题目', '毕业设计',
           '独创性声明', '申请', '硕士学位论文', '本论文', '历史文化', '社会科学版']
    for b in bad:
        if b in line:
            return False
    if not re.search(r'(学报|杂志|期刊|大学|学院|研究)', line):
        return False
    if re.search(r'(《|》|出版社|出版)', line):
        return False
    if re.match(r'^[\d\s\.\-NoVol.,（）()\[\]]+$', line):
        return False
    if line == title or (title and len(line) > 5 and line in title):
        return False
    return True

def clean_journal_name(line):
    line = re.sub(r'^\d{4}\s*年第?\d+期\s*[（(].*?[）)]', '', line).strip()
    line = re.sub(r'^No\.\d+,?\s*\d{4}\s*', '', line).strip()
    line = re.sub(r'^\d+\s*[–—\-]\s*\d+\s*', '', line).strip()
    line = re.sub(r'^[\d\s]+', '', line).strip()
    line = re.sub(r'\d{4}年第?\d+期\s*$', '', line).strip()
    return line

def extract_year_from_doi(doi):
    m = re.search(r'\.(\d{4})\.', doi)
    if m:
        y = int(m.group(1))
        if 1980 < y < 2030:
            return str(y)
    return None

def looks_like_date_range(start, end):
    """Heuristic to reject YYYY-MM or YYYY-DD style matches."""
    if not start or not end:
        return False
    try:
        s, e = int(start), int(end)
        if s > 1000 and e < 100:
            return True
        if s > e and s > 1000:
            return True
        if len(start) == 4 and len(end) == 4 and (e - s > 500 or s > e):
            return True
    except ValueError:
        pass
    return False

def extract_pdf_meta(pdf_path, basename):
    title, author, doc_type = parse_filename(basename)
    entry = {
        'file': basename,
        'type': 'pdf',
        'title': title,
        'author': author,
        'doc_type': doc_type,
    }
    
    try:
        doc = fitz.open(pdf_path)
        full_text = ''
        for i in range(min(4, len(doc))):
            full_text += doc[i].get_text()
        full_text = unicodedata.normalize('NFKC', full_text)
        
        # Detect thesis conservatively
        if re.search(r'独创性声明|毕业(论文|设计)|学位论文\s*$', full_text[:1500]):
            entry['doc_type'] = 'thesis'
        if entry.get('doc_type') == 'thesis' and not re.search(r'(学位论文|独创性声明)', full_text[:1500]):
            entry['doc_type'] = doc_type
        
        if doc_type == 'book' or os.path.splitext(basename)[1].lower() == '.epub':
            if entry.get('doc_type') != 'thesis':
                entry['doc_type'] = 'book'
        
        # 1. Citation format line (highest priority)
        cite_match = re.search(r'引文格式[：:]\s*(.+?)$', full_text, re.MULTILINE)
        if cite_match:
            parsed = parse_gb_t_citation(cite_match.group(1).strip())
            if parsed:
                entry.update(parsed)
                entry['citation_format_raw'] = cite_match.group(1).strip()
        
        # 2. Journal name from headers/footers if still missing and is article
        if not entry.get('journal') and entry.get('doc_type') == 'article':
            hf_lines = extract_hf_lines(doc)
            candidates = []
            for line in hf_lines:
                line = unicodedata.normalize('NFKC', line)
                if not is_valid_journal_name(line, title=title):
                    continue
                line = clean_journal_name(line)
                if line and len(line) > 2:
                    candidates.append(line)
            if candidates:
                c = Counter(candidates)
                best, count = c.most_common(1)[0]
                if count >= 2:
                    entry['journal'] = best
        
        # 3. DOI
        doi_match = re.search(r'DOI[：:]\s*(10\.\S+)', full_text, re.IGNORECASE)
        if doi_match:
            entry['doi'] = doi_match.group(1)
        
        # 4. Year / Volume / Issue / Pages from text if missing
        # Try year from DOI first
        if not entry.get('year') and entry.get('doi'):
            y = extract_year_from_doi(entry['doi'])
            if y:
                entry['year'] = y
        
        # Then from first 1500 chars of text to avoid references contamination
        text_head = full_text[:1500]
        if not entry.get('year'):
            m = re.search(r'(\d{4})年', text_head)
            if m:
                y = int(m.group(1))
                if 1980 < y < 2030:
                    entry['year'] = str(y)
        
        if not entry.get('issue'):
            m = re.search(r'(\d{4})年第?(\d+)期', text_head)
            if m:
                entry['year'] = m.group(1)
                entry['issue'] = m.group(2)
        
        if not entry.get('volume'):
            m = re.search(r'第(\d+)卷', text_head)
            if m:
                entry['volume'] = m.group(1)
        
        # Pages
        if not entry.get('start_page'):
            m = re.search(r'[:：]\s*(\d+)[–—\-](\d+)', text_head)
            if m:
                s1, s2 = m.group(1), m.group(2)
                if not looks_like_date_range(s1, s2):
                    entry['start_page'] = s1
                    entry['end_page'] = s2
            else:
                # Article number format across full text
                m = re.search(r'文章编号[：:]\s*\d{4}-\d{4}[（(]\s*(\d{4})\s*[）)]\s*(\d+)[–—\-](\d+)', full_text)
                if m:
                    entry['year'] = m.group(1)
                    g2, g3 = m.group(2), m.group(3)
                    if len(g2) <= 2:
                        entry['issue'] = g2
                        entry['start_page'] = g3
                    else:
                        entry['start_page'] = g2
                        entry['end_page'] = g3
        
    except Exception as e:
        entry['error'] = str(e)
    
    return entry

# Process all files
output = []
for pdf_path in sorted(glob.glob(os.path.join(ref_dir, '*.pdf'))):
    basename = os.path.basename(pdf_path)
    output.append(extract_pdf_meta(pdf_path, basename))

for caj_path in sorted(glob.glob(os.path.join(ref_dir, '*.caj'))):
    basename = os.path.basename(caj_path)
    title, author, doc_type = parse_filename(basename)
    output.append({
        'file': basename,
        'type': 'caj',
        'title': title,
        'author': author,
        'doc_type': doc_type,
        'note': 'Metadata derived from filename only; CAJ format not readable'
    })

for epub_path in sorted(glob.glob(os.path.join(ref_dir, '*.epub'))):
    basename = os.path.basename(epub_path)
    title, author, doc_type = parse_filename(basename)
    output.append({
        'file': basename,
        'type': 'epub',
        'title': title,
        'author': author,
        'doc_type': doc_type,
        'note': 'Metadata derived from filename only'
    })

json_path = os.path.join(ref_dir, '_extracted_metadata_v7.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved metadata for {len(output)} files to {json_path}")

# --- Generate Chicago Bibliography ---
def format_chicago(entry):
    author = entry.get('author', '') or 'Unknown Author'
    title = entry.get('title', '') or 'Untitled'
    journal = entry.get('journal', '')
    year = entry.get('year', '')
    volume = entry.get('volume', '')
    issue = entry.get('issue', '')
    start = entry.get('start_page', '')
    end = entry.get('end_page', '')
    doi = entry.get('doi', '')
    doc_type = entry.get('doc_type', 'article')
    
    if doc_type == 'book':
        line = f"{author}. {title}."
        if year:
            line += f" {year}."
        else:
            line += " [n.d.]."
        return line
    elif doc_type == 'thesis':
        line = f'{author}. "{title}."'
        if journal:
            line += f' {journal}'
        if year:
            line += f', {year}.'
        else:
            line += '.'
        return line
    else:
        line = f'{author}. "{title}."'
        if journal:
            line += f' {journal}'
            if volume:
                line += f' {volume}'
            if issue:
                line += f', no. {issue}'
            if year:
                line += f' ({year})'
            if start:
                line += f': {start}'
                if end:
                    line += f'–{end}'
            line += '.'
        else:
            if year:
                line += f' ({year}).'
            else:
                line += '.'
        if doi:
            line += f' {doi}.'
        return line

output.sort(key=lambda x: x.get('author', '').strip())

bib_lines = []
bib_lines.append('Bibliography')
bib_lines.append('=' * 50)
bib_lines.append('')

books = [e for e in output if e.get('doc_type') == 'book']
if books:
    bib_lines.append('Books')
    bib_lines.append('-' * 20)
    for entry in books:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

theses = [e for e in output if e.get('doc_type') == 'thesis']
if theses:
    bib_lines.append('Theses and Dissertations')
    bib_lines.append('-' * 20)
    for entry in theses:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

articles = [e for e in output if e.get('doc_type') not in ('book', 'thesis')]
if articles:
    bib_lines.append('Journal Articles')
    bib_lines.append('-' * 20)
    for entry in articles:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

bib_lines.append('')
bib_lines.append('Note: Some entries may lack volume/issue/page information because the original files are CAJ or scanned PDFs without extractable metadata. Please verify and supplement details where necessary.')

bib_path = os.path.join(ref_dir, 'Bibliography_Chicago.txt')
with open(bib_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(bib_lines))

print(f"Saved Chicago Bibliography to {bib_path}")
