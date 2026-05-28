import re

with open(r'C:\Users\lx\Desktop\前期准备\诺皋\酉阳杂俎诺皋_故事情节.txt', 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('## 【')
entries = []
for part in parts[1:]:
    m = re.match(r'(\d+)】', part)
    if not m:
        continue
    num = int(m.group(1))
    lines = part.split('\n')
    # Find original text lines between **原文：** and **白话概括：**
    in_orig = False
    orig_lines = []
    for line in lines:
        if '**原文：**' in line:
            in_orig = True
            continue
        if '**白话概括：**' in line:
            break
        if in_orig:
            orig_lines.append(line.strip())
    # Remove empty lines at start
    while orig_lines and orig_lines[0] == '':
        orig_lines.pop(0)
    first_line = orig_lines[0] if orig_lines else ''
    full_orig = '\n'.join(orig_lines)
    entries.append((num, first_line, full_orig))

with open(r'C:\Users\lx\Desktop\前期准备\诺皋\correct_mapping.txt', 'w', encoding='utf-8') as f:
    for num, fl, orig in entries:
        f.write(f"{num}: {fl[:60]}\n")

print(f"Total: {len(entries)}")
