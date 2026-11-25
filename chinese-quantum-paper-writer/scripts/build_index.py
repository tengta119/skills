#!/usr/bin/env python3
"""Index PDFs and scaffold note cards; preserve reviewed notes on reruns."""
import argparse
import json
import sys
from pathlib import Path
from common import ROOT, digest, read_note, save_json, validate_metadata, evidence_records
from pdf_to_text import extract_pdf, write_text


def scaffold(key, sha, pages):
    meta = dict(key=key, sha256=sha, status='pending', title='', authors=[], year=None, journal='', volume='', issue='', pages='', doi='', topics=[], paper_type='')
    return '---\n'+json.dumps(meta, ensure_ascii=False, indent=2)+'\n---\n'+f'''
# 论文笔记：{key}

> 自动生成的待核验模板；PDF 共 {pages} 个物理页。元数据提示见 index.json，不能直接作为正式引用。阅读原文后填写，不确定则保留 pending。

## 研究问题与背景
待填写

## 方法、假设、核心公式与算法
待填写（记录页码、输入输出、符号与适用条件）

## 作者明确提出的贡献
待填写

## 实验环境、数据、基线与指标
待填写（理论论文说明不适用项）

## 核心结论与结果
待填写

## 局限与适用边界
作者明确指出：待填写

阅读者推断：待填写（标明推断依据）

## 相关工作与潜在研究方向
待填写

## 写作结构与术语
待填写

## 可引用证据
<!-- 删除本注释后填写证据：- E01 | p. 3 | 原文支持的单一主张 -->
'''


def build(corpus, refresh_text=False):
    pdf_dir = corpus / 'pdfs'
    if not pdf_dir.is_dir():
        raise ValueError(f'PDF directory not found: {pdf_dir}')
    (corpus / 'notes').mkdir(exist_ok=True)
    paths = sorted(p for p in pdf_dir.rglob('*') if p.is_file() and p.suffix.lower() == '.pdf')
    items, errors = {}, []
    for path in paths:
        rel = path.relative_to(corpus).as_posix()
        try:
            sha = digest(path)
            key = 'q_'+sha[:12]
            if key in items:
                if items[key]['sha256'] != sha:
                    raise ValueError('key collision: contact maintainer')
                items[key]['duplicate_paths'].append(rel)
                continue
            pages, hints = extract_pdf(path)
            text_path = corpus / 'texts' / f'{key}.txt'
            if refresh_text or not text_path.exists():
                write_text(pages, text_path)
            note = corpus / 'notes' / f'{key}.md'
            if not note.exists():
                note.write_text(scaffold(key, sha, len(pages)), encoding='utf-8')
            sparse = [i for i, page in enumerate(pages, 1) if len(page.strip()) < 40]
            item = dict(key=key, sha256=sha, pdf=rel, text=text_path.relative_to(corpus).as_posix(), note=note.relative_to(corpus).as_posix(), page_count=len(pages), sparse_pages=sparse, duplicate_paths=[], metadata_hints=hints, status='pending')
            items[key] = item
            try:
                meta, body = read_note(note)
                if meta.get('key') != key or meta.get('sha256') != sha:
                    raise ValueError('note key/hash mismatch')
                if meta.get('status') not in ('pending','reviewed'):
                    raise ValueError('status must be pending or reviewed')
                if meta['status'] == 'reviewed':
                    validate_metadata(meta)
                    if not evidence_records(body, len(pages)):
                        raise ValueError('reviewed note requires evidence')
                item['status'] = meta['status']
                item['metadata'] = {k: meta.get(k) for k in ('title','authors','year','journal','volume','issue','pages','doi','topics','paper_type')}
            except (ValueError, OSError, TypeError) as exc:
                item['status'] = 'invalid'
                errors.append({'pdf': rel, 'error': str(exc)})
        except Exception as exc:
            errors.append({'pdf': rel, 'error': str(exc)})
    orphan_notes = sorted(p.name for p in (corpus/'notes').glob('q_*.md') if p.stem not in items)
    data = {'schema_version': 1, 'paper_count': len(items), 'papers': items, 'errors': errors, 'orphan_notes': orphan_notes}
    save_json(corpus/'index.json', data)
    print(f'PDFs: {len(paths)} | unique: {len(items)} | reviewed: {sum(x["status"]=="reviewed" for x in items.values())} | errors: {len(errors)} | orphan notes: {len(orphan_notes)}')
    for error in errors:
        print(f'ERROR {error["pdf"]}: {error["error"]}', file=sys.stderr)
    if not paths:
        print('No PDFs found; add original papers to corpus/pdfs.', file=sys.stderr)
    return 1 if errors or not paths else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, default=ROOT/'corpus')
    p.add_argument('--refresh-text', action='store_true')
    args = p.parse_args()
    try:
        return build(args.corpus.resolve(), args.refresh_text)
    except (ValueError, OSError) as exc:
        p.exit(1, f'{exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
