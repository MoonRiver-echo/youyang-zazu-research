import fitz
import os
import glob
import re
import json
from collections import Counter

ref_dir = r'C:\Users\lx\Desktop\前期准备\references'
output = []

def parse_filename(basename):
    """Extract title and author from filename."""
    name, ext = os.path.splitext(basename)
    # Remove z-library suffix
    name = re.sub(r'\s*\(z-library\.sk.*?\)\s*', '', name)
    name = re.sub(r'\s*\(1lib\.sk.*?\)\s*', '', name)
    name = re.sub(r'\s*\(z-lib\.sk.*?\)\s*', '', name)
    
    author = None
    title = None
    
    # Pattern: Title_作者.pdf or Title_作者(1).pdf
    if '_' in name:
        parts = name.rsplit('_', 1)
        title = parts[0].strip()
        author = parts[1].strip()
        # Remove trailing numbers like (1)
        author = re.sub(r'\s*\(\d+\)\s*$', '', author)
    else:
        # Pattern: Book Title (Author) or Book Title (Author著)
        m = re.search(r'[（(]([^)]+?著?)[）)]', name)
        if m:
            author = m.group(1).strip()
            title = name[:m.start()].strip()
        else:
            title = name.strip()
    
    # Clean up title: remove brackets like [中华现代学术名著...]
    title = re.sub(r'^\[.*?\]', '', title).strip()
    
    return title, author

def extract_journal_by_frequency(lines):
    candidates = []
    for line in lines:
        line = line.strip()
        if not line or len(line) > 40:
            continue
        # Heuristic: journal names contain these and appear in headers (repeated)
        if any(s in line for s in ['学报', '杂志', '期刊', '大学', '学院', '研究', '论坛', '集刊', '文艺']):
            # Exclude lines that are clearly not journal names
            if re.search(r'(学报|杂志|期刊|大学|学院|研究|论坛|集刊|文艺)', line):
                candidates.append(line)
    if not candidates:
        return None
    c = Counter(candidates)
    most_common = c.most_common()
    for jname, count in most_common:
        if count >= 2:
            return jname
    return most_common[0][0]

def extract_from_pdf(pdf_path, basename):
    title, author = parse_filename(basename)
    entry = {
        'file': basename,
        'type': 'pdf',
        'title': title,
        'author': author,
    }
    
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for i in range(min(4, len(doc))):
            text += doc[i].get_text()
        
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        full_text = text
        
        # --- Try to find Citation Format (引文格式) ---
        cite_match = re.search(r'引文格式[：:]\s*(.+?)(?:\n|$)', full_text)
        if cite_match:
            entry['citation_format'] = cite_match.group(1).strip()
        
        # --- Try to extract from article number line ---
        # Example: 文章编号：1674-5078（2017）01-0070-04
        # or: 文章编号: 1009-1017(2015)06-0116-06
        art_match = re.search(r'文章编号[：:]\s*(\d{4}-\d{4})[（(]\s*(\d{4})\s*[）)]\s*(\d+)[–—\-](\d+)', full_text)
        if art_match:
            entry['issn'] = art_match.group(1)
            entry['year'] = art_match.group(2)
            # The last part is tricky: could be issue-startpage or startpage-endpage
            # In format XXXX-XXXX(YYYY)MM-PPPP-LL, MM is issue, PPPP is start page, LL is page count
            # Let's keep it as issue and start page for now
            entry['issue'] = art_match.group(3)
            entry['start_page'] = art_match.group(4)
        else:
            # Try simpler year extraction
            year_match = re.search(r'(\d{4})年', full_text)
            if year_match:
                y = int(year_match.group(1))
                if 1980 < y < 2030:
                    entry['year'] = str(y)
            
            issue_match = re.search(r'(\d{4})年第?(\d+)期', full_text)
            if issue_match:
                entry['year'] = issue_match.group(1)
                entry['issue'] = issue_match.group(2)
        
        # --- Journal name via frequency ---
        journal = extract_journal_by_frequency(lines)
        if journal:
            # Clean journal name from header clutter
            journal = re.sub(r'^\d{4}\s*年第?\d+期\s*[（(].*?[）)]\s*', '', journal)
            journal = re.sub(r'^No\.\d+,?\s*\d{4}\s*', '', journal)
            journal = re.sub(r'^[\d\s\.]+$', '', journal)
            journal = journal.strip()
            if journal and len(journal) > 2:
                entry['journal'] = journal
        
        # --- Try to refine title/author from text ---
        # Find abstract marker and backtrack
        abs_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'摘\s*要|【摘\s*要】|［摘\s*要］|关键词|提\s*要', line):
                abs_idx = i
                break
        
        if abs_idx > 0:
            # Look for title among lines before abstract
            candidates = []
            start = max(0, abs_idx - 6)
            for i in range(start, abs_idx):
                line = lines[i]
                if len(line) < 6:
                    continue
                # Title characteristics
                if '《' in line or '——' in line or '…' in line or any(k in line for k in ['研究', '探析', '初探', '论', '考', '分析', '书写', '叙事']):
                    if not any(bad in line for bad in ['学报', '杂志', '期刊', '中图分类号', '文献标识码', '文章编号', '收稿日期', '作者简介']):
                        candidates.append(line)
            if candidates:
                # Usually the longest candidate closest to abstract
                best = max(candidates, key=len)
                # But sometimes title is split across lines. Try joining with previous if both short
                entry['title'] = best
                
                # Find author: usually right before or after title, short line
                title_idx = lines.index(best)
                # Check lines around title
                for offset in [-1, 1, -2]:
                    idx = title_idx + offset
                    if 0 <= idx < len(lines) and idx != abs_idx:
                        cand = lines[idx]
                        if len(cand) < 25 and '《' not in cand and not any(b in cand for b in ['学报','杂志','摘要','关键词']):
                            # Clean author
                            cand = re.sub(r'[（(].*?[）)]', '', cand).strip()
                            if cand and len(cand) > 1:
                                entry['author'] = cand
                                break
        
        # --- Page range from text patterns ---
        # Look for explicit page ranges like 32-36 near journal info
        # Or in headers: 第25卷总第179期
        vol_match = re.search(r'第(\d+)卷(?:总第\d+期)?', full_text)
        if vol_match:
            entry['volume'] = vol_match.group(1)
        
        # DOI
        doi_match = re.search(r'DOI[：:]\s*(10\.\S+)', full_text, re.IGNORECASE)
        if doi_match:
            entry['doi'] = doi_match.group(1)
        
        # If we have citation_format, try to parse it for more accurate info
        if entry.get('citation_format'):
            cf = entry['citation_format']
            # Parse GB/T format: Author. Title[J]. Journal, Year, Vol(Issue): Pages.
            # Example: 郭怡箫．《酉阳杂俎·天咫》佛道文化研究［Ｊ］．徐州工程学院学报（社会科学版），２０２４，３９（３）：３２－３６．
            m = re.search(r'(.+?)[．\.]\s*《?(.+?)》?\s*.*?［ＪＪ］.*?[．\.]\s*(.+?)[，,]\s*(\d{4})[，,]\s*(\d+)\s*[（(]\s*(\d+)\s*[）)]\s*[:：]\s*(\d+)[–—\-](\d+)', cf)
            if m:
                entry['author'] = m.group(1).strip()
                entry['title'] = '《' + m.group(2).strip() + '》' if not m.group(2).strip().startswith('《') else m.group(2).strip()
                entry['journal'] = m.group(3).strip()
                entry['year'] = m.group(4)
                entry['volume'] = m.group(5)
                entry['issue'] = m.group(6)
                entry['start_page'] = m.group(7)
                entry['end_page'] = m.group(8)
            else:
                # Simpler parse
                m = re.search(r'(.+?)[．\.]\s*(.+?)\s*［.*?］\s*[．\.]\s*(.+?)[，,]\s*(\d{4})', cf)
                if m:
                    entry['author'] = m.group(1).strip()
                    entry['title'] = m.group(2).strip()
                    entry['journal'] = m.group(3).strip()
                    entry['year'] = m.group(4)
        
        # Clean author: remove spaces inside Chinese names, but keep multiple authors separated
        if entry.get('author'):
            a = entry['author']
            a = a.replace('□', '').replace('　', ' ').strip()
            a = re.sub(r'\s+', ' ', a)
            entry['author'] = a
        
        # Clean title
        if entry.get('title'):
            t = entry['title']
            # Remove common prefixes mistakenly captured
            t = re.sub(r'^(摘\s*要[：:]\s*|【摘\s*要】\s*)', '', t)
            entry['title'] = t.strip()
        
    except Exception as e:
        entry['error'] = str(e)
    
    return entry

# --- Process all files ---
# PDFs
for pdf_path in sorted(glob.glob(os.path.join(ref_dir, '*.pdf'))):
    basename = os.path.basename(pdf_path)
    output.append(extract_from_pdf(pdf_path, basename))

# CAJs (text extraction not supported, use filename only)
for caj_path in sorted(glob.glob(os.path.join(ref_dir, '*.caj'))):
    basename = os.path.basename(caj_path)
    title, author = parse_filename(basename)
    output.append({
        'file': basename,
        'type': 'caj',
        'title': title,
        'author': author,
        'note': 'CAJ format; metadata derived from filename only'
    })

# EPUBs (filename only for now)
for epub_path in sorted(glob.glob(os.path.join(ref_dir, '*.epub'))):
    basename = os.path.basename(epub_path)
    title, author = parse_filename(basename)
    output.append({
        'file': basename,
        'type': 'epub',
        'title': title,
        'author': author,
        'note': 'EPUB; metadata derived from filename only'
    })

# Save raw metadata
json_path = os.path.join(ref_dir, '_extracted_metadata_v2.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved metadata for {len(output)} files to {json_path}")
