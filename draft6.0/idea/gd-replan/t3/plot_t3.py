"""Plot the T3 cheap-credit ladder: (1) locality dose-response, (2) overlap vs non-overlap + cost Pareto,
(3) temperature free lever, (4) top-down credit. Reads figs_t3/ and figs_topdown/ arrays; skips missing keys."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.join(HERE, "figs_t3", "arrays.npz")
AT = os.path.join(HERE, "figs_topdown", "arrays.npz")
a = np.load(A3) if os.path.exists(A3) else {}
t = np.load(AT) if os.path.exists(AT) else {}


def has(d, k):
    try:
        return k in d.files
    except Exception:
        return k in d


L = int(a["L"]) if has(a, "L") else 12
xs = np.arange(1, L + 1)
fig, ax = plt.subplots(2, 2, figsize=(14, 10))

# --- panel 1: locality dose-response (non-overlap window sweep) ---
loc = [("h_w1_probe", "w1 (pure local)", "#c0392b"), ("h_w2_probe", "w2 (adopted)", "#e67e22"),
       ("h_w4_probe", "w4", "#27ae60"), ("h_w6_probe", "w6", "#16a085"),
       ("h_w12_probe", "w12 (full e2e — UPPER BOUND)", "#2c3e50")]
for k, lab, c in loc:
    if has(a, k):
        ax[0, 0].plot(xs, a[k], "-o", color=c, label=lab, lw=2, ms=4)
ax[0, 0].set_title("(1) Locality dose-response (5 seeds): credit reach sets composing depth\n"
                   "peak marches deeper w1→w12; ~5 cap is LOCALITY, not the objective", fontsize=10)
ax[0, 0].set_xlabel("layer depth"); ax[0, 0].set_ylabel("linear-probe accuracy")
ax[0, 0].legend(fontsize=8); ax[0, 0].grid(alpha=0.3); ax[0, 0].set_xticks(xs)

# --- panel 2: overlap vs non-overlap ---
ov = [("h_w2_probe", "w2 s2 (non-ovl, depth2)", "#e67e22", "-"),
      ("h_w2s1_probe", "w2 s1 (overlap, depth2)", "#e67e22", "--"),
      ("h_w4_probe", "w4 s4 (non-ovl, depth4)", "#27ae60", "-"),
      ("h_w4s2_probe", "w4 s2 (overlap, depth4)", "#27ae60", "--"),
      ("h_w4s1_probe", "w4 s1 (overlap, depth4)", "#27ae60", ":")]
for k, lab, c, ls in ov:
    if has(a, k):
        ax[0, 1].plot(xs, a[k], ls, marker="o", color=c, label=lab, lw=2, ms=3)
ax[0, 1].set_title("(2) Overlap (stride<window): does chaining extend reach at bounded backward depth?\n"
                   "dashed/dotted = overlap; ≈ solid means overlap is a WEAK lever", fontsize=10)
ax[0, 1].set_xlabel("layer depth"); ax[0, 1].set_ylabel("linear-probe accuracy")
ax[0, 1].legend(fontsize=8); ax[0, 1].grid(alpha=0.3); ax[0, 1].set_xticks(xs)

# --- panel 3: temperature free lever ---
tp = [("h_w2_probe", "w2 temp0.5 (adopted)", "#e67e22", "-"),
      ("h_w2_t02_probe", "w2 temp0.2 (free lever)", "#8e44ad", "-"),
      ("h_w2s1_probe", "w2s1 temp0.5", "#e67e22", "--"),
      ("h_w2s1_t02_probe", "w2s1 temp0.2 (stacked)", "#8e44ad", "--")]
for k, lab, c, ls in tp:
    if has(a, k):
        ax[1, 0].plot(xs, a[k], ls, marker="o", color=c, label=lab, lw=2, ms=3)
ax[1, 0].set_title("(3) Temperature free lever (T0.1 confirm): sharper InfoNCE temp0.2\n"
                   "lifts composing depth at zero architecture cost", fontsize=10)
ax[1, 0].set_xlabel("layer depth"); ax[1, 0].set_ylabel("linear-probe accuracy")
ax[1, 0].legend(fontsize=8); ax[1, 0].grid(alpha=0.3); ax[1, 0].set_xticks(xs)

# --- panel 4: top-down credit (window=1 base) ---
td = [("td_off_probe", "λ=0 (= w1 baseline)", "#7f8c8d", "-"),
      ("td_top_l05_probe", "top λ=0.5", "#2980b9", "-"),
      ("td_top_l10_probe", "top λ=1.0", "#2980b9", "--"),
      ("td_top_l10_warm_probe", "top λ=1.0 +warmup", "#16a085", "-"),
      ("td_next_l10_probe", "next λ=1.0", "#c0392b", "--")]
for k, lab, c, ls in td:
    if has(t, k):
        ax[1, 1].plot(xs, t[k], ls, marker="o", color=c, label=lab, lw=2, ms=3)
ax[1, 1].set_title("(4) Top-down credit (objective-side, depth=1): detached reference InfoNCE\n"
                   "above λ=0 = composes; below = anchor-to-decayed-top failure", fontsize=10)
ax[1, 1].set_xlabel("layer depth"); ax[1, 1].set_ylabel("linear-probe accuracy")
ax[1, 1].legend(fontsize=8); ax[1, 1].grid(alpha=0.3); ax[1, 1].set_xticks(xs)

plt.tight_layout()
p = os.path.join(HERE, "figs_t3", "T3_RESULTS.png")
os.makedirs(os.path.dirname(p), exist_ok=True)
plt.savefig(p, dpi=130, bbox_inches="tight")
print(f"wrote {p}")
