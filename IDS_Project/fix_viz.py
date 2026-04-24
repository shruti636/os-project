import json, os

NOTEBOOK = r'IDS_Project.ipynb'
with open(NOTEBOOK, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Fix Cell 1: add plotly to installs
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        src = ''.join(cell.get('source', []))
        if 'packages = [' in src and 'matplotlib' in src and 'plotly' not in src:
            cell['source'] = (
                'import subprocess, sys\n'
                'packages = ["pandas", "numpy", "scikit-learn", "psutil",\n'
                '            "matplotlib", "seaborn", "plotly", "flask", "flask-cors"]\n'
                'for pkg in packages:\n'
                '    try:\n'
                '        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],\n'
                '                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n'
                '        print(f"  OK: {pkg}")\n'
                '    except Exception as e:\n'
                '        print(f"  WARN {pkg}: {e}")\n'
                'print("All packages processed!")\n'
            )
            print("Fixed Cell 1 (added plotly)")
            break

# New Cell 7 source with plotly fallback
new_viz = (
    'import os\n'
    '\n'
    '# Try matplotlib first; fall back to Plotly if blocked by Windows security\n'
    '_USE_PLOTLY = False\n'
    'try:\n'
    '    import matplotlib\n'
    '    matplotlib.use("Agg")  # non-interactive backend\n'
    '    import matplotlib.pyplot as plt\n'
    '    import seaborn as sns\n'
    'except Exception as _e:\n'
    '    print(f"matplotlib unavailable: {_e}")\n'
    '    print("Switching to Plotly (no DLLs needed)...")\n'
    '    _USE_PLOTLY = True\n'
    '\n'
    'if not _USE_PLOTLY:\n'
    '    fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n'
    '    fig.suptitle("IDS Model Analysis", fontsize=16, fontweight="bold")\n'
    '    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",\n'
    '                xticklabels=["Normal","Malicious"],\n'
    '                yticklabels=["Normal","Malicious"], ax=axes[0])\n'
    '    axes[0].set_title("Confusion Matrix")\n'
    '    axes[0].set_xlabel("Predicted"); axes[0].set_ylabel("Actual")\n'
    '    metrics = {"Accuracy": acc, "Precision": prec, "Recall": rec, "F1": f1}\n'
    '    colors  = ["#4CAF50","#2196F3","#FF9800","#9C27B0"]\n'
    '    bars = axes[1].bar(metrics.keys(), metrics.values(), color=colors, edgecolor="white")\n'
    '    axes[1].set_ylim(0, 1.1)\n'
    '    axes[1].set_title("Performance Metrics")\n'
    '    for bar, val in zip(bars, metrics.values()):\n'
    '        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.02,\n'
    '                     f"{val:.3f}", ha="center", fontweight="bold")\n'
    '    counts = df["label"].value_counts()\n'
    '    axes[2].pie(counts.values, labels=["Normal","Malicious"],\n'
    '                colors=["#4CAF50","#F44336"], autopct="%1.1f%%",\n'
    '                startangle=90, textprops={"fontsize": 12})\n'
    '    axes[2].set_title("Dataset Distribution")\n'
    '    plt.tight_layout()\n'
    '    os.makedirs("data", exist_ok=True)\n'
    '    plt.savefig("data/ids_analysis.png", dpi=150, bbox_inches="tight")\n'
    '    plt.show()\n'
    '    print("Chart saved to data/ids_analysis.png")\n'
    'else:\n'
    '    import plotly.graph_objects as go\n'
    '    from plotly.subplots import make_subplots\n'
    '    fig = make_subplots(\n'
    '        rows=1, cols=3,\n'
    '        subplot_titles=["Confusion Matrix","Performance Metrics","Dataset Distribution"],\n'
    '        specs=[[{"type":"heatmap"},{"type":"bar"},{"type":"pie"}]]\n'
    '    )\n'
    '    # Confusion matrix\n'
    '    fig.add_trace(go.Heatmap(\n'
    '        z=cm, x=["Normal","Malicious"], y=["Normal","Malicious"],\n'
    '        colorscale="Blues", showscale=False,\n'
    '        text=cm, texttemplate="%{text}", textfont={"size":18}), row=1, col=1)\n'
    '    # Metrics bar\n'
    '    m_names  = ["Accuracy","Precision","Recall","F1"]\n'
    '    m_values = [acc, prec, rec, f1]\n'
    '    fig.add_trace(go.Bar(\n'
    '        x=m_names, y=m_values,\n'
    '        marker_color=["#4CAF50","#2196F3","#FF9800","#9C27B0"],\n'
    '        text=[f"{v:.3f}" for v in m_values], textposition="outside"), row=1, col=2)\n'
    '    # Dataset pie\n'
    '    counts = df["label"].value_counts()\n'
    '    fig.add_trace(go.Pie(\n'
    '        labels=["Normal","Malicious"], values=counts.values,\n'
    '        marker_colors=["#4CAF50","#F44336"]), row=1, col=3)\n'
    '    fig.update_layout(\n'
    '        title_text="IDS Model Analysis", height=420, showlegend=False,\n'
    '        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="white")\n'
    '    )\n'
    '    fig.show()\n'
    '    print("Interactive Plotly chart shown (used because OS blocked matplotlib DLLs)")\n'
)

fixed = False
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        src = ''.join(cell.get('source', []))
        if 'sns.heatmap' in src or '_USE_PLOTLY' in src:
            cell['source'] = new_viz
            cell['outputs'] = []
            fixed = True
            print("Fixed Cell 7 (Visualizations with Plotly fallback)")
            break

if not fixed:
    print("WARNING: Could not find Cell 7 to fix!")

with open(NOTEBOOK, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Done - notebook updated.")
