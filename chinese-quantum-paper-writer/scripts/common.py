"""Shared corpus and note schema helpers (standard library only)."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_RE = re.compile(r'q_[0-9a-f]{12}\Z')
EVIDENCE_RE = re.compile(r'^- (E[0-9]{2,}) \| p\. ([1-9][0-9]*)(?:-([1-9][0-9]*))? \| (\S.*)$', re.M)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_note(path):
    raw = path.read_text(encoding='utf-8-sig')
    parts = raw.split('\n---\n', 1)
    if not raw.startswith('---\n') or len(parts) != 2:
        raise ValueError('expected JSON front matter between --- lines')
    meta = json.loads(parts[0][4:])
    if not isinstance(meta, dict):
        raise ValueError('metadata must be a JSON object')
    return meta, parts[1]


def evidence_records(body, pages):
    records = {}
    for line in body.splitlines():
        if not re.match(r'^- E\d', line):
            continue
        m = EVIDENCE_RE.fullmatch(line)
        if not m:
            raise ValueError(f'invalid evidence line: {line[:100]}')
        eid, a, b, claim = m.groups()
        start, end = int(a), int(b or a)
        if eid in records or not 1 <= start <= end <= pages:
            raise ValueError(f'duplicate or out-of-range evidence: {eid}')
        if any(x in claim for x in ('待填写', '待核验', '待补充')):
            raise ValueError(f'placeholder in evidence: {eid}')
        records[eid] = (start, end, claim)
    return records


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tmp.replace(path)


def validate_metadata(meta):
    for k in ('title', 'journal'):
        v = meta.get(k)
        if not isinstance(v, str) or not v.strip() or v.strip() in ('待核验', '未知', '待填写'):
            raise ValueError(f'missing verified {k}')
    authors = meta.get('authors')
    if not isinstance(authors, list) or not authors or any(not isinstance(x, str) or not x.strip() or x.strip() in ('未知','待核验','待填写') for x in authors):
        raise ValueError('authors must be a nonempty list of verified names')
    year = meta.get('year')
    if type(year) is not int or not 1800 <= year <= 2200:
        raise ValueError('year must be a four-digit integer')
    for k in ('volume','issue','pages','doi'):
        if not isinstance(meta.get(k, ''), str):
            raise ValueError(f'{k} must be a string')
    doi = meta.get('doi', '').strip()
    if doi and not re.fullmatch(r'10\.\d{4,9}/\S+', doi, flags=re.I):
        raise ValueError('invalid DOI syntax (use bare DOI)')
