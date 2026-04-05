#!/usr/bin/env python3
"""
Obsidian知识图谱可视化生成器
扫描概念页和笔记的双链关系，生成Mermaid图表和HTML可视化页面
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict

BASE = Path.home() / "Obsidian/05-资源/AI学习"
CONCEPTS = BASE / "概念"
OUTPUT = Path.home() / ".openclaw/workspace/data/knowledge-graph"

def extract_links(filepath):
    """提取[[双链]]"""
    text = filepath.read_text(encoding='utf-8')
    return list(set(re.findall(r'\[\[([^\]]+)\]\]', text)))

def scan_concepts():
    """扫描概念页"""
    nodes = []
    edges = []
    for f in CONCEPTS.glob("*.md"):
        name = f.stem
        links = extract_links(f)
        nodes.append({"id": name, "type": "concept", "links": len(links)})
        for link in links:
            edges.append({"source": name, "target": link})
    return nodes, edges

def scan_notes():
    """扫描笔记（非概念页）"""
    nodes = []
    edges = []
    for f in BASE.rglob("*.md"):
        if CONCEPTS in f.parents:
            continue
        rel = f.relative_to(BASE)
        name = f.stem
        links = extract_links(f)
        if links:
            nodes.append({"id": name, "type": "note", "links": len(links)})
            for link in links:
                edges.append({"source": name, "target": link})
    return nodes, edges

def build_stats(concept_nodes, note_nodes, all_edges):
    """统计信息"""
    link_count = defaultdict(int)
    for e in all_edges:
        link_count[e["target"]] += 1
        link_count[e["source"]] += 1
    
    top_concepts = sorted(link_count.items(), key=lambda x: -x[1])[:15]
    return {
        "total_concepts": len(concept_nodes),
        "total_notes": len(note_nodes),
        "total_edges": len(all_edges),
        "top_linked": [{"name": n, "count": c} for n, c in top_concepts],
        "orphan_concepts": [n["id"] for n in concept_nodes if link_count[n["id"]] == 0]
    }

def generate_mermaid(concept_nodes, all_edges):
    """生成Mermaid图表（只含概念页间的关系，不含笔记）"""
    concept_ids = {n["id"] for n in concept_nodes}
    lines = ["graph LR"]
    for e in all_edges:
        if e["source"] in concept_ids and e["target"] in concept_ids:
            # Mermaid不友好字符替换
            src = e["source"].replace(" ", "_").replace("-", "_")
            tgt = e["target"].replace(" ", "_").replace("-", "_")
            lines.append(f"    {src} --> {tgt}")
    return "\n".join(lines[:200])  # 限制行数

def generate_html(stats, concept_nodes, note_nodes, all_edges):
    """生成交互式HTML可视化"""
    # 构建节点和边的数据
    concept_ids = {n["id"] for n in concept_nodes}
    nodes_data = []
    for n in concept_nodes:
        nodes_data.append({"id": n["id"], "group": "concept"})
    for n in note_nodes[:50]:  # 限制笔记数量
        nodes_data.append({"id": n["id"], "group": "note"})
    
    edges_data = []
    seen = set()
    for e in all_edges:
        key = f"{e['source']}->{e['target']}"
        if key not in seen:
            seen.add(key)
            edges_data.append({"source": e["source"], "target": e["target"]})
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>安宝知识图谱</title>
<style>
body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ color: #e94560; }}
.stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
.stat {{ background: #16213e; padding: 15px; border-radius: 8px; text-align: center; }}
.stat .num {{ font-size: 2em; color: #e94560; }}
.stat .label {{ color: #999; }}
.top-list {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }}
.top-list li {{ margin: 5px 0; }}
.bar {{ display: inline-block; background: #e94560; height: 16px; border-radius: 3px; margin-left: 10px; }}
.orphan {{ color: #ffa500; }}
</style>
</head>
<body>
<h1>🧠 安宝知识图谱</h1>
<div class="stats">
  <div class="stat"><div class="num">{stats['total_concepts']}</div><div class="label">概念页</div></div>
  <div class="stat"><div class="num">{stats['total_notes']}</div><div class="label">笔记</div></div>
  <div class="stat"><div class="num">{stats['total_edges']}</div><div class="label">双链关系</div></div>
</div>
<div class="top-list">
<h2>🔥 最被引用的概念 TOP 15</h2>
<ul>
"""
    max_count = stats["top_linked"][0]["count"] if stats["top_linked"] else 1
    for item in stats["top_linked"]:
        width = int(item["count"] / max_count * 200)
        html += f'<li>{item["name"]} <span class="bar" style="width:{width}px"></span> {item["count"]}</li>\n'
    
    html += """</ul></div>"""
    
    if stats["orphan_concepts"]:
        html += '<div class="top-list"><h2>🏝️ 孤岛概念（无引用）</h2><ul>'
        for name in stats["orphan_concepts"]:
            html += f'<li class="orphan">{name}</li>'
        html += '</ul></div>'
    
    # 概念间关系图
    concept_edges = [e for e in edges_data if e["source"] in concept_ids and e["target"] in concept_ids]
    html += f"""
<div class="top-list">
<h2>🕸️ 概念关系图（{len(concept_edges)}条边）</h2>
<div id="graph" style="background:#0f3460;border-radius:8px;padding:10px;min-height:400px;">
<p style="color:#999;text-align:center;padding-top:180px;">💡 用 <a href="https://mermaid.live" style="color:#e94560">Mermaid Live</a> 渲染以下代码：</p>
<textarea style="width:100%;height:300px;background:#1a1a2e;color:#eee;border:1px solid #333;padding:10px;font-family:monospace;font-size:12px;">
{generate_mermaid(concept_nodes, all_edges)}
</textarea>
</div>
</div>
<footer style="text-align:center;color:#666;margin-top:40px;">生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} | 安宝知识图谱 v1.0</footer>
</body></html>"""
    return html

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    print("📊 扫描概念页...")
    concept_nodes, concept_edges = scan_concepts()
    print(f"   {len(concept_nodes)} 概念, {len(concept_edges)} 关系")
    
    print("📊 扫描笔记...")
    note_nodes, note_edges = scan_notes()
    print(f"   {len(note_nodes)} 笔记, {len(note_edges)} 关系")
    
    all_edges = concept_edges + note_edges
    stats = build_stats(concept_nodes, note_nodes, all_edges)
    
    # 保存统计JSON
    with open(OUTPUT / "stats.json", "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # 保存图谱数据
    with open(OUTPUT / "graph-data.json", "w") as f:
        json.dump({"nodes": concept_nodes + note_nodes, "edges": all_edges}, f, ensure_ascii=False, indent=2)
    
    # 生成HTML
    html = generate_html(stats, concept_nodes, note_nodes, all_edges)
    with open(OUTPUT / "index.html", "w") as f:
        f.write(html)
    
    # 生成Mermaid
    mermaid = generate_mermaid(concept_nodes, all_edges)
    with open(OUTPUT / "graph.mmd", "w") as f:
        f.write(mermaid)
    
    print(f"\n✅ 知识图谱生成完成！")
    print(f"   概念: {stats['total_concepts']} | 笔记: {stats['total_notes']} | 关系: {stats['total_edges']}")
    print(f"   TOP概念: {', '.join(t['name'] for t in stats['top_linked'][:5])}")
    if stats['orphan_concepts']:
        print(f"   ⚠️ 孤岛概念: {', '.join(stats['orphan_concepts'][:5])}")
    print(f"   输出: {OUTPUT}/")

if __name__ == "__main__":
    main()
