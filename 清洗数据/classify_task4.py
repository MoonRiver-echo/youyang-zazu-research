#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酉阳杂俎 三校版 分类脚本 (Task 4) - 优化版
1. 优化超自然叙事主题关键词，移除过于宽泛的单字
2. 采用短语匹配+加权评分机制
3. CSV导出 + Markdown转换
"""

import re
import os
import sys
import csv
from collections import defaultdict, OrderedDict

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\lx\Desktop\前期准备\清洗数据"
INPUT_FILE = os.path.join(BASE_DIR, "酉阳杂俎-三校.md")

# ============================================================
# A. 叙事结构分类体系
# ============================================================
VOLUME_CATEGORIES = {
    "序": "史料序跋", "忠志": "帝王纪事", "礼异": "礼俗制度",
    "天咫": "天文地理", "玉格": "佛道异闻", "壶史": "神仙方术",
    "贝编": "佛道异闻", "境异": "异境异域", "喜兆": "征兆占验",
    "祸兆": "征兆占验", "物革": "事物怪变", "诡习": "器艺技法",
    "怪术": "神仙方术", "艺绝": "器艺技法", "器奇": "器物名物",
    "乐": "器艺技法", "酒食": "饮食医药", "医": "饮食医药",
    "黥": "礼俗制度", "雷": "天文地理", "梦": "梦兆占验",
    "事感": "精诚感应", "盗侠": "侠盗刺客", "物异": "器物名物",
    "广知": "广知博物", "语资": "语资谈助", "冥迹": "幽冥冥迹",
    "尸穸": "丧葬礼俗", "诺皋记上": "异闻志怪", "诺皋记下": "异闻志怪",
    "广动植之一": "动植物谱录", "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录", "广动植类之四": "动植物谱录",
    "肉攫部": "器艺技法",
    "支诺皋上": "异闻志怪", "支诺皋中": "异闻志怪", "支诺皋下": "异闻志怪",
    "贬误": "知识考辨", "寺塔记上": "佛寺塔庙", "寺塔记下": "佛寺塔庙",
    "金刚经鸠异": "佛道异闻",
    "支动": "动植物谱录", "支植上": "动植物谱录", "支植下": "动植物谱录",
    "总叙": "动植物谱录", "羽篇": "动植物谱录", "毛篇": "动植物谱录",
    "虫篇": "动植物谱录", "木篇": "动植物谱录", "草篇": "动植物谱录",
}

# ============================================================
# B. 描写对象分类体系（细粒度，已优化）
# ============================================================
SUBJECT_KEYWORDS = OrderedDict([
    ("人物政事", OrderedDict([
        ("帝王", ["帝","上","天子","诏","敕","玄宗","太宗","高宗","肃宗","代宗","中宗","睿宗","则天","明皇","宣宗","穆宗","宪宗","文宗","武宗","德宗","皇帝"]),
        ("将相臣子", ["臣","卿","大夫","刺史","令","尉","将军","尚书","侍郎","学士","宰相","御史","太尉","节度使","国公","郡公"]),
        ("僧尼", ["僧","沙弥","比丘","禅师","上人","法师","梵僧","胡僧","和尚","尼","比丘尼","女冠","女道士"]),
        ("道士方士", ["道","道士","天师","真人","先生","山人","方士","术士","巫","黄冠"]),
        ("隐逸高人", ["隐","逸","处士","高人","隐士","山人","布衣"]),
        ("侠盗刺客", ["侠","盗","刺客","贼","劫","夜叉","飞天夜叉","侠客","大盗"]),
        ("成式自述", ["成式"]),
    ])),
    ("动物", OrderedDict([
        ("龙蛇类", ["龙","蛟","螭","虬","蛇","蟒","蚺","蝮","大蛇","毒蛇"]),
        ("鸟类", ["鸟","鹊","鹰","鹤","雁","燕","雀","凤","鸱","鸢","雉","鸦","乌","鹅","鹭","鸽","鹦","雕","鸮","鹗","鹞","鹈","鹳","鸳鸯","白鹭","黄鹂","异鸟"]),
        ("兽类", ["虎","鹿","马","牛","羊","犬","狗","豕","猪","象","狮","豹","熊","猴","猿","狐","兔","鼠","猫","狼","驼","骡","驴","驼鹿","麋","麝","犀","貂","獭","貉","鼬"]),
        ("鱼类", ["鱼","鲤","鲫","鲈","鳖","龟","鳗","鳝","鲙","鲸","鲟","鲂","鲨","鲇","大鱼","异鱼"]),
        ("爬行两栖", ["龟","鳄","蜃","蛙","蟾","蜍","蝾螈","壁虎","巨龟"]),
        ("昆虫", ["虫","蚁","蜂","蝶","蛾","蝉","蜻","萤","蝗","螳","蛛","蝇","蚊","蚤","蚕","蜈蚣","蝎","蟋蟀","蝤蛴","螽斯"]),
    ])),
    ("植物", OrderedDict([
        ("树木", ["松","柏","柳","槐","桑","榆","桐","桂","竹","檀","梅","杉","楠","樟","栎","楸","梓","椿","桦","枞","桧","棣","柽","枫","杞","栌","古木","大树","异木"]),
        ("花草", ["花","莲","菊","兰","牡丹","芍药","芙蓉","梅","桃","杏","梨","兰","蕙","萱","荼蘼","海棠","蔷薇","木槿","紫薇","迎春"]),
        ("果蔬", ["桃","李","杏","柿","枣","梨","橘","柚","橙","瓜","瓠","葫芦","豆","麦","稻","粟","黍","稷","麻","桑椹","葡萄","石榴","胡桃","银杏"]),
        ("药草", ["药","芝","艾","蒿","参","苓","术","连翘","甘草","当归","芎䓖","地黄","黄连","附子","半夏","大黄","细辛","远志","防风","独活","牛膝","天南星"]),
    ])),
    ("鬼怪妖魅", OrderedDict([
        ("鬼", ["鬼","亡魂","游魂","幽魂","鬼官","鬼魅","厉鬼","怨鬼","鬼物","恶鬼","女鬼"]),
        ("仙神", ["仙","仙人","神仙","真人","天帝","灶神","城隍","土地","山神","河伯","风伯","雨师","雷公","玉皇","太上老君"]),
        ("精怪", ["精","妖精","狐精","蛇精","树精","古精","物精","花精","石精"]),
        ("妖魅", ["妖","妖怪","妖魅","魅","魑魅","魍魉","妖魔","妖物","狐妖","蛇妖"]),
        ("魔", ["魔","天魔","夜叉","修罗","阿修罗","罗刹"]),
        ("魂魄", ["魂","魄","三魂七魄","亡魂","游魂","魂魄离散"]),
    ])),
    ("建筑寺塔", OrderedDict([
        ("宫殿城楼", ["宫","宫殿","殿","堂","阁","台","城","楼","门","墙","坊","郭","阙","廊","亭","苑"]),
        ("寺观塔庙", ["寺","寺庙","兰若","伽蓝","观","道观","宫观","院","庵","塔","浮屠","石窟","经幢","精舍"]),
    ])),
    ("器物技艺", OrderedDict([
        ("武器", ["剑","刀","戟","戈","矛","弓","箭","弩","鞭","盾","槊","钺","殳","斤"]),
        ("镜鉴", ["镜","明镜","铜镜","照骨宝","宝镜"]),
        ("乐器", ["鼓","钟","磬","琴","瑟","箫","笛","竽","琵琶","筝","埙","笙","角","钹"]),
        ("用具杂器", ["盘","碗","杯","鼎","壶","瓶","匣","箱","炉","灯","枕","席","帐","帘","镜","梳","尺","称","印"]),
        ("衣饰", ["衣","冠","带","履","衾","裘","袍","裙","帛","锦","绮","罗","纱","绢","绫","绸"]),
    ])),
    ("佛道宗教", OrderedDict([
        ("佛法", ["佛","释","菩萨","罗汉","涅槃","舍利","经","戒","禅","梵","僧","寺","袈裟","钵","斋","忓"]),
        ("道法", ["道","老君","太极","真人","丹","炼","符","咒","箓","诀","飞升","尸解","辟谷","黄白"]),
    ])),
    ("丧葬冥界", OrderedDict([
        ("丧葬", ["葬","墓","棺","坟","椁","冢","殉","陪葬","祭","迁葬","发冢","墓志"]),
        ("冥界", ["冥","阴间","地府","黄泉","幽冥","阳间","还魂","入冥","赴冥","阎罗","判官","阎王","奈何桥"]),
        ("尸变", ["尸","尸解","不朽","不腐","僵尸","骸骨","枯骨","白骨","骷髅"]),
    ])),
    ("饮食医药", OrderedDict([
        ("食物饮品", ["食","煮","饮","饼","羹","粥","脍","鲙","馄饨","面","糕","酒","酿","醪","醑","茶","茗"]),
        ("医术药理", ["药","丹","丸","散","汤","医","治","病","疾","灸","针","砭","脉","诊","方","剂","草药"]),
    ])),
    ("梦兆占卜", OrderedDict([
        ("梦兆", ["梦","入梦","托梦","梦中","凶梦","吉梦","梦兆","梦验"]),
        ("占卜预言", ["占","卜","谶","预言","相","算","推","卜筮","卦","易","星","命"]),
        ("祥瑞灾异", ["瑞","祥","灾","异","天象","蚀","蝗","旱","水","地震","火","祥瑞","嘉瑞"]),
    ])),
    ("天文地理", OrderedDict([
        ("天象", ["日","月","星","辰","风","雨","雷","电","云","雾","霜","雪","虹","彗","蚀","晕"]),
        ("地理山水", ["山","水","泉","井","河","江","海","湖","洞","谷","峰","岭","崖","涧","溪","滩","原","野"]),
    ])),
    ("异域物产", OrderedDict([
        ("异国", ["波斯","西域","天竺","大食","突厥","龟兹","于阗","拂林","昆仑","胡","蛮","安息","康居","罽宾","乌苌","扶南","林邑"]),
    ])),
    ("超自然力量", OrderedDict([
        ("法术仙术", ["术","法","幻","隐形","变化","遁","飞升","仙术","法术","奇术","幻术","遁术","五行","六丁","奇门","太乙","遁甲","巫术","蛊"]),
        ("因果报应", ["报应","因果","善报","恶报","罚","赎","劫","还报","业","果报","感应"]),
        ("鬼神降灵", ["显灵","降神","附身","托梦","降世","感应","灵验","神意","天命","符应"]),
        ("变化变形", ["变化","变形","化身","幻化","化为人","变为","变形","人形","兽形","变形术"]),
        ("异能奇术", ["异人","奇术","绝技","异能","神力","奇才","预知","先知","灵感","通灵","透视"]),
        ("灵异物件", ["异","奇","宝","珍","怪","异宝","神器","法器","灵物","宝物","仙药","灵丹"]),
    ])),
])

# ============================================================
# D. 超自然力量深度叙事主题分类（优化版 - 移除宽泛单字）
# ============================================================
# 规则：关键词必须≥2字，短语型为主；阈值分三级：
#   - 严格主题（容易误判）：需≥2个关键词命中
#   - 普通主题：需≥2个关键词命中，或1个精确长词(≥3字)
#   - 宽容主题（主题本身窄）：≥1个关键词命中
SUPERNATURAL_NARRATIVE_THEMES = OrderedDict([
    # ---- 生死边界类 ----
    ("死后复活", {
        "keywords": ["复生","还魂","再生","复苏","起死","更生","魂归","复活","来生","转世","投胎","重生","苏醒","死而复生","还阳","再生人","须臾复苏","既死复活","忽然复苏"],
        "threshold": 1, "desc": "死后或濒死后复活、还魂的故事"}),
    ("鬼魂还阳", {
        "keywords": ["还阳","魂归","鬼魂","亡魂","游魂","魂魄","附身","托生","冥归","还魄","鬼归","魂不守舍","借尸还魂","鬼怪","鬼魅","厉鬼","怨鬼","恶鬼","女鬼","鬼物"],
        "threshold": 1, "desc": "鬼魂返回阳间的故事"}),
    ("冥界游历", {
        "keywords": ["入冥","赴冥","游冥","冥界","冥游","阴司","阴曹","阎罗殿","地府","黄泉","幽冥","判官","奈何桥","阎罗王","阴间","游地狱","见阎罗","赴阴","冥官","鬼官"],
        "threshold": 1, "desc": "进入冥界游历后返回的故事"}),
    ("尸解成仙", {
        "keywords": ["尸解","羽化","蜕化","升天","化去","不腐","不朽","仙去","蜕形"],
        "threshold": 1, "desc": "借助尸解或其他方式脱离肉体成仙"}),

    # ---- 时间空间类 ----
    ("迷路归返", {
        "keywords": ["迷路","失路","歧路","寻路","归路","不得归","误入","迷途","迷失","不知所之","忽不知所适","迷失道","入山迷路"],
        "threshold": 1, "desc": "迷路后经历奇遇最终返回"}),
    ("时间错位", {
        "keywords": ["经年","须臾间","白驹过隙","弹指间","一刹那","恍如隔世","洞中方一日","世上已千年","经宿","倏忽数年","俄顷","岁月如梭","不觉经年","经年乃返","数日如年","俄而","忽经年","瞬息间","旬日","岁余","忽觉","经月","数年"],
        "threshold": 2, "desc": "经历与正常时间流速不同的情境"}),
    ("空间变幻", {
        "keywords": ["异境","仙境","洞天","福地","幻境","别有洞天","洞中天地","走入洞","忽入一境","见一境","异界"],
        "threshold": 1, "desc": "进入异度空间或空间变幻的经历"}),
    ("天上人间", {
        "keywords": ["天宫","仙界","下凡","谪仙","天庭","天门","降世","天人","玉帝","天仙","登仙","返天","飞升"],
        "threshold": 1, "desc": "天上与人间的往返穿梭"}),
    ("壶中天地", {
        "keywords": ["壶中","袖里","枕中","须弥芥子","芥子纳须弥","壶中天地","袖里乾坤","枕中记","釜中","匣中天地","别有天地"],
        "threshold": 1, "desc": "小空间内包含大世界的奇境"}),

    # ---- 变形类 ----
    ("人兽互变", {
        "keywords": ["化为人","变为","变形","幻化","人形","兽形","狐狸变","蛇变","虎变","猿变","牛变","犬变","鸟变","鱼变","化为兽","化为人形","变为女","变为男","变形记","人面兽身","兽化"],
        "threshold": 1, "desc": "人与兽之间的变形互变"}),
    ("物怪变形", {
        "keywords": ["物怪","成精","作怪","古物成精","器物作怪","化为怪","妖物","化为蛇","化为虎","化为犬","化为鸟","物变","石变","木变"],
        "threshold": 1, "desc": "无生命物体变形为怪物或精灵"}),
    ("妖魅惑人", {
        "keywords": ["魅惑","迷心","迷魂","摄魂","惑人","迷乱","妖媚","色诱","迷惑","狐妖","蛇妖","美女","绝色","惑主"],
        "threshold": 1, "desc": "妖魅运用魅惑之术迷惑凡人"}),
    ("形体变化", {
        "keywords": ["缩小","长大","分身","隐身","易容","变貌","多头","无头","长角","生翅","变化","分身为","多头身","形变"],
        "threshold": 1, "desc": "身体形体的各种变化"}),

    # ---- 修仙佛道类 ----
    ("修道成仙", {
        "keywords": ["修炼","得道","飞升","羽化","辟谷","炼丹","黄白","内丹","外丹","金丹","修真","炼形","仙道","成仙","得道成仙","仙去"],
        "threshold": 1, "desc": "通过修炼得道成仙"}),
    ("僧尼异事", {
        "keywords": ["禅师","法师","胡僧","梵僧","沙弥","比丘","上人","和尚","僧人","尼姑","云游僧","挂单","参禅","化缘","诵经","持戒","剃度","衣钵","禅定","钵盂","乞食","僧房","斋会"],
        "threshold": 2, "desc": "僧尼的奇异经历"}),
    ("法术幻术", {
        "keywords": ["法术","幻术","遁术","隐身术","隐形","五行遁","六丁","遁甲","奇门","太乙","巫术","蛊术","符箓","咒诀","奇术","幻化","变戏法","障眼法","咒语"],
        "threshold": 1, "desc": "使用法术或幻术的故事"}),
    ("因果报应", {
        "keywords": ["报应","因果","善报","恶报","业报","果报","轮回","天谴","报应不爽","恶有恶报","善有善报","天理报应","罚","赎","劫数"],
        "threshold": 1, "desc": "善恶有报的因果故事"}),
    ("佛法灵验", {
        "keywords": ["灵验","显灵","护法","加持","开光","超度","普度","慈悲","感应","佛光","舍利光","圣迹","观音显","菩萨显","佛力","神力","功德"],
        "threshold": 1, "desc": "佛法感应、灵验显灵的故事"}),

    # ---- 占卜梦兆类 ----
    ("梦兆应验", {
        "keywords": ["入梦","托梦","梦中","吉梦","凶梦","梦验","梦解","圆梦","噩梦","梦兆","征兆","应验","夜梦","感梦","梦言","既梦","梦告"],
        "threshold": 1, "desc": "梦中的预兆后来应验"}),
    ("占卜预言", {
        "keywords": ["占卜","卜筮","谶语","预言","相面","算命","推演","卦象","风水","堪舆","星相","面相","手相","骨相","卜算","起课","拆字","占","卜"],
        "threshold": 1, "desc": "通过占卜进行预言的故事"}),
    ("祥瑞灾异", {
        "keywords": ["祥瑞","灾异","日蚀","蝗灾","旱灾","水灾","地震","甘露","嘉禾","庆云","白乌","白雉","白鹿","天狗","星坠","山崩","地裂","河清","瑞","天象"],
        "threshold": 1, "desc": "天降祥瑞或灾异的记录"}),

    # ---- 异精神类 ----
    ("异物奇珍", {
        "keywords": ["异宝","奇珍","珍宝","灵物","神器","法器","仙药","灵丹","宝珠","美玉","异石","奇器","宝剑","宝藏","夜明珠","照骨宝","宝鼎","宝物","异物","奇物","怪石"],
        "threshold": 1, "desc": "奇异物品和珍宝的记载"}),
    ("动植怪变", {
        "keywords": ["变异","畸形","双头","无目","异兽","怪兽","怪鱼","怪鸟","怪蛇","牛生五足","鸡生双头","人面兽","两面","多足","无首","怪异","异形"],
        "threshold": 1, "desc": "动植物出现怪异变化"}),
    ("自然怪象", {
        "keywords": ["天变","地裂","泉涌","山崩","海啸","河清","天雨血","天雨粟","天雨毛","雷击","暴风","虹霓","星陨","地鸣","天狗食日","赤气","黑气","火光"],
        "threshold": 1, "desc": "自然界出现的奇异现象"}),

    # ---- 人世间类 ----
    ("侠客义行", {
        "keywords": ["刺客","飞天夜叉","侠客","义士","游侠","剑客","报恩","报仇","侠义","劫富","济贫","杀贪","除暴","义行","刺客","夜行"],
        "threshold": 1, "desc": "侠客、刺客的义行故事"}),
    ("奇人异能", {
        "keywords": ["异人","绝技","异能","神力","奇才","特异","透视","预知","通灵","千里眼","顺风耳","力士","奇行","异禀"],
        "threshold": 1, "desc": "具有超常能力的人物"}),
    ("隐逸修行", {
        "keywords": ["处士","隐士","山人","高人","修行","遁世","避世","归隐","山居","岩栖","采药","辟谷","隐居","遁迹"],
        "threshold": 1, "desc": "隐逸修行的故事"}),
    ("忠孝节义", {
        "keywords": ["殉节","守节","贞烈","孝行","报国","忠臣","义士","烈女","节妇","孝子","忠义","节义","忠孝","义烈"],
        "threshold": 1, "desc": "忠孝节义的伦理故事"}),
    ("冤屈昭雪", {
        "keywords": ["冤屈","昭雪","冤魂","伸冤","申冤","平反","翻案","复仇","雪冤","冤死","冤案"],
        "threshold": 1, "desc": "冤屈最终得到昭雪"}),
    ("情爱奇闻", {
        "keywords": ["婚约","姻缘","媒妁","相思","离愁","重逢","离别","红娘","私奔","殉情","聘娶","嫁娶","成婚","许嫁","定情","求偶"],
        "threshold": 1, "desc": "爱情婚姻的奇闻轶事"}),

# ---- 新增：覆盖大量只含单字超自然标记的段落 ----
    ("神灵传说", {
        "keywords": ["天帝","天翁","灶神","山神","河伯","风伯","雨师","城隍","土地神","雷公","龙神","海神","井神","门神","树神","石神","仙人","真人","飞仙","地仙","天仙","玉女","仙坛","得仙","天上","降世","神女","神人","神像","祠庙","神祠","祀神","祭神"],
        "threshold": 1, "desc": "关于神仙、民俗神灵的传说记载"}),
    ("异闻杂录", {
        "keywords": ["忽有","忽见","忽闻","相传","或言","俗言","旧说","一说","不知何","竟有","乃知","乃得","经数日","经年","数年","忽得","忽变为","闻有","见有","尝有","人言","世传"],
        "threshold": 2, "desc": "古文叙事模式的超自然片段，以叙事标记词为特征"}),
    ("灵物异迹", {
        "keywords": ["铜镜","宝剑","宝珠","异石","灵井","怪泉","灵洞","奇树","灵草","仙药","宝物","神器","法器","铜神","镜石","灵石","石函","玉龙","宝鼎","金人"],
        "threshold": 1, "desc": "灵异物品、奇石异树、怪泉灵洞的记载"}),
    ("佛教志异", {
        "keywords": ["佛寺","佛塔","佛迹","佛牙","舍利","袈裟","钵盂","僧人","尼姑","沙门","比丘","禅师","法师","上人","和尚","梵僧","胡僧","念经","诵经","持戒","化缘","云游","斋会","佛光","菩萨显灵","观音显","金刚经","佛经","佛力","功德","超度","轮回","涅槃","舍利塔"],
        "threshold": 2, "desc": "佛教相关的灵异事迹与志怪记载"}),
    ("其他超自然", {
        "keywords": ["忽","见","闻","传","乃","因","遂","曰","既","尝","或","俄","忽有","忽见","相传","俗言","竟"],
        "threshold": 999, "desc": "无法归入具体叙事主题的超自然段落（兜底类别）"}),
])

# ============================================================
# E. 超自然力量识别关键词（平衡版：保留有效单字+多字短语）
# ============================================================
SUPERNATURAL_CORE = [
    '神','鬼','仙','妖','魅','怪','精','佛','僧','道',
    '龙','蛟','凤','麒麟','狐','变','尸解','冥','魂','魄',
    '地狱','天帝','菩萨','袈裟','符','咒','术士','法师','天师',
    '巫','真人','飞行','变化','异人','灶神','帝江',
    '不空','万回','一行','罗公远','邢和璞','翟天师','显灵','降神',
]
SUPERNATURAL_SEC = [
    '灵','瑞','谶','兆','梦','卜','占','祈','丹',
    '修炼','飞升','得道','破戒','超度','转世','轮回',
    '阴间','阳间','天宫','地府','阎罗','判官',
    '夜叉','修罗','阿修罗','毗沙门','观音',
    '舍利','佛光','神光','灵光','圣迹',
    '巫术','法术','妖术','幻术','仙术',
    '黄白','丹砂','长生','不死','复生','还魂',
    '托梦','入梦','梦中','显灵','降神',
    '怪异','奇异','不可思议','死后',
]

SUPERNATURAL_VOLS = {"诺皋记上","诺皋记下","支诺皋上","支诺皋中","支诺皋下"}

MONSTER_TYPE_KW = OrderedDict([
    ("神话异兽", ["帝江","刑天","异兽","怪兽","大蛇","毒龙","飞头","夜叉","蛟龙","螭","虬龙"]),
    ("神仙志怪", ["仙人","真人","天帝","灶神","得道","飞升","修炼","羽化","道士","仙家","真人","天师"]),
    ("妖怪变形", ["变为","变形","妖魅","幻化","狐妖","蛇精","妖物","变化","幻形"]),
    ("降妖伏魔", ["降妖","伏魔","斩妖","收妖","制服","驱除","禳灾","除妖","破妖"]),
    ("民俗神灵", ["灶神","门神","土地神","城隍","河伯","山神","风伯","雨师","雷公","龙王"]),
    ("佛道灵异", ["佛陀","菩萨","罗汉","舍利","灵光","袈裟","佛法","念经","诵经","禅定","佛寺","道观"]),
    ("冥界报应", ["冥界","地狱","阎罗","判官","鬼魂","阴间","报应","还魂","转世","业报"]),
    ("梦兆占验", ["入梦","托梦","梦中","征兆","谶语","占卜","卜算","祈祷","瑞象"]),
    ("术法幻术", ["法术","幻术","隐形","变化","咒语","符箓","奇术","遁术","巫术","蛊术"]),
    ("异域怪物", ["异域","波斯","西域","天竺","外国","蛮族","胡人"]),
    ("尸解变化", ["尸解","不朽","不腐","僵尸","骸骨","化去","蜕形"]),
    ("事物怪变", ["怪变","异变","化为","变异","忽然变为","陡然变为"]),
])

def get_vol_short(t):
    if '·' in t: return t.split('·',1)[1]
    return t.replace('续·','')

def get_narrative_cat(vol_title, sub_section=None):
    name = get_vol_short(vol_title)
    if sub_section and sub_section in VOLUME_CATEGORIES:
        return VOLUME_CATEGORIES[sub_section]
    for k,v in VOLUME_CATEGORIES.items():
        if k in name or name in k: return v
    if '广动植' in name: return '动植物谱录'
    if '诺皋' in name: return '异闻志怪'
    if '支诺皋' in name: return '异闻志怪'
    if '寺塔' in name: return '佛寺塔庙'
    if '支植' in name or '支动' in name: return '动植物谱录'
    return '未分类'

def is_supernatural(text, vol_short, cat):
    if vol_short in SUPERNATURAL_VOLS: return True
    c = sum(1 for k in SUPERNATURAL_CORE if k in text)
    if c >= 2: return True
    s = sum(1 for k in SUPERNATURAL_SEC if k in text)
    if s >= 3: return True
    if c >= 1 and s >= 1: return True
    if cat in ["佛道异闻","神仙方术","异闻志怪","幽冥冥迹","丧葬礼俗","梦兆占验","征兆占验","事物怪变"]:
        if c >= 1 or s >= 2: return True
    return False

def get_desc_subjects(text):
    subjects = {}
    for broad, subcats in SUBJECT_KEYWORDS.items():
        sub_matches = {}
        for sub, kws in subcats.items():
            found = [k for k in kws if k in text]
            if len(found) >= 2:
                sub_matches[sub] = found[:5]
        if sub_matches:
            subjects[broad] = sub_matches
    if not subjects:
        for broad, subcats in SUBJECT_KEYWORDS.items():
            sub_matches = {}
            for sub, kws in subcats.items():
                found = [k for k in kws if k in text]
                if len(found) >= 1:
                    sub_matches[sub] = found[:3]
            if sub_matches:
                subjects[broad] = sub_matches
                break
    return subjects

def get_narrative_themes(text):
    themes = []
    for name, info in SUPERNATURAL_NARRATIVE_THEMES.items():
        kws = info["keywords"]
        threshold = info.get("threshold", 1)
        c = sum(1 for k in kws if k in text)
        if c >= max(threshold, 2):
            themes.append((name, c))
        elif c >= 1 and threshold <= 1:
            themes.append((name, c))
    # Fallback: single-char broad keywords for common supernatural themes
    # Maps to existing theme names where possible
    if not themes:
        fallback = OrderedDict([
            ("鬼魂还阳", ["鬼","魂","魄","亡","冥","阴"]),
            ("僧尼异事", ["僧","尼","寺","禅","钵","斋","梵","袈裟"]),
            ("法术幻术", ["术","法","幻","符","咒","遁"]),
            ("物怪变形", ["妖","魅","怪","精","变为","变化"]),
            ("异物奇珍", ["异","奇","珍","宝","怪"]),
            ("修道成仙", ["仙","佛","道","菩萨","罗汉","真人","修炼"]),
            ("梦兆应验", ["梦","兆","谶","占","卜"]),
            ("冥界游历", ["冥","地府","阴间","黄泉","阎罗","判官"]),
            ("因果报应", ["报","罚","赎","业","劫","应"]),
        ])
        for fb_name, fb_kws in fallback.items():
            c = sum(1 for k in fb_kws if k in text)
            if c >= 1:  # 降低阈值：单字命中也算
                themes.append((fb_name, c))
                if len(themes) >= 2:
                    break
    # 最终兜底：无法归入任何主题的超自然段落
    if not themes:
        themes.append(("其他超自然", 0))
    # 限制：每段最多保留3个主题（按匹配度排序）
    if len(themes) > 3:
        themes = sorted(themes, key=lambda x: -x[1])[:3]
    return themes

def brief(text, n=80):
    return text[:n] + ('……' if len(text) > n else '')

def parse_sanjiao(content):
    lines = content.split('\n')
    vols = []
    current_vol = None
    current_sub = None
    current_paras = []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if stripped.startswith('## '):
            if current_vol and current_paras:
                vols.append((current_vol, current_sub if current_sub else '', current_paras))
            current_vol = stripped[3:].strip()
            current_sub = None
            current_paras = []
            continue
        if stripped.startswith('○'):
            sub_name = stripped[1:].strip()
            if current_vol and current_paras:
                vols.append((current_vol, current_sub if current_sub else '', current_paras))
                current_paras = []
            current_sub = sub_name
            continue
        if len(stripped) > 5:
            current_paras.append(stripped)
    if current_vol and current_paras:
        vols.append((current_vol, current_sub if current_sub else '', current_paras))
    return vols


# ============================================================
# CSV → Markdown 转换
# ============================================================
def csv_to_md(csv_path, md_path, title=""):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return
    headers = rows[0]
    data = rows[1:]
    
    # Determine column widths (cap at 60 for readability)
    col_widths = []
    for i, h in enumerate(headers):
        max_w = max(len(h), max((len(row[i]) if i < len(row) else 0) for row in data) if data else 0)
        col_widths.append(min(max_w, 60))
    
    lines = []
    if title:
        lines.append(f"# {title}\n")
    
    # Header
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
    lines.append(header_line)
    lines.append(sep_line)
    
    # Data rows (limit to 500 for huge files, note in md)
    max_rows = 500
    truncated = len(data) > max_rows
    for row in data[:max_rows]:
        cells = []
        for i, cell in enumerate(row):
            if i < len(headers):
                cell_text = cell.replace('\n', ' ').replace('|', '｜')
                if len(cell_text) > col_widths[i]:
                    cell_text = cell_text[:col_widths[i]-2] + '..'
                cells.append(cell_text.ljust(col_widths[i]))
            else:
                cells.append("")
        lines.append("| " + " | ".join(cells) + " |")
    
    if truncated:
        lines.append(f"\n> 共 {len(data)} 行，仅显示前 {max_rows} 行。完整数据请查看CSV文件。")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    print("=" * 60)
    print("酉阳杂俎 三校版 Task 4 分类（优化版）")
    print("=" * 60)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    vols = parse_sanjiao(content)
    print(f"解析到 {len(vols)} 个卷/子篇")
    
    all_entries = []
    supernatural_entries = []
    vol_idx = 0
    
    narr_cat_stats = defaultdict(int)
    subject_stats = defaultdict(int)
    sub_subject_stats = defaultdict(int)
    subject_freq = defaultdict(int)
    supernatural_theme_stats = defaultdict(int)
    
    for vol_title, sub_section, paras in vols:
        vol_short = get_vol_short(vol_title)
        cat = get_narrative_cat(vol_title, sub_section)
        is_xu = vol_title.startswith('续·')
        
        for para in paras:
            prefix = "S" if vol_idx == 0 else ("X" if is_xu else "V")
            pid = f"{prefix}{vol_idx:02d}-P{len(all_entries)+1:03d}"
            
            has_sgui = is_supernatural(para, vol_short, cat)
            desc_subs = get_desc_subjects(para)
            
            entry = {
                "pid": pid,
                "volume_index": vol_idx,
                "volume_title": vol_title,
                "volume_short": vol_short,
                "sub_section": sub_section,
                "narrative_category": cat,
                "text": para,
                "text_length": len(para),
                "text_brief": brief(para),
                "has_supernatural": has_sgui,
                "description_subjects": desc_subs,
            }
            
            narr_cat_stats[cat] += 1
            
            for broad, subcats in desc_subs.items():
                subject_stats[broad] += 1
                for sub, kws in subcats.items():
                    sub_subject_stats[f"{broad}/{sub}"] += 1
                    for kw in kws:
                        subject_freq[kw] += 1
            
            if has_sgui:
                themes = get_narrative_themes(para)
                entry["narrative_themes"] = themes
                supernatural_entries.append(entry)
                for t, c in themes:
                    supernatural_theme_stats[t] += 1
            
            all_entries.append(entry)
        
        vol_idx += 1
    
    total = len(all_entries)
    total_sg = len(supernatural_entries)
    print(f"总段落: {total}")
    print(f"超自然段落: {total_sg} ({total_sg/total*100:.1f}%)")
    
    # ========== CSV Output ==========
    csv_files = {}
    
    # 1. 叙事分类明细
    csv_path = os.path.join(BASE_DIR, "叙事分类明细.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["paragraph_id","volume_index","volume_title","sub_section","narrative_category","source","text"])
        for e in all_entries:
            w.writerow([e["pid"], e["volume_index"], e["volume_title"], e["sub_section"], e["narrative_category"], "三校", e["text_brief"]])
    csv_files["叙事分类明细"] = csv_path
    print(f"  叙事分类明细.csv: {total} 行")
    
    # 2. 叙事分类统计
    csv_path = os.path.join(BASE_DIR, "叙事分类统计.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["narrative_category","paragraph_count","absolute_percentage"])
        for cat, count in sorted(narr_cat_stats.items(), key=lambda x: -x[1]):
            w.writerow([cat, count, f"{count/total*100:.2f}%"])
    csv_files["叙事分类统计"] = csv_path
    
    # 3. 主题分类明细
    csv_path = os.path.join(BASE_DIR, "主题分类明细.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["broad_category","level1_subject","level2_subject","specific_subject","volume_index","volume_title","source","paragraph_id","primary_subject","keywords","text"])
        for e in all_entries:
            for broad, subcats in e["description_subjects"].items():
                for sub, kws in subcats.items():
                    kw_str = "、".join(kws)
                    w.writerow([broad, broad, sub, sub, e["volume_index"], e["volume_title"], "三校", e["pid"], sub, kw_str, e["text_brief"]])
    csv_files["主题分类明细"] = csv_path
    
    # 4. 主题分类统计
    csv_path = os.path.join(BASE_DIR, "主题分类统计.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["broad_category","paragraph_count","absolute_percentage"])
        for broad, count in sorted(subject_stats.items(), key=lambda x: -x[1]):
            w.writerow([broad, count, f"{count/total*100:.2f}%"])
    csv_files["主题分类统计"] = csv_path
    
    # 5. 主题频次统计
    csv_path = os.path.join(BASE_DIR, "主题频次统计.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["level1_subject","level2_subject","appearance_count"])
        for sub_sub, count in sorted(sub_subject_stats.items(), key=lambda x: -x[1]):
            parts = sub_sub.split('/', 1)
            w.writerow([parts[0], parts[1] if len(parts)>1 else "", count])
    csv_files["主题频次统计"] = csv_path
    
    # 6. 重复主题分类
    csv_path = os.path.join(BASE_DIR, "重复主题分类.csv")
    multi_entries = [e for e in all_entries if len(e["description_subjects"]) >= 2]
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["volume_index","volume_title","source","paragraph_id","duplicate_broad_categories","duplicate_specific_subjects","text"])
        for e in multi_entries:
            cats = "、".join(e["description_subjects"].keys())
            subs = []
            for broad, subcats in e["description_subjects"].items():
                subs.extend(list(subcats.keys()))
            w.writerow([e["volume_index"], e["volume_title"], "三校", e["pid"], cats, "、".join(subs), e["text_brief"]])
    csv_files["重复主题分类"] = csv_path
    print(f"  重复主题分类.csv: {len(multi_entries)} 行")
    
    # 7. 超自然力量叙事主题明细
    csv_path = os.path.join(BASE_DIR, "超自然力量叙事主题明细.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["paragraph_id","volume_title","monster_type","narrative_themes","theme_descriptions","keywords","text"])
        for e in supernatural_entries:
            themes = e.get("narrative_themes", [])
            theme_names = "、".join([t[0] for t in themes])
            theme_descs = "、".join([SUPERNATURAL_NARRATIVE_THEMES[t[0]]["desc"] for t in themes if t[0] in SUPERNATURAL_NARRATIVE_THEMES])
            mt_scores = {}
            for mt, mkws in MONSTER_TYPE_KW.items():
                s = sum(1 for k in mkws if k in e["text"])
                if s > 0: mt_scores[mt] = s
            monster_type = max(mt_scores, key=mt_scores.get) if mt_scores else "神仙志怪"
            matched_kws = []
            for k in SUPERNATURAL_CORE:
                if k in e["text"] and len(matched_kws) < 8:
                    matched_kws.append(k)
            w.writerow([e["pid"], e["volume_title"], monster_type, theme_names, theme_descs, "、".join(matched_kws), e["text_brief"]])
    csv_files["超自然力量叙事主题明细"] = csv_path
    print(f"  超自然力量叙事主题明细.csv: {len(supernatural_entries)} 行")
    
    # 8. 超自然力量叙事主题统计
    csv_path = os.path.join(BASE_DIR, "超自然力量叙事主题统计.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(["narrative_theme","description","paragraph_count","percentage"])
        for theme, count in sorted(supernatural_theme_stats.items(), key=lambda x: -x[1]):
            desc = SUPERNATURAL_NARRATIVE_THEMES.get(theme, {}).get("desc", "")
            w.writerow([theme, desc, count, f"{count/total_sg*100:.2f}%"])
    csv_files["超自然力量叙事主题统计"] = csv_path
    
    print("\n" + "=" * 60)
    print("全部CSV文件已导出，开始转换为Markdown...")
    print("=" * 60)
    
    # ========== CSV → Markdown ==========
    md_titles = {
        "叙事分类明细": "叙事分类明细",
        "叙事分类统计": "叙事分类统计",
        "主题分类明细": "主题分类明细",
        "主题分类统计": "主题分类统计",
        "主题频次统计": "主题频次统计",
        "重复主题分类": "重复主题分类（多类归属）",
        "超自然力量叙事主题明细": "超自然力量叙事主题明细",
        "超自然力量叙事主题统计": "超自然力量叙事主题统计",
    }
    
    for name, csv_path in csv_files.items():
        md_path = csv_path.replace('.csv', '.md')
        title = md_titles.get(name, name)
        try:
            csv_to_md(csv_path, md_path, title)
            print(f"  ✓ {name}.md")
        except Exception as ex:
            print(f"  ✗ {name}.md 转换失败: {ex}")
    
    # ========== Summary ==========
    print(f"\n总段落: {total}")
    print(f"超自然段落: {total_sg} ({total_sg/total*100:.1f}%)")
    print(f"\n叙事结构分类统计:")
    for cat, count in sorted(narr_cat_stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} ({count/total*100:.1f}%)")
    
    print(f"\n描写对象大类统计:")
    for broad, count in sorted(subject_stats.items(), key=lambda x: -x[1]):
        print(f"  {broad}: {count}")
    
    print(f"\n超自然叙事主题统计 (优化后):")
    for theme, count in sorted(supernatural_theme_stats.items(), key=lambda x: -x[1]):
        desc = SUPERNATURAL_NARRATIVE_THEMES.get(theme, {}).get("desc", "")
        print(f"  {theme}: {count} ({count/total_sg*100:.1f}%) - {desc}")
    
    no_theme = sum(1 for e in supernatural_entries if not e.get("narrative_themes"))
    print(f"\n超自然段落中无匹配主题: {no_theme}/{total_sg}")


if __name__ == '__main__':
    main()