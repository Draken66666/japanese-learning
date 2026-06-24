#!/usr/bin/env python3
"""Third pass: fix mixed translations and add missing words."""

import re

INPUT_FILE = "src/data/vocabulary-data.ts"

# Additional dictionary for words missed in previous passes
EXTRA_DICT = {
    # Common words still missing
    "automobile": "汽车", "oneself": "自己", "skillful": "熟练的", "likeable": "讨人喜欢的",
    "ashtray": "烟灰缸", "aeroplane": "飞机", "cuisine": "料理", "stereo": "立体声",
    "greengrocer": "蔬菜水果店", "pickpocket": "扒手", "announcer": "播音员",
    "bookshelves": "书架", "bookshelf": "书架", "occasionally": "偶尔",
    "unskillful": "不熟练的", "midday": "中午", "meal": "一餐",
    "spacious": "宽敞的", "bustling": "热闹的", "luke": "微", "warm": "温暖",
    "entry": "入口", "dining": "用餐", "hall": "大厅", "sufficient": "足够的",
    "splendid": "出色的", "dining hall": "餐厅", "entry hall": "玄关",
    "western-style": "西式", "clothes": "衣服", "western": "西式",
    "old": "旧的", "not used for people": "不用于人",
    "to be understood": "被理解", "understood": "被理解",
    "america": "美国", "american": "美国的",

    # More common JLPT words
    "flu": "流感", "cold": "感冒", "cancer": "癌症", "diabetes": "糖尿病",
    "allergy": "过敏", "asthma": "哮喘", "pneumonia": "肺炎",
    "vitamin": "维生素", "protein": "蛋白质", "calorie": "卡路里",
    "nutrition": "营养", "diet": "饮食", "recipe": "食谱",
    "ingredient": "原料", "menu": "菜单", "appetizer": "开胃菜",
    "main course": "主菜", "dessert": "甜点", "beverage": "饮料",
    "cocktail": "鸡尾酒", "whiskey": "威士忌", "vodka": "伏特加",
    "champagne": "香槟", "brandy": "白兰地", "rum": "朗姆酒",
    "gin": "杜松子酒", "tequila": "龙舌兰",
    "cigarette": "香烟", "tobacco": "烟草", "pipe": "烟斗",
    "cigar": "雪茄", "match": "火柴", "lighter": "打火机",
    "candle": "蜡烛", "torch": "火把", "flashlight": "手电筒",
    "bulb": "灯泡", "tube": "灯管", "lamp": "台灯",
    "torch": "手电筒", "lantern": "灯笼",
    "blanket": "毯子", "quilt": "被子", "mattress": "床垫",
    "sheet": "床单", "cushion": "靠垫", "mat": "垫子",
    "rug": "小地毯", "mat": "垫子",
    "photo": "照片", "picture": "图片", "image": "图像",
    "portrait": "肖像", "landscape": "风景", "scenery": "风景",
    "view": "景色", "scene": "场景", "sight": "景象",
    "panorama": "全景", "vista": "远景",
    "ticket": "票", "pass": "通行证", "permit": "许可证",
    "visa": "签证", "passport": "护照", "id": "身份证",
    "identification": "身份证明", "card": "卡片", "certificate": "证书",
    "license": "执照", "permit": "许可", "authorization": "授权",
    "document": "文件", "paper": "文件", "form": "表格",
    "application": "申请表", "registration": "登记", "record": "记录",
    "file": "档案", "folder": "文件夹", "envelope": "信封",
    "parcel": "包裹", "package": "包裹", "box": "盒子",
    "stamp": "邮票", "seal": "印章", "signature": "签名",
    "autograph": "亲笔签名", "handwriting": "笔迹",
    "ink": "墨水", "pen": "钢笔", "pencil": "铅笔",
    "eraser": "橡皮", "sharpener": "卷笔刀", "ruler": "尺子",
    "compass": "圆规", "protractor": "量角器", "calculator": "计算器",
    "computer": "电脑", "laptop": "笔记本电脑", "desktop": "台式电脑",
    "tablet": "平板电脑", "smartphone": "智能手机", "mobile": "手机",
    "phone": "电话", "telephone": "电话", "fax": "传真",
    "printer": "打印机", "scanner": "扫描仪", "copier": "复印机",
    "monitor": "显示器", "screen": "屏幕", "keyboard": "键盘",
    "mouse": "鼠标", "speaker": "扬声器", "microphone": "麦克风",
    "headphone": "耳机", "earphone": "耳机", "webcam": "网络摄像头",
    "camera": "相机", "camcorder": "摄像机", "projector": "投影仪",
    "remote": "遥控器", "antenna": "天线", "cable": "电缆",
    "wire": "电线", "plug": "插头", "socket": "插座",
    "outlet": "电源插座", "switch": "开关", "button": "按钮",
    "battery": "电池", "charger": "充电器", "adapter": "适配器",
    "transformer": "变压器", "generator": "发电机", "motor": "马达",
    "engine": "引擎", "turbine": "涡轮", "pump": "泵",
    "compressor": "压缩机", "valve": "阀门", "pipe": "管道",
    "tube": "管子", "hose": "软管", "duct": "管道",
    "filter": "过滤器", "strainer": "滤网", "sieve": "筛子",
    "grid": "网格", "mesh": "网眼", "net": "网",
    "trap": "陷阱", "snare": "圈套", "bait": "诱饵",
    "hook": "钩子", "line": "线", "rod": "钓竿",
    "reel": "卷线器", "lure": "鱼饵", "fly": "假蝇",
    "net": "渔网", "trap": "陷阱",
    "garden": "花园", "yard": "院子", "lawn": "草坪",
    "fence": "栅栏", "hedge": "树篱", "wall": "墙",
    "gate": "大门", "door": "门", "entrance": "入口",
    "exit": "出口", "porch": "门廊", "veranda": "走廊",
    "balcony": "阳台", "terrace": "露台", "patio": "庭院",
    "deck": "甲板", "dock": "码头", "pier": "栈桥",
    "harbor": "港口", "port": "港口", "marina": "游艇港",
    "anchor": "锚", "sail": "帆", "mast": "桅杆",
    "deck": "甲板", "hull": "船体", "cabin": "船舱",
    "wheel": "方向盘", "helm": "舵", "rudder": "方向舵",
    "oar": "桨", "paddle": "短桨",
    "tool": "工具", "kit": "工具箱", "set": "套装",
    "equipment": "设备", "gear": "装备", "apparatus": "器械",
    "device": "装置", "gadget": "小工具", "appliance": "器具",
    "machine": "机器", "robot": "机器人", "automaton": "自动机",
    "vehicle": "车辆", "automobile": "汽车", "car": "汽车",
    "truck": "卡车", "van": "面包车", "bus": "公交车",
    "coach": "长途客车", "tram": "有轨电车", "trolley": "无轨电车",
    "train": "火车", "subway": "地铁", "metro": "地铁",
    "monorail": "单轨列车", "maglev": "磁悬浮", "bullet train": "新干线",
    "locomotive": "机车", "carriage": "车厢", "wagon": "货车",
    "bicycle": "自行车", "bike": "自行车", "motorcycle": "摩托车",
    "scooter": "踏板车", "moped": "助力车", "tricycle": "三轮车",
    "wheelchair": "轮椅", "stroller": "婴儿车", "cart": "手推车",
    "trolley": "手推车", "wagon": "推车",
    "airplane": "飞机", "plane": "飞机", "jet": "喷气式飞机",
    "helicopter": "直升机", "chopper": "直升机", "gyrocopter": "旋翼机",
    "glider": "滑翔机", "balloon": "气球", "blimp": "飞艇",
    "airship": "飞艇", "drone": "无人机", "uav": "无人机",
    "rocket": "火箭", "missile": "导弹", "spaceship": "宇宙飞船",
    "shuttle": "航天飞机", "capsule": "太空舱", "satellite": "卫星",
    "probe": "探测器", "telescope": "望远镜", "microscope": "显微镜",
    "lens": "透镜", "prism": "棱镜", "mirror": "镜子",
    "glass": "玻璃", "crystal": "水晶", "diamond": "钻石",
    "gem": "宝石", "jewel": "珠宝", "pearl": "珍珠",
    "ruby": "红宝石", "sapphire": "蓝宝石", "emerald": "祖母绿",
    "topaz": "黄玉", "amethyst": "紫水晶", "opal": "蛋白石",
    "jade": "玉", "amber": "琥珀", "coral": "珊瑚",
    "ivory": "象牙", "bone": "骨头", "horn": "角",
    "shell": "壳", "scale": "鳞", "feather": "羽毛",
    "fur": "毛皮", "leather": "皮革", "hide": "兽皮",
    "skin": "皮肤", "wool": "羊毛", "silk": "丝绸",
    "cotton": "棉", "linen": "亚麻", "hemp": "麻",
    "thread": "线", "yarn": "纱线", "string": "细绳",
    "cord": "粗绳", "rope": "绳索", "cable": "缆绳",
    "chain": "链条", "wire": "金属线", "cable": "电缆",
    "fabric": "织物", "cloth": "布", "textile": "纺织品",
    "material": "材料", "substance": "物质", "matter": "物质",
    "element": "元素", "compound": "化合物", "mixture": "混合物",
    "solution": "溶液", "suspension": "悬浮液", "emulsion": "乳液",
    "alloy": "合金", "metal": "金属", "nonmetal": "非金属",
    "mineral": "矿物", "rock": "岩石", "stone": "石头",
    "ore": "矿石", "gem": "宝石", "crystal": "水晶",
    "salt": "盐", "sugar": "糖", "starch": "淀粉",
    "protein": "蛋白质", "fat": "脂肪", "oil": "油",
    "acid": "酸", "base": "碱", "alkali": "碱",
    "chemical": "化学物质", "reagent": "试剂", "catalyst": "催化剂",
    "solvent": "溶剂", "solute": "溶质", "suspension": "悬浮",
    "gas": "气体", "liquid": "液体", "solid": "固体",
    "fluid": "流体", "vapor": "蒸汽", "steam": "蒸汽",
    "mist": "薄雾", "fog": "雾", "smog": "烟雾",
    "smoke": "烟", "soot": "煤烟", "ash": "灰烬",
    "dust": "灰尘", "dirt": "泥土", "soil": "土壤",
    "sand": "沙子", "gravel": "碎石", "pebble": "鹅卵石",
    "clay": "黏土", "mud": "泥", "sludge": "污泥",
    "water": "水", "ice": "冰", "snow": "雪",
    "rain": "雨", "drizzle": "毛毛雨", "shower": "阵雨",
    "downpour": "暴雨", "storm": "暴风雨", "thunderstorm": "雷暴",
    "hail": "冰雹", "sleet": "雨夹雪", "blizzard": "暴风雪",
    "wind": "风", "breeze": "微风", "gale": "大风",
    "gust": "阵风", "hurricane": "飓风", "typhoon": "台风",
    "tornado": "龙卷风", "cyclone": "气旋", "monsoon": "季风",
    "cloud": "云", "fog": "雾", "mist": "薄雾",
    "dew": "露水", "frost": "霜", "ice": "冰",
    "weather": "天气", "climate": "气候", "season": "季节",
    "temperature": "温度", "humidity": "湿度", "pressure": "气压",
    "forecast": "预报", "meteorology": "气象学",
    # More adjectives
    "convenient": "方便的", "inconvenient": "不方便的", "comfortable": "舒适的",
    "uncomfortable": "不舒服的", "pleasant": "愉快的", "unpleasant": "不愉快的",
    "interesting": "有趣的", "boring": "无聊的", "exciting": "令人兴奋的",
    "surprising": "令人惊讶的", "shocking": "令人震惊的", "amazing": "令人惊叹的",
    "fascinating": "迷人的", "charming": "迷人的", "attractive": "有吸引力的",
    "beautiful": "美丽的", "gorgeous": "华丽的", "stunning": "极美的",
    "magnificent": "壮丽的", "spectacular": "壮观的", "breathtaking": "令人叹为观止的",
    "ugly": "丑陋的", "hideous": "骇人的", "repulsive": "令人厌恶的",
    "disgusting": "恶心的", "nasty": "令人不快的", "awful": "可怕的",
    "terrible": "糟糕的", "horrible": "恐怖的", "dreadful": "可怕的",
    "frightful": "可怕的", "appalling": "令人震惊的", "dismal": "阴沉的",
    "gloomy": "阴暗的", "dreary": "沉闷的", "bleak": "凄凉的",
    "desolate": "荒凉的", "barren": "贫瘠的", "sterile": "无菌的",
    "fertile": "肥沃的", "rich": "富饶的", "poor": "贫瘠的",
    "lush": "茂盛的", "verdant": "翠绿的", "green": "绿色的",
    "withered": "枯萎的", "dead": "死的", "alive": "活的",
    "living": "活的", "animate": "有生命的", "inanimate": "无生命的",
    "organic": "有机的", "synthetic": "合成的", "artificial": "人工的",
    "natural": "自然的", "wild": "野生的", "tame": "驯服的",
    "domestic": "驯养的", "feral": "野性的",
    # Mixed translations to fix
    "ball-point": "圆珠", "ball-point pen": "圆珠笔",
    "younger brother": "弟弟", "younger sister": "妹妹",
    "older brother": "哥哥", "older sister": "姐姐",
    "postage stamp": "邮票", "postage": "邮费",
    "roll of film": "胶卷",
    "western-style clothes": "西服", "western-style": "西式",
    "dining hall": "食堂", "entry hall": "玄关",
    "luke warm": "温热的", "lukewarm": "微温的",
    "midday meal": "午餐",
    # More single words
    "automobile": "汽车", "vehicle": "车辆", "car": "汽车",
    "truck": "卡车", "bus": "公交车", "train": "火车",
    "ship": "船", "boat": "小船", "vessel": "船只",
    "craft": "飞行器", "aircraft": "飞机", "airplane": "飞机",
    "aeroplane": "飞机", "jet": "喷气式飞机",
    "oneself": "自己", "yourself": "你自己", "myself": "我自己",
    "himself": "他自己", "herself": "她自己", "itself": "它自己",
    "ourselves": "我们自己", "yourselves": "你们自己",
    "themselves": "他们自己",
    "skillful": "熟练的", "skilled": "熟练的", "adept": "熟练的",
    "proficient": "精通的", "expert": "专家", "master": "大师",
    "amateur": "业余者", "novice": "新手", "beginner": "初学者",
    "professional": "专业的", "amateur": "业余的",
    "likeable": "讨人喜欢的", "lovable": "可爱的", "adorable": "可爱的",
    "cute": "可爱的", "sweet": "甜美的", "darling": "亲爱的",
    "dear": "亲爱的", "beloved": "深爱的", "cherished": "珍爱的",
    "precious": "珍贵的", "valuable": "有价值的", "priceless": "无价的",
    "worthless": "无价值的", "cheap": "便宜的", "expensive": "昂贵的",
    "affordable": "负担得起的", "costly": "昂贵的", "dear": "昂贵的",
    "bustling": "热闹的", "busy": "忙碌的", "lively": "热闹的",
    "vibrant": "充满活力的", "energetic": "精力充沛的", "dynamic": "动态的",
    "active": "活跃的", "passive": "被动的",
    "spacious": "宽敞的", "roomy": "宽敞的", "ample": "充足的",
    "sufficient": "足够的", "adequate": "充分的", "enough": "足够的",
    "plenty": "充足的", "abundant": "丰富的", "plentiful": "丰富的",
    "scarce": "稀少的", "rare": "稀有的", "uncommon": "不常见的",
    "common": "常见的", "ordinary": "普通的", "usual": "通常的",
    "normal": "正常的", "regular": "定期的", "routine": "常规的",
    "standard": "标准的", "typical": "典型的", "classic": "经典的",
    "traditional": "传统的", "conventional": "常规的", "customary": "习惯的",
    "habitual": "习惯性的", "frequent": "频繁的", "occasional": "偶尔的",
    "rare": "稀有的", "seldom": "很少", "hardly": "几乎不",
    "scarcely": "几乎不", "barely": "勉强", "merely": "仅仅",
    "only": "只有", "just": "只是", "simply": "简单地",
    "purely": "纯粹地", "entirely": "完全地", "completely": "完全地",
    "totally": "完全地", "absolutely": "绝对地", "utterly": "完全地",
    "fully": "充分地", "wholly": "全部地", "partly": "部分地",
    "partially": "部分地", "somewhat": "有点", "slightly": "稍微",
    "barely": "勉强", "hardly": "几乎不",
    # Additional JLPT specific
    "greengrocer": "蔬菜店", "vegetable shop": "蔬菜店",
    "fruit shop": "水果店", "butcher shop": "肉店",
    "fish shop": "鱼店", "bakery": "面包店",
    "bookstore": "书店", "bookshop": "书店",
    "stationery shop": "文具店", "toy shop": "玩具店",
    "gift shop": "礼品店", "souvenir shop": "纪念品店",
    "duty-free shop": "免税店", "thrift shop": "二手店",
    "antique shop": "古董店", "boutique": "精品店",
    "department store": "百货商店", "convenience store": "便利店",
    "supermarket": "超市", "grocery store": "杂货店",
    "market": "市场", "bazaar": "集市", "fair": "集市",
    "mall": "购物中心", "plaza": "广场", " arcade": "商场",
    "shopping center": "购物中心", "shopping mall": "购物中心",
    # Actions
    "to get on": "上车", "to get off": "下车",
    "to get in": "进入", "to get out": "出去",
    "to put on": "穿上", "to take off": "脱下",
    "to turn on": "打开", "to turn off": "关闭",
    "to pick up": "捡起", "to put down": "放下",
    "to sit down": "坐下", "to stand up": "站起",
    "to lie down": "躺下", "to get up": "起床",
    "to wake up": "醒来", "to fall asleep": "入睡",
    "to go to bed": "就寝", "to go to sleep": "入睡",
    "to come back": "回来", "to go back": "回去",
    "to give back": "归还", "to take back": "收回",
    "to hold on": "等一下", "to hold up": "举起",
    "to look up": "查阅", "to look for": "寻找",
    "to look at": "看", "to look after": "照顾",
    "to look out": "小心", "to look forward to": "期待",
    "to find out": "查明", "to figure out": "弄清楚",
    "to point out": "指出", "to make out": "辨认",
    "to turn out": "结果是", "to work out": "锻炼",
    "to carry on": "继续", "to carry out": "执行",
    "to put away": "收好", "to put off": "推迟",
    "to put up with": "忍受", "to put together": "组装",
    "to get along": "相处", "to get over": "克服",
    "to get through": "通过", "to get away": "逃脱",
    "to get back": "取回", "to get together": "聚会",
    "to break down": "故障", "to break up": "分手",
    "to break in": "闯入", "to break out": "爆发",
    "to bring up": "抚养", "to bring about": "引起",
    "to bring back": "带回", "to bring down": "降低",
    "to call up": "打电话", "to call for": "需要",
    "to call on": "拜访", "to call off": "取消",
    "to come across": "偶遇", "to come along": "跟随",
    "to come back": "回来", "to come down": "下降",
    "to come in": "进来", "to come out": "出来",
    "to come over": "过来", "to come up": "出现",
    "to cut down": "削减", "to cut off": "切断",
    "to cut out": "删除", "to cut up": "切碎",
    "to give away": "赠送", "to give in": "屈服",
    "to give up": "放弃", "to give out": "分发",
    "to go ahead": "前进", "to go away": "离开",
    "to go by": "经过", "to go down": "下降",
    "to go on": "继续", "to go out": "外出",
    "to go over": "复习", "to go through": "经历",
    "to keep on": "继续", "to keep up": "保持",
    "to look up to": "敬佩", "to look down on": "蔑视",
    "to make up": "化妆", "to make up for": "弥补",
    "to pass away": "去世", "to pass out": "昏倒",
    "to pull over": "靠边停车", "to pull through": "度过难关",
    "to put across": "表达", "to put aside": "留出",
    "to run away": "逃跑", "to run into": "偶遇",
    "to run out": "用完", "to run over": "碾过",
    "to set up": "建立", "to set off": "出发",
    "to set out": "出发", "to set down": "放下",
    "to take after": "像", "to take apart": "拆开",
    "to take away": "拿走", "to take back": "收回",
    "to take care of": "照顾", "to take down": "取下",
    "to take in": "吸收", "to take off": "起飞",
    "to take on": "承担", "to take over": "接管",
    "to take up": "开始从事", "to think over": "仔细考虑",
    "to try on": "试穿", "to try out": "试验",
    "to turn down": "拒绝", "to turn in": "上交",
    "to turn into": "变成", "to turn over": "翻转",
    "to turn to": "求助于", "to turn up": "出现",
    "to wear out": "穿破", "to work on": "致力于",
    "to worry about": "担心",
}

# Words to directly replace (for mixed translations)
REPLACE_PAIRS = {
    "ball-point钢笔": "圆珠笔",
    "younger兄弟": "弟弟",
    "younger姐妹": "妹妹",
    "older兄弟": "哥哥",
    "older姐妹": "姐姐",
    "postage邮票": "邮票",
    "entry大厅": "玄关",
    "dining大厅": "食堂",
    "luke温暖的": "微温的",
    "midday一餐": "午餐",
    "western-style衣服": "西服",
    "spacious、宽的": "宽敞的",
    "bustling、忙的": "热闹的",
    "splendid、足够的": "出色的",
    "a喝": "喝",
    "adj.优秀": "优秀的",
    "ball-point": "圆珠",
    "old (not used for people)": "旧的",
    "to be understood": "被理解",
}

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def has_english(text):
    """Check if text contains English words (3+ letters)."""
    return bool(re.search(r'[a-zA-Z]{2,}', text))

def translate_remaining(text):
    """Try to translate remaining English in text."""
    if not text:
        return text

    # Direct replacement for known mixed translations
    for eng, chn in REPLACE_PAIRS.items():
        if eng in text:
            text = text.replace(eng, chn)

    # If now fully Chinese, return
    if not has_english(text):
        return text

    # Try phrase replacements
    for eng, chn in sorted(EXTRA_DICT.items(), key=lambda x: -len(x[0])):
        if eng.lower() in text.lower():
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            text = pattern.sub(chn, text)

    # If now fully Chinese, return
    if not has_english(text):
        return text

    # Word by word for remaining
    words = re.findall(r'[a-zA-Z]+', text)
    for word in words:
        wl = word.lower()
        if wl in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl], text, flags=re.IGNORECASE)
        elif wl.endswith('s') and wl[:-1] in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl[:-1]], text, flags=re.IGNORECASE)
        elif wl.endswith('es') and wl[:-2] in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl[:-2]], text, flags=re.IGNORECASE)
        elif wl.endswith('ing') and wl[:-3] in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl[:-3]], text, flags=re.IGNORECASE)
        elif wl.endswith('ed') and wl[:-2] in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl[:-2]], text, flags=re.IGNORECASE)
        elif wl.endswith('ly') and wl[:-2] in EXTRA_DICT:
            text = re.sub(re.escape(word), EXTRA_DICT[wl[:-2]], text, flags=re.IGNORECASE)

    return text

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stats = {'meaning_fixed': 0, 'example_fixed': 0, 'still_english': 0}

    for i, line in enumerate(lines):
        if 'meaning_zh:' not in line:
            continue

        # Fix meaning_zh
        m = re.search(r'meaning_zh:\s*"([^"]*)"', line)
        if m:
            old_zh = m.group(1)
            if has_english(old_zh):
                new_zh = translate_remaining(old_zh)
                if new_zh != old_zh:
                    line = line.replace(f'meaning_zh: "{old_zh}"', f'meaning_zh: "{new_zh}"')
                    if not has_english(new_zh):
                        stats['meaning_fixed'] += 1
                    else:
                        stats['still_english'] += 1
                else:
                    stats['still_english'] += 1

        # Fix example_translation
        et = re.search(r'example_translation:\s*"([^"]*)"', line)
        if et:
            old_et = et.group(1)
            if has_english(old_et) and not old_et.startswith('http'):
                new_et = translate_remaining(old_et)
                if new_et != old_et:
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "{new_et}"')
                    stats['example_fixed'] += 1

        lines[i] = line

    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # Final count
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        final = f.read()

    total = final.count('meaning_zh:')
    english_count = len(re.findall(r'meaning_zh:\s*"[A-Za-z]', final))
    # Also count mixed ones
    mixed_count = 0
    for m in re.finditer(r'meaning_zh:\s*"([^"]*)"', final):
        val = m.group(1)
        if has_english(val) and is_chinese(val):
            mixed_count += 1

    chinese_count = total - english_count - mixed_count

    print(f"=== Third Pass Translation Results ===")
    print(f"Meanings fixed: {stats['meaning_fixed']}")
    print(f"Examples fixed: {stats['example_fixed']}")
    print(f"Still English/mixed: {stats['still_english']}")
    print(f"Total words: {total}")
    print(f"Pure Chinese: {chinese_count}")
    print(f"Still has English: {english_count + mixed_count}")
    print(f"Chinese coverage: {chinese_count/total*100:.1f}%")
    print("DONE!")

if __name__ == '__main__':
    main()
