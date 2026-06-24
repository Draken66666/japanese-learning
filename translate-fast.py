#!/usr/bin/env python3
"""Fast multi-threaded translation using MyMemory API."""
import re, json, time, urllib.request, urllib.parse, os
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT = 'src/data/vocabulary-data.ts'
CACHE = 'translation_cache.json'

cache = {}
if os.path.exists(CACHE):
    with open(CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f'Loaded cache: {len(cache)} entries', flush=True)

def is_english(text):
    if not text: return True
    return len(re.findall(r'[a-zA-Z]', text)) / max(len(text), 1) > 0.5

def api_translate(text):
    if text in cache: return cache[text]
    try:
        url = f'https://api.mymemory.translated.net/get?q={urllib.parse.quote(text[:500])}&langpair=en|zh'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        tr = data.get('responseData', {}).get('translatedText', '')
        if tr and not tr.startswith('PLEASE') and not tr.startswith('MYMEMORY WARNING'):
            cache[text] = tr
            return tr
    except Exception as e:
        pass
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

with open(INPUT, 'r', encoding='utf-8') as f:
    content = f.read()

pat = r'\{ japanese: "(.*?)", hiragana: "(.*?)", romaji: "(.*?)", meaning_en: "(.*?)", meaning_zh: "(.*?)", jlpt_level: "(.*?)", category: "(.*?)", example_sentence: "(.*?)", example_translation: "(.*?)", is_premium: (\d+) \}'
matches = list(re.finditer(pat, content))
print(f'Total words: {len(matches)}', flush=True)

need_tr = set()
for m in matches:
    if is_english(m.group(5)):
        need_tr.add(m.group(4))

already = sum(1 for t in need_tr if t in cache)
todo = [t for t in need_tr if t not in cache]
print(f'Need translation: {len(need_tr)} (cached: {already}, todo: {len(todo)})', flush=True)

# Multi-threaded translation with 10 workers
BATCH_SIZE = 200
MAX_API = 2000
api_count = 0

for batch_start in range(0, min(len(todo), MAX_API), BATCH_SIZE):
    batch = todo[batch_start:batch_start+BATCH_SIZE]
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(api_translate, t): t for t in batch}
        for future in as_completed(futures):
            result = future.result()
            if result:
                api_count += 1
    # Save cache after each batch
    with open(CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)
    print(f'Batch {batch_start//BATCH_SIZE+1}: {api_count}/{len(todo)} translated, cache: {len(cache)}', flush=True)

print(f'API calls: {api_count}, total cache: {len(cache)}', flush=True)

# Apply translations and fix examples
new_lines = []
last_end = 0
tr_count = 0
still_en = 0
ex_fixed = 0

for m in matches:
    new_lines.append(content[last_end:m.start()])
    last_end = m.end()

    jp, hiragana, romaji = m.group(1), m.group(2), m.group(3)
    en, zh = m.group(4), m.group(5)
    level, cat = m.group(6), m.group(7)
    ex_jp, ex_zh = m.group(8), m.group(9)
    prem = m.group(10)

    if is_english(zh):
        if en in cache:
            zh = cache[en]
            tr_count += 1
        else:
            still_en += 1

    if is_english(ex_jp) or is_english(ex_zh):
        ex_jp, ex_zh = gen_example(jp, zh, cat)
        ex_fixed += 1

    new_lines.append(f'{{ japanese: "{jp}", hiragana: "{hiragana}", romaji: "{romaji}", meaning_en: "{en}", meaning_zh: "{zh}", jlpt_level: "{level}", category: "{cat}", example_sentence: "{ex_jp}", example_translation: "{ex_zh}", is_premium: {prem} }}')

new_lines.append(content[last_end:])

with open(INPUT, 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print(f'\nDONE! Translated: {tr_count}, Still English: {still_en}, Examples fixed: {ex_fixed}', flush=True)
