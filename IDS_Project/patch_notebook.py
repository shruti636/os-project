"""
Fixes Cell 7 (Visualizations) to use Plotly as a fallback
when matplotlib is blocked by Windows Application Control policy.
Also updates Cell 1 to install plotly.
"""
import json, os

NOTEBOOK = r'IDS_Project.ipynb'

with open(NOTEBOOK, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# ── Fix Cell 1: add plotly to the install list ────────────────────────────────
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        src = ''.join(cell.get('source', []))
        if "packages = ['pandas'" in src:
            cell['source'] = [
                "import subprocess, sys\n",
                "packages = ['pandas', 'numpy', 'scikit-learn', 'psutil',\n",
                "            'matplotlib', 'seaborn', 'plotly', 'flask', 'flask-cors']\n",
                "for pkg in packages:\n",
                "    try:\n",
                "        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'],\n",
                "                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n",
                "        print(f'  \u2705 {pkg}')\n",
                "    except Exception as e:\n",
                "        print(f'  \u26a0\ufe0f {pkg}: {e}')\n",
                "print('\\nAll packages processed!')\n",
            ]
            break

# ── Fix Cell 7: replace matplotlib with plotly fallback ───────────────────────
new_viz_source = """\
# ── Try matplotlib first; fall back to Plotly if Windows blocks the DLL ──────
_USE_PLOTLY = False
try:
    import matplotlib
    matplotlib.use('Agg')          # non-interactive backend avoids some DLL issues
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    _USE_PLOTLY = False
except Exception as _e:
    print(f"matplotlib blocked ({_e}). Switching to Plotly...")
    _USE_PLOTLY = True

if not _USE_PLOTLY:
    # ── Matplotlib / Seaborn charts ───────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('IDS \u2014 Model Analysis', fontsize=16, fontweight='bold')

    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Malicious'],
                yticklabels=['Normal', 'Malicious'], ax=axes[0])
    axes[0].set_title('Confusion Matrix')
    axes[0].set_xlabel('Predicted'); axes[0].set_ylabel('Actual')

    metrics = {'Accuracy': acc, 'Precision': prec, 'Recall': rec, 'F1': f1}
    colors  = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
    bars = axes[1].bar(metrics.keys(), metrics.values(), color=colors, edgecolor='white')
    axes[1].set_ylim(0, 1.1)
    axes[1].set_title('Performance Metrics')
    for bar, val in zip(bars, metrics.values()):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                     f'{val:.3f}', ha='center', fontweight='bold')

    counts = df['label'].value_counts()
    axes[2].pie(counts.values, labels=['Normal', 'Malicious'],
                colors=['#4CAF50', '#F44336'], autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 12})
    axes[2].set_title('Dataset Distribution')

    plt.tight_layout()
    os.makedirs('data', exist_ok=True)
    plt.savefig('data/ids_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    print('\u2705 Chart saved \u2192 data/ids_analysis.png')

else:
    # ── Plotly charts (no DLLs, works even when Windows blocks matplotlib) ────
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from IPython.display import display

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=['Confusion Matrix', 'Performance Metrics', 'Dataset Distribution'],
        specs=[[{'type': 'heatmap'}, {'type': 'bar'}, {'type': 'pie'}]]
    )

    # Confusion matrix heatmap
    fig.add_trace(
        go.Heatmap(z=cm, x=['Normal','Malicious'], y=['Normal','Malicious'],
                   colorscale='Blues', showscale=False,
                   text=cm, texttemplate='%{text}', textfont={"size": 18}),
        row=1, col=1
    )

    # Metrics bar chart
    metric_names  = ['Accuracy', 'Precision', 'Recall', 'F1']
    metric_values = [acc, prec, rec, f1]
    fig.add_trace(
        go.Bar(x=metric_names, y=metric_values,
               marker_color=['#4CAF50','#2196F3','#FF9800','#9C27B0'],
               text=[f'{v:.3f}' for v in metric_values],
               textposition='outside'),
        row=1, col=2
    )

    # Dataset distribution pie
    counts = df['label'].value_counts()
    fig.add_trace(
        go.Pie(labels=['Normal','Malicious'], values=counts.values,
               marker_colors=['#4CAF50','#F44336'],
               textinfo='label+percent'),
        row=1, col=3
    )

    fig.update_layout(
        title_text='\U0001f6e1\ufe0f IDS \u2014 Model Analysis',
        height=450, showlegend=False,
        paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
        font=dict(color='white')
    )
    fig.show()
    print('\u2705 Interactive Plotly chart displayed (matplotlib was blocked by Windows policy)')
"""

for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        src = ''.join(cell.get('source', []))
        if 'sns.heatmap' in src or '_USE_PLOTLY' in src:
            cell['source'] = new_viz_source
            cell['outputs'] = []
            print("  → Fixed Cell 7 (Visualizations)")
            break

with open(NOTEBOOK, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Done! Cell 7 now uses Plotly when matplotlib is blocked.")
