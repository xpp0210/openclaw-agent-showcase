#!/usr/bin/env python3
"""
wiki-ingest.py — Obsidian LLM Wiki Ingest引擎
新笔记进入时自动：提取概念 → 补双链 → 更新概念页

用法:
  wiki-ingest.py <file>              # 处理单个文件
  wiki-ingest.py --scan              # 扫描所有无双链的笔记
  wiki-inggest.py --lint             # 健康检查
"""

import os
import re
import sys
import json
import glob
from pathlib import Path
from datetime import datetime

OBSIDIAN = os.path.expanduser("~/Obsidian/05-资源/AI学习")
CONCEPTS_DIR = os.path.join(OBSIDIAN, "概念")

# 已知概念列表（从概念页目录动态加载）
def load_concepts():
    """加载所有概念页名"""
    concepts = {}
    if not os.path.isdir(CONCEPTS_DIR):
        return concepts
    for f in os.listdir(CONCEPTS_DIR):
        if f.endswith(".md") and f != "README.md":
            name = f[:-3]
            concepts[name] = os.path.join(CONCEPTS_DIR, f)
    return concepts

def extract_title(filepath):
    """从文件提取标题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # frontmatter title
    m = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # first heading
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return Path(filepath).stem

def add_backlinks(filepath, concepts):
    """给单个文件添加双链，返回添加数量"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not os.path.basename(filepath).endswith('.md') or os.path.basename(filepath) == 'README.md':
        return 0
    
    added = 0
    for concept_name in concepts:
        # 已有双链则跳过
        if f"[[{concept_name}]]" in content:
            continue
        
        # 在frontmatter之后的正文中，找第一次出现的概念名
        # 跳过frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            preamble = "---" + parts[1] + "---"
            body = parts[2]
        else:
            preamble = ""
            body = content
        
        # 概念名精确匹配（避免部分匹配）
        pattern = re.compile(r'\b' + re.escape(concept_name) + r'\b')
        match = pattern.search(body)
        if match:
            body = body[:match.start()] + f"[[{concept_name}]]" + body[match.end():]
            content = preamble + body
            added += 1
    
    if added > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return added

def update_concept_page(concept_path, note_title, note_path, relation=""):
    """在概念页的相关笔记部分添加新笔记链接"""
    with open(concept_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    link = f"- [[{note_title}]]"
    if relation:
        link += f" — {relation}"
    
    # 检查是否已存在
    if f"[[{note_title}]]" in content:
        return False
    
    # 找到"相关笔记"部分
    section_match = re.search(r'(## 相关笔记\n)', content)
    if section_match:
        insert_pos = section_match.end()
        content = content[:insert_pos] + link + "\n" + content[insert_pos:]
        with open(concept_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def lint_wiki():
    """健康检查：找矛盾/孤立页/缺失引用"""
    issues = []
    concepts = load_concepts()
    
    # 1. 孤立概念页（没有任何笔记链接到它）
    for cname, cpath in concepts.items():
        referenced = False
        for root, dirs, files in os.walk(OBSIDIAN):
            if "概念" in root:
                continue
            for fn in files:
                if fn.endswith(".md") and fn != "README.md":
                    fpath = os.path.join(root, fn)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        if f"[[{cname}]]" in f.read():
                            referenced = True
                            break
            if referenced:
                break
        if not referenced:
            issues.append(f"⚠️ 孤立概念页: {cname}（无任何笔记链接到它）")
    
    # 2. 笔记无双链
    no_links = []
    for root, dirs, files in os.walk(OBSIDIAN):
        if "概念" in root:
            continue
        for fn in files:
            if fn.endswith(".md") and fn != "README.md":
                fpath = os.path.join(root, fn)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "[[" not in content:
                    no_links.append(os.path.basename(fpath))
    if no_links:
        issues.append(f"⚠️ {len(no_links)}个笔记无任何双链: {', '.join(no_links[:5])}")
    
    # 3. 缺README的目录
    for root, dirs, files in os.walk(OBSIDIAN):
        for d in dirs:
            dpath = os.path.join(root, d)
            if not os.path.isfile(os.path.join(dpath, "README.md")):
                issues.append(f"⚠️ 缺README: {d}/")
    
    # 4. 缺frontmatter
    missing_fm = 0
    for root, dirs, files in os.walk(OBSIDIAN):
        for fn in files:
            if fn.endswith(".md") and fn != "README.md":
                fpath = os.path.join(root, fn)
                with open(fpath, 'r', encoding='utf-8') as f:
                    if not f.readline().startswith("---"):
                        missing_fm += 1
    if missing_fm:
        issues.append(f"⚠️ {missing_fm}个笔记缺frontmatter")
    
    if not issues:
        print("✅ Wiki健康检查通过，无问题")
    else:
        print(f"📋 Wiki Lint报告 ({len(issues)}个问题)")
        for issue in issues:
            print(issue)
    
    return issues

def process_file(filepath):
    """处理单个文件：提取概念+补双链+更新概念页"""
    concepts = load_concepts()
    title = extract_title(filepath)
    
    # 添加双链
    added = add_backlinks(filepath, concepts)
    
    # 更新被引用的概念页
    concepts_updated = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for cname, cpath in concepts.items():
        if f"[[{cname}]]" in content:
            if update_concept_page(cpath, title, filepath):
                concepts_updated += 1
    
    return added, concepts_updated

def scan_all():
    """扫描所有笔记，补双链"""
    concepts = load_concepts()
    total_added = 0
    files_modified = 0
    
    for root, dirs, files in os.walk(OBSIDIAN):
        if "概念" in root:
            continue
        for fn in files:
            if fn.endswith(".md") and fn != "README.md":
                fpath = os.path.join(root, fn)
                added = add_backlinks(fpath, concepts)
                if added > 0:
                    total_added += added
                    files_modified += 1
                    print(f"  ✅ {fn}: +{added}双链")
    
    print(f"\n📊 扫描完成: {files_modified}个文件修改, 共添加{total_added}个双链")
    return total_added

def main():
    if len(sys.argv) < 2:
        print("用法: wiki-ingest.py <file|--scan|--lint>")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--lint":
        lint_wiki()
    elif arg == "--scan":
        scan_all()
    else:
        filepath = os.path.abspath(arg)
        if not os.path.isfile(filepath):
            print(f"❌ 文件不存在: {filepath}")
            sys.exit(1)
        added, concepts_updated = process_file(filepath)
        print(f"✅ {os.path.basename(filepath)}: +{added}双链, 更新{concepts_updated}个概念页")

if __name__ == "__main__":
    main()
