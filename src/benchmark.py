"""Roda cada implementação sobre um arquivo e mede o tempo total (wall clock).

Cada resultado é acrescentado em results.csv.
Uso: python src/benchmark.py data/measurements_1m.txt [nome1 nome2 ...]
O tempo inclui subir o interpretador e importar a lib (igual para todos).
"""
import shutil
import subprocess
import sys
import time
import os
import csv
from pathlib import Path

IMPLS = {
    "python": [sys.executable, "src/using_python.py"],
    "pandas": [sys.executable, "src/using_pandas.py"],
    "dask": [sys.executable, "src/using_dask.py"],
    "polars": [sys.executable, "src/using_polars.py"],
    "duckdb": [sys.executable, "src/using_duckdb.py"],
    "pyarrow": [sys.executable, "src/using_pyarrow.py"],
    "awk": [shutil.which("bash") or "bash", "src/using_bash_and_awk.sh"],
}

path = sys.argv[1]
names = sys.argv[2:] or list(IMPLS)
with open(path, "rb") as f:
    rows = sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 24), b""))

print(f"{path}: {rows:,} linhas\n")
print(f"{'impl':<8} {'tempo (s)':>10} {'linhas/s':>15}")
for name in names:
    start = time.perf_counter()
    proc = subprocess.run(IMPLS[name] + [path], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONUTF8": "1"})  # Windows: stdout em cp1252 quebra com nomes acentuados
    took = time.perf_counter() - start
    if proc.returncode:
        print(f"{name:<8} {'FALHOU':>10}  {proc.stderr.strip().splitlines()[-1:]}")
    else:
        print(f"{name:<8} {took:>10.2f} {rows / took:>15,.0f}", flush=True)
        new = not Path("results.csv").exists()
        with open("results.csv", "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["linhas", "impl", "segundos", "linhas_por_s"])
            w.writerow([rows, name, round(took, 2), round(rows / took)])
