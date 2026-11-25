# Chinese Quantum Paper Writer v1.1

面向 Codex、Claude Code、Pi 等支持 Agent Skills 的中文量子计算论文写作技能。默认离线文献库；允许用户确认后补充检索。脚本不调用 LLM、不联网、不自动产生论文科学结论。

## 安装

需要 Python 3.10+。将整个目录放入 Agent 的 Skill 搜索目录（具体路径由客户端配置决定），例如项目的 `.agents/skills/`（Codex）、`.claude/skills/`（Claude Code）或 Pi 配置的 skills 路径。不要只复制 SKILL.md。也可以让 Agent 直接读取此目录的 SKILL.md。

```bash
cd chinese-quantum-paper-writer
python -m pip install -r requirements.txt
python scripts/build_index.py --corpus corpus
```

请先放入 PDF；空库会返回非零退出码。Windows PowerShell 和 Linux 均可使用上述命令，`python` 可替换为实际 Python 3 命令。外部文献库示例：`python scripts/build_index.py --corpus "D:/papers/quantum"`，其中应有 `pdfs/` 目录。脚本只扫描 `.pdf`，不修改源文件。

## 多论文项目与共享文献库

Skill 安装目录长期保存 corpus（原始 PDF、提取文本、已核验笔记、索引），而项目根保存论文任务。不要每写一篇论文就重新安装 Skill。推荐安装在 Agent 的全局技能目录（实际路径以配置为准），这样多个项目使用同一份 corpus；项目级安装则只共享该安装实例。

在项目根启动 Agent，明确要求新建或继续某篇论文。以下命令中的 `<SKILL_ROOT>`、`<PROJECT_ROOT>`、`<PAPER_ROOT>` 都要替换为实际绝对路径：

```bash
python "<SKILL_ROOT>/scripts/init_paper.py" --project-root "<PROJECT_ROOT>" --paper-id quantum-routing --at-root
```

Skill 默认一项目一论文（命令含 `--at-root`），输出直接位于 `<PROJECT_ROOT>/`。第二篇在另一个项目根启动；若同一项目内写多篇，省略 `--at-root`，分别使用不同 ID（如 `quantum-ml`），输出至 `<PROJECT_ROOT>/paper-<paper-id>/`。继续原论文时保持 ID、布局与项目路径不变，加 `--resume`。脚本拒绝覆盖已有论文文件，且拒绝将论文项目放在 Skill 内部。

```text
skill-install/chinese-quantum-paper-writer/
  corpus/pdfs/       # 共用原文
  corpus/texts/      # 共用文本
  corpus/notes/      # 共用笔记卡
  corpus/index.json  # 共用索引
quantum-routing-project/  # 第一篇项目根
  .paper-project.json
  state.md
  outline.md
  sections/
  draft.md
  final.md
  references.bib
quantum-ml-project/       # 第二篇独立项目根
  .paper-project.json
  state.md
  sections/
  final.md
```

升级旧版时，保留已有 corpus，不要用空库替换；更新 SKILL.md、README.md、scripts 等程序文件即可。旧 `workspace/` 若有稿件，先确认并复制到新建论文目录（保留原件），手工合并旧 state.md 与新 ID，不直接覆盖其他论文。共享笔记需更正时保持证据 ID 稳定，旧稿恢复时重新核验；不并行写共享索引。

## 日常使用

1. 将已下载论文放进 `corpus/pdfs/`。执行 build_index；自动抽取页级文本、计算 SHA-256 去重、创建 JSON 索引与笔记模板，保留既有笔记。`--refresh-text` 可重新抽取文本。
2. 已审核且仍有效的笔记直接复用，不必为每篇新稿重新阅读整个库；仅处理新增、未审核或需要补证据的论文。让 Agent 根据 `references/literature-analysis.md` 逐篇阅读，填写笔记；核实文献元数据和证据后标记 `reviewed`，重新建立索引。扫描件或复杂公式需要人工视觉核验或另行 OCR，脚本会记录文本不足页。不同版本的同一论文须人工去重。
3. 触发 Skill，例如：

   > 使用 chinese-quantum-paper-writer，基于 corpus 中的五种中文期刊论文，先完成入库和主题聚类，提出 3 个量子线路优化综述候选题目。不要直接写全文，等待我选择。所有事实必须有可定位的原文证据，不允许虚构实验或引用。

4. 先初始化或恢复本次论文目录，确定选题后，按阶段生成大纲、证据矩阵、分节草稿、审查报告。保留 Markdown 证据稿并执行：

```bash
python "<SKILL_ROOT>/scripts/check_citations.py" "<PAPER_ROOT>/draft.md" --refs-out "<PAPER_ROOT>/references.md" --bib-out "<PAPER_ROOT>/references.bib" --report "<PAPER_ROOT>/citation-report.json"
```

添加 `--require-evidence` 可要求每个 Markdown 引用均带证据 ID；使用 `--tex` 可检查单行 `\cite{key}` 命令（支持多个逗号分隔 key、citet/citep，无法验证证据 ID）。Markdown 使用 `[q_<12位十六进制>:E01]` 或仅文献级 `[q_<12位十六进制>]`，实际 key 由脚本生成。格式不符的引文、漏引、事实真实性、DOI 是否实际存在、语义支持均需要人工/Agent 检查。脚本发现错误时不导出新参考文献；之前的导出文件不自动删除。

## 单篇 PDF 转换

```bash
python scripts/pdf_to_text.py "corpus/pdfs/example.pdf" -o "corpus/texts/example.txt"
```

页号是 PDF 物理页。抽取顺序、公式、表格可能失真。自动笔记只是待填写模板，不是自动摘要；需要 Agent 阅读并生成真正的文献知识卡片。

## 文件说明

- `SKILL.md`：六阶段流程、触发条件、硬规则、阶段确认与状态恢复。
- `references/`：入库分析、论文结构、量子术语、引用规则、审查清单。
- `scripts/`：入库、PDF 提取、引用核验及共用数据协议。
- `templates/`：Markdown、通用中文 LaTeX 草稿；不代表目标期刊官方模板。
- `tests/`：离线合成 PDF 测试，不含真实学术论文。
- `scripts/init_paper.py`：按项目根、论文 ID 创建或恢复独立论文目录。
- `PAPER_ROOT`：由初始化脚本创建（根目录模式则使用既有项目根），保存该篇论文全部过程与成果，不在 Skill 内。

## 测试

```bash
python -m unittest discover -s tests -v
```

测试仅验证本地脚本处理流程，不评价 Agent 生成的论文质量或投稿合规性。作者应核实科学内容、实验、版权与目标期刊 AI 披露规则。
