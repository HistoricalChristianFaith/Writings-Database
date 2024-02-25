import os

def find_files(directory, extensions):
    """
    Recursively finds all files in `directory` with extensions in `extensions`.
    Returns a list of (path, relative_path) tuples.
    """
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start=directory)
                matches.append((full_path, relative_path))
    return matches

def create_menu_html(files, base_directory):
    """
    Creates the HTML content for the nested menu.
    `files` is a list of (path, relative_path) tuples.
    """
    html = '<ul>'
    for _, relative_path in files:
        link = os.path.join(base_directory, relative_path).replace('\\', '/')
        html += f'<li><a href="{link}" target="contentFrame">{relative_path}</a></li>'
    html += '</ul>'
    return html

def main(directory):
    extensions = ['.html', '.pdf', '.md']
    files = find_files(directory, extensions)
    menu_html = create_menu_html(files, directory)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Navigator</title>
    <style>
        body {{ display: flex; }}
        #menu {{ width: 20%; height: 100vh; overflow: auto; }}
        #content {{ flex-grow: 1; }}
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