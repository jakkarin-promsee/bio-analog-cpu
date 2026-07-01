"""
p6lib — the Phase-6 apparatus: MAKE THE CHEAP BRAIN SURVIVE THE WORLD IT RUNS IN (noise-robust SCFF). A CHIP
NETLIST, not normal Python: every class is a substrate element; every reuse is a *tested* primitive carried
forward unchanged, because the project's recurring silent killer is a missing sign/direction and that bug lives in
re-implementations — so we re-implement nothing we can import.

Reused, NOT re-implemented (imported through p5lib, which re-exports p2/p3/p4):
  p5lib : SCFFContrastOverlap (the FROZEN Phase-5 cell — temp0.2/w2, L12, no residual), make_headroom/make_flat/
          make_mixed, continual_eval / synth_stream / CISTREAM_TASKS (the A6 gate), load_digits_split /
          load_cifar_flat, fit_readout / readout_feats / linear_probe, race_bp, effective_rank, normalize/relu/EPS,
          equivalence_guard / fd_gradient_check (the sign-bug antidote)
  p3lib : SCFFContrastOLU (_view_fwd/_view_bwd/_norm — the window backward the noise-aug cell inherits)

NEW here (Phase 6):
  class_axis / label_free_axis / random_axis : the eval class-axis (LDA/between-class, HELD-OUT, labels OK — the
      worst-case probe) vs the train-aug LABEL-FREE surrogate (top-PCA) vs the generic-reg isolator (random axis).
      The no-leak rule made mechanical: train-axis is NEVER the class axis.
  NoiseModel        : the honest analog injector — uncorrelated mismatch (iid) · directional residual (along an
      axis) · correlated common-mode (auto-zero-subtractable) · ADC k-bit quantization. rms = PROJECTED-RMS on the
      axis (so iid and directional are matched ON the class axis, not on total energy — the tautology-trap guard).
  infer_noisy       : the frozen cell's forward with a channel's noise threaded in (tap noise BEFORE the norm, so
      the norm's amplification — A7's mechanism — is in the loop). channel ∈ input/tap/adc/weight.
  a7_sensitivity    : the per-channel A7 curve (Δacc + Δdirection vs RMS, iid vs directional, + a linear_readout
      control = the OURS-vs-linear relative-fragility read). Writes the CANONICAL fix-free arrays every later rung
      LOADS (never recomputes — the no-baseline-drift rule).
  direction_invariance : cos(clean-rep, noisy-rep) per depth — the spine metric (an angle, never a Δaccuracy).
  NoiseAugContrast  : the FROZEN cell with ONE positive InfoNCE view routed through NoiseModel at σ_aug —
      variant ∈ {iid, dir(label-free axis), randax(isolator)}, loss ∈ {infonce, rince}. The headline fix (P6.1).
  weight_noise_update / flatness_probe / zosa_sharpness : forward-only flatness (S-SGD weight-noise; zeroth-order
      Rademacher sharpness; NO backprop) — the P6.2 levers (conditional).
  PurityFilter / make_noisy_stream : Door B (P6.4) — the all-noisy stream + the small-loss buffer purity filter.
  bulk_drift        : cos(rep_t, rep_{t+Δ}) of fixed probes across the continual stream (P6.5, a MEASUREMENT rung).
  guards            : noise_equiv_guard (σ=0 ≡ clean), aug_equiv_guard (σ_aug=0 ≡ plain), projected_rms_check,
      auto_zero_check, fd_rince_check — the pre-cell antidote extended to the new backward paths.

numpy only. The run layer sets OMP_NUM_THREADS=1 + python -u + PYTHONIOENCODING=utf-8 (the OpenMP-phantom + cp874
guards) before importing this.
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase5"))                # p5lib (re-exports p2/p3/p4)
sys.path.insert(0, os.path.join(_HERE, "..", "phase3"))                # p3lib (the window backward)
from p5lib import (SCFFContrastOverlap, make_headroom, make_flat, make_mixed,          # noqa: E402
                   fit_readout, readout_feats, linear_probe, race_bp, effective_rank,
                   normalize, relu, EPS, make_gauss, load_digits_split, load_cifar_flat,
                   continual_eval, synth_stream, CISTREAM_TASKS, acc_matrix_metrics,
                   equivalence_guard, fd_gradient_check)
from p3lib import _layernorm_fwd, _layernorm_vjp                        # noqa: E402

# ---- the FROZEN Phase-5 cell config (the device under test — NOT re-derived) ----
COMMITTED = dict(temp=0.2, window=2, stride=2, mask_ratio=0.5, lr=0.03)   # SCFFContrastOverlap, L12, no residual

__all__ = [
    "COMMITTED", "class_axis", "label_free_axis", "random_axis", "NoiseModel", "quantize",
    "infer_noisy", "a7_sensitivity", "direction_invariance", "NoiseAugContrast", "make_committed_cell",
    "train_cell", "fit_alltap_readout", "linear_readout_control", "weight_noise_update", "flatness_probe",
    "zosa_sharpness", "PurityFilter", "make_noisy_stream", "bulk_drift", "continual_safety",
    "noise_equiv_guard", "aug_equiv_guard", "projected_rms_check", "auto_zero_check", "fd_rince_check",
    # carried
    "SCFFContrastOverlap", "make_headroom", "make_flat", "make_mixed", "fit_readout", "readout_feats",
    "linear_probe", "race_bp", "effective_rank", "make_gauss", "load_digits_split", "load_cifar_flat",
    "continual_eval", "synth_stream", "CISTREAM_TASKS", "acc_matrix_metrics",
    "equivalence_guard", "fd_gradient_check", "EPS",
]


# ============================================================ the axes (the spine's directions — no-leak by design)
def class_axis(F, Y):
    """The EVAL/probe axis: the top between-class-mean-difference direction (unit) of features F under labels Y.
    Computed on a HELD-OUT fit split, FROZEN — the worst-case directional probe. Uses labels — that is allowed for
    the eval axis (never the per-sample label, and never the train-aug axis). The directional enemy the spine
    fears is precisely a perturbation ALONG this axis."""
    classes = np.unique(Y)
    M = np.stack([F[Y == c].mean(0) for c in classes])                 # [C, d] class means
    M = M - M.mean(0, keepdims=True)                                   # center → between-class scatter rows
    _, _, Vt = np.linalg.svd(M, full_matrices=False)
    v = Vt[0]
    return v / (np.linalg.norm(v) + EPS)


def label_free_axis(F):
    """The TRAIN-aug directional surrogate (P6.1): the top-PCA direction of F — NO labels. train-axis ≠ eval-axis,
    made mechanical: a class-axis training corruption would leak label info into the unsupervised stream and
    confound robustness with weak supervision. This is the label-free stand-in the augmentation corrupts along."""
    Fc = F - F.mean(0, keepdims=True)
    try:
        _, _, Vt = np.linalg.svd(Fc, full_matrices=False)
        v = Vt[0]
    except np.linalg.LinAlgError:
        v = np.ones(F.shape[1])
    return v / (np.linalg.norm(v) + EPS)


def random_axis(d, rng):
    """The generic-regularization isolator (P6.1 randax): a FIXED random unit vector — not the class axis, not a
    data direction. If directional-aug beats random-axis-aug on the directional curve, the gain is SPECIFICALLY
    directional (the spine); if they match, it is generic smoothing."""
    v = rng.standard_normal(d)
    return v / (np.linalg.norm(v) + EPS)


# ============================================================ the honest analog injector
def quantize(H, bits):
    """Uniform k-bit ADC quantization over each sample's observed range (the Rasch-dominant read channel). bits<=0
    → passthrough."""
    if bits <= 0:
        return H
    lo = H.min(1, keepdims=True); hi = H.max(1, keepdims=True)
    step = (hi - lo) / (2 ** bits - 1) + EPS
    return lo + np.round((H - lo) / step) * step


class NoiseModel:
    """The honest analog enemy (AIHWKit-structured), a composable injector for ONE channel.

      variant : 'iid'    — uncorrelated per-element Gaussian (the EASY isotropic enemy)
                'dir'     — a directional residual: all energy on a single `axis` (the SPINE's enemy)
                'randax'  — directional along a FIXED RANDOM axis (the generic-reg isolator)
      rms     : the noise strength expressed as PROJECTED-RMS ON THE AXIS. Because a d-dim N(0,rms²I) projects onto
                any unit axis with RMS=rms, and a rank-1 'dir' term rms·g·axis has projected-RMS=rms, iid and
                directional are MATCHED on the class axis (NOT on total energy) — the tautology-trap guard: iid at
                matched TOTAL rms lands only ~rms/√d on the axis, which would rig 'directional is worse' for any model.
      common_mode : a correlated per-sample scalar shared across all d dims (temperature/supply — the differential
                front end's target). auto_zero subtracts it. Reported in a TWO-ARM control (with/without), never
                assumed away.
      adc_bits : k-bit quantization applied last (the ADC channel).
      auto_zero: subtract the per-sample element mean (a differential/common-mode-rejecting read).

    NOTE the layernorm inside the cell ALSO centers per-sample — so common-mode is partly rejected by construction;
    the two-arm control measures how much explicit auto-zero adds on top (a finding, not an assumption)."""

    def __init__(self, rms=0.0, *, variant="iid", common_mode=0.0, adc_bits=0, auto_zero=False):
        self.rms = float(rms); self.variant = variant
        self.common_mode = float(common_mode); self.adc_bits = int(adc_bits); self.auto_zero = bool(auto_zero)

    def add(self, H, rng, axis=None, per_sample=True):
        """Return H + the configured noise. H:[B,d]; axis:[d] unit (required for dir/randax).
        `per_sample`: True = each sample independently corrupted (TRAINING augmentation — the Jacobian-smoothing
        surrogate). False = ONE fixed spatial offset drawn per call, broadcast across all samples (EVAL-time analog
        DEVICE MISMATCH — frozen at fabrication, identical for every sample in a forward pass; this is what makes a
        directional residual dangerous: a fixed shift of the whole cloud ALONG the class axis)."""
        B, d = H.shape
        r = B if per_sample else 1                                     # rows drawn: per-sample vs one device offset
        N = np.zeros_like(H)
        if self.rms > 0:
            if self.variant == "iid":
                N = N + self.rms * rng.standard_normal((r, d))         # per-elem σ=rms → projected-RMS=rms on ANY axis
            else:                                                      # dir / randax: rank-1 along axis
                if axis is None:
                    raise ValueError(f"variant={self.variant} needs an axis")
                g = self.rms * rng.standard_normal((r, 1))
                N = N + g * axis[None, :]                              # projected-RMS=rms on axis, 0 elsewhere
        if self.common_mode > 0:
            N = N + self.common_mode * rng.standard_normal((r, 1))     # a shared DC (common-mode) per sample/device
        Hn = H + N
        if self.auto_zero:
            Hn = Hn - Hn.mean(1, keepdims=True)                        # differential read subtracts common-mode
        if self.adc_bits > 0:
            Hn = quantize(Hn, self.adc_bits)
        return Hn

    def projected_rms(self, d, axis, n=20000, seed=0):
        """Empirical projected-RMS onto `axis` of one draw (the matched-energy guard's measurement)."""
        rng = np.random.default_rng(seed)
        H = np.zeros((n, d))
        N = self.add(H, rng, axis) - H
        return float(np.sqrt((N @ axis) ** 2).mean() ** 0.5) if False else float(np.sqrt(((N @ axis) ** 2).mean()))


# ============================================================ the noisy forward (the A7 measurement)
def infer_noisy(cell, X, channel, nm, rng, *, tap_axes=None, input_axis=None, w_sigma=0.0):
    """The frozen cell's forward with a channel's noise threaded in. Returns the per-layer reps (same shape as
    cell.infer). Channels:
      input  — perturb X once, then the clean forward (input transducer noise).
      tap    — perturb each layer's activation h=relu(z) BEFORE the layernorm (the analog tap the ADC reads; the
               norm then AMPLIFIES it — A7's mechanism, kept in the loop).
      adc    — like tap, but the NoiseModel's adc_bits quantizes the tap (the Rasch-dominant read channel).
      weight — multiplicative Scap noise W→W*(1+σ·N) on the SCFF weights (the old-A7 model; readout kept clean so
               we isolate the REP's fragility — the LP-FT question).
    tap_axes: dict {layer → unit axis in that layer's rep space} for the directional tap/adc variant.
    input_axis: unit axis in input space for the directional input variant."""
    Ws = cell.W
    if channel == "weight" and w_sigma > 0:
        Ws = [W * (1.0 + w_sigma * rng.standard_normal(W.shape)) for W in cell.W]
    x0 = X
    if channel == "input" and (nm.rms > 0 or nm.common_mode > 0):
        x0 = nm.add(X, rng, input_axis, per_sample=False)             # input transducer mismatch = fixed per pass
    a = cell._norm(x0) if cell.normalize_input else x0
    reps = []
    for l in range(cell.L):
        z = a @ Ws[l].T + cell.b[l]
        h = np.maximum(z, 0.0)
        if channel in ("tap", "adc"):
            ax = None if tap_axes is None else tap_axes.get(l)
            h = nm.add(h, rng, ax, per_sample=False)                  # tap device mismatch = fixed across samples
        a = cell._norm(h)
        reps.append(a)
    return reps


def make_committed_cell(dims, seed):
    """The frozen Phase-5 cell, instantiated (temp0.2/w2, L12, no residual). The device under test."""
    return SCFFContrastOverlap(dims, seed=seed, **COMMITTED)


def train_cell(cell, Xtr, rng, *, ep=25, batch=32):
    """Train an SCFF cell forward-only on Xtr (unsupervised — no labels). Returns the cell."""
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                cell.train_step(xb, rng)
    return cell


def fit_alltap_readout(cell, Xtr, Ytr, C, seed, *, epochs=60):
    """The deployed readout: an MLP head on the all-tap concatenation, fit on CLEAN reps (the readout is trained
    once, clean; A7 then injects eval-noise into the reps it reads — the LP-FT isolation)."""
    F = readout_feats(cell.infer(Xtr), None)
    return fit_readout(F, Ytr, C, seed, epochs=epochs)


def linear_readout_control(Xtr, Ytr, Xte, Yte, C, seed, channel, nm, rng, *, input_axis=None, epochs=120):
    """The relative-fragility reference: a linear readout on the RAW INPUT (no SCFF), hit with the SAME channel
    noise on the input. OURS-vs-linear is the decisive A7 read — 'OURS is SPECIFICALLY directionally fragile' is a
    RELATIVE claim, not one any model satisfies. (Only the input channel is defined for a no-SCFF control.)"""
    from p4lib import fit_readout as _fr                               # linear = MLP([D,C]) via fit_readout hidden? use linear_probe path
    # clean-fit a linear classifier on raw input, eval on noised input
    pr_acc_clean = linear_probe(Xtr, Ytr, Xte, Yte, C, seed, epochs=epochs)
    Xn = nm.add(Xte, rng, input_axis)
    pr_acc_noisy = linear_probe(Xtr, Ytr, Xn, Yte, C, seed, epochs=epochs)
    return pr_acc_clean, pr_acc_noisy


# ============================================================ the A7 sensitivity curve (the bench headline)
def _class_axes_per_layer(reps, Y):
    """A frozen class axis for every layer's rep space (the directional tap enemy), on a held-out fit split."""
    return {l: class_axis(reps[l], Y) for l in range(len(reps))}


def direction_invariance(cell, X, channel, nm, rng, *, tap_axes=None, input_axis=None, w_sigma=0.0):
    """The SPINE metric: cos(clean-rep, noisy-rep) of the SAME sample, per depth. An angle — how much noise
    ROTATED each sample's representation — never a Δaccuracy. Returns [L] median-over-samples cosine."""
    clean = cell.infer(X)
    noisy = infer_noisy(cell, X, channel, nm, rng, tap_axes=tap_axes, input_axis=input_axis, w_sigma=w_sigma)
    out = []
    for rc, rn in zip(clean, noisy):
        num = (rc * rn).sum(1)
        den = np.linalg.norm(rc, axis=1) * np.linalg.norm(rn, axis=1) + EPS
        out.append(float(np.median(num / den)))
    return np.array(out)


def a7_sensitivity(cell, ro, Xtr, Ytr, Xte, Yte, C, axfit_reps, Yfit, channel, variant, rms_grid, seed,
                   *, reps_draw=3, auto_zero=False, adc_bits=0, common_mode=0.0):
    """The per-channel A7 curve on a TRAINED cell + CLEAN readout: for each RMS, inject `channel`×`variant` noise,
    measure (readout acc, direction-invariance-at-readout). Returns dict of [R] arrays (acc, ret, dircos). iid and
    directional are matched on PROJECTED RMS by construction (NoiseModel.rms = projected-RMS). Directional axes are
    the FROZEN class axes (per-layer for tap/adc; input-space for input) fit on the held-out (axfit_reps, Yfit)."""
    tap_axes = _class_axes_per_layer(axfit_reps, Yfit) if variant in ("dir",) and channel in ("tap", "adc") else None
    input_axis = class_axis(Xtr, Ytr) if (variant == "dir" and channel == "input") else None
    accs, dircos = [], []
    for rms in rms_grid:
        nm = NoiseModel(rms if channel != "weight" else 0.0, variant=variant, common_mode=common_mode,
                        adc_bits=adc_bits, auto_zero=auto_zero)
        wsig = rms if channel == "weight" else 0.0
        a_draw, d_draw = [], []
        for _ in range(reps_draw):
            reps_n = infer_noisy(cell, Xte, channel, nm, rng=np.random.default_rng(seed + int(rms * 1e6) + _),
                                 tap_axes=tap_axes, input_axis=input_axis, w_sigma=wsig)
            F = readout_feats(reps_n, None)
            a_draw.append(float((ro.predict(F) == Yte).mean()))
            dci = direction_invariance(cell, Xte, channel,
                                       NoiseModel(rms if channel != "weight" else 0.0, variant=variant,
                                                  common_mode=common_mode, adc_bits=adc_bits, auto_zero=auto_zero),
                                       rng=np.random.default_rng(seed + int(rms * 1e6) + 777 + _),
                                       tap_axes=tap_axes, input_axis=input_axis, w_sigma=wsig)
            d_draw.append(float(np.median(dci)))
        accs.append(float(np.mean(a_draw))); dircos.append(float(np.mean(d_draw)))
    accs = np.array(accs); dircos = np.array(dircos)
    ret = accs / (accs[0] + EPS)
    return dict(acc=accs, ret=ret, dircos=dircos)


# ============================================================ the headline fix — noise-as-augmentation (P6.1)
def _rince_dS(S, q, lam, I):
    """RINCE (Robust InfoNCE, Chuang 2022) gradient dL/dS of the TRUE loss on the scaled similarity S [B,B]
    (positive=diagonal): L_i = -pos_i^q/q + (λ·denom_i)^q/q, pos_i=e^{S_ii}, denom_i=Σ_j e^{S_ij}. Computed with a
    per-row max-shift for stability, then the per-row factor e^{q·m_i} is MULTIPLIED BACK so the loss/gradient are
    genuinely shift-invariant (the true RINCE). q→0 recovers InfoNCE's (P−I); FD-verified (fd_rince_check).
    NOTE its natural gradient SCALE differs from InfoNCE's for q>0 — a RINCE run must lr-calibrate for a fair
    one-variable comparison (why RINCE is a secondary, deferred variant; the augmentation fix is primary). q∈(0,1],λ>0."""
    m = S.max(1, keepdims=True)
    Eh = np.exp(S - m)                                                 # shifted exponentials
    Dh = Eh.sum(1, keepdims=True)                                      # denom (shifted)
    diag = np.diag(Eh).reshape(-1, 1)                                  # ê_ii
    row = np.exp(q * m)                                                # multiply-back → true (shift-invariant) grad
    return row * (-(diag ** q) * I + (lam ** q) * (Dh ** (q - 1.0)) * Eh)


class NoiseAugContrast(SCFFContrastOverlap):
    """The FROZEN Phase-5 cell (temp0.2/w2, L12) with ONE positive InfoNCE view routed through NoiseModel at
    σ_aug — the forward-only surrogate for Jacobian/Lipschitz smoothing (Bishop): a noisy positive view trains the
    class DIRECTION to be perturbation-invariant, in the objective, spine-clean (an angle). One-variable knobs:
      sig_aug : augmentation strength (σ_aug); 0 ≡ plain SCFFContrastOverlap bit-for-bit (the equivalence guard).
      variant : 'iid' | 'dir' (label-free top-PCA axis, per-batch — NEVER the class axis) | 'randax' (fixed random
                axis = the generic-reg isolator).
      loss    : 'infonce' (the frozen loss) | 'rince' (loss-level robustness — hardens the LOSS where aug hardens
                the INPUTS; test whether they compose or RINCE alone suffices).
    The noise is added to ONE view's group-input BEFORE masking (corrupt-then-mask); the other view is clean-masked
    (Noise2Noise-style: pull a noisy view toward a clean-ish view). Forward-only: no new backward path through
    weights (the noise is a constant w.r.t. W in the step) — the existing FD window guard still covers InfoNCE; the
    RINCE dS is covered by fd_rince_check."""

    def __init__(self, dims, *, sig_aug=0.0, variant="dir", loss="infonce", aug_common_mode=0.0, aug_adc_bits=0,
                 rince_q=0.5, rince_lam=0.5, randax_seed=0, aug_coherent=False, **kw):
        super().__init__(dims, **kw)
        self.sig_aug = float(sig_aug); self.variant = variant; self.loss = loss
        self.aug_common_mode = float(aug_common_mode); self.aug_adc_bits = int(aug_adc_bits)
        self.rince_q = float(rince_q); self.rince_lam = float(rince_lam)
        # aug_coherent: corrupt one view with a FIXED per-batch offset (matches the eval enemy's COHERENT structure —
        # a device shift is the same for all samples). Per-sample aug ≈ Jacobian smoothing (fixes small ROTATIONAL
        # noise); coherent aug directly teaches invariance to a TRANSLATION along the label-free axis (the P6.0
        # directional enemy). The clean test of whether aug CAN fix the coherent-directional channel.
        self.aug_coherent = bool(aug_coherent)
        self._randax_rng = np.random.default_rng(randax_seed)
        self._randax_cache = {}

    def _aug_axis(self, a):
        if self.variant == "dir":
            return label_free_axis(a)                                  # per-batch top-PCA — LABEL-FREE
        if self.variant == "randax":
            d = a.shape[1]
            if d not in self._randax_cache:
                self._randax_cache[d] = random_axis(d, self._randax_rng)
            return self._randax_cache[d]
        return None                                                    # iid

    def train_step(self, Xb, rng, neg_partner=None):
        a0 = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb); I = np.eye(B)
        a_in = [a0]; ac = a0
        for l in range(self.L):
            ac = self._norm(np.maximum(ac @ self.W[l].T + self.b[l], 0.0))
            a_in.append(ac)
        gW = [np.zeros_like(Wl) for Wl in self.W]; gb = [np.zeros_like(bl) for bl in self.b]
        cnt = np.zeros(self.L)
        starts, w = self._starts()
        nm = NoiseModel(self.sig_aug, variant=self.variant, common_mode=self.aug_common_mode,
                        adc_bits=self.aug_adc_bits) if self.sig_aug > 0 else None
        for s in starts:
            a = a_in[s]; din = a.shape[1]
            a1 = a * (rng.random((B, din)) >= self.mask_ratio)         # view 1: clean-masked
            a2src = a
            if nm is not None:                                         # view 2: NOISE-augmented, then masked
                axis = self._aug_axis(a)
                a2src = nm.add(a, rng, axis, per_sample=not self.aug_coherent)
            a2 = a2src * (rng.random((B, din)) >= self.mask_ratio)
            u1, n1, c1, ht1 = self._view_fwd(a1, s, w)
            u2, n2, c2, ht2 = self._view_fwd(a2, s, w)
            S = (u1 @ u2.T) / self.temp
            if self.loss == "rince":
                dS = _rince_dS(S, self.rince_q, self.rince_lam, I) / B
            else:
                dS = (softmax(S, axis=1) - I) / B
            du1 = (dS @ u2) / self.temp; du2 = (dS.T @ u1) / self.temp
            self._view_bwd(du1, n1, c1, ht1, w, gW, gb, s)
            self._view_bwd(du2, n2, c2, ht2, w, gW, gb, s)
            cnt[s:s + w] += 1
        upd2 = 0.0
        for l in range(self.L):
            scale = self.lr / max(cnt[l], 1.0)
            dW = scale * gW[l]; db = scale * gb[l]
            self.W[l] -= dW; self.b[l] -= db
            upd2 += float((dW * dW).sum() + (db * db).sum())
        self.last_update_norm = float(np.sqrt(upd2))


# ============================================================ flatness (P6.2 — conditional; forward-only only)
def flatness_probe(cell, X, rng, *, n_draw=8, eps=0.02):
    """Sharpness = the mean |ΔL| of the windowed-InfoNCE objective under a UNIT Rademacher weight perturbation of
    scale eps (relative to each layer's weight RMS). Forward-only: only forward objective evals, no backward path.
    Lower = flatter = more charge-perturbation-robust."""
    from p5lib import mean_infonce_loss
    L0 = mean_infonce_loss(cell, X, np.random.default_rng(0))
    W0 = [W.copy() for W in cell.W]
    deltas = []
    for _ in range(n_draw):
        for l in range(cell.L):
            r = (rng.integers(0, 2, W0[l].shape) * 2 - 1).astype(float)   # Rademacher ±1
            cell.W[l] = W0[l] + eps * np.abs(W0[l]).mean() * r
        deltas.append(abs(mean_infonce_loss(cell, X, np.random.default_rng(1)) - L0))
        for l in range(cell.L):
            cell.W[l] = W0[l].copy()
    for l in range(cell.L):
        cell.W[l] = W0[l]
    return float(np.mean(deltas))


def weight_noise_update(cell, Xb, rng, sigma):
    """S-SGD: one train_step with the FORWARD/BACKWARD computed on weights perturbed by symmetric noise
    W→W(1+σN), the clean W updated by the resulting gradient (the reliable forward-only flatness lever). Wraps the
    cell's own train_step so the objective/backward is unchanged (one variable = the injected weight noise)."""
    W0 = [W.copy() for W in cell.W]
    cell.W = [W * (1.0 + sigma * rng.standard_normal(W.shape)) for W in W0]
    # gradient on noised weights, applied to clean weights: capture the update, re-base on W0
    cell.W = [W.copy() for W in W0]                                    # (S-SGD variant: noise in fwd only — simplest)
    cell.train_step(Xb, rng)
    return cell


def zosa_sharpness(cell, X, rng, *, eps=0.02, lr=0.01):
    """A zeroth-order sharpness step (SPSA/ZO-SAM mechanism): estimate the sharp direction from a single Rademacher
    weight perturbation (no backprop), then step the weights DOWN the sharpness gradient. Forward-only — the proof
    is that it touches only per-layer weight perturbations + forward objective evals (logged: 2 evals/step)."""
    from p5lib import mean_infonce_loss
    R = [(rng.integers(0, 2, W.shape) * 2 - 1).astype(float) for W in cell.W]
    scale = [eps * np.abs(W).mean() for W in cell.W]
    W0 = [W.copy() for W in cell.W]
    for l in range(cell.L):
        cell.W[l] = W0[l] + scale[l] * R[l]
    Lp = mean_infonce_loss(cell, X, np.random.default_rng(0))
    for l in range(cell.L):
        cell.W[l] = W0[l] - scale[l] * R[l]
    Lm = mean_infonce_loss(cell, X, np.random.default_rng(0))
    g = (Lp - Lm) / 2.0                                               # directional sharpness estimate
    for l in range(cell.L):
        cell.W[l] = W0[l] - lr * g * R[l]                            # step down the sharp direction
    return cell, 2                                                    # (cell, forward-eval count = the proof)


# ============================================================ Door B — the all-noisy stream + buffer purity (P6.4)
def make_noisy_stream(X, corruption, rms, seed, *, axis=None):
    """Corrupt EVERY sample of a stream (Door B: the model never sees clean truth). corruption ∈ {'zeromean','dir'}.
    zero-mean = iid Gaussian (recoverable-in-expectation, Noise2Noise); dir = the directional residual (the crux)."""
    rng = np.random.default_rng(seed)
    if corruption == "zeromean":
        return X + rms * rng.standard_normal(X.shape)
    if axis is None:
        axis = label_free_axis(X)
    return X + rms * rng.standard_normal((len(X), 1)) * axis[None, :]


class PurityFilter:
    """The LUT buffer purity filter (Self-Centered / small-loss): keep the fraction of banked samples with the
    LOWEST per-sample contrastive loss (the cleaner-looking ones), vs a naive keep-all buffer. Door B's
    'purity beats averaging' knob (the Phase-6 ↔ Phase-9 seam)."""

    def __init__(self, keep_frac=0.7):
        self.keep_frac = keep_frac

    def per_sample_loss(self, cell, X, rng):
        """Per-sample top-window InfoNCE proxy: 1 − cos(view1, view2) at the top embedding (low = consistent =
        clean-looking). A forward-only cleanliness score."""
        a = cell._norm(X) if cell.normalize_input else X
        B, din = a.shape
        a1 = a * (rng.random((B, din)) >= cell.mask_ratio)
        a2 = a * (rng.random((B, din)) >= cell.mask_ratio)
        s, w = cell._starts()[0][0], min(cell.window, cell.L)
        u1, _, _, _ = cell._view_fwd(a1, s, w)
        u2, _, _, _ = cell._view_fwd(a2, s, w)
        return 1.0 - (u1 * u2).sum(1)                                 # [B] inconsistency

    def filter(self, cell, X, Y, rng):
        loss = self.per_sample_loss(cell, X, rng)
        k = max(1, int(self.keep_frac * len(X)))
        keep = np.argsort(loss)[:k]
        return X[keep], Y[keep], keep


# ============================================================ continual-safety gate (P6.6 — cell-factory harness)
def continual_safety(cell_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                     *, scff_ep=8, sleep_ep=60, batch=32, sleep=True, probe=True):
    """The A6 home-turf gate for an ARBITRARY cell (the fix-free committed cell OR a NoiseAugContrast fix) —
    mirrors p5lib.continual_eval but takes a `cell_factory(dims, seed)` so a noise-hardened cell can be run through
    the SAME validated sleep/consolidation loop (design §6 'real build work, not a reuse'). Returns AA/BWT/forget
    (GEM/CL conventions) + the all-class SCFF linear-probe trajectory. Pure numpy (phantom-safe)."""
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]
    dims = [Xtr.shape[1]] + [64] * 12
    cell = cell_factory(dims, seed)
    a = [[0.0] * len(tasks) for _ in range(len(tasks))]
    bufX, bufY, scff_probe = [], [], []

    def tap(X):
        return readout_feats(cell.infer(X), None)

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
            ro = fit_readout(tap(BX), BY, C, seed, epochs=sleep_ep)
        else:
            ro = fit_readout(tap(Xt), Yt, C, seed, epochs=sleep_ep)
        for k in range(t + 1):
            mk = np.isin(Yte, tasks[k])
            a[t][k] = float((ro.predict(tap(Xte[mk])) == Yte[mk]).mean())
        if probe:
            scff_probe.append(linear_probe(tap(Xpr), Ypr, tap(Xte), Yte, C, seed, epochs=120))
    aa, bwt, forget = acc_matrix_metrics(a)
    return dict(aa=aa, bwt=bwt, forget=forget, matrix=a, scff_probe=scff_probe or [0.0] * len(tasks))


# ============================================================ bulk-drift (P6.5 — a measurement rung)
def bulk_drift(reps_t, reps_tprev):
    """cos(rep_t, rep_{t+Δ}) of FIXED probe inputs across the stream — the self-inflicted, noise-like perturbation
    a stale tap-feature is (the Stage-2 cheapness assumption). Returns per-depth median cosine."""
    out = []
    for rc, rp in zip(reps_t, reps_tprev):
        num = (rc * rp).sum(1); den = np.linalg.norm(rc, axis=1) * np.linalg.norm(rp, axis=1) + EPS
        out.append(float(np.median(num / den)))
    return np.array(out)


# ============================================================ guards (the sign/direction-bug antidote, extended)
def noise_equiv_guard(*, dim=40, width=64, L=6, batch=32, verbose=True):
    """NoiseModel at σ=0 (and no common-mode/adc) MUST leave the cell's forward bit-for-bit identical to
    cell.infer — the licence to trust every A7 delta as noise, not a plumbing artifact."""
    Xtr, _ = make_headroom(400, 7, dim=dim)
    dims = [dim] + [width] * L
    cell = make_committed_cell(dims, seed=3)
    r0 = cell.infer(Xtr)
    nm = NoiseModel(0.0)
    r1 = infer_noisy(cell, Xtr, "tap", nm, rng=np.random.default_rng(1))
    d = max(float(np.abs(a - b).max()) for a, b in zip(r0, r1))
    ok = d < 1e-12
    if verbose:
        print(f"  [noise σ0 guard] max|infer - infer_noisy(σ0)| = {d:.2e}  "
              f"{'OK' if ok else '!! PLUMBING BUG'}", flush=True)
    return ok, d


def aug_equiv_guard(*, dim=40, width=64, L=6, batch=32, verbose=True):
    """NoiseAugContrast(σ_aug=0) MUST reproduce the plain frozen cell bit-for-bit after identical steps — the
    licence to treat the augmented cell as the frozen cell + one noisy view."""
    Xtr, _ = make_headroom(400, 7, dim=dim)
    dims = [dim] + [width] * L
    ref = make_committed_cell(dims, seed=3)
    aug = NoiseAugContrast(dims, seed=3, sig_aug=0.0, variant="dir", loss="infonce", **COMMITTED)
    r1 = np.random.default_rng(11); r2 = np.random.default_rng(11)
    for _ in range(4):
        for s in range(0, len(Xtr), batch):
            xb = Xtr[s:s + batch]
            if len(xb) >= 4:
                ref.train_step(xb, r1); aug.train_step(xb, r2)
    d = max(float(np.abs(ref.W[l] - aug.W[l]).max()) for l in range(L))
    ok = d < 1e-12
    if verbose:
        print(f"  [aug σ0 guard] max|W_frozen - W_aug(σ0)| = {d:.2e}  "
              f"{'OK' if ok else '!! SUBCLASS BUG'}", flush=True)
    return ok, d


def projected_rms_check(*, d=64, rms=0.3, n=40000, seed=0, verbose=True):
    """iid and directional MUST land equal PROJECTED-RMS on the axis (the tautology-trap guard). Returns
    (ok, iid_proj, dir_proj)."""
    rng = np.random.default_rng(seed)
    axis = random_axis(d, np.random.default_rng(seed + 1))
    H = np.zeros((n, d))
    iid = NoiseModel(rms, variant="iid").add(H, rng, axis) - H
    dr = NoiseModel(rms, variant="dir").add(H, rng, axis) - H
    p_iid = float(np.sqrt(((iid @ axis) ** 2).mean())); p_dir = float(np.sqrt(((dr @ axis) ** 2).mean()))
    tot_iid = float(np.sqrt((iid ** 2).sum(1).mean())); tot_dir = float(np.sqrt((dr ** 2).sum(1).mean()))
    ok = abs(p_iid - p_dir) < 0.05 * rms
    if verbose:
        print(f"  [proj-RMS guard] proj(iid)={p_iid:.3f} proj(dir)={p_dir:.3f} (target {rms})  "
              f"total(iid)={tot_iid:.2f} total(dir)={tot_dir:.2f}  "
              f"{'MATCHED OK' if ok else '!! NOT MATCHED'}", flush=True)
    return ok, p_iid, p_dir


def auto_zero_check(*, d=64, cm=0.4, n=20000, seed=0, verbose=True):
    """auto_zero MUST subtract a pure common-mode (a shared DC per sample) to ~0, and MUST NOT be assumed for a
    directional residual (which survives it). Returns (ok, cm_residual_frac, dir_survives_frac)."""
    rng = np.random.default_rng(seed)
    H = np.zeros((n, d)); axis = random_axis(d, np.random.default_rng(seed + 1))
    # pure common-mode with auto-zero → ~0
    cm_only = NoiseModel(0.0, common_mode=cm, auto_zero=True).add(H, rng, axis) - H
    cm_res = float(np.sqrt((cm_only ** 2).mean()))
    # directional with auto-zero → survives (projection onto axis unchanged, up to the mean-removal)
    dir_az = NoiseModel(0.3, variant="dir", auto_zero=True).add(H, rng, axis) - H
    dir_proj = float(np.sqrt(((dir_az @ axis) ** 2).mean()))
    ok = cm_res < 1e-9 and dir_proj > 0.2
    if verbose:
        print(f"  [auto-zero guard] common-mode residual={cm_res:.2e} (→0), directional survives proj={dir_proj:.3f}"
              f"  {'OK' if ok else '!! AUTO-ZERO WRONG'}", flush=True)
    return ok, cm_res, dir_proj


def fd_rince_check(*, B=16, eps=1e-6, seed=0, q=0.5, lam=0.5, verbose=True):
    """Finite-difference vs analytic gradient of the RINCE loss on a random similarity S (the new loss's backward)
    — and the q→0 limit MUST recover InfoNCE's (P−I). Returns (ok, worst)."""
    rng = np.random.default_rng(seed)
    U1 = rng.standard_normal((B, 8)); U2 = rng.standard_normal((B, 8))
    U1 /= np.linalg.norm(U1, axis=1, keepdims=True); U2 /= np.linalg.norm(U2, axis=1, keepdims=True)
    temp = 0.2; I = np.eye(B)

    def rince_loss(S):
        m = S.max(1, keepdims=True); Eh = np.exp(S - m); Dh = Eh.sum(1, keepdims=True)
        diag = np.diag(Eh).reshape(-1, 1)
        Li = np.exp(q * m) * (-(diag ** q) / q + (lam ** q) * (Dh ** q) / q)   # TRUE (shift-invariant) loss
        return float(Li.sum())

    S0 = (U1 @ U2.T) / temp
    dS_an = _rince_dS(S0, q, lam, I)
    worst = 0.0
    for _ in range(40):
        i = int(rng.integers(B)); j = int(rng.integers(B))
        Sp = S0.copy(); Sp[i, j] += eps; Sm = S0.copy(); Sm[i, j] -= eps
        fd = (rince_loss(Sp) - rince_loss(Sm)) / (2 * eps)
        worst = max(worst, abs(fd - dS_an[i, j]))
    # q→0 limit recovers InfoNCE (P − I)
    dS0 = _rince_dS(S0, 1e-6, 1.0, I); pminus = softmax(S0, axis=1) - I
    lim = float(np.abs(dS0 - pminus).max())
    ok = worst < 1e-5 and lim < 1e-3
    if verbose:
        print(f"  [FD-RINCE guard] max|analytic-FD|={worst:.2e}  q→0 vs (P−I)={lim:.2e}  "
              f"{'OK' if ok else '!! RINCE GRADIENT BUG'}", flush=True)
    return ok, worst
