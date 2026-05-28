#!/usr/bin/env python3
"""
酉阳杂俎 三校合并清洗脚本 v5

核心策略：
- 分卷分篇：以二校为主（二校卷名结构更完整）
- 分段：以初校为重（初校分段更细）
- 字词修正：以二校为准
- 补充：二校有而初校完全缺失的段落
- 清洗：删除所有括号注释、一X一、〈〉、{{}}、|分隔、&#x20;
"""

import re
import os
import difflib

BASE_DIR = r"C:\Users\lx\Desktop\前期准备"
CHU_XIAO = os.path.join(BASE_DIR, "prepare", "酉阳杂俎-初校.md")
ER_XIAO = os.path.join(BASE_DIR, "酉阳杂俎-二校.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "清洗数据")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "酉阳杂俎-三校.md")

# ============================================================
# 卷名映射：二校篇名 → 初校卷标记
# ============================================================
VOLUME_MAP = {
    "忠志":       "卷一·忠志",
    "礼异":       "卷一·礼异",
    "天咫":       "卷一·天咫",
    "玉格":       "卷二·玉格",
    "壶史":       "卷二·壶史",
    "贝编":       "卷三·贝编",
    "境异":       "卷四·境异",
    "喜兆":       "卷四·喜兆",
    "祸兆":       "卷四·祸兆",
    "物革":       "卷四·物革",
    "诡习":       "卷五·诡习",
    "怪术":       "卷五·怪术",
    "艺绝":       "卷六·艺绝",
    "器奇":       "卷六·器奇",
    "乐":         "卷六·乐",
    "酒食":       "卷七·酒食",
    "医":         "卷七·医",
    "黥":         "卷八·黥",
    "雷":         "卷八·雷",
    "梦":         "卷八·梦",
    "事感":       "卷九·事感",
    "盗侠":       "卷九·盗侠",
    "物异":       "卷十·物异",
    "广知":       "卷十一·广知",
    "语资":       "卷十二·语资",
    "冥迹":       "卷十三·冥迹",
    "尸穸":       None,  # 二校特有
    "诺皋记上":   "卷十四·诺皋记上",
    "诺皋记下":   "卷十五·诺皋记下",
    "广动植之一（并序）": "卷十六·广动植之一",
    "广动植之一": "卷十六·广动植之一",
    "广动植之二": "卷十七·广动植之二",
    "广动植之三": "卷十八·广动植之三",
    "广动植类之四": "卷十九·广动植类之四",
    "肉攫部":     "卷二十·肉攫部",
    # 续集（二校特有，初校无对应）
    "支诺皋上":   None,
    "支诺皋中":   None,
    "支诺皋下":   None,
    "贬误":       None,
    "寺塔记上":   None,
    "寺塔记下":   None,
    "金刚经鸠异": None,
    "支植上":     None,
    "支植下":     None,
    # 广动植中的子分类（羽篇、毛篇等属于广动植的一部分）
    "总叙":       None,  # 广动植之一开头部分
    "羽篇":       None,  # 广动植之一的子分类
    "毛篇":       None,  # 广动植之二的子分类
    "虫篇":       None,  # 广动植之三的子分类
    "木篇":       None,  # 广动植之四的子分类
    "草篇":       None,  # 广动植之四的子分类
}


def clean_text(text):
    """全面清洗文本"""
    # 1. HTML实体
    text = text.replace('&#x20;', '').replace('&nbsp;', ' ')
    # 2. {{}} 注释
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    # 3. （）中文括号注释
    text = re.sub(r'（[^）]*）', '', text)
    # 4. () 英文括号注释
    text = re.sub(r'\([^)]*\)', '', text)
    # 5. 〈〉尖括号
    text = re.sub(r'〈[^〉]*〉', '', text)
    # 6. 一X一注解 → 保留中间字
    text = re.sub(r'一(.+?)一\s*', r'\1', text)
    # 7. 零宽字符
    text = text.replace('\u200b', '').replace('\ufeff', '')
    # 8. | 分隔的元数据行
    if re.match(r'^[^|]*(\|[^|]*){2,}', text.strip()):
        return ''
    # 9. 引号统一为「」
    text = text.replace('\u201c', '\u300c').replace('\u201d', '\u300d')
    # 10. 清理多余空格
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    return text


def normalize(text):
    """归一化用于比较"""
    text = re.sub(r'\s+', '', text)
    for ch in '，。、；：？！」《》""':
        text = text.replace(ch, '')
    return text


def parse_chuxiao(content):
    """解析初校文件，返回 {卷名: [段落]} 废字典"""
    lines = content.split('\n')
    volumes = {}
    current_vol = "序"
    current_paras = []
    vol_pattern = re.compile(r'^卷([一二三四五六七八九十百零]+)\s*[·\s]\s*(.+)$')
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if '|' in stripped and re.match(r'^[^|]*(\|[^|]*){2,}', stripped):
            continue
        m = vol_pattern.match(stripped)
        if m:
            if current_paras:
                volumes[current_vol] = current_paras
            current_vol = f"卷{m.group(1)}\u00b7{m.group(2)}"
            current_paras = []
            continue
        cleaned = clean_text(stripped)
        if cleaned:
            current_paras.append(cleaned)
    if current_paras:
        volumes[current_vol] = current_paras
    return volumes


def parse_erxiao(content):
    """
    解析二校文件，返回 [(篇名, 卷标记, [段落])] 列表
    处理 &#x20; 前缀和其他格式问题
    """
    lines = content.split('\n')
    sections = []
    current_name = "序"
    current_label = "序"
    current_paras = []
    
    # 标题模式：**　忠志** 或 &#x20;**物异** 等
    heading_pattern = re.compile(r'^&?x?;?\s*\*+\s*[\u3000\s]*(.+?)\s*\*+$')
    
    for line in lines:
        stripped = line.strip()
        # 清理HTML实体前缀
        stripped = stripped.replace('&#x20;', '').replace('&nbsp;', ' ')
        
        if not stripped:
            continue
        
        # 检查标题
        m = heading_pattern.match(stripped)
        if not m:
            # 也检查非标题格式的heading（如 &#x20;**物异** ）
            if stripped.startswith('**') and stripped.endswith('**'):
                inner = stripped.replace('**', '').strip().replace('\u3000', '').replace(' ', '')
                m = type('Match', (), {'group': lambda self, n=0: inner})()
        
        if m:
            if current_paras:
                sections.append((current_name, current_label, current_paras))
            
            heading = m.group(1).strip().replace('\u3000', '').replace(' ', '')
            # 清理括号内容用于映射查找
            clean_heading = re.sub(r'（[^）]*）', '', heading)
            
            current_name = heading
            
            # 查找映射
            if heading in VOLUME_MAP:
                current_label = VOLUME_MAP[heading] or heading
            elif clean_heading in VOLUME_MAP:
                current_label = VOLUME_MAP[clean_heading] or heading
            elif heading == "序":
                current_label = "序"
            else:
                current_label = heading
            
            current_paras = []
            continue
        
        # 正文
        cleaned = clean_text(stripped)
        if cleaned:
            current_paras.append(cleaned)
    
    if current_paras:
        sections.append((current_name, current_label, current_paras))
    
    return sections


def merge_paragraphs(cx_paras, ex_paras, vol_label=""):
    """
    以初校分段为基底，用二校内容补充修正。
    策略：
    1. 保留初校的段落划分（更细）
    2. 逐段对比：高相似度时以二校文本修正字词
    3. 二校有而初校没有的段落补充到末尾
    """
    result = []
    ex_matched = set()
    
    for cx_para in cx_paras:
        cx_norm = normalize(cx_para)
        if len(cx_norm) < 10:
            result.append(cx_para)
            continue
        
        best_idx = -1
        best_score = 0
        
        for ex_i, ex_para in enumerate(ex_paras):
            if ex_i in ex_matched:
                continue
            ex_norm = normalize(ex_para)
            if not ex_norm or len(ex_norm) < 5:
                continue
            
            # 包含关系
            if cx_norm in ex_norm:
                score = 0.95
            elif ex_norm in cx_norm:
                score = 0.85
            else:
                score = difflib.SequenceMatcher(None, cx_norm, ex_norm).ratio()
            
            if score > best_score:
                best_score = score
                best_idx = ex_i
        
        if best_score > 0.55 and best_idx >= 0:
            ex_matched.add(best_idx)
            ex_para = ex_paras[best_idx]
            
            if best_score > 0.85:
                # 高度相似 - 以二校为准修正字词，但保留初校分段
                cx_len = len(cx_norm)
                ex_len = len(normalize(ex_para))
                
                if ex_len > cx_len * 1.3:
                    # 二校合并了多段 → 保留初校分段和文本
                    result.append(cx_para)
                else:
                    # 长度相近 → 用二校文本修正字词
                    result.append(ex_para)
            else:
                # 中等相似 → 保留初校
                result.append(cx_para)
        else:
            # 初校独有
            result.append(cx_para)
    
    # 二校中未匹配的段落
    ex_only = []
    for ex_i, ex_para in enumerate(ex_paras):
        if ex_i not in ex_matched:
            ex_norm = normalize(ex_para)
            if len(ex_norm) > 10:
                is_in_cx = False
                for cx_para in cx_paras:
                    cx_norm = normalize(cx_para)
                    if cx_norm and ex_norm and (ex_norm in cx_norm or cx_norm in ex_norm):
                        is_in_cx = True
                        break
                    if difflib.SequenceMatcher(None, cx_norm, ex_norm).ratio() > 0.5:
                        is_in_cx = True
                        break
                if not is_in_cx:
                    ex_only.append(ex_para)
    
    if ex_only and vol_label:
        print(f"  {vol_label}: 补充二校独有 {len(ex_only)} 段")
    result.extend(ex_only)
    
    return result


def main():
    print("=" * 60)
    print("酉阳杂俎 三校合并清洗脚本 v5")
    print("策略: 分卷分篇→二校, 分段→初校, 字词→二校")
    print("=" * 60)
    
    with open(CHU_XIAO, 'r', encoding='utf-8') as f:
        cx_content = f.read()
    with open(ER_XIAO, 'r', encoding='utf-8') as f:
        ex_content = f.read()
    
    print(f"\n初校: {len(cx_content)} 字符")
    print(f"二校: {len(ex_content)} 字符")
    
    print("\n解析初校...")
    cx_vols = parse_chuxiao(cx_content)
    print(f"  {len(cx_vols)} 卷")
    for name, paras in cx_vols.items():
        print(f"    {name}: {len(paras)} 段")
    
    print("\n解析二校...")
    ex_sections = parse_erxiao(ex_content)
    print(f"  {len(ex_sections)} 篇")
    for name, label, paras in ex_sections:
        print(f"    {name} -> {label}: {len(paras)} 段")
    
    # ============================================================
    # 合并
    # ============================================================
    print("\n合并...")
    result = []
    used_cx_labels = set()
    total_ex_only = 0
    
    # 用二校的分篇结构
    sub_section_labels = {"总叙", "羽篇", "毛篇", "虫篇", "木篇", "草篇"}
    
    for ex_name, ex_label, ex_paras in ex_sections:
        # 处理子分类（如羽篇、毛篇等属于广动植）
        if ex_name in sub_section_labels:
            # 这些是广动植的子分类，合并到上一个主卷
            if result:
                last_label, last_paras = result[-1]
                result[-1] = (last_label, last_paras + ex_paras)
                print(f"  [子分类] {ex_name} 合并到 {last_label}")
            continue
        
        # 查找初校对应卷
        cx_label = None
        if ex_name in VOLUME_MAP:
            cx_label = VOLUME_MAP[ex_name]
        clean_heading = re.sub(r'（[^）]*）', '', ex_name)
        if cx_label is None and clean_heading in VOLUME_MAP:
            cx_label = VOLUME_MAP[clean_heading]
        
        cx_paras = cx_vols.get(cx_label, None) if cx_label else None
        
        if cx_paras is not None:
            used_cx_labels.add(cx_label)
            merged = merge_paragraphs(cx_paras, ex_paras, cx_label)
            result.append((cx_label, merged))
        elif cx_label is None:
            # 二校独有（续集）
            result.append((f"续·{ex_name}", ex_paras))
            total_ex_only += len(ex_paras)
            print(f"  [二校独有] 续·{ex_name}: {len(ex_paras)} 段")
        else:
            # cx_label存在但初校中没有对应卷
            result.append((cx_label, ex_paras))
            print(f"  [仅二校] {cx_label}: {len(ex_paras)} 段")
    
    # 初校中有而二校结构中未包含的卷
    for cx_label, cx_paras in cx_vols.items():
        if cx_label not in used_cx_labels:
            result.append((cx_label, cx_paras))
            print(f"  [初校独有] {cx_label}: {len(cx_paras)} 段")
    
    # 统计
    total_paras = sum(len(p) for _, p in result)
    print(f"\n合并结果: {len(result)} 卷, {total_paras} 段")
    
    # ============================================================
    # 后处理清洗
    # ============================================================
    print("\n后处理清洗...")
    final_result = []
    for label, paras in result:
        cleaned = []
        for p in paras:
            p = clean_text(p)
            if p:
                # 移除单独一个"序"字（二校解析残留）
                if p.strip() == "序" and label != "序":
                    continue
                cleaned.append(p)
        final_result.append((label, cleaned))
    
    # 输出
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    lines = []
    for label, paras in final_result:
        lines.append(f'\n## {label}\n')
        for p in paras:
            lines.append(f'\n{p}\n')
    
    output = '\n'.join(lines)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\n三校已输出到: {OUTPUT_FILE}")
    print(f"文件大小: {len(output)} 字符")
    
    # 各卷统计
    print("\n" + "=" * 60)
    print("各卷段落统计:")
    for label, paras in final_result:
        print(f"  {label}: {len(paras)} 段")


if __name__ == "__main__":
    main()