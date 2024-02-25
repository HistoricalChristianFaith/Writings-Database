import os
import rtoml

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
    html = ''
    for name, path_or_subtree in sorted(file_tree.items(), key=lambda x: x[0]):
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            html += f'<details><summary>{name}</summary>{create_menu_html(path_or_subtree, level=level+1)}</details>'
        else:  # It's a file
            link = path_or_subtree.replace('\\', '/')
            html += f'<div><a href="{link}" target="contentFrame">{name}</a></div>'
    return html

def main(directory):
    extensions = ['.html', '.pdf', '.md']
    files = find_files(directory, extensions)
    folders_with_metadata = find_folders_with_metadata(directory)
    file_tree = build_file_tree(files, folders_with_metadata, directory)
    menu_html = create_menu_html(file_tree)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Navigator</title>
    <style>
        body {{ display: flex; }}
        #menu {{ width: 20%; height: 100vh; overflow: auto; padding-left: 10px; }}
        #content {{ flex-grow: 1; }}
        details > div, details > details {{ padding-left: 20px; }}
        details, summary {{ cursor: pointer; }}
    </style>
</head>
<body>
    <div id="menu">{menu_html}</div>
    <iframe id="content" name="contentFrame" style="width: 80%; height: 100vh;"></iframe>
</body>
</html>
        ''')
    print("Index HTML created successfully.")

if __name__ == "__main__":
    main('./')
