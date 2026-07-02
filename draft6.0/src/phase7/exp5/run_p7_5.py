"""
P7.5 — natural-data confirmation (design.md §3 P7.5) — the synthetic-artifact gate.

The question: do the bake-off ordering + the chosen head hold on REAL flat data (not a synthetic artifact)? Re-run
the headline heads on digits (64-D) and CIFAR-flat (3072-D), on the class-incremental continual stream. If the
ordering + the chosen head reproduce -> the readout story is real. If it flips on real data -> follow the
NATURAL-data verdict (real > synthetic for a deployment choice).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_5.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p7lib as P                                                       # noqa: E402
import p7cfg as CFG                                                     # noqa: E402
import plot_p7                                                          # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p7_5" + ("_quick" if QUICK else ""))
HEADS = ["linear", "cosine-ncm", "cosine-softmax", "slda", "fecam", "ranpac", "rls", "mlp"]
SCFF_EP = 2 if QUICK else CFG.SCFF_EP


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _knob_c(name):
    kb = dict(CFG.COMMITTED_KNOBS.get(name, {}))
    if name == "mlp":
        kb["epochs"] = CFG.SLEEP_EP
    return kb


def run_dataset(loader, seeds, name):
    rows = []
    for s in seeds:
        Xtr, Ytr, Xte, Yte = loader(s)
        cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, 10, s, scff_ep=SCFF_EP)
        d = {}
        for h in HEADS:
            chf = lambda ss, nm=h, kb=_knob_c(h): P.make_head(nm, 10, seed=ss, **kb)
            r = P.eval_head_on_cache(cache, chf, s)
            d[h] = dict(aa=r["aa"], bwt=r["bwt"])
        rows.append(d)
        print(f"    [{name}] seed {s}: " + " ".join(f"{h}:{d[h]['aa']:.2f}" for h in ("cosine-softmax", "slda", "rls", "mlp")), flush=True)
    return rows


def main():
    t0 = time.time()
    print(f"P7.5 — natural-data confirmation (QUICK={QUICK})", flush=True)
    seeds5 = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
    seeds3 = CFG.SEEDS[:1] if QUICK else CFG.SEEDS[:3]                  # CIFAR-flat is heavy (3072-D)
    print("  digits (64-D)...", flush=True)
    dig = run_dataset(lambda s: P.load_digits_split(s), seeds5, "digits")
    print("  cifar-flat (3072-D, heavier, 3 seeds)...", flush=True)
    try:
        cif = run_dataset(lambda s: P.load_cifar_flat(s), seeds3, "cifarflat")
    except Exception as e:
        print(f"  [cifar-flat skipped: {e}]", flush=True); cif = None

    A = dict(heads=np.array(HEADS), seeds=np.array(seeds5))
    for h in HEADS:
        A[f"nat_digits_acc_{h}"] = np.array([r[h]["aa"] for r in dig])
        A[f"nat_digits_bwt_{h}"] = np.array([r[h]["bwt"] for r in dig])
        if cif:
            A[f"nat_cifarflat_acc_{h}"] = np.array([r[h]["aa"] for r in cif])
            A[f"nat_cifarflat_bwt_{h}"] = np.array([r[h]["bwt"] for r in cif])
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    def rank(rows):
        med = {h: float(np.median([r[h]["aa"] for r in rows])) for h in HEADS}
        return med, sorted(HEADS, key=lambda h: -med[h])
    dmed, dord = rank(dig)
    manifest = dict(rung="P7.5", git=_git(), quick=QUICK, seeds_digits=seeds5, seeds_cifar=seeds3,
                    wall_s=round(time.time() - t0, 1), digits_AA=dmed, digits_order=dord,
                    versions=dict(numpy=np.__version__))
    if cif:
        cmed, cord = rank(cif); manifest["cifar_AA"] = cmed; manifest["cifar_order"] = cord
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print("\n== P7.5 NAT-ANCHOR (median AA) ==", flush=True)
    print("  digits :  " + "  ".join(f"{h}={dmed[h]:.3f}" for h in dord), flush=True)
    if cif:
        print("  cifar  :  " + "  ".join(f"{h}={manifest['cifar_AA'][h]:.3f}" for h in manifest["cifar_order"]), flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
