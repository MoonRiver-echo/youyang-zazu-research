#!/usr/bin/env python3
"""Single-file SQL Explorer for 酉阳杂俎 narrative category statistics."""

import sqlite3
import webbrowser
import threading
from flask import Flask, render_template_string, request, jsonify

DB_PATH = r"C:\Users\lx\Desktop\前期准备\prepare\narrative_category_stats.db"

app = Flask(__name__)

# ── Preset queries ──
PRESETS = [
    ("分类排行", "SELECT * FROM v_category_ranking"),
    ("分类层级", "SELECT * FROM v_category_hierarchy"),
    ("全部分类", "SELECT id, name, description, sort_order FROM categories ORDER BY sort_order"),
    ("版本信息", "SELECT * FROM editions"),
    ("段落总数", "SELECT SUM(paragraph_count) AS total_paragraphs, ROUND(SUM(percentage),2) AS total_pct FROM category_stats"),
    ("占比 > 5%", "SELECT c.name AS category, cs.paragraph_count, ROUND(cs.percentage,2) AS pct FROM category_stats cs JOIN categories c ON cs.category_id = c.id WHERE cs.percentage > 5 ORDER BY cs.percentage DESC"),
    ("占比 < 1%", "SELECT c.name AS category, cs.paragraph_count, ROUND(cs.percentage,2) AS pct FROM category_stats cs JOIN categories c ON cs.category_id = c.id WHERE cs.percentage < 1 ORDER BY cs.percentage"),
]

# ── Table metadata ──
def get_table_info():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    tables = []
    for row in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ):
        tbl = row[0]
        cols = []
        for col in cur.execute(f"PRAGMA table_info('{tbl}')"):
            cols.append({"name": col[1], "type": col[2], "notnull": bool(col[3]), "pk": bool(col[5])})
        count = cur.execute(f"SELECT COUNT(*) FROM '{tbl}'").fetchone()[0]
        tables.append({"name": tbl, "columns": cols, "row_count": count})
    conn.close()
    return tables

# ── Execute SQL ──
def execute_sql(sql, params=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        if cur.description:
            columns = [d[0] for d in cur.description]
            rows = [dict(r) for r in cur.fetchall()]
        else:
            columns = []
            rows = []
            conn.commit()
        error = None
    except Exception as e:
        columns = []
        rows = []
        error = str(e)
    finally:
        conn.close()
    return columns, rows, error

# ── HTML ──
HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>酉阳杂俎 · SQL Explorer</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
    --success: #3fb950; --error: #f85149; --warning: #d29922;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
    background: var(--bg); color: var(--text);
    min-height: 100vh; padding: 20px;
  }
  h1 {
    font-size: 1.4rem; margin-bottom: 4px;
    background: linear-gradient(135deg, var(--accent), #a371f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .subtitle { color: var(--muted); font-size: 0.8rem; margin-bottom: 16px; }
  .layout { display: grid; grid-template-columns: 240px 1fr; gap: 16px; }
  @media (max-width: 768px) { .layout { grid-template-columns: 1fr; } }

  /* Sidebar */
  .sidebar { display: flex; flex-direction: column; gap: 12px; }
  .panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px; font-size: 0.8rem;
  }
  .panel-title {
    color: var(--accent); font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 8px; font-weight: 600;
  }
  .table-badge {
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 8px; margin: 3px 0; border-radius: 4px;
    background: var(--bg); cursor: pointer; transition: background 0.15s;
  }
  .table-badge:hover { background: #1f2937; }
  .table-badge .tname { color: var(--text); }
  .table-badge .tcount { color: var(--muted); font-size: 0.7rem; }
  .col-list { padding-left: 12px; margin-top: 4px; }
  .col-item { color: var(--muted); font-size: 0.75rem; line-height: 1.6; }
  .col-item .ctype { color: #6e7681; font-size: 0.65rem; }
  .col-item .ckey { color: var(--warning); font-size: 0.65rem; }
  .preset-btn {
    display: block; width: 100%; text-align: left;
    padding: 6px 10px; margin: 3px 0; border-radius: 4px;
    background: var(--bg); border: 1px solid var(--border);
    color: var(--text); font-size: 0.78rem; cursor: pointer;
    font-family: inherit; transition: all 0.15s;
  }
  .preset-btn:hover { background: #1f2937; border-color: var(--accent); }

  /* Main */
  .main { display: flex; flex-direction: column; gap: 12px; }
  .editor {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden;
  }
  .editor-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 12px; background: #1c2128; border-bottom: 1px solid var(--border);
  }
  .editor-bar span { color: var(--muted); font-size: 0.75rem; }
  textarea {
    width: 100%; min-height: 100px; padding: 12px;
    background: transparent; color: var(--text); border: none;
    font-family: inherit; font-size: 0.85rem; resize: vertical;
    outline: none; tab-size: 2;
  }
  .btn-row { display: flex; gap: 8px; padding: 8px 12px; background: #1c2128; border-top: 1px solid var(--border); }
  .btn {
    padding: 6px 16px; border-radius: 6px; border: 1px solid var(--border);
    font-family: inherit; font-size: 0.8rem; cursor: pointer; transition: all 0.15s;
  }
  .btn-run { background: #238636; color: #fff; border-color: #2ea043; }
  .btn-run:hover { background: #2ea043; }
  .btn-clear { background: transparent; color: var(--muted); }
  .btn-clear:hover { color: var(--text); background: var(--border); }
  .btn-export { background: transparent; color: var(--accent); border-color: var(--accent); }
  .btn-export:hover { background: #1c3a5e; }

  /* Results */
  .result-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 0; font-size: 0.75rem; color: var(--muted);
  }
  .result-bar .error { color: var(--error); }
  .result-bar .ok { color: var(--success); }
  .result-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; overflow: auto; max-height: 60vh;
  }
  table {
    width: 100%; border-collapse: collapse; font-size: 0.8rem;
  }
  th {
    position: sticky; top: 0; background: #1c2128;
    padding: 8px 12px; text-align: left; color: var(--accent);
    border-bottom: 2px solid var(--border); white-space: nowrap;
  }
  td {
    padding: 6px 12px; border-bottom: 1px solid var(--border);
    max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  tr:hover td { background: #1c2128; }
  .null-val { color: #484f58; font-style: italic; }

  /* Schema DDL */
  .ddl-section { margin-top: 4px; }
  .ddl-toggle {
    color: var(--accent); cursor: pointer; font-size: 0.78rem;
    text-decoration: underline; text-underline-offset: 2px;
  }
  .ddl-block {
    display: none; margin-top: 8px; padding: 12px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; white-space: pre-wrap; font-size: 0.75rem;
    color: var(--muted); max-height: 400px; overflow: auto;
  }
  .ddl-block.show { display: block; }

  .empty-state {
    text-align: center; padding: 40px 20px;
    color: var(--muted); font-size: 0.85rem;
  }
  .empty-state .icon { font-size: 2rem; margin-bottom: 8px; }
</style>
</head>
<body>
<h1>酉阳杂俎 · SQL Explorer</h1>
<p class="subtitle">Narrative Category Statistics — 据注三次修订</p>

<div class="layout">
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="panel">
      <div class="panel-title">Tables</div>
      {% for t in tables %}
        <div class="table-badge" onclick="runSQL('SELECT * FROM {{ t.name }} LIMIT 100')">
          <span class="tname">{{ t.name }}</span>
          <span class="tcount">{{ t.row_count }} rows</span>
        </div>
        <div class="col-list">
          {% for c in t.columns %}
            <div class="col-item">
              {{ c.name }}
              <span class="ctype">{{ c.type or '-' }}</span>
              {% if c.pk %}<span class="ckey">PK</span>{% endif %}
              {% if c.notnull %}<span class="ckey">NOT NULL</span>{% endif %}
            </div>
          {% endfor %}
        </div>
      {% endfor %}
    </div>

    <div class="panel">
      <div class="panel-title">Presets</div>
      {% for label, sql in presets %}
        <button class="preset-btn" onclick="runSQL({{ sql|tojson }})">{{ label }}</button>
      {% endfor %}
    </div>
  </div>

  <!-- Main -->
  <div class="main">
    <div class="editor">
      <div class="editor-bar">
        <span>SQL</span>
        <span>Ctrl+Enter to run</span>
      </div>
      <textarea id="sql-input" spellcheck="false" placeholder="SELECT * FROM categories&#10;WHERE paragraph_count > 50&#10;ORDER BY paragraph_count DESC">SELECT * FROM v_category_ranking</textarea>
      <div class="btn-row">
        <button class="btn btn-run" onclick="executeQuery()">▶ Run</button>
        <button class="btn btn-clear" onclick="clearEditor()">✕ Clear</button>
        <button class="btn btn-export" onclick="exportCSV()">⬇ CSV</button>
      </div>
    </div>

    <div class="result-bar" id="result-bar"></div>

    <div class="result-wrap" id="result-wrap">
      <div class="empty-state" id="empty-state">
        <div class="icon">🔍</div>
        Run a query to see results
      </div>
    </div>

    <div class="ddl-section">
      <span class="ddl-toggle" onclick="toggleDDL()">Show Schema DDL</span>
      <div class="ddl-block" id="ddl-block">{{ ddl }}</div>
    </div>
  </div>
</div>

<script>
let lastColumns = [];
let lastRows = [];

function runSQL(sql) {
  document.getElementById('sql-input').value = sql;
  executeQuery();
}

async function executeQuery() {
  const sql = document.getElementById('sql-input').value.trim();
  if (!sql) return;
  const res = await fetch('/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({sql})
  });
  const data = await res.json();
  const bar = document.getElementById('result-bar');
  const wrap = document.getElementById('result-wrap');
  const emptyState = document.getElementById('empty-state');

  if (data.error) {
    bar.innerHTML = '<span class="error">⚠ ' + data.error + '</span>';
    wrap.innerHTML = '';
    emptyState && (emptyState.style.display = 'none');
    return;
  }

  lastColumns = data.columns || [];
  lastRows = data.rows || [];
  bar.innerHTML = '<span class="ok">✓ ' + lastRows.length + ' rows</span>'
    + '<span>' + lastColumns.length + ' columns · ' + data.time_ms + 'ms</span>';

  if (lastRows.length === 0) {
    wrap.innerHTML = '<div class="empty-state"><div class="icon">∅</div>0 rows returned</div>';
    return;
  }

  let html = '<table><thead><tr>';
  lastColumns.forEach(c => { html += '<th>' + c + '</th>'; });
  html += '</tr></thead><tbody>';
  lastRows.forEach(row => {
    html += '<tr>';
    lastColumns.forEach(c => {
      const v = row[c];
      html += '<td>' + (v === null ? '<span class="null-val">NULL</span>' : escHtml(String(v))) + '</td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  wrap.innerHTML = html;
}

function clearEditor() {
  document.getElementById('sql-input').value = '';
}

function exportCSV() {
  if (!lastColumns.length) return;
  let csv = lastColumns.join(',') + '\\n';
  lastRows.forEach(row => {
    csv += lastColumns.map(c => {
      let v = row[c];
      if (v === null) return '';
      v = String(v);
      if (v.includes(',') || v.includes('"') || v.includes('\\n')) {
        return '"' + v.replace(/"/g, '""') + '"';
      }
      return v;
    }).join(',') + '\\n';
  });
  const blob = new Blob(['\\uFEFF' + csv], {type: 'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'query_result.csv';
  a.click();
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function toggleDDL() {
  document.getElementById('ddl-block').classList.toggle('show');
}

document.getElementById('sql-input').addEventListener('keydown', function(e) {
  if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); executeQuery(); }
});

// Auto-run initial query
executeQuery();
</script>
</body>
</html>"""


@app.route("/")
def index():
    tables = get_table_info()
    # Collect DDL
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ddl_parts = []
    for row in cur.execute(
        "SELECT name, sql FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ):
        ddl_parts.append(f"-- {row[0]}\n{row[1]};\n")
    conn.close()

    return render_template_string(
        HTML,
        tables=tables,
        presets=PRESETS,
        ddl="\n".join(ddl_parts),
    )


@app.route("/api/query", methods=["POST"])
def api_query():
    import time
    data = request.get_json()
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"error": "Empty query", "columns": [], "rows": [], "time_ms": 0})

    # Safety: block destructive statements
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "ATTACH", "DETACH"]
    first_word = sql.lstrip().split()[0].upper() if sql.strip() else ""
    # Allow SELECT and PRAGMA only
    if first_word not in ("SELECT", "PRAGMA", "WITH", "EXPLAIN"):
        blocked = any(kw in sql.upper().split() for kw in forbidden)
        if blocked or first_word not in ("SELECT", "PRAGMA", "WITH", "EXPLAIN"):
            return jsonify({"error": f"Statement type '{first_word}' not allowed. Read-only queries only.", "columns": [], "rows": [], "time_ms": 0})

    t0 = time.time()
    columns, rows, error = execute_sql(sql)
    elapsed = round((time.time() - t0) * 1000, 1)
    if error:
        return jsonify({"error": error, "columns": [], "rows": [], "time_ms": elapsed})
    return jsonify({"columns": columns, "rows": rows, "time_ms": elapsed, "error": None})


if __name__ == "__main__":
    port = 5217
    url = f"http://localhost:{port}"
    print(f"酉阳杂俎 SQL Explorer → {url}")

    def open_browser():
        import time; time.sleep(1.2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=port, debug=False)