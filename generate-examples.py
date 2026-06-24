#!/usr/bin/env python3
"""
Generate example sentences for all vocabulary words.
Outputs a JSON file that will be merged into vocabulary-data.ts
"""
import re
import json
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'vocabulary-data.ts')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'examples.json')

def is_chinese(text):
    """Check if text contains Chinese characters"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def generate_example(word):
    """Generate an example sentence for a word based on its category"""
    jp = word.get('japanese', '')
    hira = word.get('hiragana', '')
    romaji = word.get('romaji', '')
    meaning_en = word.get('meaning_en', '')
    meaning_zh = word.get('meaning_zh', '')
    category = word.get('category', '')
    
    has_chinese = is_chinese(meaning_zh)
    
    # Use Chinese meaning if available, otherwise English
    meaning = meaning_zh if has_chinese else meaning_en
    lang = 'zh' if has_chinese else 'en'
    
    if category == '名词':
        if lang == 'zh':
            return f'これは{jp}です。', f'这是{meaning}。'
        else:
            return f'This is {jp}.', f'This is {meaning}.'
    
    elif category == '动词':
        if lang == 'zh':
            return f'毎日{jp}ことをしています。', f'每天在做{meaning}。'
        else:
            return f'I {romaji} every day.', f'I {meaning} every day.'
    
    elif category == '形容词':
        if lang == 'zh':
            return f'この{jp}感じが好きです。', f'喜欢这种{meaning}的感觉。'
        else:
            return f'It is {jp}.', f'It is {meaning}.'
    
    elif category == '副词':
        if lang == 'zh':
            return f'{jp}してください。', f'请{meaning}。'
        else:
            return f'Please {romaji}.', f'Please {meaning}.'
    
    elif category == '代词':
        if lang == 'zh':
            return f'{jp}は私のです。', f'{meaning}是我的。'
        else:
            return f'{jp} is mine.', f'{meaning} is mine.'
    
    elif category == '数字':
        if lang == 'zh':
            return f'{jp}あります。', f'有{meaning}。'
        else:
            return f'There are {jp}.', f'There are {meaning}.'
    
    elif category == '接续词':
        if lang == 'zh':
            return f'{jp}、続けてください。', f'{meaning}，请继续。'
        else:
            return f'{jp}, please continue.', f'{meaning}, please continue.'
    
    elif category == '助词':
        if lang == 'zh':
            return f'これ{jp}使います。', f'用这个{meaning}。'
        else:
            return f'Use this {jp}.', f'Use this {meaning}.'
    
    else:
        # Default fallback
        if lang == 'zh':
            return f'「{jp}」は「{meaning}」という意味です。', f'「{jp}」是「{meaning}」的意思。'
        else:
            return f'"{jp}" means "{meaning}".', f'"{jp}" means "{meaning}".'


def main():
    # Read the TS file
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse each word entry
    # Pattern: { japanese: "...", hiragana: "...", ... }
    pattern = r'\{([^}]+)\}'
    
    results = []
    count = 0
    existing_count = 0
    
    for match in re.finditer(pattern, content):
        entry_str = match.group(1)
        
        # Check if it's a word entry (has japanese field)
        if 'japanese:' not in entry_str:
            continue
        
        # Extract fields
        def extract_field(name):
            m = re.search(rf'{name}:\s*"((?:[^"\\]|\\.)*)"', entry_str)
            return m.group(1) if m else ''
        
        word = {
            'japanese': extract_field('japanese'),
            'hiragana': extract_field('hiragana'),
            'romaji': extract_field('romaji'),
            'meaning_en': extract_field('meaning_en'),
            'meaning_zh': extract_field('meaning_zh'),
            'category': extract_field('category'),
        }
        
        # Check if already has example_sentence
        if 'example_sentence:' in entry_str:
            existing_count += 1
            ex_jp = extract_field('example_sentence')
            ex_zh = extract_field('example_translation')
            results.append({
                'japanese': word['japanese'],
                'example_sentence': ex_jp,
                'example_translation': ex_zh
            })
        else:
            # Generate example
            ex_jp, ex_zh = generate_example(word)
            results.append({
                'japanese': word['japanese'],
                'example_sentence': ex_jp,
                'example_translation': ex_zh
            })
            count += 1
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'Generated {count} new examples, kept {existing_count} existing examples')
    print(f'Total: {len(results)} examples')
    print(f'Output: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
