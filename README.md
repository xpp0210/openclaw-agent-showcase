# AI Agent Showcase 🤖

> 展示如何用 OpenClaw 构建有记忆、能进化的 AI Agent 系统

## 🎯 这是什么

这是一个**可复现的 AI Agent 定制部署方案**，包含：
- 有记忆的 AI 助手（不是无状态的聊天机器人）
- Spring AI + RAG 企业级代码示例
- 自进化脚本（反思→归因→改进循环）
- Obsidian 知识库自动化工具

## 🏗️ 项目结构

```
├── spring-ai-rag-demo/    # Spring Boot 3.3 + Spring AI RAG 示例
│   ├── pom.xml
│   └── src/               # 3个Java类，最小可运行RAG
├── scripts/               # Agent自进化脚本
│   ├── reflect.sh         # 任务反思与归因分析
│   ├── article-flow.py    # 文章生产流水线状态管理
│   └── wiki-ingest.py     # Obsidian笔记双链自动补全
└── README.md
```

## ✨ 核心特性

### 1. 有记忆的 AI
- 短期记忆：对话上下文（LCM压缩）
- 长期记忆：向量数据库（MemOS）
- 情景记忆：日常日志→蒸馏→知识沉淀

### 2. 自进化循环
```
任务执行 → 反思记录 → 归因分析 → 规则更新 → 下次改进
```
93% 任务成功率（41次反思记录）

### 3. 全自动内容生产
- 选题挖掘（GitHub/X/HN 5源并行）
- 素材采集 → 写作 → 封面生成 → 微信公众号发布
- 每日定时执行

### 4. Spring AI RAG Demo
最简可运行示例，3个Java类实现检索增强生成：
- `Application.java` — 启动类
- `RagService.java` — 向量检索 + LLM
- `RagController.java` — REST API

```bash
cd spring-ai-rag-demo
# 配置 application.yml 中的 API key
mvn spring-boot:run
curl http://localhost:8080/rag?q=什么是RAG
```

## 📊 系统全景

| 维度 | 数据 |
|------|------|
| 概念知识页 | 34+ |
| Obsidian笔记 | 85+ |
| Skills | 62个 |
| 反思记录 | 41条（93%成功） |
| 已发布文章 | 5篇 |
| 自动化Cron | 10个 |

## 🛠️ 技术栈

- **Agent框架**: OpenClaw 2026.4.2
- **模型**: GLM-5.1（主力）+ MiniMax-M2.7（fallback）
- **记忆**: MemOS Local（向量+BM25混合检索）
- **知识库**: Obsidian + PARA方法
- **发布**: 微信公众号 + 多平台分发
- **后端**: Java 11 / Spring Boot / Spring AI

## 💬 需要定制？

如果你也想搭建这样的系统：
- 📧 xiepp0210@gmail.com
- 📱 微信号可通过公众号「AI驾座」获取

从选型到部署到维护，2-3天交付基础版。

## 📄 License

MIT

## 🧠 知识图谱

运行 `scripts/knowledge-graph.py` 生成可视化：

| 指标 | 数据 |
|------|------|
| 概念页 | 56 |
| 笔记 | 71 |
| 双链关系 | 862 |
| 孤岛概念 | 0 |

TOP 5 最被引用：Agent, OpenClaw, Claude Code, RAG, Skill

图数据见 `data/graph-data.json`，Mermaid图见 `data/graph.mmd`。
