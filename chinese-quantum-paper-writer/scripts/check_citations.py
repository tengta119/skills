#!/usr/bin/env python3
"""Mechanical citation validation, with optional bibliography exports."""
import argparse
import json
import re
import sys
from pathlib import Path
from common import ROOT, KEY_RE, digest, read_note, evidence_records, validate_metadata, save_json

MD_CITE = re.compile(r'\[(q_[^\]\n]*)\]')
TEX_CITE = re.compile(r'\\cite(?:t|p)?(?:\[[^\]]*\])*\{([^{}]+)\}')


def collect(text, tex=False):
    # Remove fenced code blocks and inline code in Markdown; TeX comments are ignored.
    if not tex:
        text = re.sub(r'^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text, flags=re.M|re.S)
        text = re.sub(r'`[^`\n]+`', '', text)
    for n, line in enumerate(text.splitlines(), 1):
        if tex:
            line = re.split(r'(?<!\\)%', line, maxsplit=1)[0]
            for match in TEX_CITE.finditer(line):
                for key in match[1].split(','):
                    yield n, key.strip(), None
        else:
            for match in MD_CITE.finditer(line):
                key, sep, eid = match[1].partition(':')
                yield n, key, eid if sep else None


def safe_path(root, value):
    path = (root/value).resolve()
    if not path.is_relative_to(root):
        raise ValueError('index path escapes corpus')
    return path


def load_verified(corpus, index, key):
    item = index.get(key)
    if item is None:
        raise ValueError('unknown citation key')
    if not KEY_RE.fullmatch(key):
        raise ValueError('malformed citation key')
    pdf = safe_path(corpus, item['pdf'])
    if not pdf.is_file() or digest(pdf) != item['sha256'] or key != 'q_'+item['sha256'][:12]:
        raise ValueError('source PDF missing or hash mismatch; re-index and review')
    meta, body = read_note(safe_path(corpus, item['note']))
    if meta.get('key') != key or meta.get('sha256') != item['sha256']:
        raise ValueError('note key/hash mismatch')
    if meta.get('status') != 'reviewed':
        raise ValueError('note has not been reviewed')
    validate_metadata(meta)
    records = evidence_records(body, item['page_count'])
    if not records:
        raise ValueError('no reviewed evidence records')
    return meta, records


def escape_bib(s):
    return ''.join({'\\':r'\textbackslash{}','{':r'\{','}':r'\}','%':r'\%','&':r'\&','_':r'\_','#':r'\#','$':r'\$','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s.replace('\n',' '))


def export_refs(metas, refs_out, bib_out):
    lines, entries = [], []
    for i, (key, m) in enumerate(metas.items(), 1):
        details = str(m['year'])
        if m.get('volume'): details += ', '+m['volume']
        if m.get('issue'): details += '('+m['issue']+')'
        if m.get('pages'): details += ': '+m['pages']
        doi = f'. DOI: {m["doi"]}' if m.get('doi') else ''
        lines.append(f'[{i}] {", ".join(m["authors"])}. {m["title"]}[J]. {m["journal"]}, {details}{doi}.')
        fields = {'title':escape_bib(m['title']), 'author':' and '.join('{'+escape_bib(a)+'}' for a in m['authors']), 'journal':escape_bib(m['journal']), 'year':str(m['year'])}
        for name, field in [('volume','volume'),('number','issue'),('pages','pages'),('doi','doi')]:
            if m.get(field): fields[name] = escape_bib(m[field])
        entries.append('@article{'+key+',\n'+',\n'.join(f'  {k} = {{{v}}}' for k,v in fields.items())+'\n}')
    for path, content in [(refs_out,'# 参考文献（待按期刊规范调整）\n\n'+'\n\n'.join(lines)+'\n'),(bib_out,'\n\n'.join(entries)+'\n')]:
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('draft', type=Path)
    p.add_argument('--corpus', type=Path, default=ROOT/'corpus')
    p.add_argument('--refs-out', type=Path)
    p.add_argument('--bib-out', type=Path)
    p.add_argument('--report', type=Path)
    p.add_argument('--tex', action='store_true', help='validate single-line LaTeX cite commands; no evidence anchors')
    p.add_argument('--require-evidence', action='store_true', help='require an evidence ID on every Markdown citation')
    args = p.parse_args()
    if args.tex and args.require_evidence:
        p.error('--require-evidence only works in Markdown mode')
    corpus = args.corpus.resolve()
    try:
        index = json.loads((corpus/'index.json').read_text(encoding='utf-8'))['papers']
        text = args.draft.read_text(encoding='utf-8-sig')
    except (OSError, ValueError, KeyError) as exc:
        p.exit(1, f'Cannot read draft/index: {exc}\n')
    errors, metas, cache = [], {}, {}
    count = 0
    for line, key, eid in collect(text, args.tex):
        count += 1
        try:
            if key not in cache:
                cache[key] = load_verified(corpus, index, key)
            meta, records = cache[key]
            if eid is not None and eid not in records:
                raise ValueError(f'unknown evidence ID {eid!r}')
            if args.require_evidence and eid is None:
                raise ValueError('missing evidence ID')
            metas[key] = meta
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({'line':line,'key':key,'error':str(exc)})
    if count == 0:
        errors.append({'line':0,'key':'','error':'No recognized citations; check citation syntax.'})
    report = {'passed':not errors,'citations':count,'unique_valid_keys':list(metas),'errors':errors,'scope':'mechanical only; semantic verification required'}
    if args.report:
        save_json(args.report, report)
    for err in errors:
        print(f'ERROR line {err["line"]}: {err["key"]} {err["error"]}', file=sys.stderr)
    if errors:
        print('FAIL: bibliography not exported.', file=sys.stderr)
        return 1
    export_refs(metas, args.refs_out, args.bib_out)
    print(f'PASS: {count} citation occurrences; {len(metas)} verified keys. Semantic review still required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
