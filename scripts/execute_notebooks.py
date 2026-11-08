"""Unit `outputs`: make every notebook Colab-ready and store its executed outputs.  Run from book/.

1. Replace the hidden setup cell with one that also works on Google Colab
   (it clones the course repository when the qcai package is not found).
2. Add an "Open in Colab" badge to each lab's title cell.
3. Execute each notebook top to bottom and save it WITH outputs, so the
   website, the downloaded .ipynb, and Colab all show results without a rerun.
"""
import pathlib
import sys

import nbformat
from nbclient import NotebookClient

BOOK = pathlib.Path(__file__).resolve().parents[1]
REPO = "pozapas/quantum-causal-ai"
BOOT = '''import sys, pathlib, subprocess
here = pathlib.Path.cwd()
root = next((p for p in [here, *here.parents] if (p / "qcai").is_dir()), None)
if root is None:  # for example on Google Colab: fetch the course's small teaching package
    root = pathlib.Path("quantum-causal-ai")
    if not root.exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/pozapas/quantum-causal-ai.git", str(root)], check=True)
    root = root.resolve()
sys.path.insert(0, str(root))'''


def badge(rel: str) -> str:
    return (f"[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"(https://colab.research.google.com/github/{REPO}/blob/main/{rel})")


def main() -> int:
    files = [BOOK / "index.ipynb", BOOK / "start" / "roadmap.ipynb", *sorted((BOOK / "labs").glob("*.ipynb"))]
    for f in files:
        nb = nbformat.read(str(f), 4)
        boots = [c for c in nb.cells if c.cell_type == "code" and "root = next(" in c.source]
        assert len(boots) == 1, (f.name, len(boots))
        boots[0].source = BOOT
        if f.parent.name == "labs":
            rel = f"labs/{f.name}"
            first = next(c for c in nb.cells if c.cell_type == "markdown")
            if "colab-badge.svg" not in first.source:
                first.source = first.source.rstrip() + "\n\n" + badge(rel)
        NotebookClient(nb, timeout=300, kernel_name="qcai", resources={"metadata": {"path": str(f.parent)}}).execute()
        errs = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
        assert not errs, f.name
        nbformat.write(nb, str(f))
        print("executed and saved with outputs:", f.relative_to(BOOK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
