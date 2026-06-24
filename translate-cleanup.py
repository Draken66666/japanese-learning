#!/usr/bin/env python3
"""Clean up mixed Chinese-English translations.
If meaning_zh has both Chinese and English (3+ letters), either:
1. Try to translate the remaining English
2. If can't, revert to pure English (better than mixed garbage)
"""

import re

INPUT_FILE = "src/data/vocabulary-data.ts"

# Final dictionary for cleanup
FINAL_DICT = {
    # Articles/prepositions to strip
    "a": "", "an": "", "the": "", "to": "", "of": "", "for": "", "in": "",
    "on": "", "at": "", "by": "", "with": "", "from": "", "as": "",
    "or": "、", "and": "、", "but": "但",

    # Common words
    "part-time": "兼职", "job": "工作", "work": "工作",
    "many": "许多", "much": "多", "possible": "可能的",
    "thought": "想", "absolutely": "绝对地",
    "suffix": "后缀", "familiar": "熟悉的", "female": "女性", "person": "人",
    "jam": "果酱", "glass": "玻璃", "pan": "平底锅", "baking": "烘焙",
    "petrol": "汽油", "station": "站", "gas": "汽油", "gasoline": "汽油",
    "finally": "最后", "after": "之后", "all": "全部",
    "hindrance": "妨碍", "intrusion": "侵入",
    "rubbish": "垃圾", "garbage": "垃圾", "trash": "垃圾",
    "feast": "盛宴", "banquet": "宴会",
    "steak": "牛排", "owe": "欠", "owing": "欠",
    "smell": "闻", "scent": "香味", "odor": "气味",
    "surprised": "惊讶的",
    "drink": "喝", "beverage": "饮料",
    "last": "最后", "end": "结束",
    "I": "我", "me": "我", "my": "我的",
    "old": "旧的", "new": "新的",
    "not": "不", "used": "用于", "people": "人",
    "be": "是", "understood": "被理解",
    "America": "美国", "American": "美国的",
    "bookshelf": "书架", "bookshelves": "书架",
    "greengrocer": "蔬菜水果店",
    "western": "西式", "style": "式样", "clothes": "衣服",
    "cuisine": "料理", "cooking": "烹饪",
    "automobile": "汽车", "vehicle": "车辆",
    "oneself": "自己", "yourself": "你自己",
    "skillful": "熟练的", "skilful": "熟练的",
    "likeable": "讨人喜欢的",
    "bustling": "热闹的", "busy": "忙碌的",
    "luke": "微", "warm": "温暖",
    "spacious": "宽敞的", "wide": "宽的",
    "entry": "入口", "dining": "用餐", "hall": "大厅",
    "midday": "中午", "meal": "一餐",
    "splendid": "出色的", "sufficient": "足够的",
    "ashtray": "烟灰缸", "aeroplane": "飞机",
    "stereo": "立体声", "announcer": "播音员",
    "pickpocket": "扒手", "occasionally": "偶尔",
    "unskillful": "不熟练的",
    "ball-point": "圆珠", "pen": "笔",
    "younger": "年幼的", "older": "年长的",
    "brother": "兄弟", "sister": "姐妹",
    "postage": "邮费", "stamp": "邮票",
}

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def has_english_words(text, min_len=3):
    """Check if text has English words of min_len or more characters."""
    # Find all English letter sequences
    matches = re.findall(r'[a-zA-Z]+', text)
    for m in matches:
        if len(m) >= min_len:
            return True
    return False

def clean_mixed(text):
    """Clean up mixed Chinese-English text."""
    if not text:
        return text

    # If purely Chinese, return as-is
    if is_chinese(text) and not has_english_words(text, 2):
        return text

    # If purely English (no Chinese at all), return as-is
    if not is_chinese(text):
        return text

    # Mixed: try to translate remaining English words
    result = text

    # Replace known English words with Chinese
    words = re.findall(r'[a-zA-Z]+', result)
    for word in sorted(words, key=len, reverse=True):
        wl = word.lower()
        if wl in FINAL_DICT:
            replacement = FINAL_DICT[wl]
            if replacement:
                result = re.sub(re.escape(word), replacement, result, flags=re.IGNORECASE)
            else:
                # Strip articles/prepositions
                result = re.sub(r'\b' + re.escape(word) + r'\b', '', result, flags=re.IGNORECASE)

    # Clean up: remove extra spaces, fix punctuation
    result = re.sub(r'\s+', '', result)
    result = re.sub(r'^[、,.\s]+', '', result)
    result = re.sub(r'[、,.\s]+$', '', result)
    result = re.sub(r'[、,]{2,}', '、', result)

    # Check if still mixed
    if has_english_words(result, 3):
        # Still has English - if it has Chinese too, it's still mixed
        # Try one more pass with broader dictionary
        for eng, chn in sorted(FINAL_DICT.items(), key=lambda x: -len(x[0])):
            if eng and len(eng) >= 2:
                result = re.sub(re.escape(eng), chn, result, flags=re.IGNORECASE)

        result = re.sub(r'\s+', '', result)
        result = re.sub(r'^[、,.\s]+', '', result)
        result = re.sub(r'[、,.\s]+$', '', result)

        # If STILL mixed, just keep the Chinese parts
        if has_english_words(result, 3) and is_chinese(result):
            # Extract Chinese characters and join
            chinese_parts = re.findall(r'[\u4e00-\u9fff、，。]+', result)
            if chinese_parts:
                result = ''.join(chinese_parts)
                result = re.sub(r'^[、,]+', '', result)
                result = re.sub(r'[、,]+$', '', result)

    return result

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stats = {'fixed': 0, 'unchanged': 0}

    for i, line in enumerate(lines):
        if 'meaning_zh:' not in line:
            continue

        m = re.search(r'meaning_zh:\s*"([^"]*)"', line)
        if not m:
            continue

        old_zh = m.group(1)

        # Only process mixed entries (both Chinese and English)
        if is_chinese(old_zh) and has_english_words(old_zh, 2):
            new_zh = clean_mixed(old_zh)
            if new_zh != old_zh and new_zh:
                line = line.replace(f'meaning_zh: "{old_zh}"', f'meaning_zh: "{new_zh}"')
                stats['fixed'] += 1
            else:
                stats['unchanged'] += 1
        else:
            stats['unchanged'] += 1

        # Also fix example_translation
        et = re.search(r'example_translation:\s*"([^"]*)"', line)
        if et:
            old_et = et.group(1)
            if is_chinese(old_et) and has_english_words(old_et, 3):
                new_et = clean_mixed(old_et)
                if new_et != old_et and new_et:
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "{new_et}"')

        lines[i] = line

    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # Final count
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        final = f.read()

    total = final.count('meaning_zh:')
    english_start = len(re.findall(r'meaning_zh:\s*"[A-Za-z]', final))

    # Count truly Chinese (no English words 3+ chars)
    chinese_count = 0
    mixed_count = 0
    for m in re.finditer(r'meaning_zh:\s*"([^"]*)"', final):
        val = m.group(1)
        if is_chinese(val) and not has_english_words(val, 3):
            chinese_count += 1
        elif is_chinese(val) and has_english_words(val, 3):
            mixed_count += 1

    pure_english = total - chinese_count - mixed_count

    print(f"=== Cleanup Results ===")
    print(f"Fixed: {stats['fixed']}")
    print(f"Unchanged: {stats['unchanged']}")
    print(f"Total: {total}")
    print(f"Pure Chinese: {chinese_count}")
    print(f"Mixed (Chinese+English): {mixed_count}")
    print(f"Pure English: {pure_english}")
    print(f"Chinese coverage: {(chinese_count+mixed_count)/total*100:.1f}% (including mixed)")
    print(f"Pure Chinese coverage: {chinese_count/total*100:.1f}%")
    print("DONE!")

if __name__ == '__main__':
    main()
