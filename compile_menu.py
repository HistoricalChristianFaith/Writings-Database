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
    def sort_key(item):
        name = item[0]
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
        if isinstance(path_or_subtree, dict):  # It's a subdirectory
            html += f'\n<details><summary>{name}</summary>{create_menu_html(path_or_subtree, level=level+1)}</details>'
        else:  # It's a file
            if name != "index.html":
                link = path_or_subtree.replace('\\', '/')
                name = name.replace(".html", "")
                html += f'\n<div><a href="#" onclick="loadFile(\'{link}\')">{name}</a></div>'
    return html


def main(directory):
    extensions = ['.html', '.pdf']
    files = find_files(directory, extensions)
    folders_with_metadata = find_folders_with_metadata(directory)
    file_tree = build_file_tree(files, folders_with_metadata, directory)
    menu_html = create_menu_html(file_tree)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Historical Christian Faith - Writings Database</title>
    <style>
        body { display: flex; }
        #menu { width: 20%; height: 100vh; overflow: auto; padding-left: 10px; }
        #content { flex-grow: 1; }
        details > div, details > details { padding-left: 20px; }
        details, summary { cursor: pointer; }
    </style>
    <script>
        function loadFile(filePath) {
            document.getElementById('content').removeAttribute('srcdoc');
            console.log("Loading file...", filePath)
            document.getElementById('content').src = filePath;
            const url = new URL(window.location);
            url.searchParams.set('file', filePath);
            window.history.pushState({}, '', url);
        }

        window.onload = function() {
            const urlParams = new URLSearchParams(window.location.search);
            const file = urlParams.get('file');
            if (file) {
                console.log("Onload: file...", file)
                document.getElementById('content').removeAttribute('srcdoc');
                document.getElementById('content').src = file;
            }
        };
    </script>
</head>
<body>
    <div id="menu">
        <h3><a target='_blank' href='https://historicalchristian.faith/'>Historical Christian Faith</a></h3>
        <h4><a target='_blank' href='https://github.com/HistoricalChristianFaith/Writings-Database/'>Writings Database</a></h4>
        ''' + menu_html + '''
        <br><br><br>
    </div>
    <iframe id="content" name="contentFrame" style="width: 80%; height: 100vh;" srcdoc="<p>Click on a writing on the left menu to open it here!</p><p>Note: This database is open source, and everything is in the public domain! <a target='_blank' href='https://github.com/HistoricalChristianFaith/Writings-Database/'>Contribute/fix typos here!</a></p>"></iframe>
    <script>
    document.getElementById('content').addEventListener('load', function() {
        // Make any links clicked inside the iframe open up in a new tab, instead of in the iframe.
        var iframe = document.getElementById('content');
        if(iframe.contentDocument) {
            var links = iframe.contentDocument.getElementsByTagName('a');
            for (var i = 0; i < links.length; i++) {
                //TODO: Fix, this breaks TOC href links (perhaps exclude # links? Or perhaps add _blank to each page's proper links)
                //links[i].target = '_blank';
            }
        }
    });
    </script>
</body>
</html>
        ''')
    print("Index HTML created successfully.")

if __name__ == "__main__":
    main('./')
