#!/usr/bin/env python3
"""Revert mixed garbage translations to pure English.
Better to have clean English than mixed Chinese-English garbage."""

import re

INPUT_FILE = "src/data/vocabulary-data.ts"

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def has_english_words(text, min_len=2):
    return bool(re.search(r'[a-zA-Z]{2,}', text))

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stats = {'reverted_meaning': 0, 'reverted_example': 0}

    for i, line in enumerate(lines):
        if 'meaning_zh:' not in line:
            continue

        # Extract meaning_en and meaning_zh
        en_match = re.search(r'meaning_en:\s*"([^"]*)"', line)
        zh_match = re.search(r'meaning_zh:\s*"([^"]*)"', line)

        if en_match and zh_match:
            meaning_en = en_match.group(1)
            meaning_zh = zh_match.group(1)

            # If meaning_zh is mixed (both Chinese and English words 2+ chars)
            if is_chinese(meaning_zh) and has_english_words(meaning_zh, 2):
                # Revert to English meaning
                line = line.replace(f'meaning_zh: "{meaning_zh}"', f'meaning_zh: "{meaning_en}"')
                stats['reverted_meaning'] += 1

        # Also fix example_translation mixed garbage
        et_match = re.search(r'example_translation:\s*"([^"]*)"', line)
        if et_match:
            old_et = et_match.group(1)
            if is_chinese(old_et) and has_english_words(old_et, 3):
                # For example translations, just remove the English parts
                # and keep the Chinese
                cleaned = re.sub(r'[a-zA-Z]+', '', old_et)
                cleaned = re.sub(r'\s+', '', cleaned)
                cleaned = re.sub(r'^[、,.\s]+', '', cleaned)
                cleaned = re.sub(r'[、,.\s]+$', '', cleaned)
                cleaned = re.sub(r'[、,]{2,}', '、', cleaned)

                if cleaned and is_chinese(cleaned):
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "{cleaned}"')
                else:
                    # If no Chinese left, use a generic translation
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "请参考释义。"' )
                stats['reverted_example'] += 1

        lines[i] = line

    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # Final count
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        final = f.read()

    total = final.count('meaning_zh:')
    pure_chinese = 0
    still_mixed = 0
    pure_english = 0

    for m in re.finditer(r'meaning_zh:\s*"([^"]*)"', final):
        val = m.group(1)
        if not is_chinese(val):
            pure_english += 1
        elif has_english_words(val, 2):
            still_mixed += 1
        else:
            pure_chinese += 1

    print(f"=== Revert Mixed to English Results ===")
    print(f"Meanings reverted to English: {stats['reverted_meaning']}")
    print(f"Examples cleaned: {stats['reverted_example']}")
    print(f"Total: {total}")
    print(f"Pure Chinese: {pure_chinese} ({pure_chinese/total*100:.1f}%)")
    print(f"Still mixed: {still_mixed} ({still_mixed/total*100:.1f}%)")
    print(f"Pure English: {pure_english} ({pure_english/total*100:.1f}%)")
    print("DONE!")

if __name__ == '__main__':
    main()
