import fitz
import os
import glob
import re
import json
from collections import Counter

ref_dir = r'C:\Users\lx\Desktop\前期准备\references'

def parse_filename(basename):
    """Extract title and author from filename with improved rules."""
    name, ext = os.path.splitext(basename)
    # Remove z-library / download source suffixes
    name = re.sub(r'\s*\((?:z-library\.sk|1lib\.sk|z-lib\.sk)[^)]*\)', '', name)
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)  # remove trailing (1)
    name = name.strip()
    
    author = None
    title = None
    doc_type = 'article'
    
    # Pattern: Title_作者.pdf (most common for journal articles and theses)
    if '_' in name:
        parts = name.rsplit('_', 1)
        title = parts[0].strip()
        author = parts[1].strip()
    else:
        # Pattern: Book Title (Author) or Book Title (Author著)
        m = re.search(r'[（(]([^（()]+?)(?:著|编|译)?[）)]$', name)
        if m:
            author = m.group(1).strip()
            title = name[:m.start()].strip()
            doc_type = 'book'
        else:
            title = name.strip()
    
    # Clean title: remove leading category tags like [中华现代学术名著...]
    title = re.sub(r'^\[.*?\]\s*', '', title).strip()
    
    # Clean author
    if author:
        author = re.sub(r'[（(].*?[）)]', '', author).strip()
    
    return title, author, doc_type

def extract_header_footer_lines(doc):
    """Extract text from top and bottom margins of each page."""
    lines = []
    for i in range(min(4, len(doc))):
        page = doc[i]
        h = page.rect.height
        w = page.rect.width
        top_rect = fitz.Rect(0, 0, w, h * 0.20)
        bot_rect = fitz.Rect(0, h * 0.80, w, h)
        top_text = page.get_textbox(top_rect)
        bot_text = page.get_textbox(bot_rect)
        for l in (top_text + '\n' + bot_text).splitlines():
            l = l.strip()
            if l and len(l) < 45:
                lines.append(l)
    return lines

def parse_citation_format(cf):
    """Parse Chinese GB/T 7714 citation format line into structured data."""
    result = {}
    # Full pattern with full-width punctuation
    m = re.search(
        r'(.+?)[．\.]\s*《?(.+?)》?\s*.*?[ＪJ].*?[．\.]\s*(.+?)[，,]\s*(\d{4})[，,]\s*(\d+)\s*[（(]\s*(\d+)\s*[）)]\s*[:：]\s*(\d+)[–—\-](\d+)',
        cf
    )
    if m:
        result['author'] = m.group(1).strip()
        result['title'] = m.group(2).strip()
        result['journal'] = m.group(3).strip()
        result['year'] = m.group(4)
        result['volume'] = m.group(5)
        result['issue'] = m.group(6)
        result['start_page'] = m.group(7)
        result['end_page'] = m.group(8)
        return result
    
    # Simpler pattern without pages
    m = re.search(
        r'(.+?)[．\.]\s*《?(.+?)》?\s*.*?[ＪJ].*?[．\.]\s*(.+?)[，,]\s*(\d{4})',
        cf
    )
    if m:
        result['author'] = m.group(1).strip()
        result['title'] = m.group(2).strip()
        result['journal'] = m.group(3).strip()
        result['year'] = m.group(4)
        return result
    
    # Book pattern [M]
    m = re.search(
        r'(.+?)[．\.]\s*《?(.+?)》?\s*.*?[ＭM].*?[．\.]\s*(.+?)[，,]\s*(\d{4})',
        cf
    )
    if m:
        result['author'] = m.group(1).strip()
        result['title'] = m.group(2).strip()
        result['publisher'] = m.group(3).strip()
        result['year'] = m.group(4)
        result['type'] = 'book'
        return result
    
    return None

def is_likely_journal_name(line):
    """Heuristic to check if a line is a real journal name vs. a column name or noise."""
    bad_keywords = ['摘要', '关键词', '作者简介', '中图分类号', '文献标识码', '文章编号', 
                    '收稿日期', '基金项目', '博士论坛', '工作研究', '学术探讨', '文艺与文化',
                    '研究方向', '研究者', '研究生学位论文', '通讯作者']
    for bk in bad_keywords:
        if bk in line:
            return False
    # Must contain at least one journal-ish keyword
    if not re.search(r'(学报|杂志|期刊|大学|学院|研究|论坛|集刊|文艺|文化|社会科学|科学)', line):
        return False
    # Exclude lines that are mostly numbers/punctuation
    if re.match(r'^[\d\s\.\-NoVol.,（）()\[\]]+$', line):
        return False
    return True

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
        
        # Detect thesis
        if re.search(r'学位论文|硕士学位论文|博士论文|独创性声明|毕业(论文|设计)', full_text):
            entry['doc_type'] = 'thesis'
        
        # Detect book more reliably
        if doc_type == 'book' or (re.search(r'出版社', full_text) and not re.search(r'学报|杂志|期刊', full_text)):
            # Could still be a book chapter, but treat as book for now
            if not entry.get('doc_type') == 'thesis':
                entry['doc_type'] = 'book'
        
        # 1. Citation format line (highest priority)
        cite_match = re.search(r'引文格式[：:]\s*(.+?)(?:\n|$)', full_text)
        if cite_match:
            parsed = parse_citation_format(cite_match.group(1).strip())
            if parsed:
                entry.update(parsed)
                entry['citation_format_raw'] = cite_match.group(1).strip()
        
        # 2. Journal name from headers/footers if not already found
        if not entry.get('journal') and entry.get('doc_type') == 'article':
            hf_lines = extract_header_footer_lines(doc)
            candidates = []
            for line in hf_lines:
                if not is_likely_journal_name(line):
                    continue
                # Clean prefixes
                line = re.sub(r'^\d{4}\s*年第?\d+期\s*[（(].*?[）)]', '', line).strip()
                line = re.sub(r'^No\.\d+,?\s*\d{4}\s*', '', line).strip()
                line = re.sub(r'^Journal of .*?\d{4}$', '', line).strip() # remove English journal+year combos
                if line and len(line) > 2:
                    candidates.append(line)
            if candidates:
                c = Counter(candidates)
                best, count = c.most_common(1)[0]
                if count >= 2 or len(candidates) <= 3:
                    entry['journal'] = best
        
        # 3. Year / Volume / Issue from text if missing
        if not entry.get('year'):
            m = re.search(r'(\d{4})年', full_text)
            if m:
                y = int(m.group(1))
                if 1980 < y < 2030:
                    entry['year'] = str(y)
        
        if not entry.get('issue'):
            m = re.search(r'(\d{4})年第?(\d+)期', full_text)
            if m:
                entry['year'] = m.group(1)
                entry['issue'] = m.group(2)
        
        if not entry.get('volume'):
            m = re.search(r'第(\d+)卷', full_text)
            if m:
                entry['volume'] = m.group(1)
        
        # 4. Pages
        if not entry.get('start_page'):
            # Try direct page range after colon or in article number
            m = re.search(r'[:：]\s*(\d+)[–—\-](\d+)', full_text)
            if m:
                entry['start_page'] = m.group(1)
                entry['end_page'] = m.group(2)
            else:
                # Article number format: ISSN(YYYY)MM-PPPP-LL or ISSN(YYYY)MM-PPPP-EEEE
                m = re.search(r'文章编号[：:]\s*\d{4}-\d{4}[（(]\s*(\d{4})\s*[）)]\s*(\d+)[–—\-](\d+)', full_text)
                if m:
                    entry['year'] = m.group(1)
                    # For article number format, group 2 is issue, group 3 is start page or end page? 
                    # Usually format is ISSN(YYYY)MM-PPPP-LL where LL is page count.
                    # We will treat group 2 as issue only if it is small (<=12 typically)
                    g2 = m.group(2)
                    g3 = m.group(3)
                    if len(g2) <= 2:
                        entry['issue'] = g2
                        entry['start_page'] = g3
                    else:
                        # Maybe it's start-end
                        entry['start_page'] = g2
                        entry['end_page'] = g3
        
        # 5. DOI
        doi_match = re.search(r'DOI[：:]\s*(10\.\S+)', full_text, re.IGNORECASE)
        if doi_match:
            entry['doi'] = doi_match.group(1)
        
        # Clean full-width numbers
        for key in ['year', 'volume', 'issue', 'start_page', 'end_page']:
            if entry.get(key):
                entry[key] = entry[key].replace('０','0').replace('１','1').replace('２','2').replace('３','3').replace('４','4').replace('５','5').replace('６','6').replace('７','7').replace('８','8').replace('９','9')
        
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

# Save raw metadata
json_path = os.path.join(ref_dir, '_extracted_metadata_v4.json')
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
        # Author. Title. Place: Publisher, Year.
        # We rarely have publisher/place for these files.
        line = f"{author}. {title}."
        if year:
            line += f" {year}."
        else:
            line += " [n.d.]."
        return line
    elif doc_type == 'thesis':
        # Author. "Title." Master's/PhD thesis, University, Year.
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

# Sort by author surname (simple sort by full author string)
output.sort(key=lambda x: x.get('author', '').strip())

bib_lines = []
bib_lines.append('Bibliography')
bib_lines.append('=' * 50)
bib_lines.append('')

# Books
books = [e for e in output if e.get('doc_type') == 'book']
if books:
    bib_lines.append('Books')
    bib_lines.append('-' * 20)
    for entry in books:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

# Theses
theses = [e for e in output if e.get('doc_type') == 'thesis']
if theses:
    bib_lines.append('Theses and Dissertations')
    bib_lines.append('-' * 20)
    for entry in theses:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

# Articles
articles = [e for e in output if e.get('doc_type') not in ('book', 'thesis')]
if articles:
    bib_lines.append('Journal Articles')
    bib_lines.append('-' * 20)
    for entry in articles:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

bib_path = os.path.join(ref_dir, 'Bibliography_Chicago.txt')
with open(bib_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(bib_lines))

print(f"Saved Chicago Bibliography to {bib_path}")
