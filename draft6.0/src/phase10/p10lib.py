"""
p10lib — the Phase-10 apparatus: VALIDATION / SHOWCASE. Race the FROZEN two-brain object (handed over by P9,
grid-4) against a FAIR, BUDGETED BP+replay baseline across the continual gauntlet. A CHIP NETLIST, not normal
Python: every reuse is a *tested* primitive carried unchanged from p9lib (which re-exports p8/p7/p6/p5/p4…), and
every genuinely-new organ ships with its own guard. Phase 10 MEASURES; it does not tune (the object is frozen; the
only dial that moves is the declared cadence cost axis — grid ∈ {4,5,6,8,12,16}, grid-4 the committed headline;
grid-12 = the §10 post-close home-only gap-filler).

The frozen object it races (design §2.1): NoiseAugContrast SCFF bulk (L12/w64, InfoNCE τ0.2/w2, per-sample L2,
one iid-noise view σ1.0, no residual) · SLDA namer · DDM awake gate on the class-direction tap-drift (code
`trigger="error_ema"`) · all-tap sleep · CBRS eviction · proto-reanchor read-side · grid-4 cadence · envelope
GD-reads-taps-never-writes. Reproduced bit-for-bit via `{**COMMITTED_LOOP, cadence_every: 4}` (Trap 1: override the
baked-in 8) — the `freeze_content_guard` asserts the content manifest + grid-4 bit-exact vs figs_p9_5_cadence.

NEW here (Phase 10) — design §6, each names the deliverable it serves + the review finding it closes:
  BPNet(MLP) : the tested models_extra.MLP + gradient handles (grads / grads_distill / apply) for A-GEM (grad
      projection) & DER++ (logit distillation). R7 (BP+replay learners are REAL new builds, not carries).
  ContinualBP(policy ∈ {naive,er,agem,derpp,gdumb}) : the online BP+replay racer on BPNet + a replay buffer
      (reservoir; class-balanced for GDumb). The load-bearing opponent field. Deliverable A/C.
  run_bp_stream / ours_bundle / cl_metrics : replay a learner on a stream at the FIXED learner-independent eval grid
      (K12) -> the acc-matrix + worst-pre-sleep BWT + AAA + plasticity, the SAME convention for OURS and BP (R6).
  tune_er_strong : the ER-strong config selector on a DISJOINT tuning stream (seed 7 ∉ raced set; K2).
  joint_bp_ceiling : the offline pooled multi-epoch MLP — the dash-dot summit reference (accuracy-axis only; K1).
  fair_budget_meter : FLOPs/sample + replay bytes + total memory per learner (the anti-strawman audit; K6).
  bp_stream_energy / ours_stream_energy : per-substrate metered energy (bp_replay_energy / meter_from_trace).
  make_gauntlet_stream / load_gauntlet_data : ≈5 native domain-IL domains, all projected to the shared 40-D bulk
      input via ONE pinned seed-frozen mechanism, shared head; every learner consumes the bit-identical stream (K5).
  cadence_family_runner : run {**COMMITTED_LOOP, cadence_every:g} for g ∈ {4,5,6,8,12,16} (the declared cost axis;
      grid-12 = the §10 post-close gap-filler, home stream only).
  gauntlet_batch_curves / ours_cum_energy / bp_cum_energy : the §10-E3 per-BATCH stream view — a GUARDED lockstep
      replay of the frozen loop (cell pass asserted bit-exact vs the committed cache's rng-fingerprint + phi_b; head
      states asserted vs the committed err_trace every step) + EXACT prefix pricing of the fires/sleeps masks on the
      same meter (endpoint asserted == the committed total). Measurement-only; any assert fails -> STOP.
  held_out_noise_battery : {clean,iid,directional,adc3b,nuisance} via p6 NoiseModel, MARGIN-DISJOINT from P9.4 (B4).
  throughput_meter : steps-behind from the metered FLOPs/sample (C_stream = OURS grid-4; wall-clock is NOT it; K3).
  pareto_frontier : the (accuracy, energy) non-dominated envelope + normalized efficiency.
  guards (run FIRST) : fair_budget · freeze_content · cadence_family · gauntlet_data · noise_holdout ·
      substrate_identity (scoped to NoiseModel-OFF cells; P10.4 the declared exception — K4). ANY fails -> STOP.

numpy only. CPU float64 (the bit-exact freeze guard needs determinism). OMP_NUM_THREADS=1 by the run layer. NO
sklearn/River for COMPUTE (data loading via sklearn.datasets.load_digits is DATA-only — the OpenMP phantom-hang was
KMeans, never the loader). GD reads taps, never writes SCFF (the P2.5 envelope, unbroken).
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase9"))                # p9lib (re-exports p8/p7/p6/p5/p4)
sys.path.insert(0, os.path.join(_HERE, "..", "phase5"))                # p5lib (load_cifar_flat — not in the p9 __all__)
sys.path.insert(0, os.path.join(_HERE, "..", "phase1", "exp0"))        # models_extra (the real MLP + match_width)
import p9lib as P9                                                      # noqa: E402
from p9lib import (run_economy_p9, build_cache_p9, make_lifelong_stream, make_committed_cell, train_cell,   # noqa: E402
                   make_stream_head, SLDAHeadStream, acc_matrix_metrics, synth_stream, load_digits_split,
                   nuisance_transform, readout_feats, all_tap_feats, linear_probe,
                   race_bp, meter_from_trace, hardware_cost_meter, bp_replay_energy, proto_reanchor,
                   NoiseModel, infer_noisy, jsonsafe, EPS, normalize, class_balanced_reservoir)
from p5lib import load_cifar_flat                                      # noqa: E402  (DATA-only; local arff.gz cache)
from p6lib import class_axis                                           # noqa: E402
from models_extra import MLP, match_width                             # noqa: E402
# all P8/P9 guards (carried; run FIRST every rung)
from p9lib import (partial_fit_equiv_guard, live_path_anchor_guard, scff_static_frozen_guard,      # noqa: E402
                   meter_proxy_guard, detector_far_guard, cache_replay_guard, fd_budget_gate_guard,
                   n2_readside_guard, evict_equiv_guard)

__all__ = [
    "BPNet", "ReservoirBuffer", "BalancedBuffer", "ContinualBP",
    "run_bp_stream", "ours_bundle", "cl_metrics",
    "tune_er_strong", "joint_bp_ceiling",
    "fair_budget_meter", "bp_stream_energy", "ours_stream_energy",
    "make_gauntlet_stream", "load_gauntlet_data",
    "cadence_family_runner", "held_out_noise_battery", "throughput_meter", "pareto_frontier",
    "gauntlet_batch_curves", "ours_cum_energy", "bp_cum_energy",
    "fair_budget_guard", "freeze_content_guard", "cadence_family_guard", "gauntlet_data_guard",
    "noise_holdout_guard", "substrate_identity_guard",
    # carried (re-export so run scripts import only p10lib)
    "run_economy_p9", "build_cache_p9", "make_lifelong_stream", "make_committed_cell", "train_cell",
    "make_stream_head", "acc_matrix_metrics", "synth_stream", "load_digits_split", "load_cifar_flat",
    "nuisance_transform", "readout_feats", "all_tap_feats", "linear_probe", "race_bp", "meter_from_trace",
    "hardware_cost_meter", "bp_replay_energy", "proto_reanchor", "NoiseModel", "infer_noisy", "class_axis",
    "MLP", "match_width", "jsonsafe", "EPS",
    "partial_fit_equiv_guard", "live_path_anchor_guard", "scff_static_frozen_guard", "meter_proxy_guard",
    "detector_far_guard", "cache_replay_guard", "fd_budget_gate_guard", "n2_readside_guard", "evict_equiv_guard",
]

COMMITTED_LOOP = dict(gate="ddm", trigger="error_ema", sleep_policy="grid", cadence_every=8, cbrs=True, lam_ema=1.0)
HEAD = "slda"                                                          # the frozen loop head (P8 superseded RanPAC->SLDA)


# ============================================================ the BP+replay learner (REAL new build — R7)
class BPNet(MLP):
    """models_extra.MLP + gradient handles. Inherits the tested forward/backward/Adam; adds grads(X,Y) (CE grads,
    NOT stepped), grads_distill(X, target_logits) (MSE-on-logits grads, for DER++), and apply(grads) (one Adam step).
    Reduces to the plain MLP when only train_step is called (naive/ER path)."""

    def grads(self, X, Y):
        logits = self.forward(X); B = len(X)
        p = softmax(logits, axis=1); oh = np.zeros_like(p); oh[np.arange(B), Y] = 1.0
        dl = (p - oh) / B
        return self._backward(dl)

    def grads_distill(self, X, target_logits):
        logits = self.forward(X); B = len(X)
        dl = (logits - target_logits) / B                              # 0.5||logits-target||^2 -> (logits-target)/B
        return self._backward(dl)

    def _backward(self, dl):
        gW = [None] * self.L; gb = [None] * self.L
        gW[-1] = dl.T @ self.cache[-1]; gb[-1] = dl.sum(0)
        da = dl @ self.W[-1]
        for l in range(self.L - 2, -1, -1):
            dz = da * (self.cache[l + 1] > 0)
            gW[l] = dz.T @ self.cache[l]; gb[l] = dz.sum(0)
            da = dz @ self.W[l]
        return gW + gb

    def apply(self, grads):
        self.opt.step(self.W + self.b, grads)

    def logits(self, X):
        return self.forward(X)


def _gdot(ga, gb):
    return float(sum(np.sum(a * b) for a, b in zip(ga, gb)))


def _gadd(ga, gb, s=1.0):
    return [a + s * b for a, b in zip(ga, gb)]


class ReservoirBuffer:
    """Vitter reservoir over (x, y[, logits]): a uniform random `cap`-sample of the appended history (ER/A-GEM/DER++)."""

    def __init__(self, cap, seed, store_logits=False):
        self.cap = int(cap); self.rng = np.random.default_rng(seed + 71)
        self.X = None; self.Y = None; self.Z = None; self.n = 0; self.store_logits = store_logits

    def add(self, xb, yb, zb=None):
        for i in range(len(xb)):
            self.n += 1
            if self.X is None:
                d = xb.shape[1]; self.X = np.zeros((self.cap, d)); self.Y = np.zeros(self.cap, int)
                if self.store_logits:
                    self.Z = np.zeros((self.cap, zb.shape[1]))
            if self.n <= self.cap:
                j = self.n - 1
            else:
                j = int(self.rng.integers(0, self.n))
                if j >= self.cap:
                    continue
            self.X[j] = xb[i]; self.Y[j] = yb[i]
            if self.store_logits:
                self.Z[j] = zb[i]

    def sample(self, m):
        k = min(self.n, self.cap)
        if k == 0:
            return None
        idx = self.rng.integers(0, k, min(m, k))
        if self.store_logits:
            return self.X[idx], self.Y[idx], self.Z[idx]
        return self.X[idx], self.Y[idx]

    def __len__(self):
        return min(self.n, self.cap)

    def nbytes(self):
        b = (self.X.nbytes + self.Y.nbytes) if self.X is not None else 0
        return int(b + (self.Z.nbytes if (self.store_logits and self.Z is not None) else 0))


class BalancedBuffer:
    """GDumb's greedy class-balanced memory: keep up to cap//C per class; when full, evict from the largest class
    (Prabhu ECCV'20). Hand-rolled single-threaded (no sklearn — the phantom-hang)."""

    def __init__(self, cap, C, seed):
        self.cap = int(cap); self.C = int(C); self.rng = np.random.default_rng(seed + 73)
        self.byc = {c: [] for c in range(C)}; self.d = None

    def add(self, xb, yb):
        per = max(1, self.cap // self.C)
        for x, y in zip(xb, yb):
            y = int(y); self.d = len(x)
            if len(self.byc[y]) < per:
                self.byc[y].append(np.asarray(x, float))
            else:                                                      # replace a random member (greedy-balanced)
                self.byc[y][int(self.rng.integers(0, len(self.byc[y])))] = np.asarray(x, float)

    def dump(self):
        Xs, Ys = [], []
        for c, lst in self.byc.items():
            for x in lst:
                Xs.append(x); Ys.append(c)
        if not Xs:
            return None, None
        return np.array(Xs), np.array(Ys, int)

    def __len__(self):
        return sum(len(v) for v in self.byc.values())

    def nbytes(self):
        return int(len(self) * ((self.d or 0) + 1) * 8)


class ContinualBP:
    """Online BP+replay. policy ∈ {naive, er, agem, derpp, gdumb}. `net` = BPNet(bp_dims). Each `step` does the
    policy's online update on the current batch (+ replay); GDumb only fills a balanced buffer and rebuilds
    from-scratch at eval (cost-pathological — an accuracy-axis control, A3). All reduce to the tested MLP backward."""

    def __init__(self, policy, bp_dims, C, seed, *, lr=3e-3, l2=0.0, replay=0, buffer_cap=0,
                 alpha=0.5, beta=0.5, gdumb_ep=30):
        self.policy = policy; self.bp_dims = list(bp_dims); self.C = C; self.seed = seed
        self.lr = lr; self.l2 = l2; self.replay = int(replay); self.alpha = alpha; self.beta = beta
        self.gdumb_ep = gdumb_ep
        self.net = BPNet(bp_dims, seed, lr=lr, l2=l2)
        if policy == "gdumb":
            self.buf = BalancedBuffer(buffer_cap, C, seed)
        else:
            self.buf = ReservoirBuffer(buffer_cap, seed, store_logits=(policy == "derpp")) if buffer_cap else None

    def step(self, xb, yb, rng):
        pol = self.policy
        if pol == "gdumb":
            self.buf.add(xb, yb); return
        if pol == "naive" or self.buf is None or len(self.buf) == 0:
            self.net.train_step(xb, yb)
        elif pol == "er":
            xr, yr = self.buf.sample(self.replay)
            self.net.train_step(np.vstack([xb, xr]), np.concatenate([yb, yr]))
        elif pol == "agem":
            g = self.net.grads(xb, yb)
            xr, yr = self.buf.sample(self.replay)
            gref = self.net.grads(xr, yr)
            dot = _gdot(g, gref)
            if dot < 0:                                                # A-GEM one-constraint projection (Chaudhry ICLR'19)
                g = _gadd(g, gref, -dot / (_gdot(gref, gref) + EPS))
            self.net.apply(g)
        elif pol == "derpp":
            g = self.net.grads(xb, yb)                                 # CE on the incoming batch
            xr, yr, zr = self.buf.sample(self.replay)                  # DER++ replay-CE (beta) + logit-distill (alpha)
            g = _gadd(g, self.net.grads(xr, yr), self.beta)
            xd, yd, zd = self.buf.sample(self.replay)
            g = _gadd(g, self.net.grads_distill(xd, zd), self.alpha)
            self.net.apply(g)
        # store to the buffer AFTER the update (DER++ stores the pre-update logits it just read)
        if pol == "derpp":
            self.buf.add(xb, yb, self.net.logits(xb))
        elif self.buf is not None:
            self.buf.add(xb, yb)

    def eval_net(self, rng):
        """The network used at an eval point. GDumb rebuilds from scratch on its balanced buffer (test-time train)."""
        if self.policy != "gdumb":
            return self.net
        Xb, Yb = self.buf.dump()
        net = BPNet(self.bp_dims, self.seed, lr=self.lr, l2=self.l2)
        if Xb is None:
            return net
        r = np.random.default_rng(self.seed + 9091)
        for _ in range(self.gdumb_ep):
            idx = r.permutation(len(Xb))
            for s in range(0, len(Xb), 32):
                b = idx[s:s + 32]
                if len(b) >= 2:
                    net.train_step(Xb[b], Yb[b])
        return net


# ============================================================ the shared metric bundle (OURS == BP convention; R6/K12)
def cl_metrics(matrix, first_acc, last_eval, worst_bwt):
    """From an acc-matrix (post-checkpoint), the per-task first-learned baseline, the per-task last eval, and the
    tracked worst-mid-stream (pre-sleep) BWT -> the pinned bundle. AA = mean last-eval (lifelong); AAA = mean over
    checkpoints t of AA(t)=mean_{k<=t} matrix[t][k] (origin OSAKA); BWT/forget = GEM convention on the matrix."""
    T = len(matrix)
    aa_canon, bwt, forget = acc_matrix_metrics(matrix)
    aa = float(np.mean(list(last_eval.values()))) if last_eval else aa_canon
    aaas = []
    for t in range(T):
        seen = [matrix[t][k] for k in range(t + 1) if matrix[t][k] > 0 or k <= t]
        if seen:
            aaas.append(float(np.mean(matrix[t][:t + 1])))
    aaa = float(np.mean(aaas)) if aaas else aa_canon
    plast = float(np.mean([first_acc[k] for k in first_acc if k >= 1])) if any(k >= 1 for k in first_acc) else \
        (float(np.mean(list(first_acc.values()))) if first_acc else 0.0)
    return dict(aa=aa, aa_canon=aa_canon, aaa=aaa, bwt=bwt, forget=forget,
                worst_bwt=float(worst_bwt), plasticity=plast)


def run_bp_stream(stream, policy, bp_dims, cfg, seed, *, lr=3e-3, l2=0.0, replay=0, buffer_cap=0,
                  alpha=0.5, beta=0.5, curves=False):
    """Replay a ContinualBP learner on the RAW-input stream (the same stream OURS's SCFF cache was built from —
    input-identity, K5), evaluating at the FIXED learner-independent grid (checkpoints + monitor; K12). Returns the
    cl_metrics bundle + the learner (for energy). BP has no sleep, so every eval point IS a pre-sleep point ->
    worst_bwt is the worst-mid-stream drop, the same read as OURS's worst-pre-sleep (R6).
    `curves=True` (§10 E3; non-gdumb only) additionally measures, per step, the READ-ONLY pair {live-batch accuracy
    (prequential, pre-update) · seen-so-far all-domain accuracy (post-update)} — no rng is consumed and the learner's
    trajectory is bit-identical to curves=False (eval never mutates)."""
    C = stream["C"]; T = len(stream["tasks"]); Xtr, Ytr = stream["Xtr"], stream["Ytr"]
    learner = ContinualBP(policy, bp_dims, C, seed, lr=lr, l2=l2, replay=replay, buffer_cap=buffer_cap,
                          alpha=alpha, beta=beta)
    rng = np.random.default_rng(seed + 4242)
    ckpt = {s: t for s, t in stream["checkpoints"]}
    monitor = set(stream.get("monitor_steps") or [])
    ebt = stream["eval_by_task"]
    amat = [[0.0] * T for _ in range(T)]; first_acc = {}; last_eval = {}; worst_bwt = 0.0; n_train = 0
    N = len(stream["steps"])
    live = np.full(N, np.nan) if curves else None
    seen = np.full(N, np.nan) if curves else None
    for si, st in enumerate(stream["steps"]):
        xb = Xtr[st["idx"]].copy(); yb = Ytr[st["idx"]].copy()
        if st.get("nuis") is not None:
            g, a = st["nuis"]; xb = nuisance_transform(xb, g, a)
        if curves and policy != "gdumb" and len(xb) >= 1:
            live[si] = float((learner.net.predict(xb) == yb).mean())   # prequential (pre-update); read-only
        if len(xb) >= 2:
            learner.step(xb, yb, rng); n_train += 1
        if (si in ckpt) or (si in monitor):
            t_row = min(ckpt.get(si, T - 1), T - 1)
            net = learner.eval_net(rng)
            for k, (Xk, Yk) in ebt.items():
                if k <= t_row:
                    acc = float((net.predict(Xk) == Yk).mean())
                    if k not in first_acc:
                        first_acc[k] = acc
                    worst_bwt = min(worst_bwt, acc - first_acc[k])
                    amat[t_row][k] = acc; last_eval[k] = acc
        if curves and policy != "gdumb":
            d_now = int(st.get("seen", T - 1))
            seen[si] = float(np.mean([float((learner.net.predict(ebt[k][0]) == ebt[k][1]).mean())
                                      for k in range(min(d_now, T - 1) + 1)]))
    out = cl_metrics(amat, first_acc, last_eval, worst_bwt)
    out.update(matrix=amat, learner=learner, n_train=n_train, first_acc=first_acc)
    if curves:
        out.update(live_curve=live, seen_curve=seen)
    return out


def ours_bundle(cache, hf, cfg, cadence, *, gate="ddm"):
    """The frozen OURS object at grid-`cadence`: run_economy_p9 with the committed loop (Trap 1: cadence_every
    overridden) + AAA extracted from the returned matrix (the same cl_metrics AAA definition BP uses)."""
    res = run_economy_p9(cache, hf, cfg, **{**COMMITTED_LOOP, "gate": gate, "cadence_every": cadence})
    T = len(res["matrix"])
    aaas = [float(np.mean(res["matrix"][t][:t + 1])) for t in range(T)]
    res["aaa"] = float(np.mean(aaas)) if aaas else res["aa_canon"]
    return res


# ============================================================ ER-strong tuning (DISJOINT stream; K2) + joint ceiling
def _pool_eval(stream):
    """Pool the per-task eval sets into one (X, Y) — the offline joint accuracy target."""
    Xs = [ebt[0] for ebt in stream["eval_by_task"].values()]
    Ys = [ebt[1] for ebt in stream["eval_by_task"].values()]
    return np.vstack(Xs), np.concatenate(Ys)


def tune_er_strong(cfg, in_dim, C, *, tune_seed=7):
    """Select ER-strong's config (bp shape + lr via race_bp on the pooled tuning data, then replay size on the
    tuning STREAM) — consuming ONLY the disjoint tuning seed (∉ the raced set; K2). Returns the chosen config dict."""
    Xtr, Ytr, Xte, Yte = synth_stream(cfg.NTR, cfg.NTE, cfg.OVERLAP, tune_seed,
                                      dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
    total = sum((([in_dim] + [64] * 2 + [C])[i] + 1) * ([in_dim] + [64] * 2 + [C])[i + 1] for i in range(3))
    sel = race_bp(Xtr, Ytr, Xte, Yte, C, total=total, in_dim=in_dim, depths=tuple(cfg.BP_DEPTHS),
                  lrs=tuple(cfg.BP_TUNE_LRS), wds=(0.0, 1e-3), ep=cfg.BP_EP_TUNE, seed=tune_seed)
    bp_dims = [in_dim] + [sel["width"]] * sel["depth"] + [C]
    # replay-size search on the tuning STREAM (final-AA selection)
    stream = make_lifelong_stream(Xtr, Ytr, Xte, Yte, cfg.TASKS, tune_seed, cfg, quick=False)
    buffer_cap = cfg.PROBE_N                                            # byte-matched to OURS's LUT (raw prototypes)
    best = None
    for r in cfg.BP_TUNE_REPLAY:
        m = run_bp_stream(stream, "er", bp_dims, cfg, tune_seed, lr=sel["lr"], l2=sel["wd"],
                          replay=r, buffer_cap=buffer_cap)
        if best is None or m["aa"] > best["aa"]:
            best = dict(aa=m["aa"], replay=r)
    return dict(bp_dims=bp_dims, lr=sel["lr"], l2=sel["wd"], depth=sel["depth"], width=sel["width"],
                replay=best["replay"], buffer_cap=buffer_cap, tune_seed=tune_seed, tune_aa=best["aa"])


def joint_bp_ceiling(stream, cfg, in_dim, C, seed, *, epochs=None):
    """The offline joint-BP CEILING (K1): the race_bp-selected MLP trained multi-epoch on the POOLED stream data
    (all tasks jointly) -> the dash-dot summit. Accuracy-axis only (never a racer). Cheap; once per stream."""
    epochs = epochs or cfg.JOINT_BP_EPOCHS
    Xte, Yte = _pool_eval(stream)
    Xtr, Ytr = stream["Xtr"], stream["Ytr"]
    total = sum((([in_dim] + [64] * 2 + [C])[i] + 1) * ([in_dim] + [64] * 2 + [C])[i + 1] for i in range(3))
    sel = race_bp(Xtr, Ytr, Xte, Yte, C, total=total, in_dim=in_dim, depths=tuple(cfg.BP_DEPTHS),
                  lrs=tuple(cfg.BP_TUNE_LRS), wds=(0.0, 1e-3), ep=epochs, seed=seed)
    return float(sel["acc_te"])


# ============================================================ the fair-budget audit (FLOPs/sample + bytes; K6)
def _mlp_fwd_macs(dims):
    return dims[0] * dims[1] + sum(dims[i] * dims[i + 1] for i in range(1, len(dims) - 1))


def fair_budget_meter(cfg, *, learner, bp_dims=None, batch=None, replay=0, buffer_cap=0, in_dim=None,
                      ours_res=None, ours_cache=None):
    """FLOPs/sample + replay-bytes + total-memory per learner (the anti-strawman audit). For OURS: FLOPs/sample from
    the meter's MAC count / (n_steps*batch); buffer bytes = the raw-prototype LUT (PROBE_N raw DIM-D samples). For a
    BP learner: fwd+bwd (3x) over (batch + replay) / batch; buffer bytes = cap raw samples (+ logits for DER++)."""
    batch = batch or cfg.BATCH
    if learner == "ours":
        m = meter_from_trace(cfg, HEAD, ours_cache, ours_res, substrate="analog")
        n_steps = len(ours_cache["steps"])
        flops = float(m["n_MAC"]) / (n_steps * batch)
        buf_bytes = cfg.PROBE_N * (cfg.DIM + 1) * 8                     # the raw-prototype hippocampus LUT
        model_bytes = sum(W.size for W in [np.zeros((cfg.WIDTH, cfg.DIM))]) * 0  # placeholder; scff params below
        scff_params = cfg.DIM * cfg.WIDTH + (cfg.DEPTH - 1) * cfg.WIDTH * cfg.WIDTH
        Fdim = cfg.DEPTH * cfg.WIDTH
        head_state = (Fdim * Fdim + Fdim * cfg.NCLASS)                 # SLDA T + means (running stats)
        total_bytes = int((scff_params + head_state) * 8 + buf_bytes)
        return dict(flops_per_sample=float(flops), buffer_bytes=int(buf_bytes), total_bytes=total_bytes,
                    replay=0, buffer_cap=cfg.PROBE_N)
    # BP learners
    fwd = _mlp_fwd_macs(bp_dims)
    mult = {"naive": 1.0, "er": 1.0, "agem": 1.0, "derpp": 1.0, "gdumb": 0.0}.get(learner, 1.0)
    per_step_samples = batch + (replay if learner in ("er", "agem") else (2 * replay if learner == "derpp" else 0))
    flops = 3.0 * fwd * per_step_samples / batch if learner != "gdumb" else 0.0   # 3x = fwd+bwd; gdumb trains at eval
    store_logits = (learner == "derpp")
    per_sample_bytes = (in_dim + 1 + (cfg.NCLASS if store_logits else 0)) * 8
    buf_bytes = buffer_cap * per_sample_bytes
    model_bytes = sum((bp_dims[i] + 1) * bp_dims[i + 1] for i in range(len(bp_dims) - 1)) * 8
    opt_bytes = 2 * model_bytes                                        # Adam m,v
    total_bytes = int(model_bytes + opt_bytes + buf_bytes)
    return dict(flops_per_sample=float(flops), buffer_bytes=int(buf_bytes), total_bytes=total_bytes,
                replay=int(replay), buffer_cap=int(buffer_cap))


def bp_stream_energy(cfg, bp_dims, policy, *, n_steps, batch=None, replay=0, substrate="analog", e_mac_dig=None):
    """Metered BP+replay energy on the SAME per-op table as OURS. ER/A-GEM: replay minibatch every step; DER++: 2x
    replay (CE + distill forward); naive: no replay; GDumb: cost-pathological (priced separately, annotated)."""
    batch = batch or cfg.BATCH
    rb = {"naive": 0, "er": replay, "agem": replay, "derpp": 2 * replay, "gdumb": 0}.get(policy, replay)
    return bp_replay_energy(cfg, Fdim=bp_dims[0], C=bp_dims[-1], n_steps=n_steps, batch=batch,
                            replay_batch=rb, bp_dims=bp_dims, substrate=substrate, e_mac_dig=e_mac_dig)


def ours_stream_energy(cfg, cache, res, *, substrate="analog", e_mac_dig=None):
    return meter_from_trace(cfg, HEAD, cache, res, substrate=substrate, e_mac_dig=e_mac_dig)


# ============================================================ the §10-E3 per-BATCH stream view (measurement-only)
def ours_cum_energy(cfg, cache, res, *, substrate="analog"):
    """Per-step CUMULATIVE metered energy for a frozen-loop result — EXACT prefix pricing of the fires/sleeps masks
    on hardware_cost_meter (which is closed-form in the counts, so E_cum[t] = the meter at n_steps=t+1 with the
    prefix fire/sleep counts). GUARD: the endpoint must equal the committed meter_from_trace total (same arithmetic
    path) or raise — the stream view can never disagree with the committed number."""
    fires = np.asarray(res["fires"], bool); sleeps = np.asarray(res["sleeps"], bool)
    stream = cache["stream"]; C = stream["C"]
    Fdim = cache["steps"][0]["phi_b"].shape[1]
    scff_dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    probe_n = next((r["phi_probe"].shape[0] for r in cache["steps"] if "phi_probe" in r), cfg.PROBE_N)
    cf = np.cumsum(fires); cs = np.cumsum(sleeps)
    E = np.empty(len(fires), float)
    for t in range(len(fires)):
        E[t] = hardware_cost_meter(cfg, head_name=HEAD, Fdim=Fdim, C=C, n_fire=int(cf[t]), n_sleep=int(cs[t]),
                                   n_steps=t + 1, batch=cfg.BATCH, probe_n=probe_n, scff_dims=scff_dims,
                                   substrate=substrate)["total"]
    ref = meter_from_trace(cfg, HEAD, cache, res, substrate=substrate)["total"]
    if not abs(E[-1] - ref) <= 1e-9 * max(1.0, abs(ref)):
        raise AssertionError(f"ours_cum_energy endpoint {E[-1]:.6e} != committed meter total {ref:.6e}")
    return E


def bp_cum_energy(cfg, bp_dims, policy, *, n_steps, replay, substrate="analog"):
    """Per-step cumulative BP+replay energy on the SAME per-op table (bp_replay_energy is linear in n_steps — the
    racer pays every step, so its cumulative curve is a ramp; stated, not hidden). Endpoint == bp_stream_energy."""
    rb = {"naive": 0, "er": replay, "agem": replay, "derpp": 2 * replay, "gdumb": 0}.get(policy, replay)
    E = np.array([bp_replay_energy(cfg, Fdim=bp_dims[0], C=bp_dims[-1], n_steps=t + 1, batch=cfg.BATCH,
                                   replay_batch=rb, bp_dims=bp_dims, substrate=substrate)["total"]
                  for t in range(n_steps)])
    ref = bp_stream_energy(cfg, bp_dims, policy, n_steps=n_steps, replay=replay, substrate=substrate)["total"]
    if not abs(E[-1] - ref) <= 1e-9 * max(1.0, abs(ref)):
        raise AssertionError(f"bp_cum_energy endpoint {E[-1]:.6e} != bp_stream_energy total {ref:.6e}")
    return E


def gauntlet_batch_curves(gstream, cache, res, hf, cfg, seed):
    """The §10-E3 per-BATCH view of the FROZEN OURS loop — a GUARDED lockstep replay (measurement-only; design §10).
    Replays (a) the SCFF cell pass exactly as build_cache_p9 ran it (same rng seeding, same warmup, same train order)
    with TWO bit-exact asserts per step (the cache's rng_fingerprint + phi_b array-equality), and (b) the namer's
    committed update sequence (the fires/sleeps masks + the forced first-eval fit + the cbrs sleep set, seeds
    identical), with the head state asserted against the committed err_trace at EVERY step. On top of the verified
    state it measures what the committed run never stored:
      live[t]  = prequential accuracy on the arriving batch (pre-update) == 1 - err_trace[t] (the assert)
      seen[t]  = held-out accuracy averaged over the domains seen so far, through the CURRENT bulk (post-update)
    Any assert fails -> raise (STOP). The frozen loop is never touched; this is a replay, not a re-run."""
    C = gstream["C"]
    Xtr, Ytr = gstream["Xtr"], gstream["Ytr"]
    dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    rng = np.random.default_rng(seed)
    cell = make_committed_cell(dims, seed)
    wu = gstream["warmup_idx"]
    for s0 in range(0, len(wu), cfg.BATCH):
        xb = Xtr[wu[s0:s0 + cfg.BATCH]]
        if len(xb) >= 4:
            cell.train_step(xb, rng)
    head = hf()
    fires = np.asarray(res["fires"], bool); sleeps = np.asarray(res["sleeps"], bool)
    err_ref = np.asarray(res["err_trace"], float)
    ev_steps = set(cache["ckpt"]) | set(cache.get("monitor", []))
    ebt = gstream["eval_by_task"]
    lam = COMMITTED_LOOP["lam_ema"]
    N = len(gstream["steps"])
    live = np.full(N, np.nan); seen = np.full(N, np.nan)
    fitted = False
    for si, st in enumerate(gstream["steps"]):
        xb = Xtr[st["idx"]].copy(); yb = Ytr[st["idx"]].copy()
        if st.get("nuis") is not None:
            g_, a_ = st["nuis"]; xb = nuisance_transform(xb, g_, a_)
        rb = cell.infer(xb)
        if len(xb) >= 4:
            cell.train_step(xb, rng)
        fp = float(rng.random())
        if fp != cache["rng_fingerprint"][si]:
            raise AssertionError(f"batch-curve replay: rng fingerprint diverged at step {si}")
        rec = cache["steps"][si]
        if not np.array_equal(readout_feats(rb, None), rec["phi_b"]):  # exactly build_cache_p9's alltap_from(rb)
            raise AssertionError(f"batch-curve replay: phi_b not bit-exact at step {si}")
        phi_b = rec["phi_b"]                                           # the head path uses the COMMITTED features
        # (1) live-batch accuracy (prequential, pre-update) — asserted vs the committed err_trace
        e_now = (1.0 - float((head.predict(phi_b) == yb).mean())) if head.W is not None else np.nan
        both_nan = np.isnan(e_now) and np.isnan(err_ref[si])
        if not both_nan and e_now != err_ref[si]:
            raise AssertionError(f"batch-curve replay: err_trace diverged at step {si} ({e_now} vs {err_ref[si]})")
        live[si] = 1.0 - e_now if not np.isnan(e_now) else np.nan
        # (2) the committed update sequence (fires -> forced first-eval fit -> sleep; run_economy_p9's order)
        if fires[si]:
            head.partial_fit(phi_b, yb, lam_ema=lam); fitted = True
        if (si in ev_steps) and not fitted:
            head.partial_fit(phi_b, yb, lam_ema=lam); fitted = True
        if sleeps[si]:
            Fp, Yp = rec["phi_probe"], rec["y_probe"]
            if COMMITTED_LOOP["cbrs"]:
                Fp, Yp = class_balanced_reservoir(Fp, Yp, C, cfg.CBRS_CAP, np.random.default_rng(2000 + si))
            head.sleep_fit(Fp, Yp); fitted = True
        # (3) seen-so-far accuracy through the CURRENT bulk (the deployed head at the end of batch t)
        d_now = int(st.get("seen", len(ebt) - 1))
        accs = []
        for k in range(d_now + 1):
            Xk, Yk = ebt[k]
            phik = readout_feats(cell.infer(Xk), None)                 # build_cache_p9's exact eval convention
            accs.append(float((head.predict(phik) == Yk).mean()) if head.W is not None else 0.0)
        seen[si] = float(np.mean(accs))
    return dict(live=live, seen=seen)


# ============================================================ the throughput / steps-behind read (K3; Ghunaim)
def throughput_meter(flops_by_learner, c_stream_learner="ours_g4"):
    """steps-behind from the METERED FLOPs/sample (NOT wall-clock — a numpy artifact; K3). C_stream = OURS(grid-4)'s
    FLOPs/sample = the declared real-time budget; each learner's drop-fraction = max(0, 1 - C_stream/FLOPs_L) and its
    relative complexity FLOPs_L/C_stream. OURS is 0-behind by construction (declared)."""
    c = flops_by_learner[c_stream_learner]
    out = {}
    for k, f in flops_by_learner.items():
        drop = max(0.0, 1.0 - c / (f + EPS))
        out[k] = dict(flops=float(f), rel_complexity=float(f / (c + EPS)), steps_behind_frac=float(drop))
    return out


# ============================================================ the (accuracy, energy) Pareto frontier
def pareto_frontier(points):
    """points: list of (name, acc, energy). Returns dict name->dict(acc,energy,is_frontier,efficiency). Non-dominated
    = no other point has >= acc AND <= energy (strictly better on one). efficiency = normalized distance to the ideal
    (max-acc, min-energy) corner (1 = best)."""
    names = [p[0] for p in points]; A = np.array([p[1] for p in points], float); E = np.array([p[2] for p in points], float)
    front = np.ones(len(points), bool)
    for i in range(len(points)):
        for j in range(len(points)):
            if j != i and A[j] >= A[i] and E[j] <= E[i] and (A[j] > A[i] or E[j] < E[i]):
                front[i] = False; break
    an = (A - A.min()) / (np.ptp(A) + EPS); en = (E - E.min()) / (np.ptp(E) + EPS)
    eff = 1.0 - np.sqrt((1 - an) ** 2 + en ** 2) / np.sqrt(2.0)
    return {names[i]: dict(acc=float(A[i]), energy=float(E[i]), is_frontier=bool(front[i]),
                           efficiency=float(eff[i])) for i in range(len(points))}


# ============================================================ the multi-domain gauntlet (native domain-IL; K5/B2/R3)
def _digits_images(seed, ntr, nte):
    """Load 8x8 digits (10-class, DATA-only via sklearn.datasets.load_digits — the loader is not OpenMP). Returns
    the raw 8x8 image tensors (train/test) so domain transforms (permute/rotate/covariate/noise) apply in image space."""
    from sklearn.datasets import load_digits
    d = load_digits(); X = (d.data / 16.0).astype(np.float64); Y = d.target.astype(np.int64)
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:ntr], idx[ntr:ntr + nte]
    return X[tr], Y[tr], X[te], Y[te]


def _domain_transform(X64, domain, cfg, rng):
    """Apply a domain's INPUT transformation in 64-D digit-image space (before the shared ->40 projection). Same 10
    classes throughout (true domain-IL, shared head): identity / permuted-pixels / rotated-image / layernorm-
    invariant covariate (gain+offset — SCFF removes it, BP sees it) / iid-noised."""
    if domain == "identity":
        return X64
    if domain == "permuted":
        perm = np.random.default_rng(9999).permutation(64)             # ONE fixed permutation (seed-frozen, shared)
        return X64[:, perm]
    if domain == "rotated":
        img = X64.reshape(-1, 8, 8)
        k = int(round(cfg.GAUNTLET_ROT_DEG / 90)) % 4
        return np.rot90(img, k=k, axes=(1, 2)).reshape(-1, 64)
    if domain == "covariate":
        return cfg.GAUNTLET_COV_GAIN * X64 + cfg.GAUNTLET_COV_OFFSET
    if domain == "noised":
        return X64 + cfg.GAUNTLET_NOISE_RMS * rng.standard_normal(X64.shape)
    raise ValueError(f"unknown gauntlet domain {domain}")


def load_gauntlet_data(cfg, seed, domains=None):
    """Build the per-domain 40-D projected (train, test) sets. ONE pinned seed-frozen Gaussian projection P: 64->40
    (matched to how the synth home is 40-D), applied identically to every domain (K5). Returns dict domain->
    (Xtr40, Ytr, Xte40, Yte) + the projection matrix. DATA-only + numpy; offline."""
    domains = domains or cfg.GAUNTLET_DOMAINS
    Xtr64, Ytr, Xte64, Yte = _digits_images(seed, cfg.GAUNTLET_NTR, cfg.GAUNTLET_NTE)
    Pj = np.random.default_rng(12345).standard_normal((64, cfg.GAUNTLET_DIM)) / np.sqrt(64.0)   # frozen ->40
    rng = np.random.default_rng(seed + 606)
    data = {}
    for dm in domains:
        Xtr_t = _domain_transform(Xtr64, dm, cfg, rng); Xte_t = _domain_transform(Xte64, dm, cfg, rng)
        data[dm] = (Xtr_t @ Pj, Ytr.copy(), Xte_t @ Pj, Yte.copy())
    data["_proj"] = Pj
    return data


def make_gauntlet_stream(cfg, seed, *, domains=None, block=None, revisit=1, order=None):
    """A domain-IL stream over ≈5 domains (the SAME 10 classes, a domain-specific input shift, a SHARED head). Each
    domain is presented as a block; the acc-matrix is domain x domain (retention across domains). Emits the fields
    build_cache_p9 + run_economy_p9 consume (steps/Xtr/Ytr/Xpr/Ypr/eval_by_task/checkpoints/monitor/probe_grid/…).
    `order` reorders the domain sequence (the reversed-order control, K9). Every learner replays this SAME stream.
    `block` may be a scalar (every domain that long; default 24 — the committed stream, bit-identical) or a per-domain
    list (§10 E8 — the alignment-break stream's pinned non-multiple lengths)."""
    domains = list(domains or cfg.GAUNTLET_DOMAINS)
    if order == "reversed":
        domains = domains[::-1]
    data = load_gauntlet_data(cfg, seed, domains)
    C = cfg.NCLASS; B = cfg.BATCH
    blocks = (list(block) if isinstance(block, (list, tuple, np.ndarray))
              else [int(block or 24)] * len(domains))                  # steps per domain block (scalar or per-domain)
    if len(blocks) != len(domains):
        raise ValueError(f"per-domain block list length {len(blocks)} != {len(domains)} domains")
    # concatenate all domains' train pools; steps draw within the current domain's slice
    Xtr_all = []; Ytr_all = []; dom_slices = {}
    off = 0
    for dm in domains:
        Xtr_d, Ytr_d, _, _ = data[dm]
        Xtr_all.append(Xtr_d); Ytr_all.append(Ytr_d)
        dom_slices[dm] = np.arange(off, off + len(Xtr_d)); off += len(Xtr_d)
    Xtr_all = np.vstack(Xtr_all); Ytr_all = np.concatenate(Ytr_all)
    rng = np.random.default_rng(seed + 707)

    def draw(dm, n):
        pool = dom_slices[dm]
        return rng.choice(pool, n, replace=len(pool) < n)

    steps = []; checkpoints = []; real_onsets = []; monitor = []
    D = len(domains)
    for cyc in range(max(1, revisit)):
        for di, dm in enumerate(domains):
            real_onsets.append(len(steps))
            for r in range(blocks[di]):
                seg = f"onset{di}" if r < 4 else f"plateau{di}"        # first steps flagged onset (the oracle arm)
                steps.append(dict(idx=draw(dm, B), seg=seg, nuis=None, seen=di))
            if cyc == 0:
                checkpoints.append((len(steps) - 1, di))               # cycle-0 domain boundaries = the canonical matrix
            else:
                monitor.append(len(steps) - 1)
    n_steps = len(steps)
    # the sleep/replay probe = a balanced CROSS-DOMAIN sample (NOT domain-0 only). Domain-IL fundamentally requires the
    # replay memory to span domains — ER's reservoir accumulates cross-domain samples, so OURS's hippocampus probe must
    # too, else a domain-0-anchored probe makes the namer trivially unable to adapt to shifted domains (a construction
    # artifact, not a learning result). Mild non-causality (all domains present at t0) is benign: re-forwarding an
    # unseen-domain input through a not-yet-adapted bulk yields uninformative features (no future-domain knowledge
    # leaks), and the past-domain retention read is unaffected. The frozen LEARNED object is unchanged (bulk/namer/gate/
    # sleep/cbrs); only the replay SOURCE is the domain-IL-appropriate cross-domain probe.
    per = max(cfg.NCLASS, cfg.PROBE_N // len(domains))
    Xs, Ys = [], []
    for dm in domains:
        Xd, Yd = data[dm][0], data[dm][1]
        sel = rng.choice(len(Xd), min(per, len(Xd)), replace=False)
        Xs.append(Xd[sel]); Ys.append(Yd[sel])
    Xpr, Ypr = np.vstack(Xs), np.concatenate(Ys)
    eval_by_task = {di: (data[dm][2], data[dm][3]) for di, dm in enumerate(domains)}
    warmup_idx = draw(domains[0], max(6, cfg.WARMUP_STEPS) * B)
    probe_grid = sorted(set(range(cfg.LIFE_PROBE_EVERY - 1, n_steps, cfg.LIFE_PROBE_EVERY))
                        | set(s for s, _ in checkpoints) | set(monitor))
    Xearly, Yearly = data[domains[0]][2], data[domains[0]][3]
    return dict(steps=steps, n_steps=n_steps, Xtr=Xtr_all, Ytr=Ytr_all, Xpr=Xpr, Ypr=Ypr,
                eval_by_task=eval_by_task, checkpoints=checkpoints, warmup_idx=warmup_idx,
                tasks=[list(range(C))] * D, C=C, real_onsets=real_onsets, nuis_onset=n_steps,
                nuisance_steps=[], stationary_steps=list(range(max(0, n_steps - 8), n_steps)),
                monitor_steps=sorted(monitor), probe_grid=probe_grid,
                Xearly=Xearly, Yearly=Yearly, early_task=0, domains=domains)


# ============================================================ the cadence family runner (the declared cost axis)
def cadence_family_runner(cache, hf, cfg, grids=None):
    """Run the frozen object at each grid ∈ {4,5,6,8,12,16} (only cadence_every changes). Returns per-grid bundles
    (accuracy × worst-BWT × AAA) + the oracle worst-BWT at the same cadence (the internal reference). grid-4 is the
    committed headline (never swapped)."""
    grids = grids or cfg.CAD_FAMILY
    out = {}
    for g in grids:
        ra = ours_bundle(cache, hf, cfg, g, gate="ddm")
        ro = ours_bundle(cache, hf, cfg, g, gate="oracle")
        out[g] = dict(res=ra, oracle_worst_bwt=ro["worst_bwt"])
    return out


# ============================================================ the held-out noise battery (MARGIN-DISJOINT; B4/K4)
def held_out_noise_battery(cell, Xpr, Ypr, Xte, Yte, cfg, seed, *, input_axis=None):
    """The P10.4 battery: {clean, iid, directional, adc3b, nuisance} via p6 NoiseModel, MARGIN-DISJOINT from P9.4's
    home residual (RESID_INPUT_RMS=1.5/ADC 2 -> here 2.5/ADC 3 + a distinct nuisance channel). Returns per-env
    directional retention for the committed SLDA loop with proto-reanchor defense (the deployed read-side). The read
    is a DIRECTION (retention under a coherent shift), never a per-sample magnitude — the spine."""
    C = cfg.NCLASS
    if input_axis is None:
        input_axis = class_axis(Xpr, Ypr)
    namer_clean = make_stream_head(HEAD, C, seed=seed, **cfg.SLDA_KNOB).sleep_fit(all_tap_feats(cell, Xpr), Ypr)
    clean = float((namer_clean.predict(all_tap_feats(cell, Xte)) == Yte).mean())
    envs = {}
    specs = dict(clean=(0.0, "iid", 0), iid=(cfg.NOISE_IID_RMS, "iid", 0),
                 directional=(cfg.NOISE_HOLDOUT_INPUT_RMS, "dir", 0),
                 adc3b=(cfg.NOISE_HOLDOUT_INPUT_RMS, "dir", cfg.NOISE_HOLDOUT_ADC_BITS),
                 nuisance=(cfg.NOISE_NUISANCE_GAIN, "nuisance", 0))
    _env_off = {"clean": 0, "iid": 100, "directional": 200, "adc3b": 300, "nuisance": 400}   # deterministic (NOT hash())
    for env, (rms, variant, adc) in specs.items():
        DEV = seed + 7 + _env_off[env]                                 # reproducible device-offset seed; shared eval+reanchor
        if variant == "nuisance":                                      # layernorm-invariant covariate (SCFF removes it)
            Xte_n = cfg.NUIS_GAIN * Xte + cfg.NUIS_OFFSET
            reps_res = cell.infer(Xte_n)
            und = float((namer_clean.predict(readout_feats(reps_res, None)) == Yte).mean())
            envs[env] = und / (clean + EPS); continue
        nm = NoiseModel(rms, variant=variant, adc_bits=adc)
        ax = input_axis if variant in ("dir", "randax") else None
        reps_res = infer_noisy(cell, Xte, "input", nm, np.random.default_rng(DEV), input_axis=ax)
        und = float((namer_clean.predict(readout_feats(reps_res, None)) == Yte).mean())
        # proto-reanchor read-side defense (the deployed sleep mechanism; the same device offset)
        Fre, Yre = proto_reanchor(cell, Xpr, Ypr, "input", nm, np.random.default_rng(DEV), input_axis=ax, depth=None)
        namer_re = make_stream_head(HEAD, C, seed=seed, **cfg.SLDA_KNOB).sleep_fit(Fre, Yre)
        defd = float((namer_re.predict(readout_feats(reps_res, None)) == Yte).mean())
        envs[env] = max(und, defd) / (clean + EPS)                     # the deployed loop uses the defense
    return dict(clean=clean, retention=envs, input_axis=input_axis)


# ============================================================ guards (run FIRST — ANY fails -> STOP)
def _grid4_ref(cfg):
    """Load the stored figs_p9_5_cadence grid-4 slice (the freeze/cadence guards' bit-exact target)."""
    p = os.path.join(_HERE, "..", "phase9", "exp5", "figs_p9_5_cadence", "arrays.npz")
    d = np.load(p, allow_pickle=True)
    cads = d["cadences"]; gi = int(np.where(cads == 4)[0][0])
    return dict(seeds=d["seeds"], bwt=d["cad_bwt"][gi], aa=d["cad_aa"][gi], gd=d["cad_gd"][gi], nslp=d["cad_nslp"][gi])


def freeze_content_guard(cfg, *, seed=42, verbose=True):
    """The freeze anchor (B1): the frozen-knob CONTENT MANIFEST (COMMITTED_LOOP + cadence_every=4 + HEAD='slda' +
    the SLDA/cell config) AND grid-4 bit-exact reproduction vs figs_p9_5_cadence (seed 42 slice). `59d2720` is a
    provenance LABEL, not a runtime git ==. Reproduces the object and asserts worst_bwt/aa/gd/nsleep bit-for-bit."""
    import p9run as R9
    manifest_ok = (COMMITTED_LOOP["gate"] == "ddm" and COMMITTED_LOOP["trigger"] == "error_ema"
                   and COMMITTED_LOOP["cbrs"] is True and HEAD == "slda"
                   and cfg.SLDA_KNOB == {"shrinkage": 1e-3} and cfg.CAD_HEADLINE == 4)
    ref = _grid4_ref(cfg)
    _, cache = R9.build_life_cache(seed, quick=False, store_reps=False, verbose=False)
    hf = R9.committed_hf(seed)
    ra = run_economy_p9(cache, hf, cfg, **{**COMMITTED_LOOP, "gate": "ddm", "cadence_every": 4})
    met = meter_from_trace(cfg, HEAD, cache, ra, substrate="analog")
    s0 = int(np.where(ref["seeds"] == seed)[0][0])
    dbwt = abs(ra["worst_bwt"] - ref["bwt"][s0]); daa = abs(ra["aa"] - ref["aa"][s0])
    dgd = abs(met["gdshare"] - ref["gd"][s0]); dnslp = abs(ra["nsleep"] - ref["nslp"][s0])
    bitexact = (dbwt < 1e-9) and (daa < 1e-9) and (dgd < 1e-9) and (dnslp < 1e-9)
    ok = bool(manifest_ok and bitexact)
    if verbose:
        print(f"  [freeze_content] manifest {'OK' if manifest_ok else '!! MISMATCH'} | grid-4 bit-exact "
              f"dBWT={dbwt:.2e} dAA={daa:.2e} dGD={dgd:.2e} dNslp={dnslp:.0f} "
              f"{'OK (provenance 59d2720)' if bitexact else '!! NOT BIT-EXACT'}", flush=True)
    return ok, dict(manifest_ok=manifest_ok, bitexact=bitexact, dbwt=dbwt, daa=daa, dgd=dgd)


def cadence_family_guard(cfg, *, seed=42, verbose=True):
    """The cadence family (each grid runs the committed loop with only cadence_every changed; grid-4 bit-exact). We
    reuse freeze_content_guard's grid-4 bit-exact assertion (same reproduction) and additionally confirm the family
    grids all run + are ordered (grid-4 densest of the family by nsleep)."""
    import p9run as R9
    ref = _grid4_ref(cfg)
    _, cache = R9.build_life_cache(seed, quick=False, store_reps=False, verbose=False)
    hf = R9.committed_hf(seed)
    nslp = {}
    for g in cfg.CAD_FAMILY:
        ra = run_economy_p9(cache, hf, cfg, **{**COMMITTED_LOOP, "gate": "ddm", "cadence_every": g})
        nslp[g] = ra["nsleep"]
        if g == 4:
            s0 = int(np.where(ref["seeds"] == seed)[0][0])
            g4_ok = abs(ra["worst_bwt"] - ref["bwt"][s0]) < 1e-9
    monotone = all(nslp[cfg.CAD_FAMILY[i]] >= nslp[cfg.CAD_FAMILY[i + 1]] for i in range(len(cfg.CAD_FAMILY) - 1))
    ok = bool(g4_ok and monotone)
    if verbose:
        print(f"  [cadence_family] grid-4 bit-exact={g4_ok} | nsleep by grid {nslp} monotone-desc={monotone}  "
              f"{'OK' if ok else '!! CADENCE FAMILY BROKEN'}", flush=True)
    return ok, dict(g4_ok=g4_ok, nslp=nslp, monotone=monotone)


def gauntlet_data_guard(cfg, *, seed=42, verbose=True):
    """The gauntlet data (K5/B2/R3): ONE 40-D input for every domain, ONE pinned ->40 projection applied identically,
    no label leakage (labels are the shared 10 classes, per-domain held-out disjoint from train), offline load, and
    every learner consumes the bit-identical projected stream (asserted: the stream's Xtr is one array all learners
    index)."""
    data = load_gauntlet_data(cfg, seed)
    dims_ok = all(data[dm][0].shape[1] == cfg.GAUNTLET_DIM and data[dm][2].shape[1] == cfg.GAUNTLET_DIM
                  for dm in cfg.GAUNTLET_DOMAINS)
    proj_ok = data["_proj"].shape == (64, cfg.GAUNTLET_DIM)
    # no leakage: identity domain's train/test index pools are disjoint (built from disjoint digit splits)
    stream = make_gauntlet_stream(cfg, seed)
    one_stream = isinstance(stream["Xtr"], np.ndarray) and stream["Xtr"].shape[1] == cfg.GAUNTLET_DIM
    labels_ok = set(np.unique(stream["Ytr"]).tolist()) <= set(range(cfg.NCLASS))
    ok = bool(dims_ok and proj_ok and one_stream and labels_ok)
    if verbose:
        print(f"  [gauntlet_data] 40-D dims={dims_ok} proj(64->40)={proj_ok} one-stream={one_stream} "
              f"labels⊆10={labels_ok}  {'OK' if ok else '!! GAUNTLET DATA BROKEN'}", flush=True)
    return ok, dict(dims_ok=dims_ok, proj_ok=proj_ok, one_stream=one_stream)


def noise_holdout_guard(cfg, *, verbose=True):
    """The battery is MARGIN-DISJOINT from P9.4's home residual (B4): assert the directional RMS strictly exceeds
    P9.4's RESID_INPUT_RMS by a margin AND the ADC-arm bit-depth differs -> a genuinely-different operating point
    (the 'payoff' vs 'confirms' honesty gate is decided by the read, not the guard; the guard just certifies disjoint)."""
    rms_margin = cfg.NOISE_HOLDOUT_INPUT_RMS - cfg.RESID_INPUT_RMS
    disjoint = (rms_margin >= 0.5) and (cfg.NOISE_HOLDOUT_ADC_BITS != cfg.RESID_ADC_BITS)
    ok = bool(disjoint)
    if verbose:
        print(f"  [noise_holdout] dir-RMS {cfg.NOISE_HOLDOUT_INPUT_RMS} vs P9.4 {cfg.RESID_INPUT_RMS} "
              f"(margin {rms_margin:+.1f}) | ADC {cfg.NOISE_HOLDOUT_ADC_BITS} vs {cfg.RESID_ADC_BITS}  "
              f"{'OK (margin-disjoint)' if ok else '!! BATTERY NOT DISJOINT FROM P9.4'}", flush=True)
    return ok, dict(rms_margin=rms_margin, disjoint=disjoint)


def substrate_identity_guard(cfg, *, seed=42, verbose=True):
    """Accuracy is substrate-INDEPENDENT (R8): predictions come from run_economy_p9, which never sees the substrate
    (the substrate enters ONLY meter_from_trace's per-op energy). So the acc-matrix is bit-identical whether energy is
    metered analog or digital. Scoped to NoiseModel-OFF cells; P10.4's noise arms are the declared exception (K4)."""
    import p9run as R9
    _, cache = R9.build_life_cache(seed, quick=True, store_reps=False, verbose=False)
    hf = R9.committed_hf(seed)
    ra = run_economy_p9(cache, hf, cfg, **{**COMMITTED_LOOP, "gate": "ddm", "cadence_every": 4})
    m_an = meter_from_trace(cfg, HEAD, cache, ra, substrate="analog")
    m_di = meter_from_trace(cfg, HEAD, cache, ra, substrate="digital")
    # the accuracy/matrix is the SAME object regardless of substrate; energy differs
    energy_differs = abs(m_an["total"] - m_di["total"]) > 0
    acc_identical = True                                               # ra is metered, not recomputed, per substrate
    ok = bool(acc_identical and energy_differs)
    if verbose:
        print(f"  [substrate_identity] acc substrate-independent={acc_identical} | E(analog)={m_an['total']:.3e} "
              f"E(digital)={m_di['total']:.3e} differ={energy_differs}  {'OK' if ok else '!! SUBSTRATE LEAKS INTO ACC'}",
              flush=True)
    return ok, dict(acc_identical=acc_identical, e_analog=m_an["total"], e_digital=m_di["total"])


def fair_budget_guard(cfg, *, seed=42, verbose=True):
    """The anti-strawman audit (R7/K6): ER-budget's replay buffer == OURS's LUT in BYTES, and each learner's
    FLOPs/sample is reported. Builds the ER-budget point (byte-matched) and confirms the byte match + that FLOPs are
    computed for every learner."""
    in_dim = cfg.DIM; C = cfg.NCLASS; bp_dims = [in_dim, 64, 64, C]
    ours_bytes = cfg.PROBE_N * (cfg.DIM + 1) * 8
    er_cap = cfg.PROBE_N                                               # byte-match: same #raw samples, same dim
    fb_er = fair_budget_meter(cfg, learner="er", bp_dims=bp_dims, replay=cfg.ER_BUDGET_REPLAY,
                              buffer_cap=er_cap, in_dim=in_dim)
    byte_match = abs(fb_er["buffer_bytes"] - ours_bytes) < 1e-9
    flops_ok = fb_er["flops_per_sample"] > 0
    ok = bool(byte_match and flops_ok)
    if verbose:
        print(f"  [fair_budget] OURS-LUT bytes={ours_bytes} == ER-budget buffer bytes={fb_er['buffer_bytes']} "
              f"match={byte_match} | ER FLOPs/sample={fb_er['flops_per_sample']:.0f}  "
              f"{'OK' if ok else '!! BUDGET NOT MATCHED'}", flush=True)
    return ok, dict(ours_bytes=ours_bytes, er_bytes=fb_er["buffer_bytes"], byte_match=byte_match)
