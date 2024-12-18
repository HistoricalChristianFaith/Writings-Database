import os
import rtoml
from urllib.parse import quote
import re

metadata_lookup = {}

def find_files(directory, extensions):
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions) and file != 'metadata.toml':
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start=directory)
                matches.append((full_path, relative_path))
    return matches

def find_folders_with_metadata(directory):
    folders = {}
    for root, dirs, files in os.walk(directory, topdown=True):
        if 'metadata.toml' in files:
            try:
                with open(os.path.join(root, 'metadata.toml'), 'r', encoding='utf-8') as f:
                    metadata = rtoml.load(f)
                default_year = metadata.get('default_year', '')
                folder_name = os.path.basename(root)
                if default_year:
                    folder_key = f"[{default_year} AD] {folder_name}"
                else:
                    folder_key = folder_name
                folders[root] = folder_key
                metadata_lookup[folder_key] = {
                    'default_year': metadata.get('default_year', ''),
                    'wiki': metadata.get('wiki', '')
                }
            except Exception as e:
                print(f"Error reading metadata.toml in {root}: {e}")
    return folders

def build_file_tree(files, folders, directory):
    tree = {}
    for full_path, relative_path in files:
        parts = relative_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:
            dir_path = os.path.join(directory, *parts[:parts.index(part)+1])
            if dir_path in folders:
                part = folders[dir_path]  # Use the formatted name from metadata
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = os.path.join(*parts)
    return tree

def create_menu_html(file_tree, level=0):
    def sort_key(item):
        name = item[0].lower()  # Convert the name to lowercase to ensure case-insensitive comparison

        # Check for special keywords in the name
        if "title " in name:
            return (-3, name)  # Priority for items with "title"
        elif "preface" in name:
            return (-2, name)  # Priority for items with "preface"
        elif "introduction" in name:
            return (-1, name)  # Priority for items with "introduction"
        elif "pseudo" in name and "[" not in name:
            return (3, name)  # Lower priority for items with "pseudo"
        elif "appendix" in name:
            return (2, name)  # Lower priority for items with "pseudo"

        # General pattern matching for items with trailing numbers (like "Book 10", "Similitude 2")
        match = re.search(r'(\D+)(\d+)', name)
        if match:
            text_part = match.group(1).strip()  # The non-digit part of the name
            number_part = int(match.group(2))  # The numeric part, converted to integer
            return (0, text_part, number_part)  # Sort by text first, then by number

        # Attempt to extract year from the folder name
        if name.startswith('[') and ']' in name:
            try:
                year = int(name[1:name.find(' ')].strip())
                return (0, year)  # Prioritize numeric sorting
            except ValueError:
                pass  # If conversion fails, fall back to the original name

        return (1, name)  # Non-numeric names are sorted alphabetically

    html = ''
    for name, path_or_subtree in sorted(file_tree.items(), key=sort_key):
        html += "<ul>\n"
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            metadata_url_string = ""
            if name in metadata_lookup and metadata_lookup[name]['wiki']:
                metadata_url_string = ' data-metadataurl="'+metadata_lookup[name]['wiki']+'"'
            html += '\n<li data-jstree=\'{"icon":"fas fa-folder-open"}\''+metadata_url_string+'>'+name+'\n'+create_menu_html(path_or_subtree, level=level+1)+'</li>'
        else:  # It's a file
            if name != "index.html":
                link = quote(path_or_subtree.replace('\\', '/'))
                name = name.replace(".html", "")
                html += '\n<li data-jstree=\'{"icon":"fas fa-file-alt"}\' data-fname="'+link+'">'+name+'</li>'
        html += "</ul>\n"
    return html


def main(directory):
    extensions = ['.html', '.pdf', '.htm']
    files = find_files(directory, extensions)
    folders_with_metadata = find_folders_with_metadata(directory)
    file_tree = build_file_tree(files, folders_with_metadata, directory)
    menu_html = create_menu_html(file_tree)
    
    with open('menu.html', 'w', encoding='utf-8') as f:
        f.write(menu_html)
    print("Menu HTML created successfully.")

if __name__ == "__main__":
    main('./')
