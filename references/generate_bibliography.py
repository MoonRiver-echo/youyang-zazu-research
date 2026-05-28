import json
import re
from pypinyin import pinyin, Style

COMPOUND_SURNAMES = [
    '欧阳', '司马', '上官', '皇甫', '诸葛', '尉迟', '慕容', '长孙',
    '申屠', '夏侯', '东方', '南宫', '万俟', '段干', '百里', '呼延',
    '西门', '公羊', '公孙', '令狐', '宇文', '司徒', '司空',
    '端木', '赫连', '独孤', '拓跋', '夹谷', '轩辕'
]

def get_surname_given(name):
    """Split Chinese name into (surname, given_name)."""
    name = name.strip()
    if not name:
        return name, ''
    # Check compound surnames
    for cs in COMPOUND_SURNAMES:
        if name.startswith(cs) and len(name) > len(cs):
            return name[:len(cs)], name[len(cs):]
    # Handle non-Chinese names
    if not re.match(r'^[\u4e00-\u9fff]', name):
        return name, ''
    # Single character = just surname
    if len(name) == 1:
        return name, ''
    # Default: first character is surname
    return name[0], name[1:]

def pinyin_str(text):
    """Get continuous pinyin string for a Chinese text."""
    if not text:
        return ''
    result = pinyin(str(text), style=Style.NORMAL)
    return ''.join([p[0] for p in result]).lower()

def format_authors(author_str):
    """Format author names. For Chinese: keep natural order. Multiple: use '和'."""
    authors = re.split(r'[,，]', author_str)
    authors = [a.strip() for a in authors if a.strip()]
    # Remove bracketed prefixes like [美]
    cleaned = []
    for a in authors:
        a = re.sub(r'^\[.+?\]', '', a).strip()
        if a:
            cleaned.append(a)
    if not cleaned:
        return author_str
    if len(cleaned) == 1:
        return cleaned[0]
    elif len(cleaned) == 2:
        return f"{cleaned[0]} 和 {cleaned[1]}"
    else:
        return '、'.join(cleaned[:-1]) + f"，和 {cleaned[-1]}"

def format_doi(doi):
    """Format DOI as URL."""
    if not doi:
        return ''
    doi = doi.strip().rstrip('.')
    if doi.startswith('10.'):
        return f'https://doi.org/{doi}'
    elif doi.startswith('http'):
        return doi
    return f'https://doi.org/{doi}'

def clean_fullwidth(s):
    if not s:
        return s
    m = {'０':'0','１':'1','２':'2','３':'3','４':'4','５':'5','６':'6','７':'7','８':'8','９':'9'}
    for k,v in m.items():
        s = s.replace(k,v)
    return s

def sort_key_for_entry(entry):
    """Return (surname_pinyin, given_pinyin) for sorting."""
    author = entry.get('author', '').strip()
    first_author = re.split(r'[,，]', author)[0].strip()
    first_author = re.sub(r'^\[.+?\]', '', first_author).strip()
    surname, given = get_surname_given(first_author)
    sp = pinyin_str(surname)
    gp = pinyin_str(given)
    return (sp, gp)

# Load data
with open(r'C:\Users\lx\Desktop\前期准备\references\_extracted_metadata_v7.json', 'r', encoding='utf-8') as f:
    v7 = json.load(f)
with open(r'C:\Users\lx\Desktop\前期准备\references\_extracted_metadata_v6.json', 'r', encoding='utf-8') as f:
    v6 = json.load(f)

v6_lookup = {e['file']: e for e in v6}

# Merge
merged = []
for entry in v7:
    e = dict(entry)
    fn = entry['file']
    if fn in v6_lookup:
        v6e = v6_lookup[fn]
        for key in ['journal', 'start_page', 'end_page', 'volume', 'issue', 'year', 'doi', 'doc_type', 'citation_format_raw']:
            if (key not in e or not e[key]) and key in v6e and v6e[key]:
                e[key] = v6e[key]
    merged.append(e)

# Deduplicate by (author, title)
seen = set()
deduped = []
for e in merged:
    key = (e.get('author','').strip(), e.get('title','').strip())
    if key not in seen:
        seen.add(key)
        deduped.append(e)

# Sort by author surname pinyin, then given name pinyin
deduped.sort(key=sort_key_for_entry)

# Format entries
lines = []
lines.append("Bibliography")
lines.append("=" * 50)
lines.append("")

prev_author_surname = None
EM_DASH = "———"

for entry in deduped:
    author = entry.get('author', '').strip()
    title = entry.get('title', '').strip()
    doc_type = entry.get('doc_type', 'article').strip()
    journal = entry.get('journal', '').strip()
    year = clean_fullwidth(entry.get('year', '')).strip()
    volume = clean_fullwidth(entry.get('volume', '')).strip()
    issue = clean_fullwidth(entry.get('issue', '')).strip()
    start_page = entry.get('start_page', '').strip()
    end_page = entry.get('end_page', '').strip()
    doi = entry.get('doi', '').strip()
    
    # Clean up journal field - remove embedded citation info
    if journal:
        # Remove patterns like "作者：标题" from journal
        if '：' in journal and '《' in journal.split('：')[0]:
            pass  # journal name contains book title marks, keep it
        elif '：' in journal:
            journal = journal.split('：')[-1].strip()
    
    # Determine display author (use em dash for repeated authors)
    first_author = re.split(r'[,，]', author)[0].strip()
    first_author = re.sub(r'^\[.+?\]', '', first_author).strip()
    curr_surname, _ = get_surname_given(first_author)
    curr_surname_py = pinyin_str(curr_surname)
    
    # Check if same as previous author (full name match)
    if prev_author_surname is not None and prev_author_surname == author.strip().split(',')[0].strip().split('，')[0].strip():
        display_author = EM_DASH
    else:
        display_author = format_authors(author)
    
    prev_author_surname = author.strip().split(',')[0].strip().split('，')[0].strip()
    
    # Validate pages
    valid_pages = False
    if start_page and end_page:
        try:
            sp = int(start_page)
            ep = int(end_page)
            if sp > 0 and ep > sp and (ep - sp) < 200:
                valid_pages = True
        except (ValueError, TypeError):
            pass
    
    doi_url = format_doi(doi)
    
    # Format based on doc_type
    if doc_type == 'book':
        # Book: Author. Title. [Place: Publisher, Year].
        entry_text = f"{display_author}. {title}."
        if year:
            entry_text += f" [n.p.: n.p., {year}]."
        else:
            entry_text += " n.d."
        lines.append(entry_text)
        lines.append("")
    
    elif doc_type == 'thesis':
        # Thesis: Author. "Title." Thesis, Year.
        entry_text = f"{display_author}. \"{title}.\""
        if year:
            entry_text += f" [Thesis], {year}."
        else:
            entry_text += " [Thesis]. n.d."
        if doi_url:
            entry_text += f" {doi_url}."
        lines.append(entry_text)
        lines.append("")
    
    else:
        # Article: Author. "Title." Journal Volume, no. Issue (Year): Pages. DOI.
        entry_text = f"{display_author}. \"{title}.\""
        
        # Build citation details
        cite_parts = []
        
        if journal:
            j = journal
            if volume:
                j += f" {volume}"
            if issue:
                j += f", no. {issue}"
            cite_parts.append(j)
        
        # Year
        year_str = f"({year})" if year else ""
        
        # Pages
        page_str = ""
        if valid_pages:
            page_str = f":{start_page}\u2013{end_page}"
        
        # Assemble
        if cite_parts:
            main_cite = cite_parts[0]
            if year_str:
                main_cite += f" {year_str}"
            main_cite += page_str
            entry_text += f" {main_cite}."
        elif year_str:
            entry_text += f" {year_str}."
        else:
            entry_text += " n.d."
        
        # Append DOI
        if doi_url:
            if entry_text.endswith('.'):
                entry_text = entry_text[:-1]  # Remove trailing period
            entry_text += f" {doi_url}."
        
        lines.append(entry_text)
        lines.append("")

# Add notes at the end
lines.append("---")
lines.append("")
lines.append("Note: n.d. = no date; n.p. = no publisher/place.")
lines.append("Some entries lack volume/issue/page information due to incomplete metadata extraction from CAJ files or scanned PDFs.")
lines.append("Duplicate files (e.g., two copies of the same article) have been merged into single entries.")

output = '\n'.join(lines)

with open(r'C:\Users\lx\Desktop\前期准备\references\Bibliography_Chicago.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Generated bibliography with {len(deduped)} unique entries")
print("Done!")