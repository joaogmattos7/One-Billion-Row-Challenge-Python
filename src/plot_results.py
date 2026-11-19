"""Gera benchmark_1b.png a partir de results.csv (tempo para 1 bi de linhas)."""
import csv

import matplotlib.pyplot as plt

rows = [r for r in csv.DictReader(open("results.csv", encoding="utf-8")) if r["linhas"] == "1000000000"]
rows.sort(key=lambda r: float(r["segundos"]), reverse=True)  # mais rápido no topo
names = [r["impl"] for r in rows]
secs = [float(r["segundos"]) for r in rows]

fig, ax = plt.subplots(figsize=(8, 4.2), facecolor="#fcfcfb")
ax.set_facecolor("#fcfcfb")
ax.barh(names, secs, color="#2a78d6", height=0.6)
ax.set_xscale("log")  # 10 s a 27 min: em escala linear duckdb/polars somem
for y, s in enumerate(secs):
    label = f"{s:,.0f} s".replace(",", ".") + (f"  ({s / 60:.1f} min)".replace(".", ",") if s >= 60 else "")
    ax.text(s * 1.08, y, label, va="center", color="#0b0b0b", fontsize=10)
ax.set_xlim(right=max(secs) * 6)
ax.set_xticks([10, 100, 1000], ["10", "100", "1.000"])
ax.minorticks_off()
ax.set_xlabel("segundos (escala log) — menor é melhor", color="#52514e")
ax.set_title("1 bilhão de linhas — tempo total por implementação", loc="left", color="#0b0b0b")
ax.tick_params(colors="#52514e", length=0)
ax.grid(axis="x", color="#e6e5e1", linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#c9c8c3")
fig.tight_layout()
fig.savefig("benchmark_1b.png", dpi=150)
