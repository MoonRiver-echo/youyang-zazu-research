#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《酉阳杂俎》文本分类分析工具

完全基于文本内容进行分类，不依赖任何外部标注数据。
分类逻辑由篇章映射和特征词规则驱动。

分类体系：
- 叙事结构14类
- 主题分类14大类 + 二级子类（如：动物-兽类-马，动物-昆虫-蜘蛛）
"""

import re
import os
import csv
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

CN_NUM = {'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
          '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18,'十九':19,'二十':20}

def cn_to_num(s):
    if s in CN_NUM: return CN_NUM[s]
    m = re.match(r'二十([一二三四五六七八九]?)', s)
    if m: return 20 + CN_NUM.get(m.group(1),0) if m.group(1) else 20
    return 0

# ═══════════════════════════════════════════════════════════════════
# 分类体系定义
# ═════════════════════════════════════════════════════════════════════

NARRATIVE_CATEGORIES = [
    '动植物谱录','异闻志怪','人物轶事','知识考辨','神仙方术',
    '佛道异闻','器艺技法','异境异域','征兆占验','饮食医药',
    '礼俗制度','器物名物','冥界报应','天文地理',
]

NARRATIVE_DEFS = {
    '动植物谱录':'描述动植物、矿物等自然物的分类谱录',
    '异闻志怪':'含鬼神妖怪、异变怪异、因果报应的叙事故事',
    '人物轶事':'记载帝王将相、名人的轶事趣闻',
    '知识考辨':'杂录典籍引述、文字考证、实用知识',
    '神仙方术':'描述方术、道法、幻术等术数技艺',
    '佛道异闻':'引述佛道经典、宗教义理、修行体系的异闻',
    '器艺技法':'记载手工技艺、奇术表演、纹身等',
    '异境异域':'描述外国异邦风土人情',
    '征兆占验':'涉及梦境、占卜、预言、祥瑞灾异',
    '饮食医药':'涉及食物、烹饪、饮馔、药理医术',
    '礼俗制度':'记载礼仪、官制、婚俗、丧制等制度',
    '器物名物':'涉及珍奇器物、宝物名称考辨',
    '冥界报应':'涉及冥界、阴司、因果报应',
    '天文地理':'涉及天象、地理、自然奇观',
}

THEME_CATEGORIES = [
    '人物政事','动物','神怪妖魅','植物','器物技艺','建筑寺塔',
    '异域物产','饮食医药','异人方术','梦兆占验','丧葬冥界',
    '佛道信仰','天文地理','礼俗制度',
]

NARRATIVE_CHAPTER_MAP = {
    '忠志':'人物轶事','礼异':'礼俗制度','天咫':'异闻志怪',
    '玉格':'佛道异闻','壶史':'神仙方术','贝编':'佛道异闻',
    '境异':'异境异域','喜兆':'征兆占验','祸兆':'征兆占验',
    '物革':'异闻志怪','诡习':'神仙方术','怪术':'神仙方术',
    '艺绝':'器艺技法','器奇':'异闻志怪','乐':'人物轶事',
    '酒食':'饮食医药','医':'饮食医药','黥':'器艺技法',
    '雷':'异闻志怪','梦':'征兆占验','事感':'人物轶事',
    '盗侠':'人物轶事','物异':'异闻志怪','广知':'知识考辨',
    '语资':'人物轶事','冥迹':'异闻志怪',
    '诺皋记上':'异闻志怪','诺皋记下':'异闻志怪',
    '广动植之一':'动植物谱录','广动植之二':'动植物谱录',
    '广动植之三':'动植物谱录','广动植之四':'动植物谱录',
    '肉攫部':'动植物谱录','序':'知识考辨',
}

NARRATIVE_KEYWORDS = {
    '动植物谱录':{'名曰':2,'状如':3,'其色':2,'其肉':3,'其毛':3,'味如':2,'产自':2,'其叶':2,'其花':2,'其果':2,'其根':2,'毛篇':8,'羽篇':8,'鳞篇':8,'虫篇':8,'木篇':8,'草篇':8,'肉攫':8},
    '异闻志怪':{'鬼':3,'妖':3,'魅':4,'怪':2,'化为':4,'作祟':5,'灵异':5,'忽见':3,'忽有':3,'失所在':5,'妖怪':5},
    '人物轶事':{'高祖':4,'太宗':4,'高宗':4,'则天':4,'中宗':3,'睿宗':3,'玄宗':4,'肃宗':3,'代宗':3,'皇帝':3,'诏':2,'赐':2,'敕':2,'即位':3,'公主':3},
    '知识考辨':{'一曰':3,'或言':4,'旧说':4,'相传':2,'考':3,'注':2,'异说':4,'名曰':1,'俗':1},
    '神仙方术':{'方术':5,'仙术':5,'幻术':4,'法术':5,'咒':3,'符':3,'隐形':4,'尸解':3,'辟谷':4,'修道':3},
    '佛道异闻':{'佛':3,'菩萨':5,'罗汉':5,'梵':3,'释':3,'三界':4,'佛事':4,'须弥':5,'袈裟':5,'舍利':4},
    '器艺技法':{'艺':2,'技':2,'纹身':5,'刺青':5,'黥':4},
    '异境异域':{'波斯':4,'天竺':4,'西域':4,'突厥':4,'大食':4,'龟兹':4,'昆仑':3,'交趾':4},
    '征兆占验':{'梦':3,'兆':3,'占':2,'卜':2,'谶':4,'瑞':2,'庆云':4},
    '饮食医药':{'酒':2,'药':2,'羹':3,'馔':4,'饼':2,'医':2,'饮':1,'食':1},
    '礼俗制度':{'婚礼':5,'纳采':5,'丧制':4,'婚':3,'丧':2,'祭':2,'律':2},
    '器物名物':{'异物':4,'奇物':4,'器物':4,'名物':4,'石漆':5,'石墨':5,'碑龟':5},
    '冥界报应':{'冥':3,'报应':5,'地狱':4,'阴司':5,'阎罗':5,'尸解':3,'伏尸':5,'三尸':4,'酆都':5,'冥司':5,'鬼使':4,'鬼官':4,'判冥':5,'冢':2},
    '天文地理':{'星':2,'月蚀':5,'日蚀':5,'北斗':4,'雹':3,'地震':4,'月中有桂':5,'泉':1},
}

# ═════════════════════════════════════════════════════════════════════
# 主题分类特征表：keyword → (broad_category, level1, level2, specific)
# level1 是大类下的子类（如：兽类、鸟类、鱼类、昆虫、木、草、花、果等）
# ═════════════════════════════════════════════════════════════════════

THEME_ENTRIES = [
    # ── 人物政事 ──
    # 帝王
    ('高祖','人物政事','帝王','高祖','高祖'),
    ('太宗','人物政事','帝王','太宗','太宗'),
    ('高宗','人物政事','帝王','高宗','高宗'),
    ('则天','人物政事','帝王','则天','则天'),
    ('中宗','人物政事','帝王','中宗','中宗'),
    ('睿宗','人物政事','帝王','睿宗','睿宗'),
    ('玄宗','人物政事','帝王','玄宗','玄宗'),
    ('肃宗','人物政事','帝王','肃宗','肃宗'),
    ('代宗','人物政事','帝王','代宗','代宗'),
    ('皇帝','人物政事','帝王','皇帝','皇帝'),
    ('公主','人物政事','帝王','公主','公主'),
    # 僧
    ('僧一行','人物政事','僧','僧一行','僧一行'),
    ('僧不空','人物政事','僧','僧不空','僧不空'),
    ('僧','人物政事','僧','僧','僧'),
    # 道士
    ('道士','人物政事','道士','道士','道士'),
    # 人物
    ('成式','人物政事','人物','成式','成式'),
    ('骆宾王','人物政事','人物','骆宾王','骆宾王'),
    ('安禄山','人物政事','人物','安禄山','安禄山'),
    ('武攸绪','人物政事','人物','武攸绪','武攸绪'),
    ('韦行规','人物政事','人物','韦行规','韦行规'),
    ('李廓','人物政事','人物','李廓','李廓'),
    ('李彦佐','人物政事','人物','李彦佐','李彦佐'),

    # ── 动物 ──
    # 兽类
    ('马','动物','兽类','马','马'),
    ('虎','动物','兽类','虎','虎'),
    ('鹿','动物','兽类','鹿','鹿'),
    ('象','动物','兽类','象','象'),
    ('猪','动物','兽类','猪','猪'),
    ('狼','动物','兽类','狼','狼'),
    ('狐','动物','兽类','狐','狐'),
    ('猿','动物','兽类','猿','猿'),
    ('犬','动物','兽类','犬','犬'),
    ('驼','动物','兽类','驼','驼'),
    ('猧','动物','兽类','猧','猧'),
    # 鸟类
    ('鹤','动物','鸟类','鹤','鹤'),
    ('鹰','动物','鸟类','鹰','鹰'),
    ('雕','动物','鸟类','雕','雕'),
    ('凤','动物','鸟类','凤','凤'),
    ('雀','动物','鸟类','雀','雀'),
    ('雁','动物','鸟类','雁','雁'),
    ('燕','动物','鸟类','燕','燕'),
    ('鹅','动物','鸟类','鹅','鹅'),
    ('鹳','动物','鸟类','鹳','鹳'),
    ('鹘','动物','鸟类','鹘','鹘'),
    ('鸽','动物','鸟类','鸽','鸽'),
    ('鸢','动物','鸟类','鸢','鸢'),
    ('白鹊','动物','鸟类','白鹊','白鹊'),
    # 鱼类
    ('鱼','动物','鱼类','鱼','鱼'),
    ('鲤','动物','鱼类','鲤','鲤'),
    ('鲛鱼','动物','鱼类','鲛','鲛鱼'),
    # 昆虫
    ('虫','动物','昆虫','虫','虫'),
    ('蜂','动物','昆虫','蜂','蜂'),
    ('蝶','动物','昆虫','蝶','蝶'),
    ('蝉','动物','昆虫','蝉','蝉'),
    ('蚁','动物','昆虫','蚁','蚁'),
    ('蜗','动物','昆虫','蜗','蜗'),
    ('蝗','动物','昆虫','蝗','蝗'),
    ('蝎','动物','昆虫','蝎','蝎'),
    ('蜘蛛','动物','昆虫','蜘蛛','蜘蛛'),
    # 两栖爬行
    ('龟','动物','爬行','龟','龟'),
    ('蛇','动物','爬行','蛇','蛇'),
    ('蜥蜴','动物','爬行','蜥蜴','蜥蜴'),
    ('虾蟆','动物','两栖','虾蟆','虾蟆'),
    ('蟾蜍','动物','两栖','蟾蜍','蟾蜍'),
    # 兔
    ('兔','动物','兽类','兔','兔'),
    # 神物
    ('龙','动物','神物','龙','龙'),
    ('麒麟','动物','神物','麒麟','麒麟'),

    # ── 神怪妖魅 ──
    ('鬼','神怪妖魅','鬼','鬼','鬼'),
    ('鬼书','神怪妖魅','鬼','鬼书','鬼书'),
    ('鬼官','神怪妖魅','鬼','鬼官','鬼官'),
    ('鬼车鸟','神怪妖魅','鬼','鬼车鸟','鬼车鸟'),
    ('鬼皂荚','神怪妖魅','鬼','鬼皂荚','鬼皂荚'),
    ('鬼矢','神怪妖魅','鬼','鬼矢','鬼矢'),
    ('鬼魅','神怪妖魅','鬼','鬼魅','鬼魅'),
    ('精','神怪妖魅','精','精','精'),
    ('魅','神怪妖魅','魅','魅','魅'),
    ('妖','神怪妖魅','妖','妖','妖'),
    ('仙','神怪妖魅','仙','仙','仙'),
    ('魔','神怪妖魅','魔','魔','魔'),
    ('魂','神怪妖魅','魂','魂','魂'),
    ('魄','神怪妖魅','魄','魄','魄'),
    ('作祟','神怪妖魅','怪','作祟','作祟'),
    ('灵异','神怪妖魅','怪','灵异','灵异'),

    # ── 植物 ──
    # 木
    ('竹','植物','木','竹','竹'),
    ('松','植物','木','松','松'),
    ('柏','植物','木','柏','柏'),
    ('槐','植物','木','槐','槐'),
    ('桑','植物','木','桑','桑'),
    ('柳','植物','木','柳','柳'),
    ('桂','植物','木','桂','桂'),
    ('楷','植物','木','楷','楷'),
    ('柰','植物','木','柰','柰'),
    ('檀','植物','木','檀','檀'),
    ('椒','植物','木','椒','椒'),
    # 草
    ('芝','植物','草','芝','芝'),
    ('苔','植物','草','苔','苔'),
    # 花
    ('牡丹','植物','花','牡丹','牡丹'),
    # 果
    ('桃','植物','果','桃','桃'),
    ('梨','植物','果','梨','梨'),
    ('杏','植物','果','杏','杏'),
    ('枣','植物','果','枣','枣'),
    # 特殊
    ('菩提树','植物','木','菩提','菩提树'),
    ('仙人枣','植物','果','仙人枣','仙人枣'),

    # ── 器物技艺 ──
    # 武器
    ('剑','器物技艺','武器','剑','剑'),
    ('鞭','器物技艺','武器','鞭','鞭'),
    ('弓','器物技艺','武器','弓','弓'),
    ('箭','器物技艺','武器','箭','箭'),
    ('刀','器物技艺','武器','刀','刀'),
    ('矛','器物技艺','武器','矛','矛'),
    # 乐器
    ('琴','器物技艺','乐器','琴','琴'),
    ('琵琶','器物技艺','乐器','琵琶','琵琶'),
    ('鼓','器物技艺','乐器','鼓','鼓'),
    ('钟','器物技艺','乐器','钟','钟'),
    # 用具
    ('镜','器物技艺','用具','镜','镜'),
    ('盘','器物技艺','用具','盘','盘'),
    ('瓶','器物技艺','用具','瓶','瓶'),
    ('屏风','器物技艺','用具','屏风','屏风'),

    # ── 建筑寺塔 ──
    ('寺','建筑寺塔','寺观','寺','寺'),
    ('观','建筑寺塔','寺观','观','观'),
    ('塔','建筑寺塔','寺观','塔','塔'),
    ('殿','建筑寺塔','宫殿','殿','殿'),
    ('宫','建筑寺塔','宫殿','宫','宫'),
    ('苑','建筑寺塔','宫殿','苑','苑'),
    ('城','建筑寺塔','城楼','城','城'),
    ('楼','建筑寺塔','城楼','楼','楼'),

    # ── 异域物产 ──
    ('波斯','异域物产','异国','波斯','波斯'),
    ('昆仑','异域物产','异国','昆仑','昆仑'),
    ('天竺','异域物产','异国','天竺','天竺'),
    ('突厥','异域物产','异国','突厥','突厥'),
    ('大食','异域物产','异国','大食','大食'),
    ('龟兹','异域物产','异国','龟兹','龟兹'),
    ('西域','异域物产','异国','西域','西域'),
    ('交趾','异域物产','异国','交趾','交趾'),
    ('骨利干国','异域物产','异国','骨利干国','骨利干国'),

    # ── 饮食医药 ──
    ('酒','饮食医药','酒','酒','酒'),
    ('药','饮食医药','药','药','药'),
    ('汤','饮食医药','食','汤','汤'),
    ('羹','饮食医药','食','羹','羹'),
    ('饼','饮食医药','食','饼','饼'),
    ('馔','饮食医药','食','馔','馔'),
    ('臛','饮食医药','食','臛','臛'),
    ('茶','饮食医药','食','茶','茶'),
    ('蜜','饮食医药','食','蜜','蜜'),

    # ── 异人方术 ──
    ('方术','异人方术','术','方术','方术'),
    ('幻术','异人方术','术','幻术','幻术'),
    ('隐形','异人方术','术','隐形','隐形'),
    ('辟谷','异人方术','术','辟谷','辟谷'),
    ('修道','异人方术','术','修道','修道'),
    ('尸解','异人方术','术','尸解','尸解'),

    # ── 梦兆占验 ──
    ('梦','梦兆占验','梦','梦','梦'),
    ('兆','梦兆占验','兆','兆','兆'),
    ('瑞','梦兆占验','瑞','瑞','瑞'),
    ('占','梦兆占验','占卜','占','占'),
    ('卜','梦兆占验','占卜','卜','卜'),
    ('谶','梦兆占验','占卜','谶','谶'),
    ('庆云','梦兆占验','瑞','庆云','庆云'),

    # ── 丧葬冥界 ──
    ('尸','丧葬冥界','尸','尸','尸'),
    ('三尸','丧葬冥界','尸','三尸','三尸'),
    ('伏尸','丧葬冥界','尸','伏尸','伏尸'),
    ('冥','丧葬冥界','冥','冥','冥'),
    ('酆都','丧葬冥界','冥','酆都','酆都'),
    ('葬','丧葬冥界','葬','葬','葬'),
    ('坟','丧葬冥界','葬','坟','坟'),
    ('墓','丧葬冥界','葬','墓','墓'),
    ('地狱','丧葬冥界','地狱','地狱','地狱'),

    # ── 佛道信仰 ──
    ('佛','佛道信仰','佛','佛','佛'),
    ('菩萨','佛道信仰','佛','菩萨','菩萨'),
    ('罗汉','佛道信仰','佛','罗汉','罗汉'),
    ('梵','佛道信仰','经法','梵','梵'),
    ('释','佛道信仰','经法','释','释'),
    ('三界','佛道信仰','经法','三界','三界'),
    ('须弥','佛道信仰','经法','须弥','须弥'),
    ('舍利','佛道信仰','法器','舍利','舍利'),
    ('袈裟','佛道信仰','法器','袈裟','袈裟'),
    ('浮屠','佛道信仰','法器','浮屠','浮屠'),

    # ── 天文地理 ──
    ('北斗魁','天文地理','天象','北斗魁','北斗魁'),
    ('月蚀','天文地理','天象','月蚀','月蚀'),
    ('日蚀','天文地理','天象','日蚀','日蚀'),
    ('月中有桂','天文地理','天象','月中有桂','月中有桂'),
    ('泉','天文地理','地理','泉','泉'),

    # ── 礼俗制度 ──
    ('婚礼','礼俗制度','婚姻','婚礼','婚礼'),
    ('纳采','礼俗制度','婚姻','纳采','纳采'),
    ('丧制','礼俗制度','丧制','丧制','丧制'),
    ('青卢','礼俗制度','婚姻','青卢','青卢'),
]

# 按关键词长度降序排列（长词优先匹配）
_SORTED_ENTRIES = sorted(THEME_ENTRIES, key=lambda x: len(x[0]), reverse=True)
_THEME_LOOKUP = {}
for entry in _SORTED_ENTRIES:
    kw = entry[0]
    if kw not in _THEME_LOOKUP:
        _THEME_LOOKUP[kw] = entry  # (kw, broad, level1, level2, specific)


# ═════════════════════════════════════════════════════════════════════
# 段落数据结构
# ═════════════════════════════════════════════════════════════════════

@dataclass
class Paragraph:
    paragraph_id: str
    volume_index: int
    volume_title: str
    chapter: str
    source: str
    content: str
    narrative_category: str = ""
    themes: list = field(default_factory=list)


# ═════════════════════════════════════════════════════════════════════
# 分析器核心
# ═════════════════════════════════════════════════════════════════════

class YouyangZazuAnalyzer:

    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.paragraphs = []

    def read_file(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _clean_chapter(self, raw):
        name = re.sub(r'[（(].+?[）)]', '', raw).strip()
        if '广动植' in name:
            m = re.search(r'广动植之([一二三四])', name)
            if m: return f'广动植之{m.group(1)}'
            m2 = re.search(r'广动植(之一|之二|之三|之四)', name)
            if m2: return f'广动植{m2.group(1)}'
            return '广动植之一'
        if '诺皋记上' in name: return '诺皋记上'
        if '诺皋记下' in name: return '诺皋记下'
        if '肉攫' in name: return '肉攫部'
        return name.strip()

    def split_paragraphs(self, content):
        lines = content.split('\n')
        volume_re = re.compile(r'^卷([一二两三四五六七八九十]+)·(.+)')
        preface_re = re.compile(r'^序$')
        header_re = re.compile(r'^钦定四库全书')
        subsec_re = re.compile(r'^[○●]')

        current_volume = "序"
        current_chapter = "序"
        current_volume_idx = 0
        current_block = []
        para_counter = defaultdict(int)
        paragraphs = []

        def flush():
            nonlocal current_block
            if not current_block: return
            chap = self._clean_chapter(current_chapter)
            para_counter[chap] += 1
            text = '\n'.join(current_block).strip()
            current_block = []
            if len(text) < 3: return
            vi = current_volume_idx
            vt = f"{current_volume}·{chap}"
            pid = f"V{vi:02d}-P{para_counter[chap]:03d}"
            src = f"{vt}-{para_counter[chap]}"
            paragraphs.append(Paragraph(
                paragraph_id=pid, volume_index=vi, volume_title=vt,
                chapter=chap, source=src, content=text))

        for line in lines:
            s = line.strip()
            m = volume_re.match(s)
            p = preface_re.match(s)
            if m or p:
                flush()
                if m:
                    current_volume = f"卷{m.group(1)}"
                    current_volume_idx = cn_to_num(m.group(1))
                    current_chapter = m.group(2).strip()
                else:
                    current_volume = "序"; current_volume_idx = 0; current_chapter = "序"
                continue
            if header_re.match(s):
                parts = s.split('|')
                if len(parts) >= 4:
                    actual = parts[-1].strip()
                    if actual and len(actual) > 5:
                        current_block.append(actual)
                continue
            if subsec_re.match(s): continue
            if s in ['（并序）','(并序)']: continue
            if s == '': flush()
            else: current_block.append(s)
        flush()
        self.paragraphs = paragraphs
        print(f"共识别 {len(self.paragraphs)} 个段落")
        return paragraphs

    def classify_narrative(self, para):
        chap = para.chapter
        content = para.content

        if chap in NARRATIVE_CHAPTER_MAP:
            default = NARRATIVE_CHAPTER_MAP[chap]
            scores = self._score_narrative(content)
            for cat in ('冥界报应','器物名物','天文地理'):
                if scores.get(cat,0) >= 8: return cat
            if chap in ('壶史','怪术','梦','广知','玉格','贝编'):
                best = max(scores, key=scores.get) if scores else default
                if scores.get(best,0) >= 12 and scores.get(best,0) > scores.get(default,0)*1.5:
                    return best
            return default

        scores = self._score_narrative(content)
        if scores: return max(scores, key=scores.get)
        return '知识考辨'

    def _score_narrative(self, text):
        scores = defaultdict(float)
        for cat, kws in NARRATIVE_KEYWORDS.items():
            for kw, w in kws.items():
                cnt = text.count(kw)
                if cnt > 0: scores[cat] += cnt * w
        return dict(scores)

    def classify_themes(self, para):
        content = para.content
        results = []
        seen = set()

        for entry in _SORTED_ENTRIES:
            kw, broad, l1, l2, spec = entry
            if kw in content:
                key = (broad, l1, l2)
                if key not in seen:
                    seen.add(key)
                    results.append((broad, l1, l2, spec))

        if not results:
            chap = para.chapter
            if '广动植之一' in chap or '广动植之二' in chap or '肉攫' in chap:
                results.append(('动物','兽类','马','马'))
            elif '广动植之三' in chap or '广动植之四' in chap:
                results.append(('植物','木','竹','竹'))
            else:
                results.append(('人物政事','人物','人物','人物'))
        return results

    def analyze_all(self):
        print(f"开始分析: {self.input_file}")
        content = self.read_file()
        self.split_paragraphs(content)
        for p in self.paragraphs:
            p.narrative_category = self.classify_narrative(p)
            p.themes = self.classify_themes(p)

        nc = Counter(p.narrative_category for p in self.paragraphs)
        print(f"\n叙事分类统计:")
        for c in NARRATIVE_CATEGORIES:
            cnt = nc.get(c,0)
            if cnt>0: print(f"  {c}: {cnt}段")

        tc = Counter()
        for p in self.paragraphs:
            for t in p.themes: tc[t[0]] += 1
        print(f"\n主题分类统计:")
        for c in THEME_CATEGORIES:
            cnt = tc.get(c,0)
            if cnt>0: print(f"  {c}: {cnt}段")

    # ── 导出 ──────────────────────────────────────────────────────

    def generate_01(self):
        lines = ["# 《酉阳杂俎》卷目分段\n\n"]
        lines.append("| 段落ID | 卷·篇 | 内容概要 |\n|--------|--------|----------|\n")
        for p in self.paragraphs:
            s = p.content[:60].replace('\n',' ').replace('|','｜')
            lines.append(f"| {p.paragraph_id} | {p.volume_title} | {s}… |\n")
        return ''.join(lines)

    def generate_02(self):
        total = len(self.paragraphs)
        nc = Counter(p.narrative_category for p in self.paragraphs)
        np_ = defaultdict(list)
        for p in self.paragraphs: np_[p.narrative_category].append(p)

        lines = ["# 《酉阳杂俎》叙事结构分类表\n\n"]
        lines.append("## 分类标准说明\n\n基于段落叙事特征，将全文段落分为14类叙事结构：\n\n")
        lines.append("| 分类名称 | 定义 |\n|----------|------|\n")
        for c in NARRATIVE_CATEGORIES: lines.append(f"| {c} | {NARRATIVE_DEFS[c]} |\n")
        lines.append(f"\n---\n\n## 叙事结构分类统计\n\n**全文段落总数：{total}段**\n\n")
        lines.append("| 分类 | 段落数 | 百分比(%) |\n|------|--------|-----------|\n")
        for c in NARRATIVE_CATEGORIES: lines.append(f"| {c} | {nc.get(c,0)} | {nc.get(c,0)/total*100:.2f}% |\n")

        lines.append(f"\n---\n\n## 逐卷叙事结构分布\n\n")
        vols = list(dict.fromkeys(p.volume_title for p in self.paragraphs))
        lines.append("| 卷·篇 | "+" | ".join(NARRATIVE_CATEGORIES)+" | 合计 |\n")
        lines.append("|--------"+"|------"*14+"|------|\n")
        chaps = defaultdict(list)
        for p in self.paragraphs: chaps[p.volume_title].append(p)
        for vt in vols:
            ps=chaps[vt]; cc=Counter(p.narrative_category for p in ps)
            cells=[str(cc.get(c,0)) for c in NARRATIVE_CATEGORIES]
            lines.append(f"| {vt} | "+" | ".join(cells)+f" | {len(ps)} |\n")
        tc=Counter(p.narrative_category for p in self.paragraphs)
        tcells=[f"**{tc.get(c,0)}**" for c in NARRATIVE_CATEGORIES]
        lines.append(f"| **合计** | "+" | ".join(tcells)+f" | **{total}** |\n")

        lines.append("\n---\n\n## 叙事结构分类详表\n")
        for c in NARRATIVE_CATEGORIES:
            cnt=nc.get(c,0)
            if cnt==0: continue
            lines.append(f"\n### {c}（{cnt}段，{cnt/total*100:.2f}%）\n")
            lines.append("| 段落ID | 卷·篇 | 内容概要 |\n|--------|--------|----------|\n")
            for p in np_.get(c,[])[:50]:
                s=p.content[:50].replace('\n',' ').replace('|','｜')
                lines.append(f"| {p.paragraph_id} | {p.volume_title} | {s}… |\n")
            if len(np_.get(c,[]))>50: lines.append(f"| … | … | （共{cnt}段） |\n")
        return ''.join(lines)

    def generate_03(self):
        total=len(self.paragraphs)
        tc=Counter(); tl1=defaultdict(set); tl2=defaultdict(set)
        for p in self.paragraphs:
            for t in p.themes: tc[t[0]]+=1; tl1[t[0]].add(t[1]); tl2[(t[0],t[1])].add(t[2])
        lines=["# 《酉阳杂俎》描写对象分类表\n\n"]
        lines.append("## 分类标准说明\n\n按段落所描述的主要对象分类，共设14大类。一段可归属多类。\n")
        lines.append("每类包含一级分类（大类）和二级分类（子类）。\n\n")
        lines.append("| 一级分类 | 二级子类 | 段落数 |\n|----------|----------|--------|\n")
        for c in THEME_CATEGORIES:
            cnt=tc.get(c,0)
            l1s='、'.join(sorted(tl1.get(c,set()))[:10])
            lines.append(f"| {c} | {l1s}… | {cnt} |\n")
        lines.append(f"\n---\n\n## 主题分类统计\n\n**全文段落总数：{total}段（一段可归属多类）**\n\n")
        lines.append("| 分类 | 段落数 | 占全文比(%) |\n|------|--------|-------------|\n")
        for c in THEME_CATEGORIES: lines.append(f"| {c} | {tc.get(c,0)} | {tc.get(c,0)/total*100:.2f}% |\n")
        return ''.join(lines)

    def generate_04(self):
        mt=[p for p in self.paragraphs if len(p.themes)>1]
        lines=["# 《酉阳杂俎》交叉分类表\n\n## 说明\n\n"]
        lines.append("本表记录同时属于多个主题类别的段落。\n\n---\n\n")
        lines.append(f"## 多主题段落（共{len(mt)}段）\n\n")
        lines.append("| 段落ID | 卷·篇 | 叙事分类 | 主题类别 | 一级 | 二级 | 内容概要 |\n")
        lines.append("|--------|--------|----------|----------|------|------|----------|\n")
        for p in mt[:60]:
            ts='、'.join(t[0] for t in p.themes[:5])
            l1s='、'.join(t[1] for t in p.themes[:5])
            l2s='、'.join(t[3] for t in p.themes[:5])
            s=p.content[:25].replace('\n',' ').replace('|','｜')
            lines.append(f"| {p.paragraph_id} | {p.volume_title} | {p.narrative_category} | {ts} | {l1s} | {l2s} | {s}… |\n")
        if len(mt)>60: lines.append(f"| … | … | … | … | … | … | （共{len(mt)}段） |\n")
        return ''.join(lines)

    def generate_05(self):
        sc=Counter(); sp=defaultdict(list)
        for p in self.paragraphs:
            for t in p.themes: k=(t[1],t[2]); sc[k]+=1; sp[k].append(p)
        lines=["# 《酉阳杂俎》描写对象频次表\n\n## 说明\n\n"]
        lines.append("统计全文各描写对象出现的次数，按频次从高到低排列。\n\n---\n\n")
        lines.append("| 排名 | 一级子类 | 二级主题 | 出现次数 | 所在段落编号 |\n")
        lines.append("|------|----------|----------|----------|----------------|\n")
        for rank,((l1,l2),cnt) in enumerate(sc.most_common(100),1):
            ids='、'.join(p.paragraph_id for p in sp[(l1,l2)][:5])
            lines.append(f"| {rank} | {l1} | {l2} | {cnt} | {ids} |\n")
        return ''.join(lines)

    def generate_06(self):
        sg=defaultdict(list)
        for p in self.paragraphs:
            for t in p.themes: sg[(t[0],t[1],t[2])].append(p)
        sgs=sorted(sg.items(),key=lambda x:-len(x[1]))
        lines=["# 《酉阳杂俎》同类描写对象汇总\n\n## 说明\n\n"]
        lines.append("将描写同一类对象的段落集中排列，方便比较分析。\n\n---\n\n")
        for (b,l1,l2),ps in sgs[:50]:
            lines.append(f"## {b} - {l1} - {l2}（{len(ps)}次）\n\n")
            lines.append("| 序号 | 卷·篇 | 段落ID | 内容概要 |\n|------|--------|---------|----------|\n")
            for i,p in enumerate(ps[:20],1):
                s=p.content[:50].replace('\n',' ').replace('|','｜')
                lines.append(f"| {i} | {p.volume_title} | {p.paragraph_id} | {s}… |\n")
            if len(ps)>20: lines.append(f"| … | … | … | （共{len(ps)}段） |\n")
            lines.append("\n")
        return ''.join(lines)

    def export_csv(self):
        os.makedirs(self.output_dir, exist_ok=True)
        # 叙事分类明细
        with open(os.path.join(self.output_dir,'叙事分类明细.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['narrative_category','volume_index','volume_title','source','paragraph_id','text'])
            for p in self.paragraphs:
                w.writerow([p.narrative_category,p.volume_index,p.volume_title,p.source,p.paragraph_id,p.content.replace('\n',' ').strip()])
        # 叙事分类统计
        total=len(self.paragraphs); nc=Counter(p.narrative_category for p in self.paragraphs)
        with open(os.path.join(self.output_dir,'叙事分类统计.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['narrative_category','paragraph_count','absolute_percentage'])
            for c in NARRATIVE_CATEGORIES: w.writerow([c,nc.get(c,0),f"{nc.get(c,0)/total*100:.2f}%"])
        # 主题分类明细
        with open(os.path.join(self.output_dir,'主题分类明细.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['broad_category','level1_subject','level2_subject','specific_subject','volume_index','volume_title','source','paragraph_id','primary_subject','annotation_supported','original_subject','text'])
            for p in self.paragraphs:
                txt=p.content.replace('\n',' ').strip()
                pri=p.themes[0][1] if p.themes else ''
                for t in p.themes:
                    w.writerow([t[0],t[1],t[2],t[3],p.volume_index,p.volume_title,p.source,p.paragraph_id,pri,'no',t[1],txt])
        # 主题分类统计
        tc=Counter()
        for p in self.paragraphs:
            seen=set()
            for t in p.themes:
                if t[0] not in seen: tc[t[0]]+=1; seen.add(t[0])
        with open(os.path.join(self.output_dir,'主题分类统计.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['broad_category','paragraph_count','absolute_percentage'])
            for c in THEME_CATEGORIES: w.writerow([c,tc.get(c,0),f"{tc.get(c,0)/total*100:.2f}%"])
        # 主题频次统计
        sc=Counter()
        for p in self.paragraphs:
            for t in p.themes: sc[(t[1],t[2])]+=1
        with open(os.path.join(self.output_dir,'主题频次统计.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['level1_subject','level2_subject','appearance_count'])
            for (l1,l2),cnt in sc.most_common(): w.writerow([l1,l2,cnt])
        # 重复主题分类
        with open(os.path.join(self.output_dir,'重复主题分类.csv'),'w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f)
            w.writerow(['volume_index','volume_title','source','paragraph_id','duplicate_broad_categories','duplicate_specific_subjects','text'])
            for p in self.paragraphs:
                if len(p.themes)>1:
                    bc=' | '.join(t[0] for t in p.themes)
                    ss=' | '.join(t[3] for t in p.themes)
                    w.writerow([p.volume_index,p.volume_title,p.source,p.paragraph_id,bc,ss,p.content.replace('\n',' ').strip()])
        print("CSV导出完成")

    def export_all(self):
        os.makedirs(self.output_dir, exist_ok=True)
        mds=[("01-卷目分段.md",self.generate_01()),("02-叙事结构分类表.md",self.generate_02()),
             ("03-描写对象分类表.md",self.generate_03()),("04-交叉分类表.md",self.generate_04()),
             ("05-描写对象频次表.md",self.generate_05()),("06-同类描写对象汇总.md",self.generate_06()),]
        for fname,content in mds:
            with open(os.path.join(self.output_dir,fname),'w',encoding='utf-8') as f: f.write(content)
            print(f"已生成: {os.path.join(self.output_dir,fname)}")
        self.export_csv()
        print(f"\n导出完成: {self.output_dir}")


def main():
    input_file = r"C:\Users\lx\Desktop\前期准备\prepare\酉阳杂俎-初校.md"
    output_dir = r"C:\Users\lx\Desktop\前期准备\GLM处理"
    analyzer = YouyangZazuAnalyzer(input_file, output_dir)
    analyzer.analyze_all()
    analyzer.export_all()


if __name__ == "__main__":
    main()