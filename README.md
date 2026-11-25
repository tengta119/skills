# Chinese Quantum Paper Writer 使用指南

## 简介

Chinese Quantum Paper Writer 是一个面向量子计算领域的中文学术论文写作 Skill，适用于 Codex、Claude Code、Pi 等 Agent。

支持文献分析、研究选题、大纲设计、论文撰写、引用核验及论文润色，兼容综述论文和原创研究论文。

## 目录结构

```
chinese-quantum-paper-writer/
├── SKILL.md       # 核心工作流程与约束
├── references/    # 写作规范、术语表、引用规则
├── scripts/       # PDF解析、文献入库、引用检查
├── templates/     # Markdown与LaTeX论文模板
├── corpus/
│   ├── pdfs/      # 原始论文
│   ├── texts/     # PDF提取文本
│   ├── notes/     # 结构化论文笔记卡
│   └── index.json # 文献索引
└── tests/         # 自动化测试
```

## 使用教程

### 第一步：安装 Skill

将 Skill 文件夹放入对应 Agent 的全局 Skills 目录（或者项目的.agents/skills/..）。

安装 Python 依赖：

```
pip install -r requirements.txt
```

### 第二步：导入文献

将下载的 PDF 论文放入：

```
corpus/pdfs/
```

```
使用 chinese-quantum-paper-writer Skill，初始化文献知识库。

1. 扫描 corpus/pdfs/ 中的全部论文。
2. 执行 PDF 文本提取和文献索引构建脚本。
3. 逐篇阅读论文原文，生成完整的结构化论文笔记卡，包含：
   - 基本信息与摘要
   - 研究背景与研究问题
   - 核心方法与关键公式
   - 主要创新点
   - 实验设计与实验结果
   - 研究结论与局限性
   - 关键证据及原文页码
4. 核验笔记卡内容，更新审核状态。
5. 将笔记卡及文献索引保存在 Skill 内部的 corpus/ 目录。
6. 已经完成分析且通过核验的论文直接跳过。
7. 输出文献入库报告，记录成功、失败及待核验的论文。

本次任务只构建文献知识库，不进行选题和论文写作。
```

然后使用该提示词对论文进行分析，后续导入新的论文，需要重复该步骤

### 第三步：创建论文项目

```
mkdir quantum-paper
cd quantum-paper
codex
```

### 第四步：调用 Skill

向 Agent 输入：

```
使用 chinese-quantum-paper-writer Skill，
基于共享文献库撰写一篇量子计算相关论文。

首先分析文献并提出候选选题，
等待我确认后继续写作。
所有论文产物保存在当前项目根目录。
```

### 第五步：查看论文产物

```
quantum-paper/
├── state.md              # 写作进度
├── topics.md             # 候选选题
├── outline.md            # 论文大纲
├── evidence-matrix.md    # 证据矩阵
├── sections/             # 各章节正文
├── draft.md              # 论文草稿
├── final.md              # 论文终稿
├── references.bib        # 参考文献
└── review.md             # 审稿记录
```

### 第六步：继续写作或创建新论文

继续已有论文时，在原项目中启动 Agent，并输入：

```
使用 chinese-quantum-paper-writer Skill，
恢复当前论文的写作进度并继续。
```

撰写新论文时，只需创建新的项目目录，无须重新安装 Skill 或构建已有文献库。

## 工作原理

Skill 采用**共享文献知识库 + 独立论文项目**的设计。

Agent 将原始论文转换为结构化笔记卡，提取研究问题、方法、创新点、实验结果和局限性，并在后续写作中按需读取相关文献。

整体工作流程：

```
文献入库
   ↓
论文分析与知识提取
   ↓
主题聚类与研究选题
   ↓
论文大纲设计
   ↓
分章节撰写
   ↓
引用核验与论文审查
   ↓
输出论文终稿
```

文献库永久保存在 Skill 内部，支持增量更新和跨项目复用；论文及写作过程文件保存在当前项目根目录，避免不同论文相互覆盖。

## 注意事项

综述论文可以基于已有文献开展写作；原创研究论文需要提供真实的算法、理论证明或实验成果。