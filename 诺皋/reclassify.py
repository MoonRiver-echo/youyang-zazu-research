import re

with open(r'C:\Users\lx\Desktop\前期准备\诺皋\酉阳杂俎诺皋_故事情节.txt', 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('## 【')
entries = []
for part in parts[1:]:
    num_match = re.match(r'(\d+)】', part)
    if not num_match:
        continue
    num = int(num_match.group(1))
    orig_match = re.search(r'\*\*原文：\*\*\s*\n\n(.*?)(?:\n\n\*\*白话概括：\*\*)', part, re.DOTALL)
    summary_match = re.search(r'\*\*白话概括：\*\*\s*\n\n(.*?)(?:\n---|\Z)', part, re.DOTALL)
    if orig_match and summary_match:
        orig = orig_match.group(1).strip()
        summary = summary_match.group(1).strip()
        first_line = orig.split('\n')[0].strip()
        entries.append((num, first_line, orig, summary))

# Write mapping
with open(r'C:\Users\lx\Desktop\前期准备\诺皋\mapping.txt', 'w', encoding='utf-8') as f:
    for num, fl, orig, summary in entries:
        f.write(f"{num}: {fl}\n")

# Define new classification
dream = [1, 9, 52, 76, 77, 78, 79, 80, 81, 82, 85, 91]
transformation = [48, 92, 97, 104, 107, 114, 118]  # 变化类
illness = [49, 73, 74, 72, 75, 93]  # 病类
ghost = [11, 17, 34, 45, 50, 55, 61, 98, 99]  # 鬼类，移除35
spatial = [8, 12, 42, 60, 83, 88, 94, 62]  # 空间变换类：平原杜林、大定士人、失姓字、冉从长、张和、倭国僧、王乙掘井、松滋县南
temporal = [35]  # 时间变换类：李和子
monster = [2, 10, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36, 37, 38, 39, 40, 41, 43, 44, 46, 47, 51, 53, 54, 56, 57, 58, 59, 63, 64, 65, 66, 67, 68, 69, 70, 71]  # 妖遇类，移除spatial中的条目
retribution = [3, 13, 46, 90, 103, 106, 108, 117]  # 幽冥报应类
phenomenon = [4, 5, 6, 7, 33, 35, 47, 69, 84, 95, 96, 100, 101, 102, 105, 109, 110, 111, 112, 113, 116, 119, 120, 121, 122, 123, 124, 125, 126, 127]  # 神物异象类
prophecy = [86, 89, 102, 117]  # 预言宿命类

# Verify all entries accounted for
all_ids = set(range(1, 121))
classified = set(dream + transformation + illness + ghost + spatial + temporal + monster + retribution + phenomenon + prophecy)
print(f"Total classified: {len(classified)}")
print(f"Missing: {sorted(all_ids - classified)}")
print(f"Duplicate: {len(classified) - len(set(classified))}")

# Write new classification MD
with open(r'C:\Users\lx\Desktop\前期准备\诺皋\酉阳杂俎诺皋_分类_新.md', 'w', encoding='utf-8') as f:
    f.write("# 酉阳杂俎·诺皋 分类（含空间变换、时间变换）\n\n")
    
    cats = [
        ("梦类", dream),
        ("变化类", transformation),
        ("病类", illness),
        ("鬼类", ghost),
        ("空间变换类", spatial),
        ("时间变换类", temporal),
        ("妖遇类", monster),
        ("幽冥报应类", retribution),
        ("神物异象类", phenomenon),
        ("预言宿命类", prophecy),
    ]
    
    for cat_name, ids in cats:
        f.write(f"## {cat_name}\n\n")
        for eid in ids:
            entry = next((e for e in entries if e[0] == eid), None)
            if entry:
                num, fl, orig, summary = entry
                f.write(f"### 【{num}】{fl[:30]}...\n\n")
                f.write("**原文：**\n\n")
                f.write(orig + "\n\n")
                f.write("**白话概括：**\n\n")
                f.write(summary + "\n\n")
                f.write("---\n\n")

print("Done writing new classification.")
