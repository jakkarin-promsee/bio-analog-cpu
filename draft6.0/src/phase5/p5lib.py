"""
p5lib — the Phase-5 apparatus: SOLVE DEPTH (compose it, read it cheaply). A CHIP NETLIST, not normal Python:
every class is a substrate element; every reuse is a *tested* primitive carried forward unchanged, because the
project's recurring silent killer is a missing sign/direction and that bug lives in re-implementations — so we
re-implement nothing we can import.

Phase 5 grows rung-by-rung; THIS file currently carries the **P5.0 slice** (the bench + the decay reproduction +
the guards). Later rungs ADD, they do not rewrite: PerDepthHeads (P5.4), CalibratedExit (P5.5), FrozenResidual
(P5.6), profiler/mlp_probe/truncation_racer (P5.3), the FORWARD expected-compute meter (P5.5), continual_harness
(P5.7) — see design.md §6.

Reused, NOT re-implemented:
  p3lib : SCFFContrastOLU (the adopted contrast+coordination cell — `window`, `temp`), _view_fwd/_view_bwd,
          layernorm fwd/vjp
  p4lib : make_gauss + bayes_error (the known-Bayes flat task), fit_readout / readout_feats (the GD readout),
          linear_probe (the PINNED separability metric), race_bp (the genuinely-tuned BP ceiling — the
          old-world achievable reference), n_w (weight count)
  p2lib : make_tierb (the headroom task), effective_rank, normalize / relu / EPS

NEW here (P5.0):
  SCFFContrastOverlap : SCFFContrastOLU + a coordination STRIDE — the P5.1 (`temp`) / P5.2 (`window`) cell.
                        Ported VERBATIM from draft6.0/idea/gd-replan/t3/run_t3.py. The licence to port is the equivalence
                        guard: stride==window reproduces SCFFContrastOLU bit-for-bit (a subclass bug cannot
                        masquerade as a finding).
  make_mixed          : the iso-budget flat+headroom corruption detector, DISJOINT label space (design §6's
                        deliberate refinement of P4.3's shared-label make_mixed — disjoint labels remove the
                        same-class collision so the single readout's per-subtask accuracy reflects depth-
                        corruption, not label overlap). Carries te_masks.
  equivalence_guard / fd_gradient_check : the pre-cell antidote to the sign/direction bug (run before any cell).
  cost_overlap        : (backward WORK, backward DEPTH = window) — the substrate cost meter for the cell.

numpy only. The run layer sets OMP_NUM_THREADS=1 + python -u + PYTHONIOENCODING=utf-8 (the OpenMP-phantom + cp874
guards) before importing this.
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase4"))                # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "phase3"))                # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "phase2"))                # p2lib
from p4lib import (make_gauss, bayes_error, fit_readout, readout_feats,    # noqa: E402
                   linear_probe, race_bp, n_w)
from p3lib import SCFFContrastOLU                                       # noqa: E402
from p2lib import make_tierb, effective_rank, normalize, relu, EPS      # noqa: E402
from models_extra import MLP                                           # noqa: E402  (path added by p4lib import)


def mlp_probe(Ftr, Ytr, Fte, Yte, C, seed, epochs=120, lr=3e-3, batch=64, hidden=64):
    """The lost-vs-rotated diagnostic (P5.3): an [F, hidden, C] MLP probe sharing linear_probe's EXACT protocol
    (same frozen split, epochs, lr, batch) — only the hidden layer differs, so 'rotated (MLP recovers) vs lost
    (it can't)' cannot be a probe-tuning artifact. Returns held-out accuracy."""
    pr = MLP([Ftr.shape[1], hidden, C], seed, lr=lr); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Ftr))
        for s in range(0, len(Ftr), batch):
            pr.train_step(Ftr[idx[s:s + batch]], Ytr[idx[s:s + batch]])
    return float((pr.predict(Fte) == Yte).mean())

# re-export the carried primitives so a run script imports ONE module
__all__ = [
    "SCFFContrastOverlap", "cost_overlap", "make_headroom", "make_flat", "make_mixed",
    "equivalence_guard", "fd_gradient_check", "mean_infonce_loss", "ours_budget", "mlp_probe",
    "fwd_macs_stack", "fwd_macs_head", "forward_cost_head", "forward_cost_alltap",
    "forward_cost_trunc", "exit_compute", "CISTREAM_TASKS", "synth_stream", "train_scff_stream",
    "CalibratedExit", "continual_eval", "acc_matrix_metrics", "load_digits_split", "load_cifar_flat",
    "make_gauss", "bayes_error", "fit_readout", "readout_feats", "linear_probe", "race_bp",
    "make_tierb", "effective_rank", "normalize", "relu", "EPS", "n_w",
]


# ============================================================ the cell (P5.1 temp / P5.2 window)
class SCFFContrastOverlap(SCFFContrastOLU):
    """[VERBATIM from draft6.0/idea/gd-replan/t3/run_t3.py] SCFFContrastOLU + an overlap STRIDE. Coordination groups start
    every `stride` layers; each group is EXACTLY `window` layers deep (the last group is anchored at L-window
    so the top is always covered at full depth), so the backward DEPTH (gradient chain length — the substrate-
    expensive op) is always = window regardless of overlap. `stride == window` reproduces the original
    non-overlapping SCFFContrastOLU (the equivalence guard). Per-layer gradients are divided by the layer's
    participation count, so overlap changes credit REACH, not effective lr (one-thing-changed). `temp` is the
    InfoNCE temperature (the P5.1 lever); `window`/`stride` are the P5.2 credit-reach lever."""

    def __init__(self, dims, *, stride=None, window=2, **kw):
        super().__init__(dims, window=window, **kw)
        self.stride = window if stride is None else stride

    def _starts(self):
        w = min(self.window, self.L)
        last = self.L - w
        st = list(range(0, last + 1, self.stride))
        if not st or st[-1] != last:
            st.append(last)
        return st, w

    def train_step(self, Xb, rng, neg_partner=None):
        a0 = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb); I = np.eye(B)
        # clean rep at each layer's INPUT, computed once with current (fixed) weights -> a_in[l] = input to layer l
        a_in = [a0]; ac = a0
        for l in range(self.L):
            ac = self._norm(np.maximum(ac @ self.W[l].T + self.b[l], 0.0))
            a_in.append(ac)
        gW = [np.zeros_like(Wl) for Wl in self.W]; gb = [np.zeros_like(bl) for bl in self.b]
        cnt = np.zeros(self.L)
        starts, w = self._starts()
        for s in starts:
            a = a_in[s]; din = a.shape[1]
            a1 = a * (rng.random((B, din)) >= self.mask_ratio)
            a2 = a * (rng.random((B, din)) >= self.mask_ratio)
            u1, n1, c1, ht1 = self._view_fwd(a1, s, w)
            u2, n2, c2, ht2 = self._view_fwd(a2, s, w)
            S = (u1 @ u2.T) / self.temp; P = softmax(S, axis=1); dS = (P - I) / B
            du1 = (dS @ u2) / self.temp; du2 = (dS.T @ u1) / self.temp
            self._view_bwd(du1, n1, c1, ht1, w, gW, gb, s)
            self._view_bwd(du2, n2, c2, ht2, w, gW, gb, s)
            cnt[s:s + w] += 1
        upd2 = 0.0
        for l in range(self.L):
            scale = self.lr / max(cnt[l], 1.0)                          # lr-match: divide by participation count
            dW = scale * gW[l]; db = scale * gb[l]
            self.W[l] -= dW
            self.b[l] -= db
            upd2 += float((dW * dW).sum() + (db * db).sum())
        self.last_update_norm = float(np.sqrt(upd2))                    # effective STEP magnitude (the lr-match meter)


# ============================================================ substrate cost meter (backward work, backward depth)
def _mlp_cost(dims):                                                   # full backprop work for a small MLP
    Ln = len(dims) - 1
    return sum((Ln - l) * (dims[l] + 1) * dims[l + 1] for l in range(Ln))


def cost_overlap(D, Wd, Lb, window, stride, C, readout_last_n=1):
    """(total backward WORK, max backward DEPTH). DEPTH = the gradient chain length (substrate-expensive) =
    window. WORK = sum over groups, over layers in group, of window*(din+1)*dout. Labelled substrate work,
    NEVER 'energy'. [VERBATIM from t3]"""
    dims = [D] + [Wd] * Lb
    w = min(window, Lb); last = Lb - w
    starts = list(range(0, last + 1, stride))
    if not starts or starts[-1] != last:
        starts.append(last)
    bulk = 0
    for s in starts:
        for j in range(w):
            l = s + j
            bulk += w * (dims[l] + 1) * dims[l + 1]
    readout = _mlp_cost([min(readout_last_n, Lb) * Wd, 32, C])
    return bulk + readout, w


def ours_budget(D, Wd, L, C, readout_last_n=1):
    """Total weight count of the OURS L/Wd cell (bulk + last-n readout) — the iso-budget target race_bp matches."""
    return n_w([D] + [Wd] * L) + n_w([min(readout_last_n, L) * Wd, 32, C])


# ============================================================ FORWARD-MACs meter (P5.4/P5.5 — the read-cost meter)
def fwd_macs_stack(D, Wd, depth):
    """Forward MACs to compute the SCFF reps up to `depth` layers (the matmuls; norm/relu are O(Wd), ignored)."""
    if depth <= 0:
        return 0
    return D * Wd + (depth - 1) * Wd * Wd


def fwd_macs_head(F, C, hidden=32):
    """Forward MACs of a readout head [F, hidden, C]."""
    return F * hidden + hidden * C


def forward_cost_head(D, Wd, depth, C, hidden=32):
    """Read a per-depth head at `depth`: forward to that depth + the head on Wd features (the lazy-exit cost)."""
    return fwd_macs_stack(D, Wd, depth) + fwd_macs_head(Wd, C, hidden)


def forward_cost_alltap(D, Wd, L, C, hidden=32):
    """All-tap: forward all L layers + the big head on the L·Wd concatenation (the burns-the-80/20 cost)."""
    return fwd_macs_stack(D, Wd, L) + fwd_macs_head(L * Wd, C, hidden)


def forward_cost_trunc(D, Wd, k, C, hidden=32):
    """Truncation reader: a from-scratch L=k SCFF stack read at its TOP layer (1 head) — the cost FLOOR every
    exit tier must beat (fewer Scaps = cheaper silicon)."""
    return fwd_macs_stack(D, Wd, k) + fwd_macs_head(Wd, C, hidden)


def exit_compute(D, Wd, C, depths, hidden=32):
    """The FORWARD expected-compute of an early-exit reader (design §4/§6 — a FORWARD meter; the P4 meter is
    backward-only). A sample exiting at 0-indexed depth d forwarded (d+1) SCFF layers AND ran heads 0..d (the
    gate IS the head's max-softmax, so the gate cost = the head cost). Mean over the stream, in forward-MACs;
    all-tap (forward_cost_alltap) and truncation (forward_cost_trunc) use the same primitives → commensurable."""
    per = np.array([fwd_macs_stack(D, Wd, d + 1) + (d + 1) * fwd_macs_head(Wd, C, hidden) for d in depths])
    return float(per.mean())


# ============================================================ the continual home turf (P5.5 STOP ① / P5.7 gate)
CISTREAM_TASKS = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]                # 10 classes -> 5 tasks of 2 (digits shape)


def synth_stream(n_tr, n_te, overlap, seed, *, dim=40, n_class=10, n_clusters=40):
    """The P4.5 class-incremental synthetic stream (10 classes / 40 clusters / 5 tasks of 2 — the same stream
    SHAPE as the digits A6 home). Returns Xtr,Ytr,Xte,Yte. [promoted from phase4/exp5/run_p4_5.py synth_stream]"""
    Xtr, Ytr, _ = make_gauss(n_tr, np.random.default_rng(seed), dim=dim, n_class=n_class,
                             n_clusters=n_clusters, overlap=overlap)
    Xte, Yte, _ = make_gauss(n_te, np.random.default_rng(seed + 7), dim=dim, n_class=n_class,
                             n_clusters=n_clusters, overlap=overlap)
    return Xtr, Ytr, Xte, Yte


def train_scff_stream(cell, Xtr, Ytr, tasks, seed, *, scff_ep=8, batch=32):
    """Train an SCFF cell FORWARD-ONLY through a class-incremental stream (each task's classes seen once, in
    order — the A6 setup). SCFF is unsupervised, so no labels are used HERE; the readout is consolidated
    separately (the sleep full-buffer refit). Returns the buffered (Xbuf, Ybuf) = the replay history sleep uses.
    Cell-agnostic (the A6 mechanism promoted out of phase3/exp3/run_p3_3.py's run_condition)."""
    rng = np.random.default_rng(seed)
    bufX, bufY = [], []
    for cls in tasks:
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(scff_ep):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), batch):
                xb = Xt[idx[s:s + batch]]
                if len(xb) >= 4:                                        # InfoNCE needs in-batch negatives
                    cell.train_step(xb, rng)
        bufX.append(Xt); bufY.append(Yt)
    return np.concatenate(bufX), np.concatenate(bufY)


class CalibratedExit:
    """Head max-softmax early-exit — class-CONFIDENCE, the SPINE (NOT goodness/energy, NOT entropy-of-energy).
    Given per-depth head logits, exit at the SHALLOWEST depth whose max-softmax ≥ τ (else the deepest). τ is
    calibrated CALM-style: the LOWEST τ (cheapest/shallowest) that still holds ≥ keep·(all-tap acc) on a
    calibration split DISJOINT from test. NOT a learned halting policy (cut — design §0.4/§8 C2). The spine risk
    (confidence is itself a magnitude that mis-calibrates under shift) is bounded by `oracle_depth` (the
    true-class signal) and by calibrating on early-task data, evaluating on the shifted stream (design §6)."""

    def __init__(self, L):
        self.L = L

    @staticmethod
    def conf_pred(logits_list):
        """(N,L) max-softmax confidence and (N,L) argmax class, from a list of per-depth head logits."""
        P = [softmax(Z, axis=1) for Z in logits_list]
        conf = np.stack([p.max(1) for p in P], 1)
        pred = np.stack([p.argmax(1) for p in P], 1)
        return conf, pred

    def exit_depth(self, conf, tau):
        passed = conf >= tau
        return np.where(passed.any(1), passed.argmax(1), self.L - 1)    # shallowest passing, else deepest

    def predict(self, conf, pred, tau):
        d = self.exit_depth(conf, tau)
        return pred[np.arange(len(d)), d], d

    def calibrate(self, conf_cal, pred_cal, Ycal, alltap_acc, *, keep=0.95, grid=None):
        """τ = the LOWEST threshold whose gated accuracy on the (disjoint) cal split holds ≥ keep·all-tap acc."""
        if grid is None:
            grid = np.linspace(0.25, 0.999, 60)                         # τ candidates over max-softmax ∈ (1/C, 1]
        target = keep * alltap_acc
        for tau in grid:                                                # ascending: first (cheapest) that holds
            pr, _ = self.predict(conf_cal, pred_cal, tau)
            if float((pr == Ycal).mean()) >= target:
                return float(tau)
        return float(grid[-1])                                          # none holds -> most conservative

    def oracle_depth(self, pred, Y):
        """Best-per-input layer: the SHALLOWEST depth whose head is CORRECT (else deepest) — the upper bound on
        ANY gate, and the true-class signal the label-free max-softmax proxy is scored against (the spine risk)."""
        correct = pred == Y[:, None]
        return np.where(correct.any(1), correct.argmax(1), self.L - 1)


# ============================================================ the A6 continual-safety gate (P5.7 — the spine gate)
def acc_matrix_metrics(a):
    """a[i][k] = test acc on task k after learning task i (lower-tri). Returns AA (final all-task mean), BWT
    (mean over k<T of a[T-1][k] − a[k][k]), forget (mean max-drop). [GEM/CL-survey conventions, verbatim from
    phase2/exp6]."""
    T = len(a)
    aa = float(np.mean([a[T - 1][k] for k in range(T)]))
    bwt = float(np.mean([a[T - 1][k] - a[k][k] for k in range(T - 1)])) if T > 1 else 0.0
    forget = float(np.mean([max(a[i][k] for i in range(k, T)) - a[T - 1][k] for k in range(T - 1)])) if T > 1 else 0.0
    return aa, bwt, forget


def load_digits_split(seed, n_train=1200, n_test=600):
    """The A6 home anchor (8×8 digits, 64-D). DATA ONLY — sklearn.datasets.load_digits loads a small array; no
    OpenMP compute (the phantom-hang was KMeans/LogReg, never the loader). [verbatim from phase2/exp6]."""
    from sklearn.datasets import load_digits
    d = load_digits(); X = (d.data / 16.0).astype(np.float64); Y = d.target.astype(np.int64)
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return X[tr], Y[tr], X[te], Y[te]


_CIFAR_GZ = os.path.expanduser(
    "~/scikit_learn_data/openml/openml.org/data/v1/download/16797613/CIFAR_10.arff.gz")
_CIFAR_CACHE = None


def load_cifar_flat(seed, n_train=5000, n_test=2000):
    """CIFAR-10-FLAT (3072-D, 10-class) — the 3072-D real flat anchor (design §5/§6; the Phase-2/3 'wall').
    Reads the local arff.gz cache (ported verbatim from phase3/exp0/run_p3_0.load_cifar_local). DATA ONLY."""
    global _CIFAR_CACHE
    if _CIFAR_CACHE is None:
        import gzip
        if not os.path.exists(_CIFAR_GZ):
            raise FileNotFoundError(f"CIFAR cache missing at {_CIFAR_GZ} (see phase3/exp0 load_cifar_local).")
        X = np.empty((30000, 3072), np.float32); Y = np.empty(30000, np.int64); i = 0
        with gzip.open(_CIFAR_GZ, "rt", encoding="utf-8", errors="replace") as f:
            indata = False
            for line in f:
                if not indata:
                    if line.strip().lower() == "@data":
                        indata = True
                    continue
                vals = line.rstrip("\n").split(",")
                if len(vals) != 3073:
                    continue
                X[i] = np.array(vals[:3072], np.float32); Y[i] = int(vals[3072]); i += 1
        _CIFAR_CACHE = (X[:i] / 255.0, Y[:i])
    X, Y = _CIFAR_CACHE
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te]


def continual_eval(dims, temp, window, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                   *, scff_ep=8, sleep_ep=60, batch=32, sleep=True, probe=True):
    """The A6 home-turf gate, PROMOTED from phase3/exp3/run_p3_3.run_condition and parameterized for the
    committed cell (the design §6 'real build work, not a reuse'). An SCFFContrastOverlap bulk learns FORWARD-ONLY
    through a class-incremental stream; the **all-tap** readout is sleep-consolidated (full-buffer refit) per task
    (the validated A6 mechanism — sleep recovers what online forgets). Returns AA/BWT/forget (GEM/CL conventions),
    the per-task accuracy matrix, and the all-class SCFF linear-probe trajectory (does the BULK forget?). Pure
    numpy + the numpy linear_probe (NO sklearn compute → phantom-safe). `sleep=False` = the rot control."""
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]   # fixed all-class probe set
    cell = SCFFContrastOverlap(dims, lr=0.03, seed=seed, window=window, stride=window, mask_ratio=0.5, temp=temp)
    a = [[0.0] * len(tasks) for _ in range(len(tasks))]
    bufX, bufY, scff_probe = [], [], []
    ro = None

    def tap(X):
        return readout_feats(cell.infer(X), None)                      # all-tap concat

    for t, cls in enumerate(tasks):
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(scff_ep):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), batch):
                xb = Xt[idx[s:s + batch]]
                if len(xb) >= 4:
                    cell.train_step(xb, rng)
        bufX.append(Xt); bufY.append(Yt)
        BX, BY = np.concatenate(bufX), np.concatenate(bufY)
        if sleep:
            ro = fit_readout(tap(BX), BY, C, seed, epochs=sleep_ep)     # full-buffer replay = the A6 consolidation
        else:
            ro = fit_readout(tap(Xt), Yt, C, seed, epochs=sleep_ep)     # no-sleep rot control: current task only
        for k in range(t + 1):
            mk = np.isin(Yte, tasks[k])
            a[t][k] = float((ro.predict(tap(Xte[mk])) == Yte[mk]).mean())
        if probe:
            scff_probe.append(linear_probe(tap(Xpr), Ypr, tap(Xte), Yte, C, seed, epochs=120))
    aa, bwt, forget = acc_matrix_metrics(a)
    return dict(aa=aa, bwt=bwt, forget=forget, matrix=a,
                scff_probe=scff_probe or [0.0] * len(tasks))


# ============================================================ tasks (the decay dials)
def make_headroom(n, seed, *, dim=40, n_class=4):
    """The headroom task (depth SHOULD pay) — make_tierb grid4/n_active3, the P4.3/T3 config (unchanged so the
    decay is directly comparable). No exact Bayes (compositional) -> its ceilings are w12 + tuned-BP."""
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=dim, overlap=0.6,
                      label="random", n_class=n_class)


def make_flat(n, seed, *, dim=40, n_class=4):
    """The flat task (known Bayes; depth should NOT pay) — make_gauss, the P4.3 config (overlap 0.7). Returns
    X, Y, params (params -> bayes_error for the true ceiling)."""
    X, Y, params = make_gauss(n, np.random.default_rng(seed), dim=dim, n_class=n_class, n_clusters=16, overlap=0.7)
    return X, Y, params


def make_mixed(n, seed, *, dim=40, n_class=4):
    """The corruption detector — iso-budget flat+headroom in ONE problem, DISJOINT label space (design §6's
    refinement of P4.3's shared-label make_mixed). flat (make_gauss) -> labels 0..C-1; headroom (make_tierb) ->
    labels C..2C-1; equal samples + equal class count per subtask; the two subtasks disjoint in label space, so
    the single 2C-class readout's per-subtask accuracy reflects depth-corruption, not same-label collision.
    Returns X, Y (2C classes), te_masks = {'flat','head'} (boolean, over the returned order)."""
    nf = n // 2; nh = n - nf
    Xf, Yf, _ = make_gauss(nf, np.random.default_rng(seed), dim=dim, n_class=n_class, n_clusters=16, overlap=0.7)
    Xh, Yh = make_tierb(nh, np.random.default_rng(seed + 9999), grid=4, n_active=3, dim=dim, overlap=0.6,
                        label="random", n_class=n_class)
    X = np.concatenate([Xf, Xh])
    Y = np.concatenate([Yf, Yh + n_class])                            # DISJOINT: headroom labels -> C..2C-1
    isflat = np.concatenate([np.ones(nf, bool), np.zeros(nh, bool)])
    p = np.random.default_rng(seed + 1).permutation(len(X))
    return X[p], Y[p].astype(np.int64), dict(flat=isflat[p], head=~isflat[p])


# ============================================================ guards (the sign-bug antidote — run before any cell)
def equivalence_guard(*, dim=40, width=64, L=12, batch=32, verbose=True):
    """SCFFContrastOverlap(window=2, stride=2) MUST reproduce SCFFContrastOLU(window=2) bit-for-bit — the licence
    to treat the port as the tested cell. Returns (ok, max|dW|)."""
    Xtr, _ = make_headroom(400, 7, dim=dim)
    dims = [dim] + [width] * L
    ref = SCFFContrastOLU(dims, lr=0.03, seed=3, window=2, mask_ratio=0.5, temp=0.5)
    new = SCFFContrastOverlap(dims, lr=0.03, seed=3, window=2, stride=2, mask_ratio=0.5, temp=0.5)
    r1 = np.random.default_rng(11); r2 = np.random.default_rng(11)
    for _ in range(4):
        for s in range(0, len(Xtr), batch):
            xb = Xtr[s:s + batch]
            if len(xb) >= 4:
                ref.train_step(xb, r1); new.train_step(xb, r2)
    d = max(float(np.abs(ref.W[l] - new.W[l]).max()) for l in range(L))
    ok = d < 1e-9
    if verbose:
        print(f"  [equiv guard] max|W_OLU - W_overlap(stride=window)| = {d:.2e}  "
              f"{'OK' if ok else '!! MISMATCH - subclass bug'}", flush=True)
    return ok, d


def _group_infonce_loss(model, a1, a2, s, w):
    """The windowed InfoNCE loss for one group, FIXED views — L = -mean_i log softmax(S/temp)[i,i],
    S = u1 @ u2.T. (The exact loss whose analytic gradient train_step uses; the FD reference.)"""
    u1, _, _, _ = model._view_fwd(a1, s, w)
    u2, _, _, _ = model._view_fwd(a2, s, w)
    S = (u1 @ u2.T) / model.temp
    P = softmax(S, axis=1)
    B = len(a1)
    return float(-np.log(P[np.arange(B), np.arange(B)] + EPS).mean())


def _group_analytic_gW(model, a1, a2, s, w):
    """The analytic gW/gb that train_step accumulates for ONE group (both views, shared weights) — = dL/dW of
    _group_infonce_loss, since W feeds both u1 and u2 via _view_fwd."""
    B = len(a1); I = np.eye(B)
    gW = [np.zeros_like(Wl) for Wl in model.W]; gb = [np.zeros_like(bl) for bl in model.b]
    u1, n1, c1, ht1 = model._view_fwd(a1, s, w)
    u2, n2, c2, ht2 = model._view_fwd(a2, s, w)
    S = (u1 @ u2.T) / model.temp; P = softmax(S, axis=1); dS = (P - I) / B
    du1 = (dS @ u2) / model.temp; du2 = (dS.T @ u1) / model.temp
    model._view_bwd(du1, n1, c1, ht1, w, gW, gb, s)
    model._view_bwd(du2, n2, c2, ht2, w, gW, gb, s)
    return gW, gb


def fd_gradient_check(*, dim=40, width=16, L=4, window=2, B=16, n_probe=30, eps=1e-6, seed=0, verbose=True):
    """Finite-difference vs analytic gradient of the windowed InfoNCE loss (FIXED masks) — verifies the cell's
    WHOLE backward chain (InfoNCE -> L2-norm -> layernorm -> relu -> linear, through the window). The antidote
    to the sign/direction bug: max|analytic - FD| must be < 1e-5. Returns (ok, worst)."""
    rng = np.random.default_rng(seed)
    X, _ = make_headroom(B, seed, dim=dim)
    m = SCFFContrastOverlap([dim] + [width] * L, lr=0.03, seed=seed, window=window, stride=window,
                            mask_ratio=0.5, temp=0.5)
    s, w = 0, min(window, L)
    a = m._norm(X); din = a.shape[1]
    a1 = a * (rng.random((B, din)) >= m.mask_ratio)                   # FIX the two masked views
    a2 = a * (rng.random((B, din)) >= m.mask_ratio)
    gW, _ = _group_analytic_gW(m, a1, a2, s, w)
    worst = 0.0
    for l in range(s, s + w):
        out, inn = m.W[l].shape
        for _ in range(n_probe):
            i = int(rng.integers(out)); j = int(rng.integers(inn))
            orig = m.W[l][i, j]
            m.W[l][i, j] = orig + eps; Lp = _group_infonce_loss(m, a1, a2, s, w)
            m.W[l][i, j] = orig - eps; Lm = _group_infonce_loss(m, a1, a2, s, w)
            m.W[l][i, j] = orig
            worst = max(worst, abs((Lp - Lm) / (2 * eps) - gW[l][i, j]))
    ok = worst < 1e-5
    if verbose:
        print(f"  [FD guard] max|analytic - FD| (InfoNCE window backward) = {worst:.2e}  "
              f"{'OK' if ok else '!! GRADIENT BUG'}", flush=True)
    return ok, worst


def mean_infonce_loss(model, X, rng):
    """The model's current mean windowed-InfoNCE loss over all coordination groups on a batch X (fresh masks
    from rng) — the training-health read (a falling trace = the cell is learning; the INV loss-slope panel)."""
    a0 = model._norm(X) if model.normalize_input else X
    a_in = [a0]; ac = a0
    for l in range(model.L):
        ac = model._norm(np.maximum(ac @ model.W[l].T + model.b[l], 0.0))
        a_in.append(ac)
    starts, w = model._starts()
    losses = []
    for s in starts:
        a = a_in[s]; B, din = a.shape
        a1 = a * (rng.random((B, din)) >= model.mask_ratio)
        a2 = a * (rng.random((B, din)) >= model.mask_ratio)
        losses.append(_group_infonce_loss(model, a1, a2, s, w))
    return float(np.mean(losses))
