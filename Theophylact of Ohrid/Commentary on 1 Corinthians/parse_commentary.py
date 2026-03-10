#!/usr/bin/env python3
import os
import re
import json

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VERSE_PATTERN = re.compile(r'^(1 Cor\. \d+:\d+(?:[–\-]\d+)?)\.\s+')

for filename in sorted(os.listdir(DIRECTORY)):
    if not filename.endswith('.txt'):
        continue

    filepath = os.path.join(DIRECTORY, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    entries = []
    current_ref = None
    commentary_lines = []

    for line in lines:
        match = VERSE_PATTERN.match(line)
        if match:
            # Save previous entry
            if current_ref and commentary_lines:
                entries.append({current_ref: '\n'.join(commentary_lines)})
            current_ref = match.group(1)
            commentary_lines = []
        elif current_ref is not None and line.strip():
            commentary_lines.append(line)

    # Save last entry
    if current_ref and commentary_lines:
        entries.append({current_ref: '\n'.join(commentary_lines)})

    if entries:
        json_filename = filename.replace('.txt', '.json')
        json_filepath = os.path.join(DIRECTORY, json_filename)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print(f"Created {json_filename} with {len(entries)} entries")
    else:
        print(f"Skipped {filename} (no verse entries found)")
