import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "resumo_git_log.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def git(repo, *args, autor=None):
    env = dict(os.environ)
    if autor:
        env.update(GIT_AUTHOR_NAME=autor, GIT_COMMITTER_NAME=autor,
                   GIT_AUTHOR_EMAIL="a@example.com", GIT_COMMITTER_EMAIL="a@example.com")
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


class TestResumoGitLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "commit.gpgsign", "false")

    def commitar(self, autor, n):
        arq = self.repo / "f.txt"
        with arq.open("a") as f:
            f.write(f"{autor}{n}\n")
        git(self.repo, "add", "f.txt")
        git(self.repo, "commit", "-q", "-m", f"c {autor} {n}", autor=autor)

    def test_commits_por_autor(self):
        for i in range(3):
            self.commitar("Ana Silva", i)
        self.commitar("Bruno", 0)
        r = executar(str(self.repo))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), ["3\tAna Silva", "1\tBruno", "total\t4"])

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_repo_sem_commits(self):
        self.assertEqual(executar(str(self.repo)).returncode, 3)

    def test_nao_e_repositorio(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(executar(d).returncode, 2)


if __name__ == "__main__":
    unittest.main()
