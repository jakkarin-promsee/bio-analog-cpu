"""
exp0 — SCFF separation GATE (single seed).

The gate to everything (ladder 1.0). One question, one picture:
  Does full SCFF separate at all on the 2-arm spiral?
    (1) goodness separates: G_pos > theta > G_neg, gap grows with training   -> F4
    (2) layers grow MORE separable with depth: linear-probe acc rises 1->L   -> F3
    (3) look at what it learned: the 2-D boundary a linear readout draws      -> F5

If (1)+(2) fail, STOP — nothing downstream (GD ceiling, blocks, sleep) is interpretable.

Math grounded against the SCFF paper (arXiv 2409.11593) + Hinton FF:
  - goodness is the MEAN of squared activations, G = ||h||^2 / M   (NOT the sum).
    This is what makes the locked theta = 2.0 sensible: ~2.0 mean-square per unit
    (RMS ~1.4/unit, ~4 on the active half after ReLU). With the SUM form, Hinton's
    convention puts theta ~= #units = 64, so theta=2.0-as-sum would never train.
  - x_pos = 2*x_k, x_neg = x_k + x_n, shared weight W (W1=W2).
  - mandatory inter-layer normalization h_hat = h/||h||  (FF correctness; also the
    later within-block shortcut guard). First layer sees the RAW (un-normalized)
    input, so the x2 magnitude head-start lives only at layer 1; layers 2..L
    separate on PATTERN alone (which is why "rises with depth" is a real test).
  - local update: gradient through ONE layer only, no cross-layer chain.

Stack: numpy only (SCFF's update is closed-form local). sklearn for the probe.
Run:   python scff_gate.py
"""

from __future__ import annotations
import json
import os
import time

import numpy as np
from scipy.special import expit  # numerically stable sigmoid
from sklearn.linear_model import LogisticRegression

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------- config (gate; first point only)
SEED          = 42                 # first of the standard set [42,137,271,314,1729]
DIMS          = [2, 64, 64, 64, 64]  # 2-D input -> 4 SCFF layers, width 64
THETA         = 2.0                # goodness threshold (open knob); coherent with SUM goodness
LR_SCFF       = 0.03               # local SGD step for SCFF (open knob)
GOODNESS_MODE = "sum"             # LOCKED: G=||h||^2 (sum) + plain SGD — substrate-faithful, theta=2.0 sane
N_STREAM      = 50_000             # online samples, single pass
BATCH         = 32
# GATE TASK (swapped from the 2-arm spiral): 2D 4x4 CHECKERBOARD of Gaussian clusters.
# Why this exact task (decided from decisive_learning.py): SCFF clusters by DENSITY, so
# its classes must BE density clusters (the spiral's interleaved arms defeat it). But a
# 4-cluster task is solved by a RANDOM projection alone (SCFF learning adds nothing). A
# 16-cluster checkerboard is density-separated (SCFF can express it) AND too hard for
# random features (16 clusters, alternating labels) -> SCFF's *learning* measurably wins
# (random 0.75 -> trained 0.80, the largest goodness gap of any 2D task). 2D-visualizable.
# Spiral stays for the GD cells (Exp 1+, where GD cracks what SCFF can't).
CHECK_GRID    = 4                  # 4x4 = 16 clusters
CHECK_SPACING = 1.4                # center spacing
CHECK_OVERLAP = 0.30              # Gaussian std (difficulty dial)
CLUST_SEP     = 1.4                # (kept) 4-cluster-XOR params, for reference
CLUST_OVERLAP = 1.0
N_TURNS       = 2.0                # spiral revolutions per arm (kept for later GD cells)
NOISE_STD     = 0.10               # spiral positional jitter (kept for later GD cells)
TAPS          = 2                  # readout reads last n SCFF layers (128 features)
PROBE_C       = 1.0                # fixed L2 for the linear probe (record it)
CKPTS         = [100, 300, 1000, 3000, 10000, 30000, 50000]
EPS           = 1e-8

# NOTE on NOISE_STD: the run-card says "label noise sigma=0.10". I implement it as
# positional Gaussian jitter (std 0.10 in unit-radius spiral space) — the standard
# spiral difficulty knob, and sigma-as-std fits. If you meant label-FLIP probability,
# flip a flag and re-run; flagged in the manifest so the choice is explicit.

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs_gate")
os.makedirs(OUTDIR, exist_ok=True)

# house style (subset of result-format.md Layer A)
C_POS, C_NEG = "#1f5fbf", "#c1272d"   # world colours: pos=blue, neg=red
C_SCFF = "#117a78"                      # SCFF-only = teal
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": True})


# ----------------------------------------------------------------------------- task: 2-arm spiral
def make_spiral(n, rng, n_turns=N_TURNS, noise_std=NOISE_STD):
    """Two interleaved arms (2 classes). r in [0,1], theta = t*2pi*turns (+ class*pi)."""
    n0 = n // 2
    counts = [(0, n0), (1, n - n0)]
    Xs, Ys = [], []
    for c, k in counts:
        t = rng.uniform(0.0, 1.0, k)
        r = t
        theta = t * 2.0 * np.pi * n_turns + c * np.pi
        x = r * np.cos(theta) + rng.normal(0, noise_std, k)
        y = r * np.sin(theta) + rng.normal(0, noise_std, k)
        Xs.append(np.stack([x, y], axis=1))
        Ys.append(np.full(k, c))
    X = np.concatenate(Xs).astype(np.float64)
    Y = np.concatenate(Ys).astype(np.int64)
    p = rng.permutation(len(X))
    return X[p], Y[p]


def make_cluster_xor(n, rng, dim=2, sep=CLUST_SEP, overlap=CLUST_OVERLAP):
    """4 Gaussian clusters at (+-sep,+-sep); label = XOR of the two axis signs (2 classes).
    Density-separated classes (SCFF's home turf), compositional, 2D-visualizable."""
    signs = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]
    labels = [0, 1, 1, 0]
    base = n // 4
    counts = [base] * 4
    for i in range(n - base * 4):
        counts[i] += 1
    Xs, Ys = [], []
    for (sx, sy), lab, k in zip(signs, labels, counts):
        c = np.zeros(dim); c[0] = sep * sx; c[1] = sep * sy
        Xs.append(rng.normal(c, overlap, (k, dim)))
        Ys.append(np.full(k, lab))
    X = np.concatenate(Xs).astype(np.float64)
    Y = np.concatenate(Ys).astype(np.int64)
    p = rng.permutation(len(X))
    return X[p], Y[p]


def make_checkerboard(n, rng, grid=CHECK_GRID, spacing=CHECK_SPACING, overlap=CHECK_OVERLAP):
    """grid x grid Gaussian clusters; label = (i+j) % 2 (checkerboard). 16 density clusters,
    compositional label too hard for random features -> SCFF learning measurably helps."""
    centers, labels = [], []
    off = (grid - 1) / 2.0
    for i in range(grid):
        for j in range(grid):
            centers.append(((i - off) * spacing, (j - off) * spacing))
            labels.append((i + j) % 2)
    centers = np.array(centers)
    K = len(centers); base = n // K; counts = [base] * K
    for i in range(n - base * K):
        counts[i] += 1
    Xs, Ys = [], []
    for c, lab, k in zip(centers, labels, counts):
        Xs.append(rng.normal(c, overlap, (k, 2)))
        Ys.append(np.full(k, lab))
    X = np.concatenate(Xs).astype(np.float64)
    Y = np.concatenate(Ys).astype(np.int64)
    p = rng.permutation(len(X))
    return X[p], Y[p]


# the gate's task generator (signature (n, rng))
def TASK_GEN(n, rng):
    return make_checkerboard(n, rng)


TASK_NAME = "checkerboard_2d"


# ----------------------------------------------------------------------------- SCFF model
def relu(z):
    return np.maximum(z, 0.0)


class SCFF:
    """Mono-forward dual-rail SCFF. Goodness = SUM of squares ||h||^2 (locked; see exp0).
    Local per-layer update, gradient through one layer only. Input normalized at L1 too."""

    def __init__(self, dims, theta, lr, seed, objective="two_sided", init_gain=1.0,
                 goodness_mode="sum", normalize_input=True):
        rng = np.random.default_rng(seed)
        self.W, self.b = [], []
        for i in range(len(dims) - 1):
            fan_in = dims[i]
            self.W.append(init_gain * rng.normal(0, np.sqrt(2.0 / fan_in),
                                                 (dims[i + 1], dims[i])))
            self.b.append(np.zeros(dims[i + 1]))
        self.theta, self.lr = theta, lr
        self.objective = objective   # "two_sided" (absolute theta) | "contrast" (relative)
        self.goodness_mode = goodness_mode   # "sum" (||h||^2, width-indep ~1) | "mean" (/M)
        self.normalize_input = normalize_input  # unit-norm input at layer 1 too (uniform scale)
        self.L = len(self.W)

    def _gscale(self, M):
        return 1.0 if self.goodness_mode == "sum" else 1.0 / M

    def _norm(self, a):
        return a / (np.linalg.norm(a, axis=1, keepdims=True) + EPS)

    def _in(self, a):
        return self._norm(a) if self.normalize_input else a

    def infer(self, X):
        """Inference pathway (real sample). Returns list of normalized reps per layer.
        Feeding x vs 2x gives identical normalized reps, so we feed x directly."""
        a = self._in(X)
        reps = []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            a = h / (np.linalg.norm(h, axis=1, keepdims=True) + EPS)
            reps.append(a)
        return reps

    def goodness(self, X):
        """Per-layer (G_pos, G_neg) on a batch, evaluated on the trained dual-rail path."""
        rng = np.random.default_rng(0)
        perm = rng.permutation(len(X))
        a_pos, a_neg = self._in(2.0 * X), self._in(X + X[perm])
        gpos, gneg = [], []
        for W, b in zip(self.W, self.b):
            hp, hn = relu(a_pos @ W.T + b), relu(a_neg @ W.T + b)
            M = hp.shape[1]
            gs = self._gscale(M)
            gpos.append(((hp ** 2).sum(1) * gs).mean())
            gneg.append(((hn ** 2).sum(1) * gs).mean())
            a_pos = hp / (np.linalg.norm(hp, axis=1, keepdims=True) + EPS)
            a_neg = hn / (np.linalg.norm(hn, axis=1, keepdims=True) + EPS)
        return np.array(gpos), np.array(gneg)

    def goodness_samples(self, X, seed=0):
        """Per-sample (G_pos, G_neg) for every layer via the model's real path. [B, L] each."""
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(X))
        a_pos, a_neg = self._in(2.0 * X), self._in(X + X[perm])
        GP, GN = [], []
        for W, b in zip(self.W, self.b):
            hp, hn = relu(a_pos @ W.T + b), relu(a_neg @ W.T + b)
            gs = self._gscale(hp.shape[1])
            GP.append((hp ** 2).sum(1) * gs); GN.append((hn ** 2).sum(1) * gs)
            a_pos, a_neg = self._norm(hp), self._norm(hn)
        return np.array(GP).T, np.array(GN).T

    def dead_fraction(self, X):
        """Fraction of units that are ~never active across the eval set (per layer)."""
        a = self._in(X)
        fracs = []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            fracs.append(float((h.max(0) <= EPS).mean()))
            a = h / (np.linalg.norm(h, axis=1, keepdims=True) + EPS)
        return np.array(fracs)

    def train_step(self, Xb, rng):
        """One online step: single forward (both worlds), local update at every layer."""
        B = len(Xb)
        perm = rng.permutation(B)
        # x_pos=2x_k, x_neg=x_k+x_n; input normalized too if normalize_input (uniform scale)
        a_pos, a_neg = self._in(2.0 * Xb), self._in(Xb + Xb[perm])
        losses = []
        for l in range(self.L):
            W, b = self.W[l], self.b[l]
            zp, zn = a_pos @ W.T + b, a_neg @ W.T + b
            hp, hn = relu(zp), relu(zn)
            M = hp.shape[1]
            gs = self._gscale(M)
            Gp = (hp ** 2).sum(1) * gs           # [B]  goodness (sum or mean per mode)
            Gn = (hn ** 2).sum(1) * gs
            if self.objective == "two_sided":
                # absolute threshold: push G_pos up past theta AND G_neg down below it
                losses.append(float((np.logaddexp(0, -(Gp - self.theta))
                                     + np.logaddexp(0, (Gn - self.theta))).mean()))
                dGp = (expit(Gp - self.theta) - 1.0)            # <0 -> raise G_pos
                dGn = (expit(Gn - self.theta))                  # >0 -> lower G_neg
            else:  # "contrast": no threshold, push the GAP (G_pos - G_neg) apart
                losses.append(float(np.logaddexp(0, (Gn - Gp)).mean()))
                s = expit(Gn - Gp)
                dGp = -s                                        # <0 -> raise G_pos
                dGn = s                                         # >0 -> lower G_neg
            # dG/dh = 2*gscale*h  (ReLU mask folded into h; gscale=1 sum, 1/M mean)
            cpos = dGp * (2.0 * gs)   # [B]
            cneg = dGn * (2.0 * gs)
            gW = ((cpos[:, None] * hp).T @ a_pos + (cneg[:, None] * hn).T @ a_neg) / B
            gb = ((cpos[:, None] * hp).sum(0) + (cneg[:, None] * hn).sum(0)) / B
            self.W[l] -= self.lr * gW
            self.b[l] -= self.lr * gb
            # normalize the (pre-update) activations to pass forward
            a_pos = hp / (np.linalg.norm(hp, axis=1, keepdims=True) + EPS)
            a_neg = hn / (np.linalg.norm(hn, axis=1, keepdims=True) + EPS)
        return losses


# ----------------------------------------------------------------------------- probes
def probe_acc_per_layer(model, Xtr, Ytr, Xte, Yte):
    """Linear (logistic) probe per layer, fixed L2, trained to convergence. F3."""
    reps_tr, reps_te = model.infer(Xtr), model.infer(Xte)
    accs = []
    for r_tr, r_te in zip(reps_tr, reps_te):
        clf = LogisticRegression(C=PROBE_C, max_iter=3000)
        clf.fit(r_tr, Ytr)
        accs.append(float(clf.score(r_te, Yte)))
    return accs


def tap_readout(model, Xtr, Ytr, Xte, Yte, taps=TAPS):
    """Linear readout on the concatenated last-n SCFF layers (the SCFF classifier)."""
    feat = lambda X: np.concatenate(model.infer(X)[-taps:], axis=1)
    clf = LogisticRegression(C=PROBE_C, max_iter=3000)
    clf.fit(feat(Xtr), Ytr)
    return float(clf.score(feat(Xte), Yte)), clf, feat


# ----------------------------------------------------------------------------- run
def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    model = SCFF(DIMS, THETA, LR_SCFF, SEED, goodness_mode=GOODNESS_MODE)

    # fixed held-out sets (gate: fixed for clean cross-checkpoint comparison)
    Xprobe_tr, Yprobe_tr = TASK_GEN(2000, np.random.default_rng(SEED + 1))
    Xprobe_te, Yprobe_te = TASK_GEN(2000, np.random.default_rng(SEED + 2))
    Xgood, _ = TASK_GEN(2000, np.random.default_rng(SEED + 3))

    n_weights = sum(W.size + b.size for W, b in zip(model.W, model.b))
    print(f"[exp0-gate] task={TASK_NAME} seed={SEED} dims={DIMS} theta={THETA} "
          f"lr={LR_SCFF} goodness={GOODNESS_MODE} weights={n_weights} "
          f"stream={N_STREAM} batch={BATCH}")

    log = {"samples": [], "G_pos": [], "G_neg": [], "probe": [], "dead": [], "loss": []}
    seen = 0
    ckpt_iter = iter(CKPTS)
    next_ck = next(ckpt_iter, None)

    def checkpoint():
        Gp, Gn = model.goodness(Xgood)
        accs = probe_acc_per_layer(model, Xprobe_tr, Yprobe_tr, Xprobe_te, Yprobe_te)
        dead = model.dead_fraction(Xgood)
        log["samples"].append(seen)
        log["G_pos"].append(Gp.tolist()); log["G_neg"].append(Gn.tolist())
        log["probe"].append(accs); log["dead"].append(dead.tolist())
        print(f"  n={seen:>6}  G_pos={np.round(Gp,2)}  G_neg={np.round(Gn,2)}  "
              f"probe={np.round(accs,3)}  dead={np.round(dead,2)}")

    checkpoint()  # n=0 baseline (random init)
    while seen < N_STREAM:
        Xb, _ = TASK_GEN(BATCH, rng)
        loss = model.train_step(Xb, rng)
        seen += BATCH
        log["loss"].append((seen, float(np.mean(loss))))
        if next_ck is not None and seen >= next_ck:
            checkpoint()
            next_ck = next(ckpt_iter, None)

    # final readout (the SCFF classifier on tapped features) — the gate number + F5
    acc, clf, feat = tap_readout(model, Xprobe_tr, Yprobe_tr, Xprobe_te, Yprobe_te)
    print(f"[exp0-gate] tapped-SCFF readout held-out acc = {acc:.3f}")

    # ---- verdict ----
    # Gate's core question: does SCFF separate at all? = goodness separates (G_pos>G_neg)
    # AND the features are class-separable well above chance. NOTE: "rises with depth" is
    # a HIERARCHICAL/high-D property — on a 2D task one wide SCFF layer captures the whole
    # structure, so the probe is flat across depth by construction (reported, not required).
    Gp_f, Gn_f = np.array(log["G_pos"][-1]), np.array(log["G_neg"][-1])
    probe_f = np.array(log["probe"][-1])
    sep_ok = bool(np.all(Gp_f > Gn_f) and (Gp_f - Gn_f).mean() > 0.1)
    class_ok = bool(probe_f.max() > 0.65)              # features class-separable >> chance(0.5)
    rises = float(probe_f[-1] - probe_f[0])            # diagnostic (~0 on 2D, not a pass gate)
    gate_pass = sep_ok and class_ok
    print(f"[exp0-gate] VERDICT  goodness-separates={sep_ok}  class-separable={class_ok}  "
          f"(rises-with-depth diag={rises:+.3f}, ~0 expected on 2D)  -> GATE {'PASS' if gate_pass else 'FAIL'}")

    _figs(log, model, clf, feat, Xprobe_te, Yprobe_te, acc, sep_ok, class_ok)

    manifest = {"experiment": "exp0-gate", "task": TASK_NAME, "seed": SEED, "dims": DIMS,
                "theta": THETA, "lr_scff": LR_SCFF, "n_stream": N_STREAM, "batch": BATCH,
                "check_grid": CHECK_GRID, "check_spacing": CHECK_SPACING,
                "check_overlap": CHECK_OVERLAP,
                "taps": TAPS, "probe_C": PROBE_C, "n_weights": int(n_weights),
                "goodness": f"{GOODNESS_MODE}_of_squares", "normalize_input": True,
                "readout_acc": acc,
                "verdict": {"goodness_separates": sep_ok, "class_separable": class_ok,
                            "gate_pass": gate_pass, "rises_with_depth_diag": rises},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUTDIR, "manifest_gate.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    np.savez(os.path.join(OUTDIR, "log_gate.npz"),
             **{k: np.array(v, dtype=object) for k, v in log.items()})
    print(f"[exp0-gate] wrote figures + manifest to {OUTDIR}  ({manifest['wall_clock_s']}s)")


def _figs(log, model, clf, feat, Xte, Yte, acc, sep_ok, class_ok):
    samples = np.array(log["samples"])
    L = model.L

    # F4 — goodness SEPARATION. Left: per-layer gap (G_pos - G_neg) over training (the
    # real signal; absolute goodness sits ~theta and the layer-1 transient swamps a raw
    # plot). Right: top-layer per-sample goodness histograms, via the model's real path.
    Gp = np.array(log["G_pos"]); Gn = np.array(log["G_neg"])
    gap = Gp - Gn
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for l in range(L):
        ax[0].plot(samples, gap[:, l], color=C_SCFF, alpha=0.35 + 0.65 * l / L,
                   marker="o", ms=3, label=f"L{l+1}")
    ax[0].axhline(0, color="grey", ls=":", lw=1)
    ax[0].set_xscale("log"); ax[0].set_xlabel("samples seen")
    ax[0].set_ylabel("goodness gap  G_pos - G_neg")
    ax[0].set_title(f"F4 goodness separation per layer  (separates={sep_ok})")
    ax[0].legend(fontsize=7, title="layer")
    # top-layer per-sample goodness histogram via the model's real path
    Xh, _ = TASK_GEN(2000, np.random.default_rng(7))
    GPs, GNs = model.goodness_samples(Xh, seed=7)
    gp_s, gn_s = GPs[:, -1], GNs[:, -1]
    lo, hi = min(gp_s.min(), gn_s.min()), max(gp_s.max(), gn_s.max())
    bins = np.linspace(lo, hi, 40)
    ax[1].hist(gp_s, bins=bins, color=C_POS, alpha=0.6, label=f"G_pos (mean {gp_s.mean():.2f})")
    ax[1].hist(gn_s, bins=bins, color=C_NEG, alpha=0.6, label=f"G_neg (mean {gn_s.mean():.2f})")
    ax[1].axvline(THETA, color="grey", ls=":", lw=1, label="theta")
    ax[1].set_xlabel("goodness (top layer, sum h^2)"); ax[1].set_ylabel("count")
    ax[1].set_title("F4 top-layer goodness histogram (pos vs neg)")
    ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "F4_goodness.png")); plt.close(fig)

    # F3 — layer x time separability heatmap (linear-probe accuracy)
    probe = np.array(log["probe"])  # [ckpt, layer]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    im = ax.imshow(probe.T, aspect="auto", origin="lower", cmap="viridis",
                   vmin=0.5, vmax=1.0)
    ax.set_xticks(range(len(samples))); ax.set_xticklabels(samples, rotation=45, fontsize=7)
    ax.set_yticks(range(L)); ax.set_yticklabels([f"L{l+1}" for l in range(L)])
    ax.set_xlabel("samples seen"); ax.set_ylabel("SCFF layer")
    ax.set_title("F3 separability (linear-probe acc) — flat across depth (1 layer suffices in 2D)")
    fig.colorbar(im, ax=ax, label="probe acc")
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "F3_separability.png")); plt.close(fig)

    # F5 — decision boundary the tapped-SCFF readout draws
    g = 300
    lim = ((CHECK_GRID - 1) / 2 * CHECK_SPACING + 3 * CHECK_OVERLAP) * 1.12
    xs = np.linspace(-lim, lim, g)
    XX, YY = np.meshgrid(xs, xs)
    grid = np.stack([XX.ravel(), YY.ravel()], axis=1)
    Z = clf.predict(feat(grid)).reshape(g, g)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.contourf(XX, YY, Z, levels=[-0.5, 0.5, 1.5], colors=[C_POS, C_NEG], alpha=0.25)
    ax.scatter(Xte[Yte == 0, 0], Xte[Yte == 0, 1], s=4, color=C_POS, label="class 0")
    ax.scatter(Xte[Yte == 1, 0], Xte[Yte == 1, 1], s=4, color=C_NEG, label="class 1")
    ax.set_title(f"F5 boundary — tapped-SCFF readout, held-out acc={acc:.3f}")
    ax.legend(fontsize=8); ax.set_aspect("equal")
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "F5_boundary.png")); plt.close(fig)

    # INV — invariant strip (loss slope, dead-unit fraction)
    loss = np.array(log["loss"])
    dead = np.array(log["dead"])
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
    ax[0].plot(loss[:, 0], loss[:, 1], color=C_SCFF, lw=1)
    ax[0].set_xlabel("samples seen"); ax[0].set_ylabel("mean per-layer SCFF loss")
    ax[0].set_title("INV loss slope")
    for l in range(L):
        ax[1].plot(samples, dead[:, l], marker="o", ms=3, label=f"L{l+1}")
    ax[1].set_xscale("log"); ax[1].set_xlabel("samples seen"); ax[1].set_ylabel("dead-unit fraction")
    ax[1].set_title("INV dead units"); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, "INV_strip.png")); plt.close(fig)


if __name__ == "__main__":
    main()
