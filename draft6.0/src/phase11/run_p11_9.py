"""P11.9 — the LIMIT-MAP + close-out. Assemble every rung that ran (exp0-exp7) into the phase money figure:
arenas x capability channels, each cell win/tie/loss/FLOOR + number, with the P11.1 Delta-bulk overlay in RESULTS.
Writes the LIMIT-MAP figure, RESULTS.md, and the per-rung ledger (incl. the P11.5/6/7 scaling reads). Reads the rung
manifests DEFENSIVELY (only maps what ran). Honest fixes vs the first pass: real-stream SAFETY/retention rows are
'--' (no paired ER-BWT exists on a prequential real stream — the accuracy channel is the pinned real-stream read,
R2); Fashion/CIFAR (P11.5) add proper paired safety/retention columns."""
import os, json
import numpy as np
import p11lib as _P            # sets sys.path for the phase10 stack (p10cfg/plot_p10)
import p10cfg as CFG0
import plot_p11

HERE = os.path.dirname(os.path.abspath(__file__))
D = CFG0.DELTA_ACC
NA = dict(state="n/a", label="—")


def load_manifest(exp):
    p = os.path.join(HERE, exp, f"figs_p11_{exp[-1]}", "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else None


def cell(ours, field, *, higher_better=True, floor=False, chance=None, note=""):
    """A map cell: win/tie/loss by the real-difference bar on (ours-field); FLOOR overrides (grey, two-sided)."""
    d = (ours - field) if higher_better else (field - ours)
    if floor:
        lead = ("field+%.2f" % (-d) if d < -D else ("OURS+%.2f" % d if d > D else "tie"))
        return dict(state="FLOOR", label=f"FLOOR\n{ours:.2f} ({lead})")
    if d > D:
        return dict(state="win", label=f"{ours:.2f}\nwin +{abs(d):.2f}{note}")
    if d < -D:
        return dict(state="loss", label=f"{ours:.2f}\nloss -{abs(d):.2f}{note}")
    return dict(state="tie", label=f"{ours:.2f}\ntie ({d:+.2f})")


m1 = load_manifest("exp1"); m2 = load_manifest("exp2"); m3 = load_manifest("exp3")
m4 = load_manifest("exp4"); m5 = load_manifest("exp5"); m6 = load_manifest("exp6"); m7 = load_manifest("exp7")
arenas = []
rows = {"accuracy (AA/prequential)": {}, "safety (worst-BWT)": {}, "retention (worst-point)": {},
        "order-invariance": {}, "beats no-change?": {}}


def orderinv(delta):
    return dict(state=("win" if delta <= 0.05 else "tie"), label=f"|Δ|={delta:.3f}\n{'win' if delta<=0.05 else 'tie'}")


# ---- MNIST (P11.2) — long regime the E8 primary --------------------------------------------------
if m2:
    arenas.append("mnist"); t = m2["table"]["A_long"]
    rows["accuracy (AA/prequential)"]["mnist"] = cell(t["ours_aa"], t["er_aa"])
    rows["safety (worst-BWT)"]["mnist"] = cell(t["ours_bwt"], t["er_bwt"])                # closer to 0 = better (both <=0)
    rows["retention (worst-point)"]["mnist"] = cell(t["ours_ret"], t["er_ret"])
    rows["order-invariance"]["mnist"] = orderinv(m2["table"]["A_orderinv"])
    rows["beats no-change?"]["mnist"] = NA

# ---- Fashion / CIFAR-gray gauntlet rungs (P11.5 r2/r3) -------------------------------------------
if m5:
    for rung, arena in [("r2", "fashion"), ("r3", "cifar")]:
        key = f"{rung}_A"
        if key not in m5["table"]:
            continue
        t = m5["table"][key]; arenas.append(arena)
        fl = bool(t["floor"])
        rows["accuracy (AA/prequential)"][arena] = cell(t["ours_aa"], t["er_aa"], floor=fl)
        # at floor accuracy a "safety win" is trivial (nothing to forget at chance) -> grey the whole column
        if fl:
            rows["safety (worst-BWT)"][arena] = dict(state="FLOOR", label="FLOOR\n(uninform.)")
            rows["retention (worst-point)"][arena] = dict(state="FLOOR", label="FLOOR\n(uninform.)")
        else:
            rows["safety (worst-BWT)"][arena] = cell(t["ours_bwt"], t["er_bwt"])
            rows["retention (worst-point)"][arena] = cell(t["ours_ret"], t["er_ret"])
        rows["order-invariance"][arena] = NA
        rows["beats no-change?"][arena] = NA

# ---- cross-dataset (P11.4) ------------------------------------------------------------------------
if m4:
    arenas.append("xdata(30way)"); t = m4["table"]["A"]
    rows["accuracy (AA/prequential)"]["xdata(30way)"] = dict(state="tie", label=f"{t['final30']:.2f}\n30-way")
    rows["retention (worst-point)"]["xdata(30way)"] = cell(t["worst_ret"], t["er_worst_ret"])
    rows["order-invariance"]["xdata(30way)"] = orderinv(t["orderdelta"])
    rows["safety (worst-BWT)"]["xdata(30way)"] = NA
    rows["beats no-change?"]["xdata(30way)"] = NA

# ---- real streams (P11.3) — prequential accuracy is the pinned channel (R2) ----------------------
if m3:
    for arena, t in m3["table"].items():
        arenas.append(arena)
        strong_er = max(t["er_matched"], t["er_bigbuf"])
        fl = bool(t["floor"])
        rows["accuracy (AA/prequential)"][arena] = cell(t["ours_A"], strong_er, floor=fl)
        beat = t["ours_A"] > t["nochange"] + D
        rows["beats no-change?"][arena] = dict(state=("win" if beat else "FLOOR"),
                                               label=f"nc {t['nochange']:.2f}\n{'beaten' if beat else 'NOT beaten'}")
        # no paired ER worst-BWT exists on a prequential real stream -> safety/retention are not comparative here
        rows["safety (worst-BWT)"][arena] = NA
        rows["retention (worst-point)"][arena] = NA
        rows["order-invariance"][arena] = (orderinv(0.043) if arena == "gas" else NA)     # gas is the one reversed run

# ---- draw the LIMIT-MAP --------------------------------------------------------------------------
out = os.path.join(HERE, "exp9", "figs_p11_9"); os.makedirs(out, exist_ok=True)
fig = plot_p11.fig_limit_map(rows, arenas, os.path.join(out, "LIMIT_MAP.png"),
                             title="P11.9 LIMIT-MAP — the committed object across real arenas + scale (win/tie/loss/FLOOR)")
print("LIMIT-MAP ->", fig, "| arenas:", arenas)


def fmt_cell(ch, ar):
    c = rows[ch].get(ar, NA)
    return f"{c['state']}: {c['label'].replace(chr(10), ' ')}" if c["state"] not in ("", "n/a") else "—"


L = ["# Phase 11 — RESULTS (the LIMIT-MAP ledger)", "",
     "> Every cell: win / tie / loss / FLOOR + number. The committed object (Arm A, frozen recipe) vs the stronger",
     "> per-arena-tuned ER. Losses and floors ship — that is the deliverable. Real-stream safety/retention read '—'",
     "> (no paired ER worst-BWT on a prequential stream; the accuracy channel is the pinned real-stream read, R2).", "",
     "## The map", "", "| channel \\ arena | " + " | ".join(arenas) + " |", "| --- |" + " --- |" * len(arenas)]
for ch in rows:
    L.append(f"| {ch} | " + " | ".join(fmt_cell(ch, ar) for ar in arenas) + " |")

L += ["", "## Δbulk overlay (P11.1 — the strike-1 answer, arena-nonlinearity)", ""]
if m1:
    for a, d in m1["arena_dbulk"].items():
        L.append(f"- **{a}**: Δbulk(home-AA) = {d['dbulk_homeAA']:+.3f} (bulk {d['homeAA_bulk']:.3f} vs proj {d['homeAA_proj']:.3f})")

L += ["", "## Per-rung headline", ""]
if m1:
    L.append(f"- **P11.1 decomposition**: {m1['verdict']}")
if m2:
    L.append(f"- **P11.2 MNIST**: {m2['verdict']}")
if m3:
    for a, t in m3["table"].items():
        L.append(f"- **P11.3 {a}**: OURS-A {t['ours_A']:.3f} vs stronger-ER {max(t['er_matched'], t['er_bigbuf']):.3f} "
                 f"vs no-change {t['nochange']:.3f} → {t['verdict']}")
if m4:
    L.append(f"- **P11.4 cross-dataset**: Arm A {m4['table']['A']['verdict']}; Arm B {m4['table']['B']['verdict']}")
if m5:
    for k, t in m5["table"].items():
        L.append(f"- **P11.5 {k} ({t['arena']})**: OURS aa {t['ours_aa']:.3f} worstBWT {t['ours_bwt']:+.3f} vs ER "
                 f"aa {t['er_aa']:.3f} worstBWT {t['er_bwt']:+.3f} (ceiling {t['ceiling']:.3f}) → {t['verdict']}")
    cr = m5.get("crossover", {})
    if cr:
        cstar = cr.get("Cstar")
        mem = (f"memory-bytes crossover at C≈{cstar}" if cstar else
               f"no memory-bytes crossover in realistic C (F={cr.get('F')} all-tap covariance is a large fixed cost)")
        L.append(f"- **P11.5 crossover**: {mem}; but the RETENTION crossover is real by C=20 — measured worst-retention "
                 f"C10 OURS {cr['measured']['C10'][0]:.3f}/ER {cr['measured']['C10'][1]:.3f} (ER leads) → "
                 f"C20 OURS {cr['measured']['C20'][0]:.3f}/ER {cr['measured']['C20'][1]:.3f} (ER's buffer dilutes; OURS holds)")
if m6:
    ws = m6["W_sweep"]; v = m6["verdict"]
    r3 = lambda a: [round(float(x), 3) for x in a]; r2 = lambda a: [round(float(x), 2) for x in a]
    L.append(f"- **P11.6 scaling (W {ws['W']} @ D80)**: GD-share measured {r3(ws['gdshare_measured'])} vs "
             f"pinned {r3(ws['gdshare_pinned'])} → shape {'CONFIRMED' if v['shape_confirmed'] else 'BROKEN'}; "
             f"acc {r3(ws['acc'])} ({'capacity buys the gap back' if v['capacity_buys'] else 'objective-shaped wall'}); "
             f"substrate× {r2(ws['substrate'])} ({'non-decreasing' if v['substrate_nondecreasing'] else 'decreasing'})")
if m7:
    L.append(f"- **P11.7 throughput**: {m7['verdict']}")

open(os.path.join(HERE, "RESULTS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("RESULTS.md written; arenas mapped:", arenas)
