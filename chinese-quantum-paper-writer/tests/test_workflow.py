"""Synthetic fixtures only; no published paper or scientific claim is implied."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.corpus = Path(self.tmp.name)/'corpus'
        (self.corpus/'pdfs').mkdir(parents=True)
        self.pdf = self.corpus/'pdfs'/'fixture.pdf'
        with fitz.open() as doc:
            for i in range(2):
                page = doc.new_page()
                page.insert_text((72, 72), f'Synthetic test fixture page {i+1}; this is not a real paper.')
            doc.save(self.pdf)
        self.draft = Path(self.tmp.name)/'draft.md'

    def run_script(self, name, *args, code=0):
        r = subprocess.run([sys.executable, str(ROOT/'scripts'/name), *map(str,args)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(r.returncode, code, r.stdout+r.stderr)
        return r

    def index(self):
        self.run_script('build_index.py','--corpus',self.corpus)
        return json.loads((self.corpus/'index.json').read_text(encoding='utf-8'))

    def review(self, key, item, evidence='- E01 | p. 2 | Synthetic fixture evidence.'):
        path = self.corpus/item['note']
        raw = path.read_text(encoding='utf-8')
        front, body = raw[4:].split('\n---\n',1)
        meta = json.loads(front)
        meta.update(status='reviewed',title='Synthetic fixture',authors=['Test Author'],year=2025,journal='Synthetic fixture journal')
        path.write_text('---\n'+json.dumps(meta)+'\n---\n'+body+'\n'+evidence+'\n',encoding='utf-8')
        return path

    def check(self, text, *args, code=0):
        self.draft.write_text(text,encoding='utf-8')
        return self.run_script('check_citations.py',self.draft,'--corpus',self.corpus,*args,code=code)

    def test_end_to_end_and_duplicate(self):
        shutil.copyfile(self.pdf, self.corpus/'pdfs'/'z-copy.pdf')
        index = self.index()
        self.assertEqual(index['paper_count'],1)
        key, item = next(iter(index['papers'].items()))
        self.assertEqual(len(item['duplicate_paths']),1)
        self.assertIn('PDF PAGE 2',(self.corpus/item['text']).read_text(encoding='utf-8'))
        self.check(f'Claim [{key}:E01]',code=1)
        note = self.review(key,item)
        before = note.read_bytes()
        self.assertEqual(self.index()['papers'][key]['status'],'reviewed')
        self.assertEqual(note.read_bytes(),before)
        bib = Path(self.tmp.name)/'refs.bib'
        refs = Path(self.tmp.name)/'refs.md'
        report = Path(self.tmp.name)/'report.json'
        self.check(f'Claim [{key}:E01]', '--require-evidence','--bib-out',bib,'--refs-out',refs,'--report',report)
        self.assertIn('@article{'+key,bib.read_text(encoding='utf-8'))
        self.assertTrue(json.loads(report.read_text(encoding='utf-8'))['passed'])
        self.check(f'Claim [{key}:E99]',code=1)
        self.check('Claim [q_000000000000:E01]',code=1)
        self.check(f'Claim [{key}]','--require-evidence',code=1)
        self.check(r'Claim \cite{'+key+'}', '--tex')
        self.check('No citation',code=1)
        self.pdf.write_bytes(b'modified PDF')
        self.check(f'Claim [{key}:E01]',code=1)

    def test_out_of_range(self):
        key, item = next(iter(self.index()['papers'].items()))
        self.review(key,item,'- E01 | p. 3 | Synthetic fixture evidence.')
        self.run_script('build_index.py','--corpus',self.corpus,code=1)
        self.check(f'Claim [{key}:E01]',code=1)

    def test_single_pdf_extract(self):
        out = Path(self.tmp.name)/'out.txt'
        self.run_script('pdf_to_text.py',self.pdf,'-o',out)
        self.assertIn('PDF PAGE 2',out.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
