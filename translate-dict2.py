#!/usr/bin/env python3
"""Second pass translation: comprehensive EN-ZH dictionary for remaining English meanings."""

import re
import json

INPUT_FILE = "src/data/vocabulary-data.ts"

# Comprehensive EN-ZH dictionary (much larger than first pass)
DICT = {
    # Common nouns
    "butter": "黄油", "heater": "取暖器", "guitar": "吉他", "metre": "米", "meter": "米",
    "vase": "花瓶", "stamp": "邮票", "postage": "邮费", "car": "汽车", "vehicle": "车辆",
    "brother": "兄弟", "sister": "姐妹", "younger": "年幼的", "older": "年长的",
    "colour": "颜色", "color": "颜色", "gloomy": "阴暗的", "noisy": "吵闹的",
    "annoying": "烦人的", "late": "迟的", "slow": "慢的", "splendid": "出色的",
    "excellent": "优秀的", "ball": "球", "pen": "笔", "point": "尖头",
    "et": "等", "cetera": "等", "well": "好的",
    "unpleasant": "令人不快的", "afterwards": "之后", "after": "之后",
    # Animals
    "dog": "狗", "cat": "猫", "bird": "鸟", "fish": "鱼", "horse": "马",
    "cow": "牛", "pig": "猪", "sheep": "羊", "rabbit": "兔子", "mouse": "老鼠",
    "rat": "老鼠", "bear": "熊", "lion": "狮子", "tiger": "老虎", "monkey": "猴子",
    "elephant": "大象", "snake": "蛇", "duck": "鸭子", "chicken": "鸡", "insect": "昆虫",
    "bee": "蜜蜂", "fly": "苍蝇", "spider": "蜘蛛", "whale": "鲸鱼", "shark": "鲨鱼",
    # Body
    "head": "头", "hair": "头发", "face": "脸", "eye": "眼睛", "ear": "耳朵",
    "nose": "鼻子", "mouth": "嘴", "tooth": "牙齿", "tongue": "舌头", "neck": "脖子",
    "shoulder": "肩膀", "arm": "手臂", "hand": "手", "finger": "手指", "leg": "腿",
    "foot": "脚", "knee": "膝盖", "back": "背", "chest": "胸", "stomach": "胃",
    "heart": "心脏", "blood": "血", "skin": "皮肤", "bone": "骨头", "brain": "大脑",
    # Food
    "rice": "米饭", "bread": "面包", "meat": "肉", "egg": "鸡蛋", "milk": "牛奶",
    "tea": "茶", "coffee": "咖啡", "water": "水", "juice": "果汁", "wine": "酒",
    "beer": "啤酒", "sake": "日本酒", "soup": "汤", "noodle": "面条", "cake": "蛋糕",
    "fruit": "水果", "apple": "苹果", "orange": "橙子", "banana": "香蕉", "grape": "葡萄",
    "vegetable": "蔬菜", "potato": "土豆", "tomato": "番茄", "onion": "洋葱", "carrot": "胡萝卜",
    "sugar": "糖", "salt": "盐", "oil": "油", "cheese": "奶酪", "sandwich": "三明治",
    "chocolate": "巧克力", "ice": "冰", "cream": "奶油", "dessert": "甜点", "snack": "零食",
    # Nature
    "sun": "太阳", "moon": "月亮", "star": "星星", "sky": "天空", "cloud": "云",
    "rain": "雨", "snow": "雪", "wind": "风", "storm": "暴风雨", "thunder": "雷",
    "lightning": "闪电", "fire": "火", "earth": "大地", "ground": "地面", "stone": "石头",
    "rock": "岩石", "sand": "沙子", "dust": "灰尘", "mud": "泥", "ice": "冰",
    "mountain": "山", "river": "河", "lake": "湖", "sea": "海", "ocean": "海洋",
    "beach": "海滩", "island": "岛屿", "forest": "森林", "tree": "树", "wood": "木材",
    "flower": "花", "grass": "草", "leaf": "叶子", "root": "根", "seed": "种子",
    "spring": "春天", "summer": "夏天", "autumn": "秋天", "fall": "秋天", "winter": "冬天",
    # House
    "house": "房子", "home": "家", "room": "房间", "kitchen": "厨房", "bathroom": "浴室",
    "bedroom": "卧室", "living": "起居", "door": "门", "window": "窗户", "wall": "墙壁",
    "floor": "地板", "ceiling": "天花板", "roof": "屋顶", "garden": "花园", "yard": "院子",
    "gate": "大门", "fence": "栅栏", "garage": "车库", "basement": "地下室", "attic": "阁楼",
    "chair": "椅子", "table": "桌子", "desk": "书桌", "bed": "床", "sofa": "沙发",
    "shelf": "架子", "drawer": "抽屉", "mirror": "镜子", "clock": "时钟", "lamp": "灯",
    "light": "灯", "carpet": "地毯", "curtain": "窗帘", "blanket": "毯子", "pillow": "枕头",
    "towel": "毛巾", "cup": "杯子", "glass": "玻璃杯", "plate": "盘子", "bowl": "碗",
    "chopstick": "筷子", "fork": "叉子", "spoon": "勺子", "knife": "刀", "pot": "锅",
    "pan": "平底锅", "bottle": "瓶子", "kettle": "水壶", "refrigerator": "冰箱", "oven": "烤箱",
    # Clothing
    "shirt": "衬衫", "coat": "外套", "jacket": "夹克", "suit": "西装", "dress": "连衣裙",
    "skirt": "裙子", "trousers": "裤子", "pants": "裤子", "jeans": "牛仔裤", "shoe": "鞋子",
    "boot": "靴子", "sock": "袜子", "hat": "帽子", "cap": "帽子", "glove": "手套",
    "scarf": "围巾", "tie": "领带", "belt": "腰带", "uniform": "制服", "pajama": "睡衣",
    "raincoat": "雨衣", "pocket": "口袋", "button": "纽扣", "collar": "衣领", "sleeve": "袖子",
    # Transport
    "train": "火车", "bus": "公交车", "car": "汽车", "bicycle": "自行车", "bike": "自行车",
    "airplane": "飞机", "plane": "飞机", "ship": "船", "boat": "小船", "truck": "卡车",
    "taxi": "出租车", "subway": "地铁", "helicopter": "直升机", "rocket": "火箭",
    "station": "车站", "airport": "机场", "port": "港口", "ticket": "票", "fare": "车费",
    "wheel": "车轮", "engine": "引擎", "brake": "刹车", "seat": "座位", "door": "门",
    # School/Work
    "school": "学校", "class": "班级", "classroom": "教室", "teacher": "老师", "student": "学生",
    "pupil": "学生", "book": "书", "notebook": "笔记本", "paper": "纸", "pencil": "铅笔",
    "eraser": "橡皮", "ruler": "尺子", "dictionary": "词典", "test": "考试", "exam": "考试",
    "homework": "作业", "lesson": "课程", "subject": "科目", "math": "数学", "science": "科学",
    "history": "历史", "geography": "地理", "art": "美术", "music": "音乐", "English": "英语",
    "Japanese": "日语", "language": "语言", "word": "单词", "letter": "信", "sentence": "句子",
    "question": "问题", "answer": "回答", "grade": "成绩", "score": "分数", "degree": "学位",
    "office": "办公室", "company": "公司", "factory": "工厂", "shop": "商店", "store": "商店",
    "bank": "银行", "hospital": "医院", "library": "图书馆", "museum": "博物馆", "park": "公园",
    "hotel": "酒店", "restaurant": "餐厅", "cafe": "咖啡馆", "bar": "酒吧", "cinema": "电影院",
    "theater": "剧院", "zoo": "动物园", "church": "教堂", "temple": "寺庙", "university": "大学",
    "college": "学院", "work": "工作", "job": "职业", "worker": "工人", "employee": "雇员",
    "manager": "经理", "boss": "老板", "president": "总统", "king": "国王", "queen": "女王",
    "prince": "王子", "princess": "公主", "doctor": "医生", "nurse": "护士", "lawyer": "律师",
    "soldier": "士兵", "police": "警察", "thief": "小偷", "farmer": "农民", "fisherman": "渔夫",
    "cook": "厨师", "baker": "面包师", "writer": "作家", "artist": "艺术家", "singer": "歌手",
    "actor": "演员", "dancer": "舞者", "player": "选手", "athlete": "运动员",
    # Time
    "time": "时间", "day": "天", "week": "周", "month": "月", "year": "年",
    "hour": "小时", "minute": "分钟", "second": "秒", "morning": "早上", "afternoon": "下午",
    "evening": "傍晚", "night": "晚上", "noon": "中午", "midnight": "午夜", "dawn": "黎明",
    "dusk": "黄昏", "today": "今天", "yesterday": "昨天", "tomorrow": "明天", "now": "现在",
    "then": "那时", "past": "过去", "future": "未来", "present": "现在", "moment": "瞬间",
    "date": "日期", "birthday": "生日", "holiday": "假日", "vacation": "假期", "festival": "节日",
    "century": "世纪", "decade": "十年", "schedule": "日程", "deadline": "截止日期",
    "January": "一月", "February": "二月", "March": "三月", "April": "四月", "May": "五月",
    "June": "六月", "July": "七月", "August": "八月", "September": "九月", "October": "十月",
    "November": "十一月", "December": "十二月",
    "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三", "Thursday": "星期四",
    "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日",
    # Numbers/Quantities
    "one": "一", "two": "二", "three": "三", "four": "四", "five": "五",
    "six": "六", "seven": "七", "eight": "八", "nine": "九", "ten": "十",
    "hundred": "百", "thousand": "千", "million": "百万", "billion": "十亿",
    "first": "第一", "second": "第二", "third": "第三", "half": "一半", "quarter": "四分之一",
    "double": "双倍", "single": "单个", "pair": "一对", "dozen": "一打",
    "zero": "零", "none": "没有", "some": "一些", "many": "许多", "few": "少数",
    "several": "几个", "all": "全部", "each": "每个", "every": "每个",
    # Verbs
    "to be": "是", "to have": "有", "to do": "做", "to make": "制作", "to go": "去",
    "to come": "来", "to see": "看", "to look": "看", "to watch": "观看", "to hear": "听到",
    "to listen": "听", "to say": "说", "to speak": "说", "to talk": "谈话", "to tell": "告诉",
    "to ask": "询问", "to answer": "回答", "to read": "读", "to write": "写", "to draw": "画",
    "to eat": "吃", "to drink": "喝", "to cook": "烹饪", "to sleep": "睡觉", "to wake": "醒来",
    "to stand": "站", "to sit": "坐", "to walk": "走", "to run": "跑", "to jump": "跳",
    "to fly": "飞", "to swim": "游泳", "to drive": "驾驶", "to ride": "骑", "to stop": "停止",
    "to start": "开始", "to begin": "开始", "to end": "结束", "to finish": "完成", "to continue": "继续",
    "to open": "打开", "to close": "关", "to shut": "关闭", "to turn": "转", "to move": "移动",
    "to push": "推", "to pull": "拉", "to hold": "拿", "to catch": "抓住", "to throw": "扔",
    "to give": "给", "to take": "拿", "to receive": "收到", "to send": "发送", "to bring": "带来",
    "to buy": "买", "to sell": "卖", "to pay": "支付", "to cost": "花费", "to spend": "花费",
    "to save": "保存", "to use": "使用", "to need": "需要", "to want": "想要", "to wish": "希望",
    "to hope": "希望", "to think": "思考", "to know": "知道", "to understand": "理解", "to remember": "记得",
    "to forget": "忘记", "to learn": "学习", "to teach": "教", "to study": "学习", "to practice": "练习",
    "to try": "尝试", "to help": "帮助", "to wait": "等待", "to hurry": "匆忙", "to rest": "休息",
    "to work": "工作", "to play": "玩", "to sing": "唱歌", "to dance": "跳舞", "to laugh": "笑",
    "to cry": "哭", "to smile": "微笑", "to love": "爱", "to like": "喜欢", "to hate": "讨厌",
    "to fear": "害怕", "to worry": "担心", "to believe": "相信", "to trust": "信任", "to doubt": "怀疑",
    "to change": "改变", "to become": "成为", "to grow": "成长", "to increase": "增加", "to decrease": "减少",
    "to rise": "上升", "to fall": "落下", "to drop": "掉落", "to break": "打破", "to repair": "修理",
    "to fix": "修理", "to build": "建造", "to destroy": "毁坏", "to create": "创造", "to choose": "选择",
    "to decide": "决定", "to plan": "计划", "to prepare": "准备", "to arrange": "安排",
    "to meet": "见面", "to visit": "拜访", "to invite": "邀请", "to welcome": "欢迎",
    "to call": "呼叫", "to phone": "打电话", "to mail": "邮寄", "to contact": "联系",
    "to bathe": "洗澡", "to shower": "淋浴", "to wash": "洗", "to clean": "清洁", "to brush": "刷",
    "to cut": "切", "to slice": "切片", "to chop": "剁", "to mix": "混合", "to stir": "搅拌",
    "to pour": "倒", "to boil": "煮", "to fry": "煎", "to bake": "烤", "to grill": "烧烤",
    "to wear": "穿", "to put": "放", "to remove": "移除", "to take off": "脱下",
    "to lose": "丢失", "to find": "找到", "to search": "搜索", "to seek": "寻找", "to discover": "发现",
    "to show": "展示", "to hide": "隐藏", "to cover": "覆盖", "to uncover": "揭开",
    "to tie": "系", "to untie": "解开", "to wrap": "包裹", "to pack": "打包",
    "to fill": "填满", "to empty": "清空", "to carry": "携带", "to deliver": "交付",
    "to lend": "借出", "to borrow": "借入", "to rent": "租", "to hire": "雇用",
    "to obey": "服从", "to refuse": "拒绝", "to accept": "接受", "to admit": "承认",
    "to permit": "允许", "to forbid": "禁止", "to allow": "允许", "to prevent": "阻止",
    "to protect": "保护", "to attack": "攻击", "to defend": "防御", "to fight": "战斗",
    "to win": "赢", "to lose": "输", "to beat": "打败", "to surrender": "投降",
    "to join": "加入", "to separate": "分开", "to divide": "分割", "to share": "分享",
    "to unite": "联合", "to connect": "连接", "to combine": "结合", "to gather": "聚集",
    "to collect": "收集", "to scatter": "散开", "to distribute": "分配", "to spread": "传播",
    "to travel": "旅行", "to journey": "旅行", "to explore": "探索", "to arrive": "到达",
    "to depart": "出发", "to leave": "离开", "to return": "返回", "to stay": "停留",
    "to live": "居住", "to exist": "存在", "to die": "死", "to kill": "杀", "to murder": "谋杀",
    "to born": "出生", "to marry": "结婚", "to divorce": "离婚", "to adopt": "收养",
    "to count": "计数", "to calculate": "计算", "to measure": "测量", "to weigh": "称重",
    "to check": "检查", "to test": "测试", "to examine": "检查", "to inspect": "视察",
    "to prove": "证明", "to demonstrate": "演示", "to show": "显示", "to display": "展示",
    "to explain": "解释", "to describe": "描述", "to report": "报告", "to announce": "宣布",
    "to state": "陈述", "to express": "表达", "to claim": "声称", "to argue": "争论",
    "to discuss": "讨论", "to debate": "辩论", "to negotiate": "谈判", "to persuade": "说服",
    "to convince": "使信服", "to encourage": "鼓励", "to discourage": "使灰心", "to praise": "赞美",
    "to blame": "责备", "to criticize": "批评", "to complain": "抱怨", "to apologize": "道歉",
    "to forgive": "原谅", "to punish": "惩罚", "to reward": "奖励", "to thank": "感谢",
    "to greet": "问候", "to introduce": "介绍", "to recommend": "推荐", "to suggest": "建议",
    "to advise": "建议", "to warn": "警告", "to remind": "提醒", "to inform": "通知",
    "to notify": "通知", "to update": "更新", "to record": "记录", "to register": "登记",
    "to apply": "申请", "to submit": "提交", "to cancel": "取消", "to postpone": "推迟",
    "to delay": "延迟", "to hurry": "催促", "to rush": "冲", "to slow": "放慢",
    "to relax": "放松", "to calm": "平静", "to excite": "使兴奋", "to bore": "使无聊",
    "to interest": "使感兴趣", "to surprise": "使惊讶", "to shock": "使震惊", "to scare": "恐吓",
    "to frighten": "吓唬", "to threaten": "威胁", "to dare": "敢", "to challenge": "挑战",
    # Adjectives
    "big": "大的", "small": "小的", "large": "大的", "tiny": "微小的", "huge": "巨大的",
    "tall": "高的", "short": "短的", "long": "长的", "wide": "宽的", "narrow": "窄的",
    "thick": "厚的", "thin": "薄的", "deep": "深的", "shallow": "浅的", "high": "高的",
    "low": "低的", "heavy": "重的", "light": "轻的", "hard": "硬的", "soft": "软的",
    "smooth": "光滑的", "rough": "粗糙的", "sharp": "锋利的", "dull": "钝的", "flat": "平的",
    "round": "圆的", "square": "方的", "straight": "直的", "curved": "弯曲的",
    "good": "好的", "bad": "坏的", "nice": "好的", "kind": "善良的", "gentle": "温柔的",
    "cruel": "残忍的", "mean": "刻薄的", "rude": "粗鲁的", "polite": "礼貌的", "friendly": "友好的",
    "unfriendly": "不友好的", "happy": "快乐的", "sad": "悲伤的", "angry": "生气的", "mad": "疯的",
    "glad": "高兴的", "joyful": "欢乐的", "cheerful": "愉快的", "depressed": "沮丧的", "lonely": "孤独的",
    "afraid": "害怕的", "scared": "害怕的", "frightened": "害怕的", "terrified": "恐惧的",
    "nervous": "紧张的", "anxious": "焦虑的", "worried": "担心的", "calm": "冷静的", "relaxed": "放松的",
    "tired": "疲倦的", "sleepy": "困倦的", "exhausted": "精疲力竭的", "energetic": "精力充沛的",
    "bored": "无聊的", "busy": "忙碌的", "free": "空闲的", "available": "可用的",
    "sick": "生病的", "ill": "生病的", "healthy": "健康的", "strong": "强壮的", "weak": "虚弱的",
    "young": "年轻的", "old": "老的", "new": "新的", "fresh": "新鲜的", "modern": "现代的",
    "ancient": "古老的", "traditional": "传统的", "classic": "经典的", "popular": "受欢迎的",
    "famous": "著名的", "unknown": "未知的", "familiar": "熟悉的", "strange": "奇怪的",
    "normal": "正常的", "unusual": "不寻常的", "common": "常见的", "rare": "稀有的",
    "special": "特别的", "ordinary": "普通的", "usual": "通常的", "unusual": "不寻常的",
    "beautiful": "美丽的", "ugly": "丑陋的", "pretty": "漂亮的", "handsome": "英俊的",
    "cute": "可爱的", "lovely": "可爱的", "wonderful": "精彩的", "terrible": "可怕的",
    "horrible": "恐怖的", "awful": "糟糕的", "great": "伟大的", "amazing": "惊人的",
    "fantastic": "极好的", "brilliant": "杰出的", "perfect": "完美的", "imperfect": "不完美的",
    "clean": "干净的", "dirty": "脏的", "wet": "湿的", "dry": "干的", "hot": "热的",
    "cold": "冷的", "warm": "温暖的", "cool": "凉爽的", "freezing": "冰冻的", "boiling": "沸腾的",
    "sweet": "甜的", "sour": "酸的", "bitter": "苦的", "spicy": "辣的", "salty": "咸的",
    "delicious": "美味的", "tasty": "好吃的", "tasteless": "无味的", "fresh": "新鲜的",
    "expensive": "昂贵的", "cheap": "便宜的", "rich": "富有的", "poor": "贫穷的",
    "safe": "安全的", "dangerous": "危险的", "easy": "容易的", "difficult": "困难的",
    "hard": "难的", "simple": "简单的", "complicated": "复杂的", "complex": "复杂的",
    "clear": "清楚的", "unclear": "不清楚的", "obvious": "明显的", "vague": "模糊的",
    "important": "重要的", "unimportant": "不重要的", "necessary": "必要的", "unnecessary": "不必要的",
    "possible": "可能的", "impossible": "不可能的", "probable": "可能的", "unlikely": "不太可能的",
    "certain": "确定的", "sure": "确定的", "uncertain": "不确定的", "doubtful": "可疑的",
    "true": "真实的", "false": "假的", "real": "真的", "fake": "假的", "genuine": "真正的",
    "right": "正确的", "wrong": "错误的", "correct": "正确的", "incorrect": "不正确的",
    "proper": "适当的", "improper": "不适当的", "appropriate": "合适的", "inappropriate": "不合适的",
    "fair": "公平的", "unfair": "不公平的", "equal": "平等的", "unequal": "不平等的",
    "same": "相同的", "different": "不同的", "similar": "相似的", "identical": "完全相同的",
    "first": "第一的", "last": "最后的", "final": "最终的", "initial": "最初的",
    "open": "打开的", "closed": "关闭的", "full": "满的", "empty": "空的",
    "ready": "准备好的", "unready": "未准备好的", "complete": "完整的", "incomplete": "不完整的",
    "finished": "完成的", "unfinished": "未完成的", "successful": "成功的", "failed": "失败的",
    "fast": "快的", "quick": "快速的", "rapid": "迅速的", "slow": "慢的",
    "early": "早的", "late": "迟的", "prompt": "及时的", "delayed": "延迟的",
    "loud": "大声的", "quiet": "安静的", "silent": "沉默的", "noisy": "吵闹的",
    "bright": "明亮的", "dark": "黑暗的", "dim": "昏暗的", "pale": "苍白的",
    "rich": "浓郁的", "light": "淡的", "deep": "深的", "vivid": "鲜艳的",
    "heavy": "沉重的", "light": "轻的", "thick": "浓的", "thin": "稀的",
    # Adverbs
    "very": "非常", "really": "真的", "truly": "真正地", "quite": "相当", "rather": "相当",
    "fairly": "颇", "pretty": "相当", "somewhat": "有点", "slightly": "稍微",
    "extremely": "极其", "incredibly": "难以置信地", "remarkably": "显著地",
    "always": "总是", "usually": "通常", "often": "经常", "sometimes": "有时",
    "rarely": "很少", "seldom": "很少", "never": "从不", "ever": "曾经",
    "again": "再次", "still": "仍然", "yet": "还", "already": "已经",
    "just": "刚才", "recently": "最近", "lately": "近来", "soon": "很快",
    "immediately": "立即", "instantly": "即刻", "suddenly": "突然", "gradually": "逐渐地",
    "finally": "最后", "eventually": "最终", "ultimately": "最终",
    "here": "这里", "there": "那里", "everywhere": "到处", "nowhere": "无处",
    "somewhere": "某处", "anywhere": "任何地方",
    "up": "向上", "down": "向下", "out": "外面", "in": "里面", "away": "远离",
    "back": "回来", "forward": "向前", "backward": "向后", "aside": "旁边",
    "together": "一起", "apart": "分开", "alone": "独自",
    "quickly": "快速地", "slowly": "慢慢地", "carefully": "小心地", "carelessly": "粗心地",
    "easily": "容易地", "hardly": "几乎不", "barely": "勉强", "scarcely": "几乎不",
    "well": "好地", "badly": "差地", "properly": "适当地", "improperly": "不适当地",
    "correctly": "正确地", "incorrectly": "不正确地", "safely": "安全地", "dangerously": "危险地",
    "happily": "快乐地", "sadly": "悲伤地", "angrily": "愤怒地", "calmly": "冷静地",
    "quietly": "安静地", "loudly": "大声地", "softly": "轻柔地", "gently": "温柔地",
    "kindly": "亲切地", "politely": "礼貌地", "rudely": "粗鲁地", "friendly": "友好地",
    "certainly": "当然", "definitely": "肯定地", "absolutely": "绝对地", "positively": "肯定地",
    "probably": "可能", "possibly": "可能", "perhaps": "也许", "maybe": "也许",
    "of course": "当然", "naturally": "自然地", "obviously": "明显地", "clearly": "清楚地",
    "apparently": "显然", "evidently": "显然", "seemingly": "看似",
    "fortunately": "幸运地", "unfortunately": "不幸地", "luckily": "幸运地", "unluckily": "不幸地",
    "honestly": "诚实地", "frankly": "坦率地", "seriously": "认真地", "jokingly": "开玩笑地",
    "surprisingly": "令人惊讶地", "unexpectedly": "出乎意料地", "strangely": "奇怪地",
    "interestingly": "有趣地", "amusingly": "有趣地", "sadly": "可悲地",
    "firstly": "首先", "secondly": "其次", "thirdly": "第三", "lastly": "最后",
    "above all": "最重要的是", "after all": "毕竟", "in fact": "事实上", "actually": "实际上",
    "indeed": "确实", "truly": "真正地", "really": "真的",
    # Common phrases/patterns
    "used for": "用于", "used to": "用于", "in order to": "为了", "so as to": "以便",
    "because of": "因为", "due to": "由于", "thanks to": "多亏",
    "instead of": "而不是", "rather than": "而不是",
    "in front of": "在前面", "behind": "在后面", "next to": "旁边", "beside": "旁边",
    "between": "之间", "among": "之中", "through": "通过", "across": "横过",
    "along": "沿着", "around": "周围", "about": "关于", "against": "反对",
    "without": "没有", "within": "在内", "beyond": "超越", "beneath": "下方",
    "towards": "朝向", "toward": "朝向", "upon": "在上方",
    "at first": "起初", "at last": "终于", "at least": "至少", "at most": "至多",
    "for example": "例如", "for instance": "例如", "such as": "比如",
    "in general": "一般来说", "in particular": "特别地", "in short": "简而言之",
    "on the other hand": "另一方面", "on the contrary": "相反",
    "as well": "也", "as well as": "以及", "as if": "好像", "as though": "好像",
    "even if": "即使", "even though": "即使", "although": "虽然", "though": "虽然",
    "unless": "除非", "until": "直到", "till": "直到", "since": "自从", "once": "一旦",
    "whether": "是否", "whenever": "每当", "wherever": "无论哪里", "whoever": "无论谁",
    # More specific JLPT vocabulary
    "splendid": "壮丽的", "magnificent": "宏伟的", "grand": "盛大的", "noble": "高贵的",
    "humble": "谦虚的", "modest": "谦虚的", "proud": "骄傲的", "ashamed": "惭愧的",
    "guilty": "有罪的", "innocent": "无辜的", "honest": "诚实的", "dishonest": "不诚实的",
    "loyal": "忠诚的", "faithful": "忠实的", "reliable": "可靠的", "unreliable": "不可靠的",
    "responsible": "负责任的", "irresponsible": "不负责任的", "careful": "仔细的", "careless": "粗心的",
    "diligent": "勤奋的", "lazy": "懒惰的", "hardworking": "勤勉的", "idle": "懒惰的",
    "clever": "聪明的", "wise": "明智的", "foolish": "愚蠢的", "stupid": "愚蠢的",
    "smart": "聪明的", "intelligent": "智能的", "genius": "天才", "talented": "有才华的",
    "skilled": "熟练的", "experienced": "有经验的", "amateur": "业余的", "professional": "专业的",
    "eager": "渴望的", "enthusiastic": "热情的", "passionate": "热情的", "indifferent": "冷漠的",
    "curious": "好奇的", "interested": "感兴趣的", "bored": "无聊的", "excited": "兴奋的",
    "satisfied": "满意的", "dissatisfied": "不满意的", "content": "满足的", "discontent": "不满的",
    "grateful": "感激的", "thankful": "感谢的", "regretful": "后悔的", "remorseful": "悔恨的",
    "jealous": "嫉妒的", "envious": "羡慕的", "greedy": "贪婪的", "generous": "慷慨的",
    "selfish": "自私的", "selfless": "无私的", "stubborn": "固执的", "flexible": "灵活的",
    "patient": "耐心的", "impatient": "不耐烦的", "tolerant": "宽容的", "intolerant": "不宽容的",
    "brave": "勇敢的", "cowardly": "胆小的", "bold": "大胆的", "timid": "胆怯的",
    "confident": "自信的", "insecure": "不安全的", "humble": "谦卑的", "arrogant": "傲慢的",
    "honest": "诚实的", "sincere": "真诚的", "genuine": "真诚的", "fake": "虚假的",
    "holy": "神圣的", "sacred": "神圣的", "secular": "世俗的", "spiritual": "精神的",
    "hollow": "空心的", "solid": "固体的", "liquid": "液体的", "gas": "气体",
    "golden": "金色的", "silver": "银色的", "bronze": "青铜色", "copper": "铜色",
    "crimson": "深红色的", "scarlet": "猩红色的", "pink": "粉红色", "purple": "紫色",
    "violet": "紫罗兰色", "indigo": "靛蓝色", "navy": "藏青色", "teal": "蓝绿色",
    "olive": "橄榄色", "lime": "酸橙色", "mint": "薄荷色", "coral": "珊瑚色",
    "amber": "琥珀色", "ivory": "象牙色", "beige": "米色", "tan": "棕褐色",
    # More nouns
    "money": "钱", "price": "价格", "cost": "费用", "fee": "费用", "tax": "税",
    "bill": "账单", "receipt": "收据", "invoice": "发票", "budget": "预算",
    "salary": "薪水", "wage": "工资", "income": "收入", "profit": "利润", "loss": "损失",
    "debt": "债务", "loan": "贷款", "interest": "利息", "investment": "投资",
    "account": "账户", "cash": "现金", "check": "支票", "card": "卡片", "credit": "信用",
    "insurance": "保险", "contract": "合同", "agreement": "协议", "treaty": "条约",
    "law": "法律", "rule": "规则", "regulation": "规定", "policy": "政策",
    "right": "权利", "duty": "义务", "obligation": "责任", "responsibility": "责任",
    "freedom": "自由", "liberty": "自由", "justice": "正义", "fairness": "公平",
    "equality": "平等", "fraternity": "博爱", "peace": "和平", "war": "战争",
    "battle": "战斗", "conflict": "冲突", "struggle": "斗争", "competition": "竞争",
    "victory": "胜利", "defeat": "失败", "triumph": "凯旋", "disaster": "灾难",
    "crisis": "危机", "emergency": "紧急", "danger": "危险", "risk": "风险",
    "accident": "事故", "injury": "伤害", "wound": "伤口", "scar": "疤痕",
    "disease": "疾病", "illness": "疾病", "fever": "发烧", "cough": "咳嗽",
    "headache": "头痛", "stomachache": "胃痛", "toothache": "牙痛", "backache": "背痛",
    "medicine": "药", "drug": "药物", "pill": "药丸", "injection": "注射",
    "operation": "手术", "treatment": "治疗", "therapy": "疗法", "recovery": "康复",
    "health": "健康", "fitness": "健康", "strength": "力量", "weakness": "弱点",
    "power": "力量", "energy": "能量", "force": "力", "pressure": "压力",
    "weight": "重量", "mass": "质量", "volume": "体积", "size": "大小",
    "shape": "形状", "form": "形式", "pattern": "图案", "design": "设计",
    "style": "风格", "fashion": "时尚", "trend": "趋势", "custom": "习俗",
    "habit": "习惯", "hobby": "爱好", "interest": "兴趣", "passion": "热情",
    "dream": "梦想", "goal": "目标", "aim": "目的", "purpose": "目的",
    "reason": "原因", "cause": "原因", "result": "结果", "effect": "效果",
    "consequence": "后果", "outcome": "结果", "impact": "影响", "influence": "影响",
    "advantage": "优势", "disadvantage": "劣势", "benefit": "利益", "harm": "害处",
    "merit": "优点", "demerit": "缺点", "strength": "优点", "weakness": "缺点",
    "problem": "问题", "issue": "问题", "trouble": "麻烦", "difficulty": "困难",
    "solution": "解决方案", "answer": "答案", "response": "回应", "reaction": "反应",
    "question": "问题", "doubt": "怀疑", "suspicion": "怀疑", "belief": "信念",
    "faith": "信仰", "trust": "信任", "hope": "希望", "expectation": "期望",
    "surprise": "惊讶", "shock": "震惊", "wonder": "惊奇", "admiration": "钦佩",
    "respect": "尊重", "honor": "荣誉", "pride": "骄傲", "shame": "羞耻",
    "guilt": "罪恶感", "regret": "后悔", "pity": "遗憾", "sympathy": "同情",
    "empathy": "共情", "compassion": "怜悯", "mercy": "仁慈", "kindness": "善意",
    "love": "爱", "affection": "喜爱", "friendship": "友谊", "relationship": "关系",
    "connection": "联系", "bond": "纽带", "tie": "纽带", "link": "链接",
    "family": "家庭", "parent": "父母", "father": "父亲", "mother": "母亲",
    "son": "儿子", "daughter": "女儿", "husband": "丈夫", "wife": "妻子",
    "uncle": "叔叔", "aunt": "阿姨", "cousin": "表亲", "nephew": "侄子", "niece": "侄女",
    "grandfather": "祖父", "grandmother": "祖母", "grandson": "孙子", "granddaughter": "孙女",
    "child": "孩子", "baby": "婴儿", "infant": "幼儿", "kid": "小孩",
    "adult": "成人", "teenager": "青少年", "youth": "青年", "elder": "长者",
    "friend": "朋友", "enemy": "敌人", "rival": "对手", "partner": "伙伴",
    "colleague": "同事", "neighbor": "邻居", "stranger": "陌生人", "guest": "客人",
    "host": "主人", "visitor": "访客", "tourist": "游客", "passenger": "乘客",
    "customer": "顾客", "client": "客户", "patient": "病人", "victim": "受害者",
    "witness": "证人", "suspect": "嫌疑人", "criminal": "罪犯", "judge": "法官",
    "jury": "陪审团", "witness": "证人",
    # Places
    "city": "城市", "town": "城镇", "village": "村庄", "countryside": "乡村",
    "capital": "首都", "district": "区", "neighborhood": "社区", "suburb": "郊区",
    "street": "街道", "road": "路", "avenue": "大道", "highway": "高速公路",
    "bridge": "桥", "tunnel": "隧道", "crossing": "十字路口", "intersection": "交叉路口",
    "corner": "角落", "block": "街区", "building": "建筑", "tower": "塔",
    "skyscraper": "摩天大楼", "monument": "纪念碑", "statue": "雕像", "fountain": "喷泉",
    "square": "广场", "plaza": "广场", "mall": "购物中心", "market": "市场",
    "fair": "集市", "exhibition": "展览", "gallery": "画廊", "studio": "工作室",
    "laboratory": "实验室", "workshop": "车间", "warehouse": "仓库", "barn": "谷仓",
    "castle": "城堡", "palace": "宫殿", "mansion": "宅邸", "cottage": "小屋",
    "tent": "帐篷", "cabin": "小木屋", "shelter": "庇护所", "camp": "营地",
    # Objects
    "tool": "工具", "instrument": "器具", "device": "设备", "machine": "机器",
    "equipment": "设备", "apparatus": "器械", "appliance": "器具", "gadget": "小工具",
    "computer": "电脑", "laptop": "笔记本电脑", "phone": "手机", "tablet": "平板",
    "screen": "屏幕", "monitor": "显示器", "keyboard": "键盘", "mouse": "鼠标",
    "printer": "打印机", "scanner": "扫描仪", "camera": "相机", "lens": "镜头",
    "film": "胶卷", "battery": "电池", "cable": "电缆", "wire": "电线",
    "plug": "插头", "socket": "插座", "switch": "开关", "button": "按钮",
    "key": "钥匙", "lock": "锁", "handle": "把手", "knob": "旋钮",
    "container": "容器", "box": "盒子", "case": "箱子", "bag": "包", "sack": "麻袋",
    "basket": "篮子", "barrel": "桶", "bucket": "水桶", "tub": "盆",
    "jar": "罐子", "can": "罐头", "tin": "锡罐", "tube": "管子",
    "pipe": "管子", "hose": "软管", "valve": "阀门", "pump": "泵",
    "wheel": "轮子", "axle": "轴", "gear": "齿轮", "spring": "弹簧",
    "nail": "钉子", "screw": "螺丝", "bolt": "螺栓", "nut": "螺母",
    "hammer": "锤子", "saw": "锯子", "drill": "钻头", "file": "锉刀",
    "chisel": "凿子", "plane": "刨子", "wrench": "扳手", "plier": "钳子",
    "scissors": "剪刀", "knife": "刀", "blade": "刀片", "razor": "剃刀",
    "needle": "针", "pin": "大头针", "thread": "线", "string": "绳子",
    "rope": "绳索", "cord": "细绳", "chain": "链条", "belt": "皮带",
    "net": "网", "mesh": "网眼", "grid": "网格", "lattice": "格子",
    "frame": "框架", "stand": "支架", "bracket": "托架", "shelf": "架子",
    "rack": "架子", "hook": "钩子", "hanger": "衣架", "peg": "挂钉",
    # Abstract
    "idea": "想法", "thought": "想法", "concept": "概念", "notion": "观念",
    "theory": "理论", "hypothesis": "假设", "principle": "原理", "rule": "规则",
    "law": "定律", "fact": "事实", "truth": "真相", "reality": "现实",
    "illusion": "幻觉", "fantasy": "幻想", "imagination": "想象力", "dream": "梦",
    "memory": "记忆", "recollection": "回忆", "reminder": "提醒",
    "knowledge": "知识", "wisdom": "智慧", "understanding": "理解", "insight": "洞察力",
    "judgment": "判断", "opinion": "观点", "view": "看法", "perspective": "视角",
    "belief": "信念", "conviction": "确信", "assumption": "假设", "presumption": "假定",
    "evidence": "证据", "proof": "证明", "testimony": "证词", "witness": "见证",
    "argument": "论点", "reasoning": "推理", "logic": "逻辑", "sense": "感觉",
    "meaning": "意义", "significance": "重要性", "importance": "重要性", "value": "价值",
    "worth": "价值", "price": "价格", "cost": "成本", "expense": "花费",
    "quality": "质量", "quantity": "数量", "amount": "数量", "number": "数字",
    "total": "总计", "sum": "总和", "average": "平均", "rate": "比率",
    "ratio": "比例", "percentage": "百分比", "proportion": "比例", "fraction": "分数",
    "level": "水平", "degree": "程度", "extent": "范围", "range": "范围",
    "limit": "限制", "boundary": "边界", "border": "边界", "edge": "边缘",
    "side": "侧面", "surface": "表面", "top": "顶部", "bottom": "底部",
    "center": "中心", "middle": "中间", "core": "核心", "heart": "中心",
    "part": "部分", "portion": "部分", "section": "部分", "segment": "段",
    "piece": "块", "bit": "一点", "fragment": "碎片", "scrap": "碎片",
    "whole": "整体", "entirety": "全部", "totality": "总体",
    "category": "类别", "class": "类别", "type": "类型", "kind": "种类",
    "sort": "种类", "variety": "种类", "form": "形式", "version": "版本",
    "model": "模型", "pattern": "模式", "example": "例子", "instance": "实例",
    "sample": "样本", "specimen": "标本", "case": "案例",
    # Events/Activities
    "event": "事件", "occasion": "场合", "happening": "事件", "occurrence": "发生",
    "incident": "事件", "affair": "事务", "matter": "事情", "business": "事务",
    "activity": "活动", "action": "行动", "deed": "行为", "act": "行为",
    "performance": "表现", "achievement": "成就", "success": "成功", "failure": "失败",
    "attempt": "尝试", "effort": "努力", "try": "尝试", "endeavor": "努力",
    "process": "过程", "procedure": "程序", "method": "方法", "way": "方法",
    "means": "手段", "approach": "方法", "technique": "技术", "skill": "技能",
    "practice": "练习", "training": "训练", "exercise": "锻炼", "drill": "操练",
    "game": "游戏", "sport": "运动", "match": "比赛", "tournament": "锦标赛",
    "race": "比赛", "contest": "竞赛", "competition": "竞争", "championship": "锦标赛",
    "show": "表演", "performance": "表演", "concert": "音乐会", "play": "戏剧",
    "movie": "电影", "film": "电影", "drama": "戏剧", "opera": "歌剧",
    "ballet": "芭蕾舞", "dance": "舞蹈", "song": "歌曲", "music": "音乐",
    "art": "艺术", "painting": "绘画", "drawing": "图画", "sculpture": "雕塑",
    "photograph": "照片", "picture": "图片", "image": "图像", "portrait": "肖像",
    "story": "故事", "tale": "故事", "narrative": "叙事", "account": "叙述",
    "report": "报告", "article": "文章", "essay": "论文", "composition": "作文",
    "novel": "小说", "fiction": "小说", "poetry": "诗歌", "poem": "诗",
    "letter": "信", "message": "消息", "note": "笔记", "memo": "备忘录",
    "document": "文件", "record": "记录", "file": "文件", "data": "数据",
    "information": "信息", "news": "新闻", "report": "报道", "announcement": "公告",
    "statement": "声明", "declaration": "宣言", "speech": "演讲", "talk": "谈话",
    "conversation": "对话", "dialogue": "对话", "discussion": "讨论", "debate": "辩论",
    "argument": "争论", "dispute": "争议", "quarrel": "争吵", "fight": "打架",
    # JLPT specific
    "convenience store": "便利店", "department store": "百货商店", "gas station": "加油站",
    "post office": "邮局", "police station": "警察局", "fire station": "消防站",
    "bookstore": "书店", "bakery": "面包店", "butcher": "肉店", "florist": "花店",
    "barber": "理发师", "hairdresser": "美发师", "pharmacy": "药房", "clinic": "诊所",
    "entrance": "入口", "exit": "出口", "reception": "接待处", "counter": "柜台",
    "lobby": "大厅", "hallway": "走廊", "corridor": "走廊", "staircase": "楼梯",
    "elevator": "电梯", "escalator": "自动扶梯", "stairs": "楼梯",
    "balcony": "阳台", "terrace": "露台", "veranda": "走廊",
    "chimney": "烟囱", "fireplace": "壁炉", "radiator": "暖气片",
    "mailbox": "邮箱", "address": "地址", "stamp": "邮票", "envelope": "信封",
    "parcel": "包裹", "package": "包裹", "delivery": "快递",
    "passport": "护照", "visa": "签证", "ticket": "票", "reservation": "预订",
    "luggage": "行李", "baggage": "行李", "suitcase": "手提箱",
    "map": "地图", "guide": "指南", "direction": "方向", "sign": "标志",
    "signal": "信号", "symbol": "符号", "mark": "标记", "label": "标签",
    "tag": "标签", "sticker": "贴纸", "badge": "徽章", "logo": "标志",
    "flag": "旗帜", "banner": "横幅", "poster": "海报", "notice": "通知",
    "advertisement": "广告", "ad": "广告", "commercial": "商业广告",
    # Colors
    "red": "红色", "blue": "蓝色", "yellow": "黄色", "green": "绿色", "black": "黑色",
    "white": "白色", "gray": "灰色", "grey": "灰色", "brown": "棕色", "orange": "橙色",
    # Materials
    "metal": "金属", "iron": "铁", "steel": "钢", "gold": "金", "silver": "银",
    "copper": "铜", "aluminum": "铝", "lead": "铅", "tin": "锡", "zinc": "锌",
    "glass": "玻璃", "plastic": "塑料", "rubber": "橡胶", "leather": "皮革",
    "paper": "纸", "cardboard": "纸板", "cloth": "布", "fabric": "织物",
    "cotton": "棉", "silk": "丝绸", "wool": "羊毛", "linen": "亚麻",
    "nylon": "尼龙", "polyester": "聚酯纤维",
    "wood": "木材", "timber": "木材", "lumber": "木材", "board": "木板",
    "stone": "石头", "brick": "砖", "concrete": "混凝土", "cement": "水泥",
    "clay": "黏土", "ceramic": "陶瓷", "porcelain": "瓷器",
    "sand": "沙子", "soil": "土壤", "dirt": "泥土", "mud": "泥",
    # More common words
    "thing": "东西", "object": "物体", "item": "物品", "article": "物品",
    "product": "产品", "goods": "商品", "merchandise": "商品", "commodity": "商品",
    "material": "材料", "substance": "物质", "matter": "物质", "element": "元素",
    "ingredient": "成分", "component": "组件", "part": "零件", "piece": "部件",
    "unit": "单位", "module": "模块", "section": "部分",
    "system": "系统", "network": "网络", "structure": "结构", "framework": "框架",
    "organization": "组织", "institution": "机构", "society": "社会", "community": "社区",
    "group": "组", "team": "团队", "crew": "组员", "staff": "员工",
    "committee": "委员会", "council": "理事会", "board": "董事会", "assembly": "大会",
    "government": "政府", "state": "国家", "nation": "国家", "country": "国家",
    "world": "世界", "earth": "地球", "globe": "地球", "universe": "宇宙",
    "space": "太空", "nature": "自然", "environment": "环境", "surroundings": "周围环境",
    # Common adjective meanings
    "convenient": "方便的", "inconvenient": "不方便的", "useful": "有用的", "useless": "无用的",
    "available": "可用的", "unavailable": "不可用的", "accessible": "可访问的", "inaccessible": "不可访问的",
    "acceptable": "可接受的", "unacceptable": "不可接受的", "suitable": "合适的", "unsuitable": "不合适的",
    "comfortable": "舒适的", "uncomfortable": "不舒适的", "pleasant": "令人愉快的", "unpleasant": "令人不快的",
    "popular": "受欢迎的", "unpopular": "不受欢迎的", "famous": "著名的", "infamous": "臭名昭著的",
    "favorite": "最喜欢的", "beloved": "深爱的", "dear": "亲爱的",
    "worth": "值得的", "valuable": "有价值的", "valueless": "无价值的", "precious": "珍贵的",
    "rare": "稀有的", "common": "常见的", "unique": "独特的", "ordinary": "普通的",
    "strange": "奇怪的", "familiar": "熟悉的", "unknown": "未知的", "mysterious": "神秘的",
    "secret": "秘密的", "public": "公共的", "private": "私人的", "personal": "个人的",
    "official": "官方的", "informal": "非正式的", "formal": "正式的",
    "national": "国家的", "international": "国际的", "global": "全球的", "local": "本地的",
    "rural": "农村的", "urban": "城市的", "suburban": "郊区的",
    "eastern": "东方的", "western": "西方的", "northern": "北方的", "southern": "南方的",
    "inner": "内部的", "outer": "外部的", "upper": "上部的", "lower": "下部的",
    "central": "中央的", "surrounding": "周围的",
    "maximum": "最大的", "minimum": "最小的", "average": "平均的", "medium": "中等的",
    "extra": "额外的", "spare": "备用的", "additional": "附加的",
    "main": "主要的", "primary": "首要的", "secondary": "次要的", "minor": "次要的",
    "major": "主要的", "chief": "首席的", "principal": "主要的", "leading": "领先的",
    "only": "唯一的", "sole": "唯一的", "single": "单一的", "double": "双倍的",
    "multiple": "多个的", "various": "各种各样的", "diverse": "多样的",
    "certain": "某个", "some": "一些", "any": "任何", "every": "每个", "each": "每个",
    "all": "全部", "both": "两者", "neither": "两者都不", "either": "任何一个",
    "none": "没有", "nothing": "什么都没有", "nobody": "没有人", "no one": "没有人",
    "someone": "某人", "somebody": "某人", "anyone": "任何人", "anybody": "任何人",
    "everyone": "每个人", "everybody": "每个人", "something": "某事", "anything": "任何事",
    "everything": "一切", "nothing": "什么都没有",
    # Greetings and common expressions
    "hello": "你好", "goodbye": "再见", "good morning": "早上好", "good afternoon": "下午好",
    "good evening": "晚上好", "good night": "晚安", "thank you": "谢谢", "thanks": "谢谢",
    "sorry": "对不起", "excuse me": "打扰一下", "please": "请", "yes": "是", "no": "不",
    "ok": "好的", "okay": "好的", "sure": "当然", "of course": "当然",
    "welcome": "欢迎", "congratulations": "恭喜", "happy birthday": "生日快乐",
    "merry christmas": "圣诞快乐", "happy new year": "新年快乐",
    "pardon": "原谅", "bless you": "保佑你", "cheers": "干杯",
    # More verbs
    "to exist": "存在", "to happen": "发生", "to occur": "发生", "to appear": "出现",
    "to disappear": "消失", "to vanish": "消失", "to emerge": "出现", "to arise": "产生",
    "to seem": "似乎", "to appear": "似乎", "to look": "看起来",
    "to become": "变成", "to turn": "变成", "to grow": "变得", "to get": "变得",
    "to remain": "保持", "to stay": "停留", "to keep": "保持", "to hold": "持有",
    "to let": "让", "to allow": "允许", "to permit": "许可", "to enable": "使能够",
    "to cause": "导致", "to make": "使", "to force": "强迫", "to compel": "强迫",
    "to require": "需要", "to demand": "要求", "to request": "请求", "to order": "命令",
    "to forbid": "禁止", "to prohibit": "禁止", "to ban": "禁止", "to restrict": "限制",
    "to limit": "限制", "to control": "控制", "to manage": "管理", "to govern": "统治",
    "to rule": "统治", "to lead": "领导", "to guide": "引导", "to direct": "指导",
    "to conduct": "进行", "to carry out": "执行", "to perform": "执行", "to execute": "执行",
    "to complete": "完成", "to finish": "完成", "to accomplish": "完成", "to achieve": "实现",
    "to succeed": "成功", "to fail": "失败", "to miss": "错过", "to lose": "失去",
    "to gain": "获得", "to acquire": "获得", "to obtain": "获得", "to get": "得到",
    "to earn": "赚取", "to win": "赢得", "to receive": "收到", "to accept": "接受",
    "to reject": "拒绝", "to decline": "婉拒", "to refuse": "拒绝", "to deny": "否认",
    "to admit": "承认", "to confess": "坦白", "to acknowledge": "承认",
    "to prove": "证明", "to verify": "验证", "to confirm": "确认", "to check": "检查",
    "to test": "测试", "to examine": "检查", "to inspect": "视察", "to investigate": "调查",
    "to research": "研究", "to study": "研究", "to analyze": "分析", "to review": "回顾",
    "to evaluate": "评估", "to assess": "评估", "to judge": "判断", "to determine": "确定",
    "to decide": "决定", "to choose": "选择", "to select": "挑选", "to pick": "挑选",
    "to prefer": "更喜欢", "to favor": "偏爱", "to support": "支持", "to back": "支持",
    "to oppose": "反对", "to resist": "抵抗", "to fight": "战斗", "to battle": "战斗",
    "to attack": "攻击", "to defend": "防御", "to protect": "保护", "to guard": "守卫",
    "to save": "拯救", "to rescue": "营救", "to help": "帮助", "to assist": "协助",
    "to aid": "援助", "to serve": "服务", "to treat": "对待", "to handle": "处理",
    "to deal with": "处理", "to cope with": "应对", "to manage": "应对",
    "to solve": "解决", "to resolve": "解决", "to settle": "解决", "to fix": "修理",
    "to repair": "修复", "to mend": "修补", "to restore": "恢复", "to recover": "恢复",
    "to cure": "治愈", "to heal": "愈合", "to treat": "治疗",
    "to clean": "清洁", "to wash": "洗", "to wipe": "擦", "to sweep": "扫",
    "to dust": "除尘", "to polish": "擦亮", "to shine": "发光",
    "to arrange": "整理", "to organize": "组织", "to sort": "分类", "to classify": "分类",
    "to order": "排序", "to arrange": "安排", "to display": "展示", "to exhibit": "展览",
    "to present": "呈现", "to show": "显示", "to reveal": "揭示", "to disclose": "披露",
    "to expose": "暴露", "to uncover": "揭露", "to discover": "发现", "to find": "找到",
    "to invent": "发明", "to create": "创造", "to produce": "生产", "to manufacture": "制造",
    "to make": "制造", "to build": "建造", "to construct": "建设", "to assemble": "组装",
    "to form": "形成", "to shape": "塑造", "to design": "设计", "to plan": "计划",
    "to develop": "开发", "to improve": "改进", "to enhance": "增强", "to upgrade": "升级",
    "to update": "更新", "to modify": "修改", "to change": "改变", "to alter": "更改",
    "to adjust": "调整", "to adapt": "适应", "to fit": "适合", "to suit": "适合",
    "to match": "匹配", "to compare": "比较", "to contrast": "对比",
    "to measure": "测量", "to weigh": "称重", "to count": "计数", "to calculate": "计算",
    "to estimate": "估计", "to guess": "猜测", "to predict": "预测", "to forecast": "预报",
    "to expect": "期望", "to anticipate": "预期", "to await": "等待", "to wait": "等待",
    "to delay": "延迟", "to postpone": "推迟", "to cancel": "取消", "to quit": "退出",
    "to stop": "停止", "to pause": "暂停", "to resume": "恢复", "to continue": "继续",
    "to repeat": "重复", "to review": "复习", "to practice": "练习", "to train": "训练",
    "to exercise": "锻炼", "to work out": "锻炼",
    "to compete": "竞争", "to race": "比赛", "to play": "玩耍",
    "to enjoy": "享受", "to like": "喜欢", "to love": "爱", "to adore": "爱慕",
    "to hate": "讨厌", "to dislike": "不喜欢", "to despise": "鄙视",
    "to respect": "尊重", "to admire": "钦佩", "to appreciate": "欣赏", "to value": "重视",
    "to envy": "嫉妒", "to resent": "怨恨", "to forgive": "原谅", "to pardon": "宽恕",
    "to blame": "责备", "to accuse": "指控", "to charge": "指控", "to sue": "起诉",
    "to convict": "定罪", "to sentence": "判刑", "to punish": "惩罚", "to reward": "奖励",
    "to praise": "表扬", "to compliment": "称赞", "to flatter": "奉承",
    "to criticize": "批评", "to complain": "抱怨", "to protest": "抗议",
    "to argue": "争论", "to debate": "辩论", "to discuss": "讨论", "to negotiate": "谈判",
    "to agree": "同意", "to disagree": "不同意", "to approve": "批准", "to disapprove": "不赞成",
    "to accept": "接受", "to reject": "拒绝", "to admit": "承认", "to deny": "否认",
    "to promise": "承诺", "to guarantee": "保证", "to swear": "发誓", "to vow": "发誓",
    "to bet": "打赌", "to risk": "冒险", "to chance": "碰运气", "to dare": "胆敢",
    "to attempt": "尝试", "to try": "尝试", "to endeavor": "努力", "to strive": "奋斗",
    "to struggle": "挣扎", "to fight": "奋斗", "to work": "工作", "to labor": "劳动",
    "to earn": "赚取", "to save": "节省", "to spend": "花费", "to waste": "浪费",
    "to invest": "投资", "to borrow": "借入", "to lend": "借出", "to owe": "欠",
    "to pay": "支付", "to charge": "收费", "to bill": "开账单", "to tip": "给小费",
    "to cost": "花费", "to price": "定价", "to value": "估价", "to assess": "评估",
    "to buy": "购买", "to purchase": "购买", "to shop": "购物", "to order": "订购",
    "to sell": "出售", "to trade": "交易", "to exchange": "交换", "to swap": "交换",
    "to return": "退还", "to refund": "退款", "to exchange": "更换",
    "to deliver": "送", "to send": "发送", "to ship": "运送", "to mail": "邮寄",
    "to post": "邮寄", "to forward": "转交", "to transfer": "转移",
    "to receive": "收到", "to accept": "接收", "to collect": "收集", "to gather": "收集",
    "to welcome": "迎接", "to greet": "问候", "to meet": "见面", "to see off": "送行",
    "to visit": "访问", "to call on": "拜访", "to drop by": "顺便拜访",
    "to invite": "邀请", "to welcome": "欢迎", "to host": "招待",
    "to introduce": "介绍", "to present": "介绍", "to recommend": "推荐",
    "to suggest": "建议", "to advise": "忠告", "to propose": "提议", "to urge": "敦促",
    "to warn": "警告", "to alert": "提醒", "to remind": "提醒", "to notify": "通知",
    "to inform": "告知", "to announce": "宣布", "to declare": "宣告", "to state": "声明",
    "to express": "表达", "to convey": "传达", "to communicate": "交流", "to share": "分享",
    "to tell": "告诉", "to say": "说", "to speak": "说话", "to talk": "谈话",
    "to whisper": "低语", "to shout": "喊叫", "to yell": "大叫", "to scream": "尖叫",
    "to cry": "哭喊", "to laugh": "笑", "to smile": "微笑", "to giggle": "咯咯笑",
    "to sigh": "叹气", "to cough": "咳嗽", "to sneeze": "打喷嚏", "to yawn": "打哈欠",
    "to breathe": "呼吸", "to inhale": "吸气", "to exhale": "呼气",
    "to eat": "吃", "to bite": "咬", "to chew": "嚼", "to swallow": "吞咽",
    "to drink": "喝", "to sip": "啜饮", "to gulp": "大口喝",
    "to taste": "品尝", "to smell": "闻", "to feel": "感觉", "to touch": "触摸",
    "to see": "看见", "to look": "看", "to watch": "观看", "to observe": "观察",
    "to stare": "凝视", "to glance": "瞥", "to glare": "怒视", "to peek": "偷看",
    "to listen": "听", "to hear": "听到", "to overhear": "无意中听到",
    "to think": "思考", "to consider": "考虑", "to ponder": "沉思", "to reflect": "反思",
    "to remember": "记得", "to recall": "回忆", "to memorize": "记住", "to forget": "忘记",
    "to know": "知道", "to learn": "学习", "to study": "学习", "to teach": "教",
    "to educate": "教育", "to train": "训练", "to instruct": "指导", "to coach": "辅导",
    "to guide": "引导", "to lead": "带领", "to follow": "跟随", "to chase": "追赶",
    "to pursue": "追求", "to hunt": "狩猎", "to track": "追踪", "to trail": "尾随",
    "to escape": "逃跑", "to flee": "逃离", "to run away": "逃跑", "to hide": "躲藏",
    "to seek": "寻找", "to search": "搜索", "to look for": "寻找",
    "to find": "找到", "to discover": "发现", "to uncover": "发现", "to reveal": "揭示",
    "to open": "打开", "to close": "关", "to shut": "关闭", "to lock": "锁",
    "to unlock": "开锁", "to seal": "密封",
    "to push": "推", "to pull": "拉", "to drag": "拖", "to draw": "拉",
    "to lift": "举起", "to raise": "抬起", "to elevate": "提升", "to hoist": "升起",
    "to lower": "放下", "to drop": "掉下", "to fall": "落下", "to sink": "下沉",
    "to rise": "上升", "to ascend": "上升", "to climb": "爬", "to descend": "下降",
    "to jump": "跳", "to leap": "跳跃", "to bound": "跳跃", "to bounce": "弹跳",
    "to run": "跑", "to sprint": "冲刺", "to jog": "慢跑", "to walk": "走",
    "to step": "迈步", "to march": "行军", "to stumble": "绊倒", "to fall": "摔倒",
    "to sit": "坐", "to stand": "站", "to lie": "躺", "to kneel": "跪",
    "to bend": "弯腰", "to bow": "鞠躬", "to lean": "靠", "to rest": "休息",
    "to sleep": "睡觉", "to nap": "小睡", "to doze": "打瞌睡", "to snore": "打鼾",
    "to wake": "醒来", "to arise": "起床", "to get up": "起床",
    "to turn": "转", "to spin": "旋转", "to rotate": "旋转", "to revolve": "旋转",
    "to twist": "扭转", "to roll": "滚动", "to flip": "翻转",
    "to move": "移动", "to go": "去", "to come": "来", "to arrive": "到达",
    "to leave": "离开", "to depart": "出发", "to return": "返回", "to go back": "回去",
    "to travel": "旅行", "to journey": "旅行", "to tour": "游览", "to explore": "探索",
    "to wander": "漫游", "to roam": "闲逛", "to stroll": "散步", "to walk": "步行",
    "to drive": "驾驶", "to ride": "骑", "to fly": "飞", "to sail": "航行",
    "to swim": "游泳", "to dive": "潜水", "to float": "漂浮", "to sink": "下沉",
    "to enter": "进入", "to exit": "退出", "to pass": "通过", "to cross": "穿过",
    "to reach": "到达", "to approach": "接近", "to near": "靠近",
    "to put": "放", "to place": "放置", "to set": "设置", "to lay": "放",
    "to position": "定位", "to install": "安装", "to fit": "安装",
    "to remove": "移除", "to take off": "脱下", "to detach": "分离", "to disconnect": "断开",
    "to attach": "附上", "to connect": "连接", "to join": "连接", "to link": "链接",
    "to tie": "系", "to bind": "绑", "to fasten": "固定", "to secure": "固定",
    "to wrap": "包裹", "to fold": "折叠", "to roll": "卷", "to pack": "打包",
    "to cover": "覆盖", "to uncover": "揭开", "to wrap": "包", "to unwrap": "拆开",
    "to fill": "填满", "to empty": "倒空", "to pour": "倒", "to spill": "洒",
    "to mix": "混合", "to stir": "搅拌", "to blend": "混合", "to combine": "结合",
    "to separate": "分开", "to divide": "分割", "to split": "劈开", "to cut": "切",
    "to slice": "切片", "to chop": "剁", "to dice": "切丁", "to mince": "切碎",
    "to break": "打破", "to crack": "破裂", "to crush": "压碎", "to smash": "粉碎",
    "to tear": "撕", "to rip": "撕裂", "to shred": "撕碎",
    "to wear": "穿", "to put on": "穿上", "to dress": "穿衣", "to undress": "脱衣",
    "to wash": "洗", "to clean": "清洁", "to brush": "刷", "to comb": "梳",
    "to shave": "刮", "to cut": "剪", "to trim": "修剪", "to style": "做造型",
    "to bathe": "洗澡", "to shower": "淋浴", "to soak": "浸泡", "to rinse": "冲洗",
    "to dry": "擦干", "to wipe": "擦", "to rub": "搓", "to scrub": "刷洗",
    "to polish": "擦亮", "to shine": "擦亮", "to wax": "打蜡",
    "to cook": "烹饪", "to bake": "烤", "to roast": "烘烤", "to grill": "烧烤",
    "to fry": "煎", "to boil": "煮", "to steam": "蒸", "to simmer": "炖",
    "to heat": "加热", "to warm": "温热", "to cool": "冷却", "to freeze": "冷冻",
    "to melt": "融化", "to thaw": "解冻", "to chill": "冰镇",
    "to light": "点燃", "to burn": "燃烧", "to extinguish": "熄灭", "to put out": "扑灭",
    "to ignite": "点火", "to kindle": "点燃",
    "to blow": "吹", "to puff": "喷", "to breathe": "呼吸", "to gasp": "喘息",
    "to sing": "唱歌", "to hum": "哼", "to whistle": "吹口哨", "to play": "演奏",
    "to dance": "跳舞", "to perform": "表演", "to act": "表演", "to direct": "导演",
    "to draw": "画", "to paint": "绘画", "to sketch": "素描", "to color": "上色",
    "to write": "写", "to type": "打字", "to print": "打印", "to copy": "复制",
    "to record": "录音", "to film": "拍摄", "to photograph": "拍照", "to video": "录像",
    "to read": "读", "to scan": "扫描", "to browse": "浏览", "to skim": "略读",
    "to translate": "翻译", "to interpret": "口译", "to decode": "解码", "to encode": "编码",
}

# Additional dictionary for multi-word phrases
PHRASES = {
    "to be, to have": "是、有",
    "used for inanimate objects": "用于无生命物体",
    "to hear, to listen to, to ask": "听、倾听、询问",
    "to hear, to listen to": "听、倾听",
    "late, slow": "迟的、慢的",
    "noisy, annoying": "吵闹的、烦人的",
    "ball-point pen": "圆珠笔",
    "ball-point": "圆珠",
    "younger brother": "弟弟",
    "younger sister": "妹妹",
    "older brother": "哥哥",
    "older sister": "姐姐",
    "postage stamp": "邮票",
    "roll of film": "胶卷",
    "a vase": "花瓶",
    "et cetera": "等等",
    "well…": "嗯…",
    "well": "好的",
    "to bathe, to shower": "洗澡、淋浴",
    "inanimate objects": "无生命物体",
    "inanimate": "无生命的",
    "objects": "物体",
}

def is_chinese(text):
    """Check if text contains Chinese characters."""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def is_english(text):
    """Check if text is primarily English (ASCII letters)."""
    if not text:
        return False
    # Remove common punctuation and spaces
    cleaned = re.sub(r'[,;.\s\(\)\-\'\"…]', '', text)
    if not cleaned:
        return False
    # If it starts with ASCII letters and has no Chinese
    if is_chinese(text):
        return False
    return bool(re.match(r'^[a-zA-Z]', text))

def translate_word_by_word(text):
    """Translate English text word by word using dictionary."""
    if not text or is_chinese(text):
        return text

    # Check phrases first
    for eng, chn in sorted(PHRASES.items(), key=lambda x: -len(x[0])):
        if eng.lower() in text.lower():
            # Replace case-insensitively
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            text = pattern.sub(chn, text)

    # If already translated by phrases, check
    if is_chinese(text) and not re.search(r'[a-zA-Z]{2,}', text):
        return text

    # Split by comma/semicolon for multiple meanings
    parts = re.split(r'[,;]', text)
    translated_parts = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if is_chinese(part):
            translated_parts.append(part)
            continue

        # Remove "to " prefix for verbs
        clean = part
        if clean.lower().startswith("to "):
            clean = clean[3:]

        # Try direct lookup
        lower = clean.lower()
        if lower in DICT:
            translated_parts.append(DICT[lower])
            continue

        # Try with "to " prefix
        if ("to " + lower) in DICT:
            translated_parts.append(DICT["to " + lower])
            continue

        # Word by word
        words = clean.split()
        translated_words = []
        all_found = True
        for word in words:
            # Clean punctuation
            w = word.strip('.,!?\'\"()…')
            wl = w.lower()

            # Direct lookup
            if wl in DICT:
                translated_words.append(DICT[wl])
            # Plural
            elif wl.endswith('s') and wl[:-1] in DICT:
                translated_words.append(DICT[wl[:-1]])
            elif wl.endswith('es') and wl[:-2] in DICT:
                translated_words.append(DICT[wl[:-2]])
            # Past tense
            elif wl.endswith('ed') and wl[:-2] in DICT:
                translated_words.append(DICT[wl[:-2]])
            elif wl.endswith('ed') and wl[:-1] in DICT:
                translated_words.append(DICT[wl[:-1]])
            # Gerund
            elif wl.endswith('ing') and wl[:-3] in DICT:
                translated_words.append(DICT[wl[:-3]])
            elif wl.endswith('ing') and wl[:-3] + 'e' in DICT:
                translated_words.append(DICT[wl[:-3] + 'e'])
            # Adverb
            elif wl.endswith('ly') and wl[:-2] in DICT:
                translated_words.append(DICT[wl[:-2]])
            else:
                all_found = False
                translated_words.append(word)

        if all_found:
            translated_parts.append(''.join(translated_words))
        else:
            translated_parts.append(part)

    result = '、'.join(translated_parts)
    return result

def fix_example_translation(translation, meaning_zh):
    """Fix example translation that still contains English."""
    if not translation:
        return translation
    if is_chinese(translation) and not re.search(r'[a-zA-Z]{3,}', translation):
        return translation

    # Replace any remaining English with Chinese meaning
    result = translation
    for eng, chn in sorted(DICT.items(), key=lambda x: -len(x[0])):
        if eng.lower() in result.lower():
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            result = pattern.sub(chn, result)

    # Also try word by word
    if is_english(result):
        translated = translate_word_by_word(result)
        if translated != result:
            result = translated

    return result

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stats = {
        'meaning_translated': 0,
        'meaning_still_english': 0,
        'example_fixed': 0,
        'total_chinese': 0,
    }

    for i, line in enumerate(lines):
        if 'meaning_zh:' not in line:
            continue

        # Extract meaning_zh value
        m = re.search(r'meaning_zh:\s*"([^"]*)"', line)
        if not m:
            continue

        old_zh = m.group(1)

        # Check if still English
        if is_english(old_zh) or (not is_chinese(old_zh) and re.search(r'[a-zA-Z]{2,}', old_zh)):
            new_zh = translate_word_by_word(old_zh)
            if new_zh != old_zh and (is_chinese(new_zh) or not re.search(r'[a-zA-Z]{3,}', new_zh)):
                line = line.replace(f'meaning_zh: "{old_zh}"', f'meaning_zh: "{new_zh}"')
                stats['meaning_translated'] += 1
            else:
                stats['meaning_still_english'] += 1
        else:
            stats['total_chinese'] += 1

        # Fix example_translation if it contains English
        et = re.search(r'example_translation:\s*"([^"]*)"', line)
        if et:
            old_et = et.group(1)
            if re.search(r'[a-zA-Z]{3,}', old_et) and not old_et.startswith('http'):
                new_et = fix_example_translation(old_et, old_zh if 'old_zh' in dir() else '')
                if new_et != old_et:
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "{new_et}"')
                    stats['example_fixed'] += 1

        lines[i] = line

    # Write back
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # Final count
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        final = f.read()

    total = final.count('meaning_zh:')
    english_count = len(re.findall(r'meaning_zh:\s*"[A-Za-z]', final))
    chinese_count = total - english_count

    print(f"=== Second Pass Translation Results ===")
    print(f"Meanings translated this pass: {stats['meaning_translated']}")
    print(f"Meanings still English: {stats['meaning_still_english']}")
    print(f"Example translations fixed: {stats['example_fixed']}")
    print(f"Total words: {total}")
    print(f"Total Chinese: {chinese_count}")
    print(f"Still English: {english_count}")
    print(f"Chinese coverage: {chinese_count/total*100:.1f}%")
    print("DONE!")

if __name__ == '__main__':
    main()
