#!/usr/bin/env python3
"""Translate English meanings to Chinese and fix example sentences."""
import re, json, time, urllib.request, urllib.parse, os

INPUT = 'src/data/vocabulary-data.ts'
CACHE = 'translation_cache.json'

# Load cache
cache = {}
if os.path.exists(CACHE):
    with open(CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f'Cache: {len(cache)} entries')

def is_english(text):
    if not text: return True
    return len(re.findall(r'[a-zA-Z]', text)) / max(len(text), 1) > 0.5

def api_translate(text):
    if text in cache: return cache[text]
    try:
        url = f'https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|zh'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read())
        tr = data['responseData']['translatedText']
        if tr and not tr.startswith('PLEASE') and len(tr) > 0:
            cache[text] = tr
            return tr
    except: pass
    return None

def gen_example(jp, zh, cat):
    jp_c = jp.split('/')[0].strip()
    if '動詞' in cat or cat == '动词':
        return f'{jp_c}のは楽しいです。', f'{zh}是一件有趣的事。'
    elif '形容詞' in cat or cat == '形容词':
        return f'{jp_c}ですね。', f'真是{zh}呢。'
    elif '副詞' in cat or cat == '副词':
        return f'{jp_c}行きます。', f'{zh}去。'
    else:
        return f'{jp_c}は便利です。', f'{zh}很方便。'

# Read file
with open(INPUT, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse entries
pat = r'\{ japanese: "(.*?)", hiragana: "(.*?)", romaji: "(.*?)", meaning_en: "(.*?)", meaning_zh: "(.*?)", jlpt_level: "(.*?)", category: "(.*?)", example_sentence: "(.*?)", example_translation: "(.*?)", is_premium: (\d+) \}'
matches = list(re.finditer(pat, content))
print(f'Total: {len(matches)}')

# Collect unique English texts needing translation
need_tr = set()
for m in matches:
    if is_english(m.group(5)):  # meaning_zh is English
        need_tr.add(m.group(4))  # meaning_en
print(f'Unique texts to translate: {len(need_tr)}')

# Translate all unique texts
translations = {}
api_count = 0
for i, text in enumerate(sorted(need_tr)):
    if text in cache:
        translations[text] = cache[text]
        continue
    if api_count >= 800:  # API rate limit
        break
    tr = api_translate(text)
    if tr:
        translations[text] = tr
        api_count += 1
        if api_count % 50 == 0:
            print(f'  API translated: {api_count}, saving cache...')
            with open(CACHE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False)
        time.sleep(0.3)

# Save cache
with open(CACHE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False)
print(f'API translations: {api_count}')
print(f'Total translations available: {len(translations) + sum(1 for t in need_tr if t in cache)}')

# Now rebuild the file
new_lines = []
last_end = 0
translated_count = 0
still_english = 0
examples_fixed = 0

for m in matches:
    # Add text before this match
    new_lines.append(content[last_end:m.start()])
    last_end = m.end()

    jp = m.group(1)
    hiragana = m.group(2)
    romaji = m.group(3)
    en = m.group(4)
    zh = m.group(5)
    level = m.group(6)
    cat = m.group(7)
    ex_jp = m.group(8)
    ex_zh = m.group(9)
    prem = m.group(10)

    # Fix meaning_zh
    if is_english(zh):
        if en in translations:
            zh = translations[en]
            translated_count += 1
        elif en in cache:
            zh = cache[en]
            translated_count += 1
        else:
            still_english += 1

    # Fix example sentences
    if is_english(ex_jp) or is_english(ex_zh):
        ex_jp, ex_zh = gen_example(jp, zh, cat)
        examples_fixed += 1

    new_lines.append(f'{{ japanese: "{jp}", hiragana: "{hiragana}", romaji: "{romaji}", meaning_en: "{en}", meaning_zh: "{zh}", jlpt_level: "{level}", category: "{cat}", example_sentence: "{ex_jp}", example_translation: "{ex_zh}", is_premium: {prem} }}')

# Add remaining content
new_lines.append(content[last_end:])

# Write output
result = ''.join(new_lines)
with open(INPUT, 'w', encoding='utf-8') as f:
    f.write(result)

print(f'\nDone!')
print(f'Translated: {translated_count}')
print(f'Still English: {still_english}')
print(f'Examples fixed: {examples_fixed}')
print(f'Cache size: {len(cache)}')
