import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'scripts/init_paper.py'

class PaperProjects(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)

    def run_init(self, paper_id, *args, root=None, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(root or self.project), '--paper-id', paper_id, *args], cwd=self.project, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout+result.stderr)
        return result

    def test_two_papers_and_resume(self):
        a = Path(self.run_init('routing').stdout.strip())
        b = Path(self.run_init('learning').stdout.strip())
        self.assertNotEqual(a,b)
        (a/'draft.md').write_text('first draft', encoding='utf-8')
        self.run_init('routing', ok=False)
        self.run_init('routing','--resume')
        self.assertEqual((a/'draft.md').read_text(), 'first draft')
        self.assertFalse((b/'draft.md').exists())
        self.run_init('missing','--resume',ok=False)

    def test_direct_root_and_collision(self):
        out = Path(self.run_init('routing','--at-root').stdout.strip())
        self.assertEqual(out,self.project)
        self.assertEqual(json.loads((out/'.paper-project.json').read_text())['paper_id'],'routing')
        (out/'final.md').write_text('finished',encoding='utf-8')
        self.run_init('other','--at-root',ok=False)
        self.run_init('other','--at-root','--resume',ok=False)
        self.run_init('routing','--at-root','--resume')
        self.assertEqual((out/'final.md').read_text(),'finished')

    def test_existing_output_and_invalid_paths(self):
        (self.project/'final.md').write_text('existing',encoding='utf-8')
        self.run_init('routing','--at-root',ok=False)
        self.assertFalse((self.project/'.paper-project.json').exists())
        self.run_init('../escape',ok=False)
        self.run_init('routing',root=ROOT,ok=False)

if __name__ == '__main__':
    unittest.main()
