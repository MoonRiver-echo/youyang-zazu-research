import json
import re
import os

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

# Search for key stories and save results to file
results = []

queries = {
    '吴刚伐桂': ['吴刚','伐桂','月桂'],
    '修月人': ['修月','七宝合成','八万二千户'],
    '胡桃杀人': ['胡桃','柳氏','碎首'],
    '刘录事': ['刘录事','骨珠子','茶瓯'],
    '夜叉娶妻': ['夜叉','娶','妻']
}

for name, kws in queries.items():
    for kw in kws:
        idx = text.find(kw)
        if idx != -1:
            snippet = text[max(0,idx-100):idx+200]
            results.append(f"=== {name} / keyword: {kw} ===\n{snippet}\n\n")
            break

with open(r'C:\Users\lx\Desktop\前期准备\youyang-website\scripts\search_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Search results saved to search_results.txt")
