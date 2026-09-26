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
        "Geometry as the engineered object", "A first tour of canonical geometries",
        "Two directions of design: geometry first and source first", "What makes it hard",
        "Performance inside one spacetime: a preview"]),
    ("part1-foundations", "ch02-lorentzian-geometry", "Lorentzian Geometry for Design", [
        "Causal structure and proper time", "Observers, frames and tetrads",
        "Killing vectors, stationarity and conserved quantities", "Horizons and surface gravity",
        "Congruences, expansion and focusing"]),
    ("part1-foundations", "ch03-three-plus-one", "The 3+1 Split", [
        "Foliations, lapse and shift", "Extrinsic curvature", "The constraints read as demand",
        "Evolution equations and stresses", "Worked examples", "ADM, Komar and Bondi masses"]),
    ("part1-foundations", "ch04-stress-energy-algebra", "Stress-Energy and Its Algebra", [
        "Components and observers", "Hawking--Ellis types and their scope",
        "Type from 3+1 data", "Canonical matter models and their types",
        "Pointwise and nonlinear energy conditions"]),
    ("part1-foundations", "ch05-quantum-fields", "Quantum Fields on Curved Backgrounds", [
        "Renormalized stress and the trace anomaly", "States and vacuum polarization",
        "Horizon temperatures", "The species bound", "Validity limits of semiclassical gravity"]),
    ("part1-foundations", "ch06-energy-bounds", "Energy Conditions and Quantum Bounds", [
        "Quantum violation of pointwise conditions", "Worldline inequalities and quantum interest",
        "Null-contracted bounds", "Smeared and quantum null energy conditions",
        "Averaged null energy", "Exact scopes for design use"]),
    ("part1-foundations", "ch07-global-structure", "Global Structure: Causality, Topology, Chronology", [
        "Causality conditions and time functions", "Topology change", "Topological censorship",
        "Faster-than-light theorems and their definitions", "Chronology and its protection"]),
    ("part1-foundations", "ch08-canonical-geometries", "The Canonical Engineered Geometries", [
        "Static traversable wormholes", "Thin-shell and cut-and-paste wormholes", "Warp metrics",
        "Krasnikov tubes and superluminal subways", "The positive-energy debate, 2021--2026",
        "The warp--wormhole correspondence"]),
    ("part2-specifying", "ch09-geometry-to-demand", "From Geometry to Demand", [
        "The geometry fixes the demand", "The demand ledger",
        "Normalization and absolute scale", "Smoothness class of a prescription"]),
    ("part2-specifying", "ch10-testing-demand", "Testing the Demand", [
        "Complete tensor, all observers", "Time dependence and the blindness of static checks",
        "Transitions to vacuum", "Matrix inequalities and certified bounds between samples",
        "Degenerate tensors", "Type as a match to source families"]),
    ("part2-specifying", "ch11-global-performance", "Global Structure and Performance Claims", [
        "Declaring topology, ends and exterior", "The causality class of a design",
        "Performance inside one spacetime",
        "Coordination and control without superluminal signals"]),
    ("part2-specifying", "ch12-occupants", "Occupants", [
        "Occupant observables", "Computing occupant observables from the metric",
        "Occupant requirements in crewed designs"]),
    ("part2-specifying", "ch13-certifying-demand", "Computing and Certifying the Demand", [
        "Code verification: manufactured solutions and observed order",
        "Solution verification aimed at decisions",
        "Domains, surrogates, reduced models and fitted closures",
        "Solver statuses", "Reference solutions for testing"]),
    ("part3-design-response", "ch14-design-matrices", "Design Matrices", [
        "Design elements and physical channels", "Identity-backed and measured entries",
        "Coupling, decoupling and adjustment order", "Identities before numerics",
        "Zoning and its hazard"]),
    ("part3-design-response", "ch15-lapse", "The Lapse", [
        "Clock, redshift, frames and refractive index",
        "Stress without energy where the shift is uniform",
        "The lapse-only NEC lemma and the Komar balance",
        "Scheduling lapse elements in time", "Measured examples"]),
    ("part3-design-response", "ch16-shift", "The Shift", [
        "Carriage and flat interior regions", "Energy density from shear and vorticity",
        "Momentum and vorticity", "Null energies at shear-layer edges",
        "The shift under a varying lapse", "Adjustment order for lapse and shift"]),
    ("part3-design-response", "ch17-spatial-geometry", "The Spatial Geometry", [
        "Curved slices and the three-curvature channel", "Stretch and conformal factors",
        "Product and warped-product geometries", "The lapse in static spherical geometries",
        "Throats: flare-out cost, tension and topology", "Thin shells and junctions"]),
    ("part3-design-response", "ch18-moving-structures", "Moving Structures", [
        "The pattern frame and Killing energy", "Light surfaces and horizons",
        "Overtaken light and matter", "Front shape and normal speed",
        "Semiclassical response at fronts", "Momentum, steering and radiation"]),
    ("part3-design-response", "ch19-scaling", "Scaling Laws", [
        "Size", "Speed and the steady-lane rescaling",
        "Wall thickness under quantum inequalities", "Shape"]),
    ("part3-design-response", "ch20-strategies", "Strategies and Their Price", [
        "The catalogue", "Where the NEC violation goes", "Class choices"]),
    ("part4-supply", "ch21-supply-problem", "The Supply Problem", [
        "Algebraic range of source families", "Class-level exclusions first", "Absolute scale"]),
    ("part4-supply", "ch22-ordinary-matter", "Ordinary Matter and Classical Fields", [
        "Strength-to-energy ratios and the dominant energy condition",
        "Electromagnetic stresses and confinement", "Strings, sheets and oriented ensembles",
        "Junction stress and charged shells", "Storage limits"]),
    ("part4-supply", "ch23-quantum-sources", "Quantum Sources", [
        "Casimir systems and the mirror's energy", "States with negative energy density",
        "Field counts and constraints no tuning removes",
        "Vacuum polarization and the anomaly as sources",
        "Quantum-sourced wormholes: long and short", "Scope of quantum exclusions"]),
    ("part4-supply", "ch24-nec-violating-fields", "Classical NEC-Violating Fields and Modified Gravity", [
        "Canonical fields and curvature couplings", "Higher-derivative scalars",
        "Stability and no-go results", "Superluminality and ultraviolet completion",
        "Algebraic range", "Curvature sectors of modified gravity"]),
    ("part4-supply", "ch25-net-supply-assemblies", "Net Supply and Assemblies", [
        "NEC-satisfying parts only add to the deficit", "Accounting boundaries and gain chains",
        "Holding costs", "Component tensors on one shared geometry",
        "Interaction contracts, recoil and the complete ledger",
        "Function and physical realization"]),
    ("part4-supply", "ch26-realizability", "Realizability and Screening", [
        "Spending design freedom on sourceability", "Forward checks of simplified designs",
        "Realizability and passivity inside the design loop",
        "A screening sequence with exact scopes"]),
    ("part5-dynamics", "ch27-dynamics", "Dynamics, Back-Reaction and Stability", [
        "Prescribed metrics and solutions", "Evolving warp spacetimes with matter",
        "Semiclassical back-reaction", "Stability of NEC-violating sources and wormholes",
        "Fields on engineered backgrounds"]),
    ("part6-method", "ch28-design-studies", "Design Studies", [
        "Attribution and sensitivity maps", "Matched comparisons",
        "Forks and set-based exploration", "Single-gate distortion",
        "Absolute and relative figures of merit"]),
    ("part6-method", "ch29-credibility", "Credibility and Claim Scope", [
        "Naming results by the check passed", "Multi-axis credibility and readiness",
        "Kinematic and sourcing claims", "Program hazards"]),
    ("part6-method", "ch30-frontier", "The Frontier", [
        "Open sourcing classes", "Dynamics and stability", "Quantum questions",
        "Global questions"]),
]

APPENDICES = [
    ("appendices", "appA-laboratory", "Analogue Systems and Laboratory Negative Energy", [
        "Analogue gravity", "Laboratory negative-energy modalities",
        "Casimir measurements and their readout", "Quantum energy teleportation"]),
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
