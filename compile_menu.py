import os
import rtoml

def find_files_and_folders(directory, extensions):
    matches = []
    folders = {}
    for root, dirs, files in os.walk(directory, topdown=True):
        # Only process metadata.toml at the root level of each folder
        if 'metadata.toml' in files:
            metadata_path = os.path.join(root, 'metadata.toml')
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = rtoml.load(f)
                default_year = metadata.get('default_year', '')
                folder_name = os.path.basename(root)
                folders[root] = (folder_name, default_year)
            except Exception as e:
                print(f"Error reading metadata.toml in {root}: {e}")

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start=directory)
                matches.append((full_path, relative_path))

    return matches, folders

def build_file_tree(files, folders, directory):
    tree = {}
    # Insert folders with metadata first, sorted by year
    for path, (folder_name, default_year) in sorted(folders.items(), key=lambda x: x[1][1]):
        relative_path = os.path.relpath(path, start=directory)
        tree_key = f"[{default_year} AD] {folder_name}" if default_year else folder_name
        tree[tree_key] = {}
    
    # Now insert files into the tree
    for _, relative_path in files:
        parts = relative_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:
            # Skip over directory names that have been replaced with the formatted key
            if part in folders:
                continue
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = relative_path
    return tree

def create_menu_html(file_tree, level=0):
    html = ''
    indent = '  ' * level  # Increase indentation for nested items
    for name, path_or_subtree in sorted(file_tree.items(), key=lambda x: x[0]):
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            html += f'{indent}<details><summary>{name}</summary>{create_menu_html(path_or_subtree, level=level+1)}</details>'
        else:  # It's a file
            link = path_or_subtree.replace('\\', '/')
            html += f'{indent}<div><a href="{link}" target="contentFrame">{name}</a></div>'
    return html

def main(directory):
    extensions = ['.html', '.pdf', '.md']
    files, folders = find_files_and_folders(directory, extensions)
    file_tree = build_file_tree(files, folders, directory)
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
