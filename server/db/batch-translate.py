#!/usr/bin/env python3
"""
Batch translate remaining English meanings to Chinese using MyMemory API.
Updates vocabulary-data.js in place.
"""

import json
import os
import time
import urllib.request
import urllib.parse
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_FILE = os.path.join(SCRIPT_DIR, 'vocabulary-data.js')
CACHE_FILE = os.path.join(SCRIPT_DIR, 'zh_translation_cache.json')

# Load cache
cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f"Loaded {len(cache)} cached translations")

# SSL context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def translate_mymemory(text, retries=3):
    """Translate using MyMemory API."""
    if not text or len(text) > 450:
        return None

    # Check cache
    if text in cache:
        return cache[text]

    for attempt in range(retries):
        try:
            encoded = urllib.parse.quote(text)
            url = f'https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh-CN&de=japaneselearning@example.com'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, context=ctx, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))

            if data.get('responseStatus') == 200 or data.get('responseData', {}).get('status') == 200:
                translated = data['responseData']['translatedText']
                # Clean up
                if translated and translated != text and not translated.startswith('MYMEMORY WARNING'):
                    cache[text] = translated
                    return translated

            # Check for quota limit
            if 'MYMEMORY WARNING' in str(data.get('responseData', {}).get('translatedText', '')):
                print(f"  API quota limit reached!")
                return None

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None

        time.sleep(0.3)

    return None


def main():
    # Parse vocabulary-data.js to get the data
    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the array data between [ and ];
    start = content.index('[')
    end = content.rindex(']')
    array_str = content[start:end+1]

    # Use a simple approach: find all meaning_en and meaning_zh pairs
    import re

    # Find all entries with their line numbers
    lines = content.split('\n')
    updated_count = 0
    total_to_translate = 0

    # First pass: count how many need translation
    for line in lines:
        if 'meaning_en:' in line and 'meaning_zh:' in line:
            # Extract meanings
            en_match = re.search(r'meaning_en:\s*"((?:[^"\\]|\\.)*)"', line)
            zh_match = re.search(r'meaning_zh:\s*"((?:[^"\\]|\\.)*)"', line)
            if en_match and zh_match:
                en = en_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
                zh = zh_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
                if en == zh:  # Needs translation
                    total_to_translate += 1

    print(f"Total words needing translation: {total_to_translate}")
    print(f"Starting batch translation...\n")

    # Second pass: translate
    for i, line in enumerate(lines):
        if 'meaning_en:' not in line or 'meaning_zh:' not in line:
            continue

        en_match = re.search(r'meaning_en:\s*"((?:[^"\\]|\\.)*)"', line)
        zh_match = re.search(r'meaning_zh:\s*"((?:[^"\\]|\\.)*)"', line)
        if not en_match or not zh_match:
            continue

        en = en_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
        zh = zh_match.group(1).replace('\\"', '"').replace('\\\\', '\\')

        if en != zh:
            continue  # Already translated

        # Translate
        translated = translate_mymemory(en)
        if translated and translated != en:
            # Escape for JS
            translated_escaped = translated.replace('\\', '\\\\').replace('"', '\\"')
            old_zh = zh_match.group(0)
            new_zh = f'meaning_zh: "{translated_escaped}"'
            lines[i] = line.replace(old_zh, new_zh)
            updated_count += 1

            if updated_count % 100 == 0:
                print(f"  Progress: {updated_count}/{total_to_translate} translated")
                # Save cache
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False)
                # Save partial vocabulary file
                with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

        # Check if we hit quota
        if translated is None and en not in cache:
            print(f"  Stopping at {updated_count} translations (API limit or error)")
            break

    # Save final results
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)

    print(f"\nBatch translation complete!")
    print(f"Translated: {updated_count}")
    print(f"Cache size: {len(cache)}")


if __name__ == '__main__':
    main()
