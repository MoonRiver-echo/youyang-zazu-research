import fitz
import os
import glob
import re
import json
from collections import Counter

ref_dir = r'C:\Users\lx\Desktop\前期准备\references'
output = []

# --- helpers ---
def extract_citation_format(text):
    m = re.search(r'引文格式[：:]\s*(.+?)(?:\n|$)', text)
    if m:
        return m.group(1).strip()
    return None

def extract_doi(text):
    m = re.search(r'DOI[：:]\s*(10\.\S+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def extract_year_volume_issue_pages(text):
    # GB/T style: year, volume(issue): start-end
    m = re.search(r'(\d{4})\s*[，,]\s*(\d+)\s*\((\d+)\)\s*[:：]\s*(\d+)[–—\-]+(\d+)', text)
    if m:
        return {'year': m.group(1), 'volume': m.group(2), 'issue': m.group(3), 'start_page': m.group(4), 'end_page': m.group(5)}
    # 2024年第3期
    m = re.search(r'(\d{4})年第?(\d+)期', text)
    if m:
        return {'year': m.group(1), 'volume': None, 'issue': m.group(2), 'start_page': None, 'end_page': None}
    return None

def extract_journal_from_header(text):
    lines = text.splitlines()
    candidates = []
    for line in lines[:30]:
        line = line.strip()
        if not line:
            continue
        if any(suf in line for suf in ['学报', '杂志', '期刊', '研究', '论坛', '集刊', '月刊', '年报', '大学', '学院']):
            if 5 < len(line) < 40:
                candidates.append(line)
    for line in lines[-30:]:
        line = line.strip()
        if not line:
            continue
        if any(suf in line for suf in ['学报', '杂志', '期刊', '研究', '论坛', '集刊', '月刊', '年报', '大学', '学院']):
            if 5 < len(line) < 40:
                candidates.append(line)
    if candidates:
        c = Counter(candidates)
        return c.most_common(1)[0][0]
    return None

def extract_title_and_author_from_text(text, basename):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = None
    author = None
    for i, line in enumerate(lines[:20]):
        if '《' in line and '》' in line and len(line) > 5:
            title = line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if len(next_line) < 20 and '摘要' not in next_line and '关键词' not in next_line and '提要' not in next_line:
                    author = next_line.strip()
            break
    if not title:
        for line in lines[:30]:
            if '《' in line and '》' in line:
                title = line
                break
    if not title:
        title = basename
    return title, author

# --- process PDFs ---
pdfs = sorted(glob.glob(os.path.join(ref_dir, '*.pdf')))
for pdf_path in pdfs:
    basename = os.path.basename(pdf_path)
    entry = {'file': basename, 'type': 'pdf'}
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for i in range(min(3, len(doc))):
            text += doc[i].get_text()
        entry['extracted_text_sample'] = text[:1500]

        cite = extract_citation_format(text)
        if cite:
            entry['citation_format'] = cite

        doi = extract_doi(text)
        if doi:
            entry['doi'] = doi

        yvip = extract_year_volume_issue_pages(text)
        if yvip:
            entry.update(yvip)

        journal = extract_journal_from_header(text)
        if journal:
            entry['journal'] = journal

        title, author = extract_title_and_author_from_text(text, basename)
        entry['title'] = title
        entry['author'] = author

    except Exception as e:
        entry['error'] = str(e)
    output.append(entry)

# --- process EPUBs ---
epubs = sorted(glob.glob(os.path.join(ref_dir, '*.epub')))
for epub_path in epubs:
    basename = os.path.basename(epub_path)
    entry = {'file': basename, 'type': 'epub', 'note': 'EPUB metadata not extracted automatically'}
    output.append(entry)

# --- process CAJs ---
cajs = sorted(glob.glob(os.path.join(ref_dir, '*.caj')))
for caj_path in cajs:
    basename = os.path.basename(caj_path)
    entry = {'file': basename, 'type': 'caj'}
    name_part = os.path.splitext(basename)[0]
    entry['title_author_guess'] = name_part
    output.append(entry)

json_path = os.path.join(ref_dir, '_extracted_metadata.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Processed {len(output)} files. Metadata saved to {json_path}")
