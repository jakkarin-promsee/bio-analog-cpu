#!/usr/bin/env python3
"""
Structural graphify links for experiment PNGs — no vision.

Every figure in this repo is emitted by plot_*.py under an exp folder that already has
experiment-*.md (full context), figs_*/manifest.json, and usually a phase-report embed.
This script creates image nodes + EXTRACTED edges from that parent context only.

Usage (repo root):
    python tools/graphify_link_figures.py
    python tools/graphify_link_figures.py --merge   # merge into graphify-out/.graphify_semantic.json

Output: graphify-out/.graphify_figures_structural.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "graphify-out" / ".graphify_figures_structural.json"
SCAN_ROOTS = [ROOT / "draft5.0" / "src", ROOT / "draft6.0" / "src"]
EMBED_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+\.png)\)", re.I)
FIG_BULLET_RE = re.compile(
    r"^\s*[-*]\s*\*\*([^*]+)\*\*.*?\]\(([^)]*?([^/\\]+\.png))\)", re.I | re.M
)
SAVEFIG_RE = re.compile(r"""savefig\s*\(\s*[^'"]*['"]([^'"]+\.png)['"]""", re.I)


def slug_path(rel: Path) -> str:
    """graphify-style node stem from repo-relative path without extension."""
    parts = []
    for seg in rel.with_suffix("").parts:
        s = seg.lower()
        s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
        if s:
            parts.append(s)
    return "_".join(parts)


def node_id(rel: Path) -> str:
    return slug_path(rel)


def experiment_card_id(exp_dir: Path) -> str | None:
    cards = sorted(exp_dir.glob("experiment-*.md"))
    if not cards:
        return None
    card = cards[0]
    rel = card.relative_to(ROOT)
    # experiment-0.md -> ..._experiment_0_doc (matches semantic chunk convention)
    m = re.search(r"experiment-(\d+)", card.name, re.I)
    if not m:
        return slug_path(rel) + "_doc"
    stem = slug_path(rel.parent / f"experiment_{m.group(1)}")
    return f"{stem}_doc"


def phase_report_path(exp_dir: Path) -> Path | None:
    phase = exp_dir.parent  # phaseN
    for name in ("phase-report.md", f"{phase.name}-report.md", "README.md"):
        p = phase / name
        if p.exists():
            return p
    return None


def caption_from_report(png_rel: Path, report: Path) -> str | None:
    text = report.read_text(encoding="utf-8", errors="replace")
    key = png_rel.as_posix().replace("\\", "/")
    name = png_rel.name
    for alt, href in EMBED_RE.findall(text):
        href_norm = href.replace("\\", "/")
        if href_norm.endswith(name) or key.endswith(href_norm.lstrip("./")):
            return alt.strip()
    return None


def rationale_from_experiment(exp_dir: Path, png_name: str) -> str | None:
    cards = sorted(exp_dir.glob("experiment-*.md"))
    for card in cards:
        text = card.read_text(encoding="utf-8", errors="replace")
        for m in FIG_BULLET_RE.finditer(text):
            if m.group(3).lower() == png_name.lower():
                return f"{m.group(1).strip()} — from {card.name}"
        if png_name in text:
            # fallback: line containing the filename
            for line in text.splitlines():
                if png_name in line and len(line) < 400:
                    return line.strip().lstrip("-* ").strip()
    return None


def plot_script_for(exp_dir: Path, png_name: str) -> Path | None:
    for plot in exp_dir.glob("plot*.py"):
        try:
            src = plot.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in SAVEFIG_RE.finditer(src):
            if Path(m.group(1)).name.lower() == png_name.lower():
                return plot
    return None


def manifest_summary(figs_dir: Path) -> str | None:
    mf = figs_dir / "manifest.json"
    if not mf.exists():
        return None
    try:
        d = json.loads(mf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    bits = []
    if d.get("experiment"):
        bits.append(f"run={d['experiment']}")
    if d.get("task"):
        bits.append(f"task={d['task']}")
    if d.get("results_median"):
        bits.append("medians in manifest")
    return "; ".join(bits) if bits else None


def collect_pngs() -> list[Path]:
    out = []
    for base in SCAN_ROOTS:
        if not base.exists():
            continue
        out.extend(base.rglob("*.png"))
    return sorted(set(out))


def build_fragment() -> dict:
    nodes, edges = [], []
    for png in collect_pngs():
        rel = png.relative_to(ROOT)
        exp_dir = png.parent
        while exp_dir.name.startswith("figs") or exp_dir.name in ("figures", "figs_gate"):
            exp_dir = exp_dir.parent
        nid = node_id(rel)
        abs_src = str(png.resolve())

        parts = []
        cap = None
        report = phase_report_path(exp_dir)
        if report:
            cap = caption_from_report(rel, report)
        rat = rationale_from_experiment(exp_dir, png.name)
        man = manifest_summary(png.parent)
        plot = plot_script_for(exp_dir, png.name)

        if cap:
            parts.append(f"Report embed: {cap}")
        if rat:
            parts.append(rat)
        if man:
            parts.append(man)
        if not parts:
            parts.append(f"Experiment figure emitted under {exp_dir.relative_to(ROOT)}")

        label = cap or png.stem.replace("_", " ")
        nodes.append({
            "id": nid,
            "label": label,
            "file_type": "image",
            "source_file": abs_src,
            "source_location": None,
            "source_url": None,
            "captured_at": None,
            "author": None,
            "contributor": None,
            "rationale": " ".join(parts),
        })

        card_id = experiment_card_id(exp_dir)
        if card_id:
            edges.append({
                "source": nid,
                "target": card_id,
                "relation": "references",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": abs_src,
                "source_location": None,
                "weight": 1.0,
            })

        if report:
            rid = slug_path(report.relative_to(ROOT)) + "_doc"
            edges.append({
                "source": nid,
                "target": rid,
                "relation": "references",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": abs_src,
                "source_location": None,
                "weight": 1.0,
            })

        if plot:
            pid = slug_path(plot.relative_to(ROOT))
            edges.append({
                "source": pid,
                "target": nid,
                "relation": "references",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": str(plot.resolve()),
                "source_location": None,
                "weight": 1.0,
            })

    return {"nodes": nodes, "edges": edges, "hyperedges": [], "input_tokens": 0, "output_tokens": 0}


def merge_into_semantic(fragment: dict) -> None:
    sem_path = ROOT / "graphify-out" / ".graphify_semantic.json"
    if sem_path.exists():
        sem = json.loads(sem_path.read_text(encoding="utf-8"))
    else:
        sem = {"nodes": [], "edges": [], "hyperedges": []}
    seen = {n["id"] for n in sem["nodes"]}
    for n in fragment["nodes"]:
        if n["id"] not in seen:
            sem["nodes"].append(n)
            seen.add(n["id"])
    sem["edges"].extend(fragment["edges"])
    sem_path.write_text(json.dumps(sem, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge", action="store_true", help="Append fragment to .graphify_semantic.json")
    args = ap.parse_args()
    fragment = build_fragment()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fragment, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(fragment['nodes'])} figure nodes, {len(fragment['edges'])} edges -> {OUT.relative_to(ROOT)}")
    if args.merge:
        merge_into_semantic(fragment)
        print("Merged into graphify-out/.graphify_semantic.json (re-run graph build to refresh graph.json)")


if __name__ == "__main__":
    main()
