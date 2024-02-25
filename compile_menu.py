import os

def find_files(directory, extensions):
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start=directory)
                matches.append((full_path, relative_path))
    return matches

def build_file_tree(files):
    tree = {}
    for full_path, relative_path in files:
        parts = relative_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:  # Navigate/create subdirectories.
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = relative_path  # Set the file at the correct place in the tree.
    return tree

def create_menu_html(file_tree, base_path='', level=0):
    html = ''
    indent = '  ' * level  # Increase indentation for nested items
    for name, path_or_subtree in file_tree.items():
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            html += f'{indent}<details><summary>{name}</summary>{create_menu_html(path_or_subtree, base_path=base_path, level=level+1)}</details>'
        else:  # It's a file
            # Ensure base_path is used correctly to avoid duplicate folder names
            if level == 0:  # At root level, include the name in the path
                link = os.path.join(base_path, name).replace('\\', '/')
            else:  # For nested items, the path is already included
                link = os.path.join(base_path, path_or_subtree).replace('\\', '/')
            html += f'{indent}<div><a href="{link}" target="contentFrame">{name}</a></div>'
    return html

def main(directory):
    extensions = ['.html', '.pdf', '.md']
    files = find_files(directory, extensions)
    file_tree = build_file_tree(files)
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
    print("Menu HTML created successfully.")

if __name__ == "__main__":
    main('./')