#!/usr/bin/env python3
"""
Merge generated example sentences into vocabulary-data.ts
"""
import re
import json
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'vocabulary-data.ts')
EXAMPLES_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'examples.json')

def escape_for_js(text):
    """Escape special characters for JavaScript string"""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

def main():
    # Read examples
    with open(EXAMPLES_FILE, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    
    # Create lookup: japanese -> (example_sentence, example_translation)
    example_map = {}
    for ex in examples:
        example_map[ex['japanese']] = (ex['example_sentence'], ex['example_translation'])
    
    # Read the TS file
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each line
    lines = content.split('\n')
    new_lines = []
    modified_count = 0
    
    for line in lines:
        if 'japanese:' not in line or 'is_premium:' not in line:
            new_lines.append(line)
            continue
        
        # Check if already has example_sentence
        if 'example_sentence:' in line:
            new_lines.append(line)
            continue
        
        # Extract japanese word
        jp_match = re.search(r'japanese:\s*"([^"]*)"', line)
        if not jp_match:
            new_lines.append(line)
            continue
        
        jp_word = jp_match.group(1)
        
        # Find example
        if jp_word not in example_map:
            new_lines.append(line)
            continue
        
        ex_jp, ex_zh = example_map[jp_word]
        ex_jp_escaped = escape_for_js(ex_jp)
        ex_zh_escaped = escape_for_js(ex_zh)
        
        # Insert example_sentence and example_translation before is_premium
        new_line = line.replace(
            'is_premium:',
            f'example_sentence: "{ex_jp_escaped}", example_translation: "{ex_zh_escaped}", is_premium:'
        )
        new_lines.append(new_line)
        modified_count += 1
    
    # Write output
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f'Modified {modified_count} entries')
    print(f'File size: {os.path.getsize(INPUT_FILE) / 1024:.1f} KB')

if __name__ == '__main__':
    main()
