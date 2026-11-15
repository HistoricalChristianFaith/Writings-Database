import os
import re
import subprocess
from html import escape
from urllib.parse import quote

import rtoml

EXTENSIONS = ('.html', '.htm', '.pdf')
# Root-level files that are site plumbing, not works.
SKIP_ROOT_FILES = {'menu.html'}

metadata_lookup = {}


def git_files(directory):
    """Paths (relative, '/'-separated) of files committed to the repo.

    Using the git index instead of walking the disk keeps gitignored or untracked
    scratch folders (standardization/, _ref/, tmp/, ...) out of the menu. A new work
    must be `git add`-ed before it shows up.
    """
    out = subprocess.run(['git', '-C', directory, 'ls-files', '-z'],
                         check=True, capture_output=True).stdout
    paths = [p for p in out.decode('utf-8').split('\0') if p]
    return [p for p in paths if os.path.isfile(os.path.join(directory, p))]


def find_files(paths):
    matches = []
    for p in paths:
        if not p.lower().endswith(EXTENSIONS):
            continue
        if '/' not in p and p in SKIP_ROOT_FILES:
            continue
        if os.path.basename(p) == 'index.html':
            continue
        matches.append(p)
    return matches


def find_folders_with_metadata(paths, directory):
    folders = {}
    for p in paths:
        if os.path.basename(p) != 'metadata.toml':
            continue
        folder = os.path.dirname(p)
        try:
            with open(os.path.join(directory, p), 'r', encoding='utf-8') as f:
                metadata = rtoml.load(f)
        except Exception as e:
            print(f"Error reading {p}: {e}")
            continue
        default_year = metadata.get('default_year', '')
        folder_name = os.path.basename(folder)
        folder_key = f"[{default_year} AD] {folder_name}" if default_year != '' else folder_name
        folders[folder] = folder_key
        metadata_lookup[folder_key] = {
            'default_year': default_year,
            'wiki': metadata.get('wiki', ''),
        }
    return folders


def build_file_tree(files, folders):
    tree = {}
    for p in files:
        parts = p.split('/')
        current_level = tree
        for i, part in enumerate(parts[:-1]):
            dir_path = '/'.join(parts[:i + 1])
            current_level = current_level.setdefault(folders.get(dir_path, part), {})
        current_level[parts[-1]] = p
    return tree


def display_name(name, is_file):
    if is_file:
        root, ext = os.path.splitext(name)
        if ext.lower() in EXTENSIONS:
            return root
    return name


def natural(s):
    """'sermon 229b' -> ('sermon ', 229, 'b'): every number compares numerically.
    re.split with a capture group alternates str/int, so positions always match in type."""
    return tuple(int(c) if i % 2 else c for i, c in enumerate(re.split(r'(\d+)', s)))


YEAR_PREFIX = re.compile(r'\[(-?\d+) ad\] ')


def sort_key(item):
    raw, value = item
    label = display_name(raw, not isinstance(value, dict))
    name = label.lower()
    year = 0
    m = YEAR_PREFIX.match(name)
    if m:  # dated author folder "[430 AD] Augustine of Hippo": chronological
        rank, year, rest = 0, int(m.group(1)), name[m.end():]
    else:
        rest = name
        if "title " in name:
            rank = -3
        elif "preface" in name:
            rank = -2
        elif "introduction" in name:
            rank = -1
        elif "pseudo" in name:
            rank = 3
        elif "appendix" in name:
            rank = 2
        elif re.search(r'\d', name):
            rank = 0  # numbered series ("Book 10", "Sermon 229B") before plain titles
        else:
            rank = 1
    # Full name (then exact case) as tiebreakers so the order never depends on the
    # filesystem's listing order.
    return (rank, year, natural(rest), name, label)


def create_menu_html(file_tree, level=0):
    html = ''
    for name, path_or_subtree in sorted(file_tree.items(), key=sort_key):
        html += "<ul>\n"
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            metadata_url_string = ""
            if name in metadata_lookup and metadata_lookup[name]['wiki']:
                metadata_url_string = ' data-metadataurl="' + escape(metadata_lookup[name]['wiki']) + '"'
            html += ('\n<li data-jstree=\'{"icon":"fas fa-folder-open"}\'' + metadata_url_string + '>'
                     + escape(name, quote=False) + '\n'
                     + create_menu_html(path_or_subtree, level=level + 1) + '</li>')
        else:  # It's a file
            link = quote(path_or_subtree)
            label = escape(display_name(name, True), quote=False)
            html += '\n<li data-jstree=\'{"icon":"fas fa-file-alt"}\' data-fname="' + link + '">' + label + '</li>'
        html += "</ul>\n"
    return html


def main(directory):
    paths = git_files(directory)
    files = find_files(paths)
    folders_with_metadata = find_folders_with_metadata(paths, directory)
    file_tree = build_file_tree(files, folders_with_metadata)
    menu_html = create_menu_html(file_tree)

    with open(os.path.join(directory, 'menu.html'), 'w', encoding='utf-8') as f:
        f.write(menu_html)
    print("Menu HTML created successfully.")


if __name__ == "__main__":
    main('./')
