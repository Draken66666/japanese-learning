#!/usr/bin/env python3
"""Final cleanup: fix remaining mixed translations with 1-2 char English fragments."""

import re

INPUT_FILE = "src/data/vocabulary-data.ts"

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def has_any_english(text):
    """Check if text has any English letters at all."""
    return bool(re.search(r'[a-zA-Z]', text))

def clean_final(text):
    """Final cleanup of mixed text."""
    if not text or not is_chinese(text) or not has_any_english(text):
        return text

    result = text

    # Remove standalone English articles/prepositions (1-2 char words)
    result = re.sub(r'\b[aA]\b', '', result)
    result = re.sub(r'\b[anAN]{2}\b', '', result)
    result = re.sub(r'\b[toTo]{2}\b', '', result)
    result = re.sub(r'\b[ofOF]{2}\b', '', result)
    result = re.sub(r'\b[inIN]{2}\b', '', result)
    result = re.sub(r'\b[onON]{2}\b', '', result)
    result = re.sub(r'\b[atAT]{2}\b', '', result)
    result = re.sub(r'\b[byBY]{2}\b', '', result)
    result = re.sub(r'\b[asAS]{2}\b', '', result)
    result = re.sub(r'\b[orOR]{2}\b', '、', result)
    result = re.sub(r'\b[Ii]\b', '我', result)

    # Remove standalone short English words that are clearly fragments
    result = re.sub(r'\b[a-zA-Z]{1,2}\b', '', result)

    # Clean up punctuation
    result = re.sub(r'\s+', '', result)
    result = re.sub(r'^[、,.\s]+', '', result)
    result = re.sub(r'[、,.\s]+$', '', result)
    result = re.sub(r'[、,]{2,}', '、', result)
    result = re.sub(r'^[、,]+', '', result)
    result = re.sub(r'[、,]+$', '', result)

    return result

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stats = {'fixed': 0, 'example_fixed': 0}

    for i, line in enumerate(lines):
        if 'meaning_zh:' not in line:
            continue

        # Fix meaning_zh
        m = re.search(r'meaning_zh:\s*"([^"]*)"', line)
        if m:
            old_zh = m.group(1)
            if is_chinese(old_zh) and has_any_english(old_zh):
                new_zh = clean_final(old_zh)
                if new_zh != old_zh and new_zh and is_chinese(new_zh):
                    if not has_any_english(new_zh) or not re.search(r'[a-zA-Z]{2,}', new_zh):
                        line = line.replace(f'meaning_zh: "{old_zh}"', f'meaning_zh: "{new_zh}"')
                        stats['fixed'] += 1

        # Fix example_translation
        et = re.search(r'example_translation:\s*"([^"]*)"', line)
        if et:
            old_et = et.group(1)
            if is_chinese(old_et) and has_any_english(old_et) and not old_et.startswith('http'):
                new_et = clean_final(old_et)
                if new_et != old_et and new_et and is_chinese(new_et):
                    line = line.replace(f'example_translation: "{old_et}"', f'example_translation: "{new_et}"')
                    stats['example_fixed'] += 1

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
        elif has_any_english(val):
            still_mixed += 1
        else:
            pure_chinese += 1

    print(f"=== Final Cleanup Results ===")
    print(f"Meanings fixed: {stats['fixed']}")
    print(f"Examples fixed: {stats['example_fixed']}")
    print(f"Total: {total}")
    print(f"Pure Chinese: {pure_chinese} ({pure_chinese/total*100:.1f}%)")
    print(f"Still mixed: {still_mixed} ({still_mixed/total*100:.1f}%)")
    print(f"Pure English: {pure_english} ({pure_english/total*100:.1f}%)")
    print("DONE!")

if __name__ == '__main__':
    main()
