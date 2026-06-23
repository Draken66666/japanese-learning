#!/usr/bin/env python3
"""
Generate comprehensive vocabulary-data.js from JLPT vocabulary JSON files.
Uses curated Chinese translation dictionary + existing data.
"""

import json
import os
import re
import sys
from collections import Counter

# ============================================================
# Curated English-to-Chinese translation dictionary
# Covers common JLPT vocabulary meanings
# ============================================================
EN_ZH_DICT = {
    # Common verbs
    "to go": "去", "to come": "来", "to eat": "吃", "to drink": "喝", "to see": "看",
    "to watch": "观看", "to look": "看", "to listen": "听", "to hear": "听到",
    "to speak": "说", "to talk": "谈话", "to say": "说", "to tell": "告诉",
    "to read": "读", "to write": "写", "to buy": "买", "to sell": "卖",
    "to make": "做", "to do": "做", "to work": "工作", "to study": "学习",
    "to teach": "教", "to learn": "学", "to understand": "理解", "to know": "知道",
    "to think": "想", "to feel": "感觉", "to remember": "记住", "to forget": "忘记",
    "to open": "打开", "to close": "关闭", "to put": "放", "to take": "拿",
    "to give": "给", "to receive": "收到", "to send": "发送", "to bring": "带来",
    "to use": "使用", "to make/do": "做", "to begin": "开始", "to start": "开始",
    "to end": "结束", "to finish": "完成", "to stop": "停止", "to continue": "继续",
    "to change": "改变", "to become": "变成", "to happen": "发生", "to exist": "存在",
    "to live": "生活", "to die": "死", "to grow": "成长", "to increase": "增加",
    "to decrease": "减少", "to rise": "上升", "to fall": "落下", "to stand": "站",
    "to sit": "坐", "to lie down": "躺下", "to walk": "走", "to run": "跑",
    "to fly": "飞", "to swim": "游泳", "to drive": "驾驶", "to ride": "骑",
    "to return": "返回", "to enter": "进入", "to exit": "退出", "to arrive": "到达",
    "to leave": "离开", "to stay": "停留", "to move": "移动", "to carry": "搬运",
    "to hold": "拿", "to touch": "触摸", "to push": "推", "to pull": "拉",
    "to throw": "扔", "to catch": "接", "to break": "打破", "to fix": "修理",
    "to build": "建造", "to destroy": "破坏", "to cut": "切", "to tear": "撕",
    "to burn": "烧", "to boil": "煮", "to cook": "做饭", "to wash": "洗",
    "to clean": "清洁", "to wipe": "擦", "to wear": "穿", "to put on": "穿上",
    "to take off": "脱下", "to sleep": "睡", "to wake up": "醒来", "to rest": "休息",
    "to wait": "等", "to hurry": "赶", "to be late": "迟到", "to meet": "见面",
    "to visit": "拜访", "to invite": "邀请", "to welcome": "欢迎", "to answer": "回答",
    "to ask": "问", "to request": "请求", "to refuse": "拒绝", "to accept": "接受",
    "to agree": "同意", "to disagree": "不同意", "to choose": "选择", "to decide": "决定",
    "to try": "尝试", "to test": "测试", "to check": "检查", "to examine": "检查",
    "to help": "帮助", "to save": "救", "to protect": "保护", "to attack": "攻击",
    "to defend": "防御", "to fight": "战斗", "to win": "赢", "to lose": "输",
    "to play": "玩", "to sing": "唱", "to dance": "跳舞", "to laugh": "笑",
    "to cry": "哭", "to smile": "微笑", "to shout": "喊", "to whisper": "低语",
    "to borrow": "借", "to lend": "借出", "to owe": "欠", "to pay": "支付",
    "to cost": "花费", "to earn": "赚", "to spend": "花费", "to save money": "存钱",
    "to trade": "交易", "to exchange": "交换", "to compare": "比较", "to match": "匹配",
    "to gather": "聚集", "to scatter": "散开", "to join": "加入", "to separate": "分开",
    "to connect": "连接", "to divide": "分割", "to share": "分享", "to compete": "竞争",
    "to marry": "结婚", "to divorce": "离婚", "to be born": "出生", "to raise": "养育",
    "to guide": "引导", "to lead": "带领", "to follow": "跟随", "to obey": "服从",
    "to rule": "统治", "to control": "控制", "to manage": "管理", "to organize": "组织",
    "to plan": "计划", "to prepare": "准备", "to arrange": "安排", "to order": "订购",
    "to book": "预订", "to reserve": "预约", "to cancel": "取消", "to delay": "推迟",
    "to hurry up": "快点", "to relax": "放松", "to enjoy": "享受", "to suffer": "受苦",
    "to worry": "担心", "to fear": "害怕", "to hope": "希望", "to wish": "祝愿",
    "to desire": "渴望", "to need": "需要", "to want": "想要", "to like": "喜欢",
    "to love": "爱", "to hate": "讨厌", "to prefer": "更喜欢", "to miss": "想念",
    # Common adjectives
    "good": "好", "bad": "坏", "big": "大", "small": "小", "new": "新", "old": "旧",
    "high": "高", "low": "低", "tall": "高", "short": "矮", "long": "长", "wide": "宽",
    "narrow": "窄", "deep": "深", "shallow": "浅", "thick": "厚", "thin": "薄",
    "heavy": "重", "light": "轻", "hard": "硬", "soft": "软", "sharp": "锋利",
    "dull": "钝", "smooth": "光滑", "rough": "粗糙", "round": "圆", "square": "方",
    "straight": "直", "curved": "弯", "flat": "平", "empty": "空", "full": "满",
    "open": "开", "closed": "关", "bright": "明亮", "dark": "暗", "clear": "清楚",
    "cloudy": "多云", "sunny": "晴朗", "hot": "热", "cold": "冷", "warm": "温暖",
    "cool": "凉爽", "dry": "干", "wet": "湿", "clean": "干净", "dirty": "脏",
    "beautiful": "美丽", "ugly": "丑陋", "pretty": "漂亮", "cute": "可爱",
    "handsome": "英俊", "fast": "快", "slow": "慢", "quick": "迅速", "early": "早",
    "late": "晚", "young": "年轻", "old (age)": "老", "strong": "强", "weak": "弱",
    "healthy": "健康", "sick": "生病", "safe": "安全", "dangerous": "危险",
    "easy": "容易", "difficult": "难", "simple": "简单", "complex": "复杂",
    "important": "重要", "unimportant": "不重要", "necessary": "必要", "unnecessary": "不必要",
    "possible": "可能", "impossible": "不可能", "certain": "确定", "uncertain": "不确定",
    "true": "真", "false": "假", "real": "真实", "fake": "假", "right": "对",
    "wrong": "错", "correct": "正确", "incorrect": "不正确", "same": "相同",
    "different": "不同", "similar": "相似", "equal": "相等", "fair": "公平",
    "unfair": "不公平", "free": "免费", "expensive": "贵", "cheap": "便宜",
    "rich": "富", "poor": "穷", "happy": "快乐", "sad": "悲伤", "angry": "生气",
    "lonely": "孤独", "bored": "无聊", "excited": "兴奋", "calm": "冷静",
    "nervous": "紧张", "surprised": "惊讶", "scared": "害怕", "tired": "累",
    "energetic": "精力充沛", "busy": "忙", "free (time)": "空闲", "ready": "准备好",
    "unready": "未准备", "complete": "完整", "incomplete": "不完整", "perfect": "完美",
    "imperfect": "不完美", "fresh": "新鲜", "stale": "不新鲜", "sweet": "甜",
    "sour": "酸", "spicy": "辣", "salty": "咸", "bitter": "苦", "delicious": "好吃",
    "tasty": "美味", "tasteless": "无味", "noisy": "吵", "quiet": "安静",
    "loud": "大声", "soft (sound)": "轻声", "comfortable": "舒适", "uncomfortable": "不舒服",
    "convenient": "方便", "inconvenient": "不方便", "useful": "有用", "useless": "无用",
    "interesting": "有趣", "boring": "无聊", "fun": "有趣", "funny": "好笑",
    "serious": "严肃", "silly": "傻", "smart": "聪明", "stupid": "笨",
    "wise": "明智", "foolish": "愚蠢", "kind": "亲切", "cruel": "残忍",
    "gentle": "温柔", "strict": "严格", "polite": "礼貌", "rude": "粗鲁",
    "honest": "诚实", "dishonest": "不诚实", "brave": "勇敢", "cowardly": "胆小",
    "lazy": "懒惰", "diligent": "勤奋", "careful": "小心", "careless": "粗心",
    "patient": "耐心", "impatient": "不耐烦", "generous": "慷慨", "selfish": "自私",
    "humble": "谦虚", "proud": "骄傲", "shy": "害羞", "confident": "自信",
    "lucky": "幸运", "unlucky": "不幸", "famous": "有名", "unknown": "无名",
    "popular": "受欢迎", "unpopular": "不受欢迎", "common": "常见", "rare": "稀有",
    "normal": "正常", "strange": "奇怪", "usual": "通常", "unusual": "不寻常",
    "ordinary": "普通", "special": "特别", "typical": "典型", "atypical": "非典型",
    "natural": "自然", "artificial": "人工", "raw": "生", "cooked": "熟",
    "ripe": "熟", "unripe": "未熟", "alive": "活着", "dead": "死",
    "awake": "醒着", "asleep": "睡着", "present": "出席", "absent": "缺席",
    "available": "可用", "unavailable": "不可用", "visible": "可见", "invisible": "不可见",
    "audible": "可听", "inaudible": "不可听", "acceptable": "可接受", "unacceptable": "不可接受",
    "enjoyable": "令人愉快", "reliable": "可靠", "unreliable": "不可靠", "flexible": "灵活",
    "stiff": "僵硬", "stable": "稳定", "unstable": "不稳定", "steady": "稳定",
    # Common nouns
    "person": "人", "people": "人们", "man": "男人", "woman": "女人", "child": "孩子",
    "boy": "男孩", "girl": "女孩", "baby": "婴儿", "friend": "朋友", "family": "家庭",
    "father": "父亲", "mother": "母亲", "brother": "兄弟", "sister": "姐妹",
    "son": "儿子", "daughter": "女儿", "husband": "丈夫", "wife": "妻子",
    "parent": "父母", "grandfather": "祖父", "grandmother": "祖母", "uncle": "叔伯",
    "aunt": "阿姨", "cousin": "堂表亲", "teacher": "老师", "student": "学生",
    "doctor": "医生", "nurse": "护士", "lawyer": "律师", "engineer": "工程师",
    "worker": "工人", "farmer": "农民", "chef": "厨师", "driver": "司机",
    "soldier": "士兵", "police": "警察", "artist": "艺术家", "musician": "音乐家",
    "writer": "作家", "actor": "演员", "scientist": "科学家", "businessman": "商人",
    "guest": "客人", "host": "主人", "neighbor": "邻居", "stranger": "陌生人",
    "king": "国王", "queen": "女王", "president": "总统", "leader": "领导者",
    "enemy": "敌人", "ally": "盟友", "partner": "伙伴", "rival": "对手",
    "name": "名字", "age": "年龄", "birthday": "生日", "life": "生活", "death": "死亡",
    "health": "健康", "body": "身体", "head": "头", "face": "脸", "eye": "眼睛",
    "ear": "耳朵", "nose": "鼻子", "mouth": "嘴", "tooth": "牙齿", "tongue": "舌头",
    "hand": "手", "foot": "脚", "arm": "手臂", "leg": "腿", "finger": "手指",
    "heart": "心", "blood": "血", "skin": "皮肤", "hair": "头发", "brain": "大脑",
    "stomach": "胃", "back": "背", "neck": "脖子", "shoulder": "肩膀", "chest": "胸",
    "food": "食物", "rice": "米饭", "bread": "面包", "meat": "肉", "fish": "鱼",
    "vegetable": "蔬菜", "fruit": "水果", "egg": "鸡蛋", "milk": "牛奶", "tea": "茶",
    "coffee": "咖啡", "water": "水", "juice": "果汁", "wine": "酒", "beer": "啤酒",
    "salt": "盐", "sugar": "糖", "oil": "油", "soup": "汤", "noodle": "面条",
    "cake": "蛋糕", "candy": "糖果", "ice cream": "冰淇淋", "snack": "零食",
    "breakfast": "早饭", "lunch": "午饭", "dinner": "晚饭", "meal": "餐",
    "house": "房子", "home": "家", "room": "房间", "kitchen": "厨房", "bathroom": "浴室",
    "bedroom": "卧室", "living room": "客厅", "door": "门", "window": "窗", "wall": "墙",
    "floor": "地板", "ceiling": "天花板", "roof": "屋顶", "garden": "花园", "yard": "院子",
    "table": "桌子", "chair": "椅子", "bed": "床", "sofa": "沙发", "desk": "书桌",
    "shelf": "架子", "drawer": "抽屉", "mirror": "镜子", "clock": "时钟", "lamp": "灯",
    "telephone": "电话", "computer": "电脑", "television": "电视", "radio": "收音机",
    "camera": "相机", "book": "书", "newspaper": "报纸", "magazine": "杂志", "letter": "信",
    "pen": "笔", "pencil": "铅笔", "paper": "纸", "notebook": "笔记本", "bag": "包",
    "wallet": "钱包", "key": "钥匙", "umbrella": "伞", "glasses": "眼镜", "watch": "手表",
    "clothes": "衣服", "shirt": "衬衫", "pants": "裤子", "skirt": "裙子", "dress": "连衣裙",
    "shoe": "鞋", "sock": "袜子", "hat": "帽子", "coat": "外套", "jacket": "夹克",
    "glove": "手套", "scarf": "围巾", "tie": "领带", "uniform": "制服", "suit": "西装",
    "car": "汽车", "bicycle": "自行车", "train": "火车", "bus": "公交车", "airplane": "飞机",
    "ship": "船", "boat": "小船", "taxi": "出租车", "truck": "卡车", "motorcycle": "摩托车",
    "road": "路", "street": "街道", "bridge": "桥", "station": "车站", "airport": "机场",
    "port": "港口", "park": "公园", "school": "学校", "hospital": "医院", "bank": "银行",
    "post office": "邮局", "store": "商店", "shop": "店", "restaurant": "餐厅",
    "hotel": "酒店", "library": "图书馆", "museum": "博物馆", "church": "教堂",
    "temple": "寺庙", "factory": "工厂", "office": "办公室", "company": "公司",
    "university": "大学", "city": "城市", "town": "镇", "village": "村庄", "country": "国家",
    "world": "世界", "earth": "地球", "sky": "天空", "sea": "海", "mountain": "山",
    "river": "河", "lake": "湖", "forest": "森林", "field": "田野", "island": "岛",
    "beach": "海滩", "desert": "沙漠", "valley": "山谷", "hill": "小山", "cliff": "悬崖",
    "sun": "太阳", "moon": "月亮", "star": "星星", "cloud": "云", "rain": "雨",
    "snow": "雪", "wind": "风", "storm": "暴风雨", "thunder": "雷", "lightning": "闪电",
    "fog": "雾", "ice": "冰", "fire": "火", "smoke": "烟", "dust": "灰尘",
    "stone": "石头", "rock": "岩石", "sand": "沙", "mud": "泥", "metal": "金属",
    "gold": "金", "silver": "银", "iron": "铁", "copper": "铜", "wood": "木",
    "tree": "树", "flower": "花", "grass": "草", "leaf": "叶子", "root": "根",
    "seed": "种子", "branch": "树枝", "fruit (botany)": "果实", "animal": "动物",
    "dog": "狗", "cat": "猫", "bird": "鸟", "horse": "马", "cow": "牛",
    "pig": "猪", "sheep": "羊", "chicken": "鸡", "duck": "鸭", "rabbit": "兔子",
    "mouse": "老鼠", "lion": "狮子", "tiger": "老虎", "bear": "熊", "elephant": "大象",
    "monkey": "猴子", "snake": "蛇", "frog": "青蛙", "insect": "昆虫", "bee": "蜜蜂",
    "butterfly": "蝴蝶", "spider": "蜘蛛", "fly": "苍蝇", "mosquito": "蚊子",
    "time": "时间", "day": "天", "night": "夜", "morning": "早上", "evening": "晚上",
    "afternoon": "下午", "today": "今天", "tomorrow": "明天", "yesterday": "昨天",
    "week": "周", "month": "月", "year": "年", "hour": "小时", "minute": "分钟",
    "second": "秒", "season": "季节", "spring": "春天", "summer": "夏天",
    "autumn": "秋天", "winter": "冬天", "holiday": "假日", "weekend": "周末",
    "birthday": "生日", "date": "日期", "now": "现在", "past": "过去", "future": "未来",
    "present": "现在", "moment": "瞬间", "century": "世纪", "decade": "十年",
    "money": "钱", "price": "价格", "cost": "费用", "tax": "税", "salary": "工资",
    "bill": "账单", "receipt": "收据", "cash": "现金", "check": "支票", "card": "卡",
    "credit card": "信用卡", "bank account": "银行账户", "interest": "利息", "loan": "贷款",
    "debt": "债务", "investment": "投资", "profit": "利润", "loss": "亏损",
    "business": "生意", "trade": "贸易", "market": "市场", "shop": "商店",
    "sale": "销售", "discount": "折扣", "advertisement": "广告", "product": "产品",
    "service": "服务", "customer": "顾客", "order": "订单", "delivery": "配送",
    "color": "颜色", "red": "红", "blue": "蓝", "green": "绿", "yellow": "黄",
    "black": "黑", "white": "白", "brown": "棕", "purple": "紫", "pink": "粉红",
    "orange (color)": "橙色", "gray": "灰", "gold (color)": "金色", "silver (color)": "银色",
    "number": "数字", "one": "一", "two": "二", "three": "三", "four": "四",
    "five": "五", "six": "六", "seven": "七", "eight": "八", "nine": "九",
    "ten": "十", "hundred": "百", "thousand": "千", "ten thousand": "万",
    "million": "百万", "first": "第一", "second (ordinal)": "第二", "third": "第三",
    "half": "半", "double": "双倍", "zero": "零",
    "language": "语言", "word": "词", "sentence": "句子", "letter (alphabet)": "字母",
    "sound": "声音", "voice": "声音", "noise": "噪音", "music": "音乐", "song": "歌曲",
    "story": "故事", "news": "新闻", "information": "信息", "knowledge": "知识",
    "idea": "想法", "thought": "思想", "question": "问题", "answer": "答案",
    "problem": "问题", "solution": "解决方案", "reason": "原因", "result": "结果",
    "cause": "原因", "effect": "效果", "purpose": "目的", "goal": "目标",
    "plan": "计划", "dream": "梦想", "hope": "希望", "wish": "愿望",
    "love": "爱", "hate": "恨", "anger": "愤怒", "joy": "喜悦", "sadness": "悲伤",
    "fear": "恐惧", "courage": "勇气", "luck": "运气", "fate": "命运",
    "nature": "自然", "environment": "环境", "weather": "天气", "temperature": "温度",
    "energy": "能量", "power": "力量", "strength": "强度", "weakness": "弱点",
    "beauty": "美", "truth": "真理", "lie": "谎言", "secret": "秘密",
    "rule": "规则", "law": "法律", "right (legal)": "权利", "duty": "义务",
    "freedom": "自由", "justice": "正义", "peace": "和平", "war": "战争",
    "victory": "胜利", "defeat": "失败", "history": "历史", "culture": "文化",
    "art": "艺术", "science": "科学", "technology": "技术", "religion": "宗教",
    "philosophy": "哲学", "education": "教育", "politics": "政治", "economy": "经济",
    "society": "社会", "community": "社区", "tradition": "传统", "custom": "习俗",
    "habit": "习惯", "manner": "礼貌", "respect": "尊重", "honor": "荣誉",
    "shame": "耻辱", "pride": "骄傲", "guilt": "罪过", "innocence": "无辜",
    "memory": "记忆", "experience": "经验", "skill": "技能", "talent": "才能",
    "ability": "能力", "effort": "努力", "patience": "耐心", "wisdom": "智慧",
    "stupidity": "愚蠢", "kindness": "善良", "cruelty": "残忍", "honesty": "诚实",
    "faith": "信仰", "trust": "信任", "doubt": "怀疑", "belief": "信念",
    "opinion": "意见", "view": "观点", "perspective": "视角", "attitude": "态度",
    "feeling": "感觉", "emotion": "情感", "sensation": "感觉", "instinct": "本能",
    "consciousness": "意识", "mind": "心灵", "soul": "灵魂", "spirit": "精神",
    "matter": "物质", "material": "材料", "substance": "物质", "element": "元素",
    "quality": "质量", "quantity": "数量", "size": "大小", "shape": "形状",
    "weight": "重量", "height": "高度", "width": "宽度", "depth": "深度",
    "length": "长度", "distance": "距离", "direction": "方向", "position": "位置",
    "location": "位置", "place": "地方", "space": "空间", "area": "区域",
    "volume": "体积", "level": "水平", "degree": "程度", "extent": "范围",
    "limit": "限制", "border": "边界", "edge": "边缘", "center": "中心",
    "middle": "中间", "side": "旁边", "front": "前面", "back": "后面",
    "left": "左", "right (direction)": "右", "top": "顶部", "bottom": "底部",
    "inside": "里面", "outside": "外面", "up": "上", "down": "下",
    "north": "北", "south": "南", "east": "东", "west": "西",
    "work": "工作", "job": "职业", "career": "事业", "profession": "专业",
    "task": "任务", "duty": "职责", "role": "角色", "function": "功能",
    "meeting": "会议", "conference": "大会", "lecture": "讲座", "lesson": "课程",
    "class": "班级", "course": "课程", "subject": "科目", "test": "考试",
    "exam": "考试", "grade": "成绩", "score": "分数", "homework": "作业",
    "report": "报告", "essay": "论文", "document": "文件", "file": "文件",
    "data": "数据", "record": "记录", "list": "列表", "schedule": "日程",
    "calendar": "日历", "map": "地图", "sign": "标志", "label": "标签",
    "ticket": "票", "passport": "护照", "visa": "签证", "license": "执照",
    "permission": "许可", "approval": "批准", "agreement": "协议", "contract": "合同",
    "treaty": "条约", "promise": "承诺", "oath": "誓言", "vow": "誓约",
    "game": "游戏", "sport": "运动", "match": "比赛", "race": "赛跑",
    "team": "团队", "player": "选手", "coach": "教练", "fan": "粉丝",
    "prize": "奖品", "medal": "奖牌", "trophy": "奖杯", "champion": "冠军",
    "music": "音乐", "movie": "电影", "film": "影片", "play": "戏剧",
    "dance": "舞蹈", "painting": "绘画", "photo": "照片", "picture": "图片",
    "drawing": "图画", "design": "设计", "pattern": "图案", "style": "风格",
    "fashion": "时尚", "trend": "趋势", "mode": "模式", "method": "方法",
    "way": "方式", "process": "过程", "step": "步骤", "stage": "阶段",
    "phase": "阶段", "period": "时期", "era": "时代", "epoch": "纪元",
    "event": "事件", "incident": "事故", "accident": "意外", "disaster": "灾难",
    "crisis": "危机", "emergency": "紧急", "danger": "危险", "risk": "风险",
    "threat": "威胁", "warning": "警告", "alarm": "警报", "signal": "信号",
    "message": "消息", "letter": "信", "email": "邮件", "call": "电话",
    "conversation": "对话", "discussion": "讨论", "debate": "辩论", "argument": "争论",
    "fight": "打架", "conflict": "冲突", "quarrel": "口角", "dispute": "争执",
    "agreement": "同意", "compromise": "妥协", "settlement": "解决", "resolution": "决议",
    # Greetings and expressions
    "thank you": "谢谢", "thanks": "感谢", "hello": "你好", "goodbye": "再见",
    "good morning": "早上好", "good afternoon": "下午好", "good evening": "晚上好",
    "good night": "晚安", "sorry": "对不起", "excuse me": "打扰了", "please": "请",
    "yes": "是", "no": "不", "maybe": "也许", "ok": "好的", "okay": "好的",
    "welcome": "欢迎", "congratulations": "恭喜", "cheers": "干杯",
    "of course": "当然", "not at all": "一点也不", "never mind": "没关系",
    # Common adverbs
    "very": "非常", "quite": "相当", "rather": "相当", "too": "太", "so": "如此",
    "really": "真的", "truly": "真正地", "certainly": "当然", "surely": "一定",
    "probably": "大概", "possibly": "可能", "perhaps": "也许", "maybe": "也许",
    "always": "总是", "usually": "通常", "often": "经常", "sometimes": "有时",
    "rarely": "很少", "never": "从不", "again": "再次", "still": "仍然",
    "yet": "还", "already": "已经", "just": "刚刚", "now": "现在",
    "then": "那时", "soon": "很快", "later": "后来", "immediately": "立即",
    "suddenly": "突然", "gradually": "逐渐", "finally": "最后", "eventually": "最终",
    "recently": "最近", "lately": "近来", "currently": "当前", "previously": "以前",
    "before": "之前", "after": "之后", "during": "期间", "while": "当",
    "since": "自从", "until": "直到", "up to": "多达", "about": "关于",
    "almost": "几乎", "nearly": "将近", "hardly": "几乎不", "barely": "勉强",
    "especially": "特别地", "particularly": "特别", "specifically": "具体地",
    "generally": "一般地", "mainly": "主要地", "mostly": "大部分", "largely": "很大程度上",
    "together": "一起", "separately": "分别地", "alone": "独自", "instead": "代替",
    "however": "然而", "therefore": "因此", "moreover": "此外", "furthermore": "而且",
    "besides": "此外", "otherwise": "否则", "meanwhile": "同时", "anyway": "总之",
    "anyhow": "无论如何", "somehow": "以某种方式", "somewhat": "有点", "anywhere": "任何地方",
    "somewhere": "某处", "nowhere": "无处", "everywhere": "到处",
    "forward": "向前", "backward": "向后", "upward": "向上", "downward": "向下",
    "inside": "里面", "outside": "外面", "upstairs": "楼上", "downstairs": "楼下",
    "abroad": "国外", "home": "家", "away": "离开", "back": "回来",
    # Common concepts
    "thing": "东西", "object": "物体", "item": "物品", "article": "物品",
    "part": "部分", "piece": "块", "section": "部分", "portion": "份",
    "whole": "整体", "total": "总计", "all": "全部", "every": "每个",
    "each": "每个", "some": "一些", "any": "任何", "many": "许多",
    "much": "很多", "few": "少", "little": "少", "several": "几个",
    "various": "各种", "different": "不同", "same": "相同", "similar": "相似",
    "such": "这种", "certain": "某个", "particular": "特定", "specific": "具体",
    "this": "这个", "that": "那个", "these": "这些", "those": "那些",
    "I": "我", "you": "你", "he": "他", "she": "她", "it": "它",
    "we": "我们", "they": "他们", "my": "我的", "your": "你的", "his": "他的",
    "her": "她的", "its": "它的", "our": "我们的", "their": "他们的",
    "myself": "我自己", "yourself": "你自己", "himself": "他自己", "herself": "她自己",
    "itself": "它自己", "ourselves": "我们自己", "themselves": "他们自己",
    "who": "谁", "what": "什么", "when": "什么时候", "where": "哪里", "why": "为什么",
    "how": "怎么", "which": "哪个", "whose": "谁的",
    "father": "父亲", "mother": "母亲", "parent": "父母", "sibling": "兄弟姐妹",
    "grandparent": "祖父母", "grandchild": "孙辈", "relative": "亲戚",
    "morning": "早上", "noon": "中午", "afternoon": "下午", "evening": "傍晚",
    "night": "夜晚", "midnight": "午夜", "dawn": "黎明", "dusk": "黄昏",
    "Sunday": "星期日", "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
    "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六",
    "January": "一月", "February": "二月", "March": "三月", "April": "四月",
    "May": "五月", "June": "六月", "July": "七月", "August": "八月",
    "September": "九月", "October": "十月", "November": "十一月", "December": "十二月",
    "spring": "春天", "summer": "夏天", "autumn": "秋天", "fall": "秋天", "winter": "冬天",
    # Common phrases
    "good luck": "祝好运", "take care": "保重", "see you": "再见", "pardon": "原谅",
    "thank you very much": "非常感谢", "you're welcome": "不客气", "no problem": "没问题",
    "that's right": "没错", "I see": "我明白了", "I understand": "我理解",
    "I don't know": "我不知道", "I think so": "我这样认为", "I don't think so": "我不这样认为",
    "is that so": "是吗", "really?": "真的吗", "what?": "什么", "why?": "为什么",
    "how much": "多少钱", "how many": "多少", "how old": "多大",
    "what time": "几点", "what day": "星期几", "what kind": "哪种",
    # Additional common words
    "every day": "每天", "every morning": "每天早上", "every night": "每天晚上",
    "every week": "每周", "every month": "每月", "every year": "每年",
    "this morning": "今天早上", "this evening": "今天晚上", "this week": "这周",
    "this month": "这个月", "this year": "今年", "next week": "下周",
    "next month": "下个月", "next year": "明年", "last week": "上周",
    "last month": "上个月", "last year": "去年",
    "east": "东", "west": "西", "north": "北", "south": "南",
    "left": "左", "right": "右", "center": "中心", "middle": "中间",
    "front": "前", "back": "后", "side": "旁边", "top": "上",
    "bottom": "下", "inside": "内", "outside": "外",
    "problem": "问题", "question": "问题", "answer": "回答", "reply": "回复",
    "question (polite)": "问题", "matter": "事情", "affair": "事务",
    "business": "生意", "company": "公司", "store": "店", "shop": "商店",
    "school": "学校", "class": "课", "lesson": "课", "study": "学习",
    "research": "研究", "experiment": "实验", "theory": "理论", "practice": "实践",
    "fact": "事实", "truth": "真相", "lie": "谎言", "secret": "秘密",
    "dream": "梦", "wish": "愿望", "desire": "欲望", "hope": "希望",
    "plan": "计划", "project": "项目", "program": "程序", "system": "系统",
    "method": "方法", "way": "方法", "means": "手段", "technique": "技术",
    "skill": "技能", "ability": "能力", "power": "力", "force": "力量",
    "strength": "强度", "weakness": "弱点", "advantage": "优势", "disadvantage": "劣势",
    "benefit": "利益", "harm": "害处", "good": "好", "bad": "坏",
    "right": "对", "wrong": "错", "true": "真", "false": "假",
    "real": "真实", "fake": "假", "genuine": "真正", "artificial": "人工",
    "natural": "自然", "normal": "正常", "strange": "奇怪", "weird": "怪异",
    "common": "普通", "special": "特别", "unusual": "不寻常", "rare": "稀有",
    "frequent": "频繁", "occasional": "偶尔", "regular": "定期", "irregular": "不规则",
    "public": "公共", "private": "私人", "official": "正式", "informal": "非正式",
    "formal": "正式", "casual": "随便", "professional": "专业", "amateur": "业余",
    "personal": "个人", "general": "一般", "specific": "具体", "particular": "特定",
    "individual": "个人", "group": "群体", "team": "团队", "organization": "组织",
    "society": "社会", "community": "社区", "nation": "国家", "world": "世界",
    "international": "国际", "national": "国家", "local": "本地", "regional": "地区",
    "domestic": "国内", "foreign": "外国", "traditional": "传统", "modern": "现代",
    "ancient": "古代", "old": "旧", "new": "新", "current": "当前",
    "past": "过去", "future": "未来", "present": "现在", "recent": "最近",
    "old-fashioned": "老式", "up-to-date": "最新", "outdated": "过时",
    "warm": "温暖", "cool": "凉", "mild": "温和", "severe": "严重",
    "gentle": "温柔", "rough": "粗", "smooth": "光滑", "sharp": "锋利",
    "dull": "钝", "flat": "平", "round": "圆", "square": "方",
    "straight": "直", "curved": "曲", "bent": "弯", "broken": "破",
    "complete": "完全", "incomplete": "不完全", "whole": "整个", "partial": "部分",
    "full": "满", "empty": "空", "solid": "固体", "liquid": "液体",
    "gas": "气体", "wet": "湿", "dry": "干", "clean": "干净",
    "dirty": "脏", "neat": "整洁", "messy": "凌乱",
    "heavy": "重", "light": "轻", "thick": "厚", "thin": "薄",
    "deep": "深", "shallow": "浅", "high": "高", "low": "低",
    "wide": "宽", "narrow": "窄", "broad": "宽", "vast": "广阔",
    "huge": "巨大", "tiny": "微小", "enormous": "庞大", "minute": "微小",
    "grand": "宏伟", "humble": "简陋", "magnificent": "壮丽", "plain": "朴素",
    "fancy": "华丽", "simple": "简单", "complex": "复杂", "complicated": "复杂",
    "easy": "容易", "difficult": "困难", "hard": "难", "soft": "软",
    "tough": "坚韧", "fragile": "易碎", "strong": "强", "weak": "弱",
    "powerful": "强大", "feeble": "虚弱", "healthy": "健康", "sick": "生病",
    "ill": "病", "well": "好", "fine": "好", "poor": "差",
    "rich": "富有", "wealthy": "富裕", "poor": "贫穷", "needy": "贫困",
    "expensive": "贵", "costly": "昂贵", "cheap": "便宜", "inexpensive": "不贵",
    "free": "免费", "priceless": "无价", "valuable": "有价值", "worthless": "无价值",
    "useful": "有用", "helpful": "有帮助", "useless": "无用", "harmful": "有害",
    "safe": "安全", "dangerous": "危险", "risky": "冒险", "secure": "安全",
    "certain": "确定", "sure": "确信", "uncertain": "不确定", "doubtful": "可疑",
    "clear": "清楚", "obvious": "明显", "vague": "模糊", "unclear": "不清楚",
    "bright": "明亮", "dark": "暗", "dim": "昏暗", "light": "轻",
    "fast": "快", "quick": "快速", "rapid": "迅速", "swift": "敏捷",
    "slow": "慢", "sluggish": "缓慢", "lazy": "懒", "diligent": "勤奋",
    "active": "活跃", "passive": "被动", "busy": "忙", "idle": "闲",
    "early": "早", "late": "晚", "on time": "准时", "delayed": "延误",
    # More words
    "cat": "猫", "dog": "狗", "bird": "鸟", "horse": "马", "cow": "牛",
    "pig": "猪", "sheep": "羊", "chicken": "鸡", "fish": "鱼", "insect": "虫",
    "tree": "树", "flower": "花", "grass": "草", "leaf": "叶", "root": "根",
    "seed": "种子", "fruit": "水果", "vegetable": "蔬菜", "mushroom": "蘑菇",
    "mountain": "山", "river": "河", "lake": "湖", "sea": "海", "ocean": "洋",
    "island": "岛", "forest": "森林", "desert": "沙漠", "valley": "山谷",
    "waterfall": "瀑布", "cave": "洞", "cliff": "悬崖", "beach": "海滩",
    "shore": "岸", "coast": "海岸", "harbor": "港", "bay": "海湾",
    "sun": "太阳", "moon": "月亮", "star": "星", "planet": "行星",
    "earth": "地球", "world": "世界", "universe": "宇宙", "space": "太空",
    "sky": "天空", "cloud": "云", "rain": "雨", "snow": "雪", "ice": "冰",
    "wind": "风", "storm": "暴风雨", "fog": "雾", "mist": "薄雾",
    "fire": "火", "flame": "火焰", "smoke": "烟", "ash": "灰",
    "dust": "灰尘", "dirt": "泥土", "mud": "泥", "sand": "沙",
    "stone": "石头", "rock": "岩石", "metal": "金属", "iron": "铁",
    "steel": "钢", "copper": "铜", "gold": "金", "silver": "银",
    "glass": "玻璃", "plastic": "塑料", "rubber": "橡胶", "leather": "皮革",
    "cotton": "棉", "silk": "丝", "wool": "羊毛", "paper": "纸",
    "wood": "木", "board": "板", "stick": "棍", "rod": "杆",
    "string": "线", "rope": "绳", "wire": "金属线", "chain": "链条",
    "nail": "钉子", "screw": "螺丝", "bolt": "螺栓", "nut": "螺母",
    "tool": "工具", "hammer": "锤子", "saw": "锯", "knife": "刀",
    "scissors": "剪刀", "axe": "斧", "shovel": "铲", "rake": "耙",
    "needle": "针", "pin": "别针", "button": "纽扣", "zipper": "拉链",
    "lock": "锁", "key": "钥匙", "handle": "把手", "knob": "旋钮",
    "wheel": "轮", "gear": "齿轮", "engine": "引擎", "motor": "马达",
    "machine": "机器", "device": "设备", "instrument": "仪器", "equipment": "装备",
    "tool": "工具", "appliance": "家电", "furniture": "家具",
    # Body and health
    "body": "身体", "head": "头", "hair": "头发", "face": "脸", "forehead": "额头",
    "eye": "眼", "eyebrow": "眉毛", "eyelash": "睫毛", "ear": "耳朵", "nose": "鼻子",
    "mouth": "嘴", "lip": "嘴唇", "tooth": "牙", "tongue": "舌头", "chin": "下巴",
    "cheek": "脸颊", "neck": "脖子", "throat": "喉咙", "shoulder": "肩膀",
    "arm": "手臂", "elbow": "肘", "wrist": "手腕", "hand": "手", "finger": "手指",
    "thumb": "拇指", "nail": "指甲", "palm": "手掌", "chest": "胸", "back": "背",
    "stomach": "肚子", "waist": "腰", "hip": "臀部", "leg": "腿", "knee": "膝盖",
    "ankle": "脚踝", "foot": "脚", "toe": "脚趾", "heart": "心脏", "lung": "肺",
    "liver": "肝", "kidney": "肾", "stomach (organ)": "胃", "brain": "脑",
    "nerve": "神经", "muscle": "肌肉", "bone": "骨头", "joint": "关节",
    "skin": "皮肤", "blood": "血", "sweat": "汗", "tear": "眼泪",
    # Common actions
    "to sleep": "睡觉", "to rest": "休息", "to wake": "醒来", "to get up": "起床",
    "to lie": "躺", "to sit": "坐", "to stand": "站", "to walk": "走",
    "to run": "跑", "to jump": "跳", "to climb": "爬", "to fall": "摔倒",
    "to carry": "搬", "to push": "推", "to pull": "拉", "to throw": "扔",
    "to catch": "接", "to hold": "握", "to release": "释放", "to drop": "掉",
    "to lift": "举", "to lower": "降", "to raise": "升起", "to bend": "弯",
    "to straighten": "弄直", "to turn": "转", "to spin": "旋转", "to roll": "滚",
    "to slide": "滑", "to slip": "滑倒", "to crash": "撞", "to hit": "打",
    "to punch": "拳击", "to kick": "踢", "to slap": "拍", "to pat": "轻拍",
    "to stroke": "抚摸", "to grab": "抓", "to grip": "紧握", "to squeeze": "挤",
    "to pinch": "捏", "to bite": "咬", "to chew": "嚼", "to swallow": "吞",
    "to lick": "舔", "to breathe": "呼吸", "to cough": "咳嗽", "to sneeze": "打喷嚏",
    "to yawn": "打哈欠", "to hiccup": "打嗝", "to burp": "打嗝",
    "to smile": "微笑", "to laugh": "笑", "to cry": "哭", "to weep": "哭泣",
    "to sob": "抽泣", "to sigh": "叹气", "to groan": "呻吟", "to moan": "呻吟",
    "to scream": "尖叫", "to shout": "喊", "to yell": "大叫", "to whisper": "低语",
    "to murmur": "嘟囔", "to mumble": "含糊说", "to stutter": "结巴",
}

def translate_to_chinese(en_meaning):
    """Translate English meaning to Chinese using curated dictionary."""
    if not en_meaning:
        return ""

    en_lower = en_meaning.lower().strip()

    # Direct lookup
    if en_lower in EN_ZH_DICT:
        return EN_ZH_DICT[en_lower]

    # Try without articles
    for prefix in ['to ', 'a ', 'an ', 'the ']:
        if en_lower.startswith(prefix):
            stripped = en_lower[len(prefix):]
            if stripped in EN_ZH_DICT:
                return EN_ZH_DICT[stripped]

    # Try with "to " prefix for verbs
    if en_lower.startswith('to '):
        verb = en_lower[3:]
        if verb in EN_ZH_DICT:
            return EN_ZH_DICT[verb]

    # Try partial match - first word
    words = en_lower.split()
    if words and words[0] in EN_ZH_DICT:
        # Check if it's a compound meaning
        if len(words) <= 2:
            return EN_ZH_DICT[words[0]]

    # Try the whole phrase without punctuation
    clean = en_lower.rstrip('.,;!?')
    if clean in EN_ZH_DICT:
        return EN_ZH_DICT[clean]

    # No match found - return English as fallback
    return en_meaning


# Part of speech classification
def classify_pos(word, hiragana, meaning):
    """Classify part of speech based on word form and meaning."""
    # Check for particles
    particles = {'は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで', 'より', 'へ', 'も', 'か', 'や', 'の', 'ね', 'よ', 'ねえ', 'な', 'さ'}
    if word in particles:
        return '助词'

    # Check for conjunctions
    conjunctions = {'そして', 'しかし', 'でも', 'だから', 'それで', 'それに', 'また', 'または', 'それとも', 'けれど', 'けれども', 'だが', 'ただし', 'なお', 'さらに', 'そこで', 'つまり', 'すなわち', '一方', '他方', 'および', 'ならびに', 'また', '及び', '若しくは'}
    if word in conjunctions:
        return '接续词'

    # Check for pronouns
    pronouns = {'私', '僕', '俺', '彼', '彼女', 'これ', 'それ', 'あれ', 'どれ', 'ここ', 'そこ', 'あそこ', 'どこ', 'こちら', 'そちら', 'あちら', 'どちら', '何', '誰', 'いつ', '我々', '自分', '自身', '各自', '誰か', '何か', '此れ', '其れ', '何方', '此方', '其方', '彼方', '此処', '其処', '彼処', '何処', '此ちら', '其ちら'}
    if word in pronouns:
        return '代词'

    # Check for numbers
    number_kanji = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '億', '兆', '零', '〇'}
    if word and all(c in number_kanji for c in word if c.strip()):
        return '数字'

    # Check for verbs
    if word == 'する' or word.endswith('する'):
        return '动词'
    if word == 'くる' or word == '來る':
        return '动词'
    if meaning.lower().startswith('to '):
        return '动词'

    # Check for い-adjectives
    if hiragana.endswith('い') and len(hiragana) >= 2:
        non_adj = {'これ', 'それ', 'あれ', 'どれ', 'ここ', 'そこ', 'あそこ', 'どこ', 'こちら', 'そちら', 'あちら', 'どちら', 'いつ', 'いい', 'よい', 'かわいい', 'かっこいい', 'すごい', 'やばい', 'ちゃう', 'しまう', 'しまう', 'ほう', 'こう', 'そう', 'ああ', 'どう'}
        if word not in non_adj and hiragana not in non_adj:
            meaning_lower = meaning.lower()
            adj_keywords = ['wide', 'narrow', 'high', 'low', 'big', 'small', 'new', 'old', 'good', 'bad', 'hot', 'cold', 'fast', 'slow', 'bright', 'dark', 'heavy', 'light', 'thick', 'thin', 'deep', 'shallow', 'sweet', 'spicy', 'cheap', 'expensive', 'beautiful', 'ugly', 'strong', 'weak', 'young', 'noisy', 'quiet', 'sad', 'happy', 'lonely', 'scary', 'interesting', 'boring', 'difficult', 'easy', 'long', 'short', 'far', 'near', 'many', 'few', 'warm', 'cool', 'delicious', 'terrible', 'great', 'awful', 'wonderful', 'horrible', 'nice', 'mean', 'kind', 'cruel', 'gentle', 'strict', 'polite', 'rude', 'honest', 'brave', 'lazy', 'careful', 'careless', 'patient', 'generous', 'selfish', 'humble', 'proud', 'shy', 'confident', 'lucky', 'famous', 'popular', 'common', 'rare', 'normal', 'strange', 'ordinary', 'special', 'dangerous', 'safe', 'uncomfortable', 'comfortable', 'convenient', 'inconvenient', 'useful', 'useless', 'red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'purple', 'pink', 'gray', 'grey', 'orange', 'gold', 'silver', 'clever', 'smart', 'stupid', 'wise', 'foolish', 'silly', 'serious', 'funny', 'fun', 'fresh', 'stale', 'sour', 'bitter', 'salty', 'tasteless', 'tasty', 'loud', 'mild', 'severe', 'huge', 'tiny', 'grand', 'plain', 'fancy', 'tough', 'fragile', 'powerful', 'feeble', 'wealthy', 'needy', 'costly', 'priceless', 'valuable', 'worthless', 'helpful', 'harmful', 'risky', 'secure', 'uncertain', 'doubtful', 'obvious', 'vague', 'unclear', 'dim', 'rapid', 'swift', 'sluggish', 'active', 'passive', 'idle', 'amazing', 'awesome', 'terrible', 'dreadful', 'frightful', 'horrid', 'nasty', 'grumpy', 'gloomy', 'dizzy', 'drowsy', 'sleepy', 'hungry', 'thirsty', 'full', 'empty', 'sturdy', 'flimsy', 'rickety', 'steep', 'flat', 'round', 'square', 'straight', 'crooked', 'bent', 'broken', 'shallow', 'crisp', 'soggy', 'elastic', 'rigid', 'flexible', 'stiff', 'hollow', 'solid', 'dense', 'sparse', 'blurry', 'faint', 'vivid', 'pale', 'dull', 'vibrant', 'grimy', 'pristine', 'tarnished', 'rusty', 'shiny', 'glossy', 'matte', 'transparent', 'opaque', 'translucent']
            if any(kw in meaning_lower for kw in adj_keywords):
                return '形容词'
            if hiragana.endswith('しい') or hiragana.endswith('たい') or hiragana.endswith('ない'):
                return '形容词'

    # Check for adverbs
    adverbs = {'とても', 'かなり', 'ずっと', 'もっと', 'いつも', 'よく', 'ときどき', 'いろいろ', 'だんだん', 'どんどん', 'ますます', 'わざわざ', 'せっかく', 'やっと', 'ついに', 'とうとう', 'つい', 'すぐ', 'もう', 'まだ', 'また', 'きっと', 'たぶん', 'おそらく', 'もちろん', 'もし', 'いくら', 'どんなに', 'どうしても', '必ず', '絶対に', '全く', '完全に', '直接', '間接に', '特に', '主に', '専ら', '少し', 'ちょっと', 'たくさん', 'あまり', '十分', '足りない', '多分', '確か', '本当に', '実は', '実に', '割と', 'わりと', '比較的', '相當', '非常に', '極めて', '至極', '大変', '実に', '誠に', '恐らく', '或いは', '若しくは'}
    if word in adverbs:
        return '副词'
    if meaning.lower().endswith('ly'):
        return '副词'

    # Default: noun
    return '名词'


# Example sentences for common words
example_sentences = {
    '食べる': ('毎日朝ごはんを食べます。', '每天早上吃早饭。'),
    '飲む': ('水を飲みます。', '喝水。'),
    '行く': ('学校に行きます。', '去学校。'),
    '来る': ('友達が来ます。', '朋友来。'),
    '見る': ('テレビを見ます。', '看电视。'),
    '聞く': ('音楽を聞きます。', '听音乐。'),
    '話す': ('日本語を話します。', '说日语。'),
    '読む': ('本を読みます。', '读书。'),
    '書く': ('手紙を書きます。', '写信。'),
    '買う': ('本を買います。', '买书。'),
    'する': ('勉強をします。', '学习。'),
    'ある': ('机の上に本があります。', '桌子上有书。'),
    'いる': ('部屋に猫がいます。', '房间里有猫。'),
    '大きい': ('大きい家に住んでいます。', '住在大房子里。'),
    '小さい': ('小さい犬が好きです。', '喜欢小狗。'),
    '新しい': ('新しい車を買いました。', '买了新车。'),
    '古い': ('古い建物があります。', '有古老的建筑。'),
    '良い': ('良い天気ですね。', '天气真好啊。'),
    '悪い': ('天気が悪いです。', '天气不好。'),
    '高い': ('この山は高いです。', '这座山很高。'),
    '安い': ('このりんごは安いです。', '这个苹果很便宜。'),
    '面白い': ('この本は面白いです。', '这本书很有趣。'),
    '難しい': ('日本語は難しいです。', '日语很难。'),
    '易しい': ('この問題は易しいです。', '这个问题很简单。'),
    '楽しい': ('旅行は楽しいです。', '旅行很快乐。'),
    '美味しい': ('この料理は美味しいです。', '这道菜很好吃。'),
    '暑い': ('今日は暑いです。', '今天很热。'),
    '寒い': ('冬は寒いです。', '冬天很冷。'),
    '速い': ('新幹線は速いです。', '新干线很快。'),
    '遅い': ('電車が遅いです。', '电车很慢。'),
    '学生': ('私は学生です。', '我是学生。'),
    '先生': ('田中先生は先生です。', '田中先生是老师。'),
    '学校': ('学校は遠いです。', '学校很远。'),
    '日本語': ('日本語を勉強しています。', '在学日语。'),
    '友達': ('友達に会いました。', '见了朋友。'),
    '時間': ('時間がありません。', '没有时间。'),
    '今日': ('今日はいい天気です。', '今天天气好。'),
    '明日': ('明日学校に行きます。', '明天去学校。'),
    '昨日': ('昨日映画を見ました。', '昨天看了电影。'),
    '家': ('家に帰ります。', '回家。'),
    '水': ('水を飲んでください。', '请喝水。'),
    '本': ('本を読みます。', '读书。'),
    '車': ('車を運転します。', '开车。'),
    '電話': ('電話をかけます。', '打电话。'),
    '天気': ('天気がいいです。', '天气好。'),
    '仕事': ('仕事をしています。', '在工作。'),
    'お金': ('お金があります。', '有钱。'),
    '名前': ('名前は何ですか。', '叫什么名字？'),
}


def main():
    # Load all JLPT level data
    levels_map = {5: 'N5', 4: 'N4', 3: 'N3', 2: 'N2', 1: 'N1'}
    all_words = []

    for level_num, level_name in levels_map.items():
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'n{level_num}.json')
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found, skipping {level_name}")
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = 0
            for item in data:
                word = item.get('word', '').strip()
                meaning = item.get('meaning', '').strip()
                furigana = item.get('furigana', item.get('hiragana', '')).strip()
                romaji = item.get('romaji', '').strip()
                if not word or not meaning:
                    continue
                all_words.append({
                    'japanese': word,
                    'hiragana': furigana,
                    'romaji': romaji,
                    'meaning_en': meaning,
                    'meaning_zh': '',
                    'jlpt_level': level_name,
                    'category': '',
                    'is_premium': 0 if level_num == 5 else 1,
                })
                count += 1
            print(f"Loaded {level_name}: {count} words")

    print(f"\nTotal words loaded: {len(all_words)}")

    # Deduplicate
    seen = {}
    deduped = []
    for w in all_words:
        key = (w['japanese'], w['hiragana'])
        if key not in seen:
            seen[key] = len(deduped)
            deduped.append(w)
        else:
            idx = seen[key]
            level_order = {'N5': 5, 'N4': 4, 'N3': 3, 'N2': 2, 'N1': 1}
            if level_order.get(w['jlpt_level'], 0) > level_order.get(deduped[idx]['jlpt_level'], 0):
                deduped[idx] = w

    all_words = deduped
    print(f"After deduplication: {len(all_words)} words")

    # Classify POS
    for w in all_words:
        w['category'] = classify_pos(w['japanese'], w['hiragana'], w['meaning_en'])

    # Translate to Chinese
    print("\nTranslating meanings to Chinese...")
    translated_count = 0
    fallback_count = 0
    for i, w in enumerate(all_words):
        w['meaning_zh'] = translate_to_chinese(w['meaning_en'])
        if w['meaning_zh'] != w['meaning_en']:
            translated_count += 1
        else:
            fallback_count += 1
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i+1}/{len(all_words)} (translated: {translated_count}, fallback: {fallback_count})")

    print(f"Translation complete: {translated_count} translated, {fallback_count} using English fallback")

    # Add example sentences
    for w in all_words:
        if w['japanese'] in example_sentences:
            w['example_sentence'] = example_sentences[w['japanese']][0]
            w['example_translation'] = example_sentences[w['japanese']][1]

    # Sort by JLPT level then by reading
    level_order = {'N5': 1, 'N4': 2, 'N3': 3, 'N2': 4, 'N1': 5}
    all_words.sort(key=lambda w: (level_order.get(w['jlpt_level'], 9), w['hiragana']))

    # Print statistics
    print(f"\n=== Statistics ===")
    print(f"Total words: {len(all_words)}")
    level_dist = Counter(w['jlpt_level'] for w in all_words)
    print("Level distribution:")
    for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
        free = sum(1 for w in all_words if w['jlpt_level'] == level and w['is_premium'] == 0)
        premium = sum(1 for w in all_words if w['jlpt_level'] == level and w['is_premium'] == 1)
        print(f"  {level}: {level_dist.get(level, 0)} words (free: {free}, premium: {premium})")
    cat_dist = Counter(w['category'] for w in all_words)
    print("Category distribution:")
    for cat, count in cat_dist.most_common():
        print(f"  {cat}: {count}")

    # Generate JS file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocabulary-data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('// Complete JLPT vocabulary data (N5-N1)\n')
        f.write(f'// Total: {len(all_words)} words\n')
        f.write('// Source: tanos.co.uk JLPT vocabulary lists (CC-BY by Jonathan Waller)\n')
        f.write('// Enhanced with Chinese translations and POS classification\n\n')
        f.write('export const vocabularyData = [\n')

        for i, w in enumerate(all_words):
            def escape_js(s):
                if not s:
                    return ''
                return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

            entry_parts = [
                f'japanese: "{escape_js(w["japanese"])}"',
                f'hiragana: "{escape_js(w["hiragana"])}"',
                f'romaji: "{escape_js(w["romaji"])}"',
                f'meaning_en: "{escape_js(w["meaning_en"])}"',
                f'meaning_zh: "{escape_js(w["meaning_zh"])}"',
                f'jlpt_level: "{w["jlpt_level"]}"',
                f'category: "{w["category"]}"',
                f'is_premium: {w["is_premium"]}',
            ]

            if w.get('example_sentence'):
                entry_parts.append(f'example_sentence: "{escape_js(w["example_sentence"])}"')
                entry_parts.append(f'example_translation: "{escape_js(w["example_translation"])}"')

            f.write(f'  {{ {", ".join(entry_parts)} }}')
            if i < len(all_words) - 1:
                f.write(',\n')
            else:
                f.write('\n')

        f.write('];\n')

    file_size = os.path.getsize(output_path)
    print(f"\nGenerated {output_path}")
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print("\nDone!")


if __name__ == '__main__':
    main()
