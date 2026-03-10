#!/usr/bin/env python3
import os
import re

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VERSE_PATTERN = re.compile(r'^(1 Cor\. \d+:\d+)–(\d+\.\s+)', re.MULTILINE)

for filename in sorted(os.listdir(DIRECTORY)):
    if not filename.endswith('.txt'):
        continue

    filepath = os.path.join(DIRECTORY, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = VERSE_PATTERN.sub(r'\1-\2', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count = content.count('–') - new_content.count('–')
        print(f"{filename}: replaced {count} en-dash(es) in verse references")
    else:
        print(f"{filename}: no changes needed")
