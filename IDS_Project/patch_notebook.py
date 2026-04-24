"""
Rebuilds IDS_Project.ipynb to be 100% self-contained.
Adds a Cell 2 that writes all project files to disk,
so only the .ipynb file needs to be shared.
"""
import json, os, textwrap

NOTEBOOK = r'IDS_Project.ipynb'
BASE     = os.path.dirname(os.path.abspath(NOTEBOOK))

# ── Read every project file we need to embed ──────────────────────────────────
def read(rel):
    with open(os.path.join(BASE, rel), 'r', encoding='utf-8') as f:
        return f.read()

files = {
    'utils.py':               read('utils.py'),
    'feature_extraction.py':  read('feature_extraction.py'),
    'data_collection.py':     read('data_collection.py'),
    'malware_simulator.py':   read('malware_simulator.py'),
    'model_training.py':      read('model_training.py'),
    'detector.py':            read('detector.py'),
    'real_time_collector.py': read('real_time_collector.py'),
    'main.py':                read('main.py'),
    'app.py':                 read('app.py'),
    'templates/index.html':   read('templates/index.html'),
}

# ── Build the source for the "Write Files" cell ───────────────────────────────
lines = [
    "import os\n",
    "\n",
    "# This cell writes every project file to disk.\n",
    "# It runs automatically so the notebook works on ANY laptop\n",
    "# even if you only have the .ipynb file.\n",
    "\n",
    "os.makedirs('templates', exist_ok=True)\n",
    "os.makedirs('data',      exist_ok=True)\n",
    "os.makedirs('models',    exist_ok=True)\n",
    "\n",
    "_files = {}\n",
]

for fname, content in files.items():
    # Represent file content as a raw string safely
    safe = content.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
    lines.append(f'_files[{fname!r}] = """{safe}"""\n')

lines += [
    "\n",
    "for _path, _content in _files.items():\n",
    "    _dir = os.path.dirname(_path)\n",
    "    if _dir:\n",
    "        os.makedirs(_dir, exist_ok=True)\n",
    "    with open(_path, 'w', encoding='utf-8') as _f:\n",
    "        _f.write(_content)\n",
    "\n",
    "print(f'✅ {len(_files)} project files written to disk.')\n",
    "print('   Files:', ', '.join(_files.keys()))\n",
]

write_cell = {
    'cell_type': 'code',
    'execution_count': None,
    'id': 'cell_write_files',
    'metadata': {},
    'outputs': [],
    'source': lines,
}

write_md = {
    'cell_type': 'markdown',
    'id': 'cell_write_files_md',
    'metadata': {},
    'source': [
        '## 📁 Cell 2 — Write All Project Files\n',
        '\n',
        'This cell **recreates every project file** from code embedded in this notebook.\n',
        'Run it once and all the `.py` modules and the dashboard HTML are ready.\n',
        '\n',
        '> This makes the notebook **fully portable** — just share the `.ipynb` file!',
    ],
}

# ── Also fix / replace the Flask launcher cell (Cell 11) ──────────────────────
flask_source = """\
import subprocess, sys, os, time, socket

# ── Find or use current project directory ─────────────────────────────────────
PROJECT_DIR = os.getcwd()
if not os.path.exists(os.path.join(PROJECT_DIR, "app.py")):
    # Walk up the tree to find it
    candidate = PROJECT_DIR
    for _ in range(6):
        parent = os.path.dirname(candidate)
        if parent == candidate: break
        candidate = parent
        if os.path.exists(os.path.join(candidate, "app.py")):
            PROJECT_DIR = candidate
            break

os.chdir(PROJECT_DIR)
print(f"Project directory: {PROJECT_DIR}")

FLASK_PORT = 5000

def _port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

if _port_open(FLASK_PORT):
    print(f"IDS server already running on port {FLASK_PORT}")
else:
    print("Starting IDS Flask server ...")
    subprocess.Popen(
        [sys.executable, os.path.join(PROJECT_DIR, "app.py")],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(40):
        time.sleep(0.5)
        if _port_open(FLASK_PORT):
            print("IDS server is LIVE!")
            break
    else:
        print("WARNING: Server did not respond in 20s.")

from IPython.display import IFrame, display, HTML
link = f"http://127.0.0.1:{FLASK_PORT}"
display(HTML(
    '<h3>\\U0001f6e1\\ufe0f IDS Live Dashboard &mdash; '
    f'<a href="{link}" target="_blank">Open in new tab \\U0001f517</a></h3>'
))
display(IFrame(src=link, width="100%", height=760))
print(f"Dashboard: {link}")
"""

flask_cell = {
    'cell_type': 'code',
    'execution_count': None,
    'id': 'cell_flask_code',
    'metadata': {},
    'outputs': [],
    'source': flask_source,
}

flask_md = {
    'cell_type': 'markdown',
    'id': 'cell_flask_md',
    'metadata': {},
    'source': [
        '## \U0001f310 Cell 11 — Launch the Full IDS Live Dashboard\n',
        '\n',
        'Starts the Flask IDS backend and embeds the live dashboard inside the notebook.\n',
        '\n',
        '> Dashboard auto-refreshes every 1.5 s with live detection events.',
    ],
}

# ── Load the notebook ──────────────────────────────────────────────────────────
with open(NOTEBOOK, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove old injected cells
def is_injected(cell):
    ids = {'cell_write_files', 'cell_write_files_md', 'cell_flask_md', 'cell_flask_code'}
    if cell.get('id') in ids:
        return True
    src = ''.join(cell.get('source', []))
    return 'FLASK_PORT' in src or '_files[' in src

nb['cells'] = [c for c in nb['cells'] if not is_injected(c)]

# Insert Write-Files cell right after Cell 1 (install cell)
nb['cells'].insert(2, write_cell)
nb['cells'].insert(2, write_md)

# Insert Flask launcher before the last markdown
last_pos = len(nb['cells']) - 1
nb['cells'].insert(last_pos, flask_cell)
nb['cells'].insert(last_pos, flask_md)

with open(NOTEBOOK, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Done! Notebook is now 100% self-contained.")
print(f"Share only:  IDS_Project.ipynb")
print(f"New cell 2 writes {len(files)} project files automatically.")
