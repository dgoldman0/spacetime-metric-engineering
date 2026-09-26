"""Write chapter and appendix skeleton files for the book scaffold.

Each skeleton holds the chapter title and label, an empty chapter-plan box,
the section headings of 05_STRUCTURE.md with labels, and an exercises stub.
Existing files are left untouched unless --force is given, so hand-written
plans are never overwritten.
"""
import re
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent / "book"

CHAPTERS = [
    ("part1-foundations", "ch01-inverse-problem", "Spacetime Engineering: The Inverse Problem", [
        "Geometry as the engineered object", "A first tour of five canonical geometries",
        "The design loop", "What makes it hard", "Performance inside one spacetime"]),
    ("part1-foundations", "ch02-lorentzian-geometry", "Lorentzian Geometry for Design", [
        "Causal structure and proper time", "Observers, frames and tetrads",
        "Killing vectors, stationarity and conserved quantities", "Horizons and surface gravity",
        "Congruences, expansion and focusing", "Optical geometry of static metrics"]),
    ("part1-foundations", "ch03-three-plus-one", "The 3+1 Split", [
        "Foliations, lapse and shift", "Extrinsic curvature", "The constraints read as demand",
        "Evolution equations and stresses", "Worked examples", "ADM and Komar masses"]),
    ("part1-foundations", "ch04-stress-energy-algebra", "Stress-Energy and Its Algebra", [
        "Components and observers", "Hawking--Ellis types and their scope",
        "Type from 3+1 data", "Canonical matter models and their types",
        "Pointwise energy conditions"]),
    ("part1-foundations", "ch05-energy-bounds", "Energy Conditions and Quantum Bounds", [
        "Quantum violation of pointwise conditions", "Worldline inequalities and quantum interest",
        "Null-contracted bounds", "Smeared and quantum null energy conditions",
        "Averaged null energy", "Exact scopes for design use"]),
    ("part1-foundations", "ch06-global-structure", "Global Structure: Topology, Causality, Chronology", [
        "Topology change", "Topological censorship", "Causality conditions and time functions",
        "Faster-than-light theorems and their definitions", "Chronology and its protection"]),
    ("part1-foundations", "ch07-semiclassical", "Semiclassical Response", [
        "Renormalized stress and the trace anomaly", "Vacuum polarization and quantum states",
        "Horizon temperatures", "The species bound", "Instability of superluminal fronts",
        "Validity limits"]),
    ("part1-foundations", "ch08-canonical-geometries", "The Canonical Engineered Geometries", [
        "Traversable wormholes", "Warp metrics", "Krasnikov tubes",
        "The positive-energy debate, 2021--2026", "The warp--wormhole correspondence",
        "Horizons, swept matter and control"]),
    ("part2-specifying", "ch09-geometry-to-demand", "From Geometry to Demand", [
        "The geometry fixes the demand", "The demand ledger", "Functional zoning",
        "Normalization and absolute scale"]),
    ("part2-specifying", "ch10-testing-demand", "Testing the Demand", [
        "Complete tensor, all observers", "Time dependence and the blindness of static checks",
        "Transitions to vacuum", "Matrix inequalities and certified bounds between samples",
        "Degenerate tensors", "Type as a match to source families"]),
    ("part2-specifying", "ch11-global-performance", "Global Structure and Performance Claims", [
        "Declaring topology, ends and exterior", "The causality class of a design",
        "Performance inside one spacetime", "Coordination without superluminal signals"]),
    ("part2-specifying", "ch12-occupants", "Occupants", [
        "Occupant observables", "Flat compartments", "Choosing the occupant clock",
        "Occupants under single-gate optimization"]),
    ("part2-specifying", "ch13-certifying-demand", "Computing and Certifying the Demand", [
        "Code verification: manufactured solutions and observed order",
        "Solution verification aimed at decisions", "Domains, surrogates and reduced models",
        "Solver statuses", "Reference solutions for testing"]),
    ("part3-design-response", "ch14-design-matrices", "Design Matrices", [
        "Design elements and physical channels", "Identity-backed and measured entries",
        "Coupling, decoupling and adjustment order", "Identities before numerics",
        "Zoning and its hazard"]),
    ("part3-design-response", "ch15-lapse", "The Lapse", [
        "Clock, redshift and refractive index", "Stress without energy where the shift is uniform",
        "The lapse-only NEC lemma and the Komar balance", "The lapse in static spherical geometries",
        "Time staging", "Measured examples"]),
    ("part3-design-response", "ch16-shift", "The Shift", [
        "Carriage", "Energy density from shear and vorticity", "Momentum and vorticity",
        "Type IV at shear-layer edges", "Speed as a lapse contrast", "Energy scaling with speed"]),
    ("part3-design-response", "ch17-spatial-geometry", "The Spatial Geometry", [
        "Curved slices and the three-curvature channel", "Stretch and conformal factors",
        "Spherical warped products", "Throats: flare-out cost, tension and topology",
        "Thin shells and junctions"]),
    ("part3-design-response", "ch18-coupling", "Coupling the Elements", [
        "The complete tensor of the flat-slice lapse--shift class",
        "Lapse under a varying shift", "Product regions", "Adjustment order",
        "The combined design matrix"]),
    ("part3-design-response", "ch19-moving-structures", "Moving Structures", [
        "The pattern frame and Killing energy", "Light surfaces and horizons",
        "Overtaken light and matter", "Front design", "Semiclassical response at fronts",
        "Momentum and steering"]),
    ("part3-design-response", "ch20-scaling", "Scaling Laws", [
        "Size", "Speed", "Wall thickness under quantum inequalities", "Shape"]),
    ("part3-design-response", "ch21-strategies", "Strategies and Their Price", [
        "The catalogue", "Where the NEC violation goes", "Class choices"]),
    ("part4-supply", "ch22-supply-problem", "The Supply Problem", [
        "Algebraic range of source families", "Class-level exclusions first",
        "Absolute scale", "A screening sequence with exact scopes"]),
    ("part4-supply", "ch23-ordinary-matter", "Ordinary Matter under Relativistic Stress", [
        "Strength-to-energy ratios", "Electromagnetic stresses and confinement",
        "Strings, sheets and oriented ensembles", "Junction stress and charged shells",
        "Storage limits"]),
    ("part4-supply", "ch24-quantum-sources", "Quantum Sources", [
        "Casimir systems and the mirror's energy", "States with negative energy density",
        "Field counts and the species bound", "Vacuum polarization and the anomaly",
        "Scope of quantum exclusions"]),
    ("part4-supply", "ch25-nec-violating-fields", "Classical NEC-Violating Fields", [
        "Canonical fields and curvature couplings", "Higher-derivative scalars",
        "Stability and no-go results", "Superluminality and ultraviolet completion",
        "Algebraic range"]),
    ("part4-supply", "ch26-net-supply", "Net Supply", [
        "NEC-satisfying parts only add to the deficit",
        "Accounting boundaries and gain chains", "Holding costs"]),
    ("part4-supply", "ch27-assemblies", "Assemblies", [
        "Component tensors on one shared geometry", "Interaction contracts and recoil",
        "Function and physical realization", "Momentum exchange by radiation"]),
    ("part4-supply", "ch28-realizability", "Realizability as a Design Objective", [
        "Spending design freedom on sourceability", "Forward checks of simplified designs",
        "Realizability inside the design loop"]),
    ("part5-dynamics", "ch29-dynamics", "Dynamics, Back-Reaction and Stability", [
        "Prescribed metrics and solutions", "Evolving warp spacetimes with matter",
        "Semiclassical back-reaction", "Stability of NEC-violating sources",
        "Fields on engineered backgrounds"]),
    ("part6-method", "ch30-design-studies", "Design Studies", [
        "Attribution and sensitivity maps", "Matched comparisons",
        "Forks and set-based exploration", "Single-gate distortion",
        "Absolute and relative figures of merit"]),
    ("part6-method", "ch31-credibility", "Credibility and Claim Scope", [
        "Naming results by the check passed", "Multi-axis credibility and readiness",
        "Kinematic and sourcing claims", "Program hazards"]),
    ("part6-method", "ch32-frontier", "The Frontier", [
        "Open sourcing classes", "Dynamics and stability", "Quantum questions",
        "Global questions"]),
]

APPENDICES = [
    ("appendices", "appA-laboratory", "Laboratory Analogues and Experiments", [
        "Analogue gravity", "Laboratory negative-energy modalities",
        "Casimir experiments and their readout", "Quantum energy teleportation"]),
    ("appendices", "appB-computational", "Computational Companion", [
        "General modules", "Worked notebooks", "Reproducing the book's checks"]),
    ("appendices", "appC-units", "Units, Scales and Conversions", [
        "Geometric and Planck units", "Converting a demand to SI units", "Reference scales"]),
    ("appendices", "appD-reference-solutions", "Reference Solutions and Their Stress Tensors", [
        "Schwarzschild in Painlev\\'e--Gullstrand coordinates", "FRW cosmologies",
        "The Ellis and Morris--Thorne wormholes", "Alcubierre and Nat\\'ario metrics"]),
]


def slug(text, limit=5):
    text = re.sub(r"\\['`^\"~]", "", text)
    words = re.findall(r"[a-z0-9]+", text.lower())
    stop = {"the", "and", "of", "a", "an", "its", "their", "for", "to", "in", "as", "with", "on"}
    words = [w for w in words if w not in stop] or words
    return "-".join(words[:limit])


def chapter_file(part, stem, title, sections, appendix=False):
    key = re.sub(r"^(ch\d\d|app[A-D])-", "", stem)
    kind = "app" if appendix else "ch"
    lines = [
        "% !TEX root = ../main.tex",
        f"\\chapter{{{title}}}\\label{{{kind}:{key}}}",
        "",
        "\\begin{chapterplan}",
        "\\planitem{Status} Skeleton; plan to be written from the evidence packet.",
        "\\end{chapterplan}",
        "",
    ]
    for sec in sections:
        lines += [
            f"\\section{{{sec}}}\\label{{sec:{key}:{slug(sec)}}}",
            "",
            "\\begin{plan}",
            "To be written.",
            "\\end{plan}",
            "",
        ]
    if not appendix:
        lines += ["\\begin{exercises}", "\\item To be written.", "\\end{exercises}", ""]
    return "\n".join(lines)


def main():
    force = "--force" in sys.argv
    written = skipped = 0
    for group, appendix in ((CHAPTERS, False), (APPENDICES, True)):
        for part, stem, title, sections in group:
            path = BOOK / part / f"{stem}.tex"
            if path.exists() and not force:
                skipped += 1
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(chapter_file(part, stem, title, sections, appendix))
            written += 1
    print(f"written {written}, kept {skipped}")


if __name__ == "__main__":
    main()
