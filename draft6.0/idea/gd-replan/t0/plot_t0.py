"""Plot the T0 results: the locality sweep (the decisive panel) + the depth-scaled/contrast grid."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs_t0")
a = np.load(os.path.join(OUT, "arrays.npz"))
L = int(a["L"]); xs = np.arange(1, L + 1)

fig, (axL, axG) = plt.subplots(1, 2, figsize=(13, 5))

# --- panel 1: T0.2 locality sweep (the money figure) ---
loc = [("loc_w1_local_probe", "w=1 (pure local)", "#c0392b"),
       ("loc_w2_adopted_probe", "w=2 (adopted)", "#e67e22"),
       ("loc_w4_probe", "w=4", "#27ae60"),
       ("loc_w12_e2e_probe", "w=12 (full e2e backprop)", "#2c3e50")]
for k, lab, c in loc:
    if k in a:
        axL.plot(xs, a[k], "-o", color=c, label=lab, lw=2, ms=4)
axL.set_title("T0.2 — locality control: credit reach sets the composing depth\n"
              "(same InfoNCE; window 1→12) → ~5 ceiling is LOCALITY-bound", fontsize=11)
axL.set_xlabel("layer depth"); axL.set_ylabel("linear-probe accuracy (class separability)")
axL.legend(fontsize=9); axL.grid(alpha=0.3); axL.set_xticks(xs)

# --- panel 2: T0.1 grid — passes don't move the peak, temperature does ---
grid = [("grid_base_lr03_ep25_probe", "lr.03 ep25 (anchor)", "#7f8c8d", "-"),
        ("grid_lr03_ep150_probe", "lr.03 ep150 (6x passes)", "#2980b9", "-"),
        ("grid_lr10_ep150_probe", "lr.10 ep150 (max train)", "#8e44ad", "--"),
        ("grid_temp02_ep75_probe", "temp=0.2 (sharper contrast)", "#16a085", "-")]
for k, lab, c, ls in grid:
    if k in a:
        axG.plot(xs, a[k], ls, marker="o", color=c, label=lab, lw=2, ms=4)
axG.set_title("T0.1 — depth-scaled training grid\n"
              "lr/passes don't move the peak; sharper contrast (temp) does", fontsize=11)
axG.set_xlabel("layer depth"); axG.set_ylabel("linear-probe accuracy")
axG.legend(fontsize=9); axG.grid(alpha=0.3); axG.set_xticks(xs)

plt.tight_layout()
p = os.path.join(OUT, "T0_RESULTS.png")
plt.savefig(p, dpi=130, bbox_inches="tight")
print(f"wrote {p}")
