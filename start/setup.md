---
title: Run the labs
subtitle: On Google Colab, on your own computer, or on Binder
---

Every lab on this site already shows all of its results, so you can read it without running anything. To change the code and see what happens, run it yourself in one of three ways.

## Option 1: Google Colab (fastest)

Every lab has an **Open in Colab** badge under its title. Click it, then choose *Runtime → Run all*. The first cell fetches the course's small `qcai` package for you, so nothing else needs installing. Colab also opens the saved results, so you can read first and run later.

## Option 2: your own computer

Install Python 3.10 or newer. Then run these commands in a terminal:

```bash
git clone https://github.com/pozapas/quantum-causal-ai.git
cd quantum-causal-ai
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt jupyterlab
jupyter lab
```

Open any notebook in `labs/`. The labs need `numpy`, `matplotlib`, `plotly`, `networkx`, and `IPython` (installed with `ipykernel`), plus the small `qcai` teaching package that ships with the book. `requirements.txt` also pins `scipy` and `pandas`.

## Option 3: Binder

The launch button on a lab page can start a temporary Jupyter server on [mybinder.org](https://mybinder.org), built from the book's repository. Start-up can take a few minutes, and Binder deletes the session when you close it.

:::{note} Ready for real quantum software?
After the labs, try the same experiments with an open-source quantum SDK such as Qiskit or PennyLane [@pennylane]. The labs leave these packages out on purpose, so they run anywhere and stay short enough to read.
:::
