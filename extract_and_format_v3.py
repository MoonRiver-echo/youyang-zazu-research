import fitz
import os
import glob
import re
import json
from collections import Counter

ref_dir = r'C:\Users\lx\Desktop\前期准备\references'
output = []

def parse_filename(basename):
    """Extract title and author from filename with improved rules."""
    name, ext = os.path.splitext(basename)
    # Remove z-library / download source suffixes
    name = re.sub(r'\s*\((?:z-library\.sk|1lib\.sk|z-lib\.sk)[^)]*\)', '', name)
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)  # remove trailing (1)
    name = name.strip()
    
    author = None
    title = None
    doc_type = 'article'  # default assumption
    
    # Detect books by extension or keywords in filename
    lower_name = name.lower()
    if '著' in name or '编' in name or '译' in name or ext == '.epub':
        # Could be a book, but many articles also have '著' in citation inside filename? No, usually not.
        pass
    
    # Pattern: Title_作者.pdf (most common for journal articles)
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
    """Extract text from top and bottom margins of each page to find headers/footers."""
    lines = []
    for i in range(min(3, len(doc))):
        page = doc[i]
        h = page.rect.height
        w = page.rect.width
        # Top 15% and bottom 15% of page
        top_rect = fitz.Rect(0, 0, w, h * 0.18)
        bot_rect = fitz.Rect(0, h * 0.82, w, h)
        top_text = page.get_textbox(top_rect)
        bot_text = page.get_textbox(bot_rect)
        for l in (top_text + '\n' + bot_text).splitlines():
            l = l.strip()
            if l and len(l) < 50:
                lines.append(l)
    return lines

def parse_citation_format(cf):
    """Parse Chinese GB/T 7714 citation format line."""
    result = {}
    # Full pattern: 作者．《标题》[J]．期刊名，年份，卷（期）：页码-页码．
    # Using full-width punctuation
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
    
    # Simpler: Author. Title[J]. Journal, Year.
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
    
    return None

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
        
        # Get full text from first 3 pages
        full_text = ''
        for i in range(min(3, len(doc))):
            full_text += doc[i].get_text()
        
        # 1. Citation format line (most reliable)
        cite_match = re.search(r'引文格式[：:]\s*(.+?)(?:\n|$)', full_text)
        if cite_match:
            parsed = parse_citation_format(cite_match.group(1).strip())
            if parsed:
                entry.update(parsed)
                entry['citation_format_raw'] = cite_match.group(1).strip()
        
        # 2. Headers/footers for journal name
        if not entry.get('journal'):
            hf_lines = extract_header_footer_lines(doc)
            candidates = []
            for line in hf_lines:
                if any(s in line for s in ['学报', '杂志', '期刊', '大学', '学院', '研究', '论坛', '集刊', '文艺', '文化']):
                    if len(line) < 40 and not re.match(r'^\d+$', line):
                        # Clean obvious prefixes
                        line = re.sub(r'^\d{4}\s*年第?\d+期\s*[（(].*?[）)]', '', line).strip()
                        line = re.sub(r'^No\.\d+,?\s*\d{4}\s*', '', line).strip()
                        if line:
                            candidates.append(line)
            if candidates:
                c = Counter(candidates)
                entry['journal'] = c.most_common(1)[0][0]
        
        # 3. Year, Volume, Issue from text
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
        
        # 4. Pages from article number line
        art_match = re.search(r'文章编号[：:]\s*\S+?[（(]\s*\d{4}\s*[）)]\s*(\d+)[–—\-](\d+)', full_text)
        if art_match and not entry.get('start_page'):
            # In many CN journals, format is ISSN(YYYY)MM-PPPP-CC where MM=issue, PPPP=start page, CC=page count
            # But some use direct page ranges. We treat it as issue-start page for now unless citation_format gave it.
            if not entry.get('citation_format_raw'):
                entry['issue'] = art_match.group(1)
                entry['start_page'] = art_match.group(2)
        
        # Try explicit page range like : 32-36 or 32—36
        if not entry.get('end_page'):
            m = re.search(r'[:：]\s*(\d+)[–—\-](\d+)', full_text)
            if m:
                entry['start_page'] = m.group(1)
                entry['end_page'] = m.group(2)
        
        # 5. DOI
        doi_match = re.search(r'DOI[：:]\s*(10\.\S+)', full_text, re.IGNORECASE)
        if doi_match:
            entry['doi'] = doi_match.group(1)
        
        # 6. Detect if it's actually a book from filename or content
        if '出版社' in full_text and not entry.get('journal'):
            # Could be a book, but hard to tell without more info
            pass
        
    except Exception as e:
        entry['error'] = str(e)
    
    return entry

# Process all files
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

# Save
json_path = os.path.join(ref_dir, '_extracted_metadata_v3.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved metadata for {len(output)} files to {json_path}")

# --- Generate Chicago Bibliography ---
def format_chicago(entry):
    """Format a single entry in Chicago Notes-Bibliography style for Chinese sources."""
    author = entry.get('author', '')
    title = entry.get('title', '')
    journal = entry.get('journal', '')
    year = entry.get('year', '')
    volume = entry.get('volume', '')
    issue = entry.get('issue', '')
    start = entry.get('start_page', '')
    end = entry.get('end_page', '')
    doi = entry.get('doi', '')
    doc_type = entry.get('doc_type', 'article')
    
    # Clean full-width numbers to half-width for consistency
    def to_halfwidth(s):
        if not s:
            return s
        s = s.replace('０','0').replace('１','1').replace('２','2').replace('３','3').replace('４','4')
        s = s.replace('５','5').replace('６','6').replace('７','7').replace('８','8').replace('９','9')
        return s
    
    year = to_halfwidth(year)
    volume = to_halfwidth(volume)
    issue = to_halfwidth(issue)
    start = to_halfwidth(start)
    end = to_halfwidth(end)
    
    if not author:
        author = 'Unknown Author'
    if not title:
        title = 'Untitled'
    
    parts = []
    
    if doc_type == 'book':
        # Author. Title. Place: Publisher, Year.
        # We rarely have publisher/place for these files.
        parts.append(f"{author}. {title}.")
        if year:
            parts.append(f"{year}.")
        else:
            parts.append("[n.d.].")
        return " ".join(parts)
    else:
        # Journal article: Author. "Title." Journal Volume, no. Issue (Year): Pages. DOI.
        # For Chinese articles in Chicago style, often keep Chinese title, sometimes with translation in brackets.
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

bib_lines = []
bib_lines.append('Bibliography')
bib_lines.append('=' * 40)
bib_lines.append('')

# Separate books and articles
books = [e for e in output if e.get('doc_type') == 'book']
articles = [e for e in output if e.get('doc_type') != 'book']

if books:
    bib_lines.append('Books')
    bib_lines.append('-' * 20)
    for entry in books:
        bib_lines.append(format_chicago(entry))
    bib_lines.append('')

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
