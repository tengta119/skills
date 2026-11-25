#!/usr/bin/env python3
"""Create or resume an isolated paper workspace under an explicit project root."""
import argparse
import json
import re
from pathlib import Path
from common import ROOT

MANIFEST = '.paper-project.json'
FILES = ('state.md', 'corpus-audit.md', 'literature-map.md', 'topics.md',
         'outline.md', 'evidence-matrix.md', 'sections', 'draft.md', 'final.md',
         'references.md', 'references.bib', 'citation-report.json', 'review.md',
         'paper.tex', 'experiments', 'figures')


def init(project_root, paper_id, at_root=False, resume=False):
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError('project root must be an existing directory')
    if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', paper_id)
            or paper_id.upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}):
        raise ValueError('paper ID must be a portable ASCII slug (letters, digits, hyphen, underscore)')
    if project_root.is_relative_to(ROOT):
        raise ValueError('project root must be outside the skill directory')
    out = project_root if at_root else project_root / f'paper-{paper_id}'
    if out.resolve() != out or out.is_relative_to(ROOT) or ROOT.is_relative_to(out) and not at_root:
        raise ValueError('unsafe paper directory')
    manifest = out / MANIFEST
    expected = {'schema_version': 1, 'paper_id': paper_id, 'layout': 'root' if at_root else 'folder'}
    if resume:
        if not manifest.is_file() or manifest.is_symlink():
            raise ValueError('no existing paper manifest; use initialization for a new paper')
        if json.loads(manifest.read_text(encoding='utf-8')) != expected:
            raise ValueError('manifest identity/layout mismatch')
        if not (out/'state.md').is_file() or (out/'state.md').is_symlink():
            raise ValueError('state.md missing or unsafe; recover manually')
        for name in FILES:
            if (out/name).is_symlink():
                raise ValueError(f'unsafe symbolic link: {name}')
    else:
        if not at_root:
            out.mkdir(exist_ok=False)
        for name in (MANIFEST, *FILES):
            target = out/name
            if target.exists() or target.is_symlink():
                raise ValueError(f'existing paper output: {target}; use --resume only for the same paper, or choose a new ID')
        with manifest.open('x', encoding='utf-8') as f:
            f.write(json.dumps(expected, ensure_ascii=False, indent=2)+'\n')
        with (out/'state.md').open('x', encoding='utf-8') as f:
            f.write(f'# 论文任务状态\n\n- 论文 ID：{paper_id}\n- 阶段：Phase 0\n- 类型：待确认\n- 题目：待确认\n- 目标期刊：待确认\n- 文献范围：待确认\n- 已确认决策：无\n- 下一步：确认任务范围\n')
        (out/'sections').mkdir()
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--paper-id', required=True)
    p.add_argument('--at-root', action='store_true', help='one paper directly in the project root')
    p.add_argument('--resume', action='store_true', help='resume only the matching existing paper')
    args = p.parse_args()
    try:
        print(init(args.project_root, args.paper_id, args.at_root, args.resume))
    except (ValueError, OSError) as exc:
        p.exit(1, f'{exc}\n')

if __name__ == '__main__':
    main()
