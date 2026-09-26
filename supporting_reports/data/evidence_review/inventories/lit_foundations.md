# Foundations and Verification Canon for a Textbook on Spacetime (Metric) Engineering

> **Errata (audit 2026-09-26, `../audit_synthesis.md` §5).**
> - 'Results commonly overstated' item 9 and the closing-table row 'type IV is a test-field effect': Martín-Moruno–Visser 2021 force Type I with back-reaction in static spacetimes (outer domain and horizons), on horizons and axes of stationary axisymmetric spacetimes, on bifurcate Killing horizons and in some Bianchi cosmologies. The back-reacted evaporating (Unruh) case is open (audit §1.9).


Compiled 2026-09-26. Every entry below was checked against a record fetched on that date: an arXiv abstract page, a publisher abstract page, a publisher catalogue page, or (for entries marked **PARTIAL** or **UNVERIFIED**) citation metadata only. The textbook codifies the field's established results; the canon is organized by discipline topic.

## How the items were checked

- **arXiv items.** Each abstract page `https://arxiv.org/abs/<id>` was downloaded and parsed for title, authors, the full abstract, comments, journal reference, related DOI and the complete submission history. The parsed pages are stored verbatim in `lit_foundations_evidence/arxiv_abstract_pages_parsed_2026-09-26.txt`, 120 records in all. Two of those records came from wrong IDs, arXiv:0911.3380 and gr-qc/9903038, and are excluded from the canon.
- **Version pinning.** Each arXiv citation gives the latest version at fetch time, for example `arXiv:2003.01815v2 (2020-06-05)`. Cite that exact version string in the book.
- **Full-text checks.** For the results most prone to overstatement, the PDF was converted with `pdftotext` and the relevant theorem statements were read. These are Fewster–Roman 2003, Friedman–Schleich–Witt 1993, Graham–Olum 2007, Faulkner et al. 2016, Hartman et al. 2017, Freivogel–Krommydas 2018, Ford–Roman 1997, Kontou–Sanders 2020 and Martín-Moruno–Visser 2021. The extracted texts sit in `lit_foundations_evidence/`. Tags of the form "(text §/eq.)" mark claims read in the body of a paper.
- **Pre-arXiv papers.** Publisher abstract pages were read through WebFetch (APS, Springer). Citation metadata comes from the Crossref record for the DOI. Where only metadata could be retrieved, the entry is marked **PARTIAL (metadata only)**. Its content claim is then unverified from the primary source.
- **Books.** These were checked against publisher pages (Springer and University of Chicago Press pages give the table of contents), Crossref DOI records or the Open Library ISBN catalogue. The extent of the check is stated for each book.
- **Status labels.**
  - **Theorem:** a rigorous proof under stated hypotheses.
  - **Proof (physics-level):** a general argument that its authors call a proof, with continuum or regularity assumptions stated.
  - **Derivation:** an explicit calculation or argument within a model, or one that is conditional on an assumption.
  - **Numerical:** a computed result.
  - **Conjecture/Proposal.**
  - **Review.**

---

## Area 1. Energy conditions and their classification

**1.1 Kontou & Sanders (2020). Review.**
- **Citation:** E.-A. Kontou, K. Sanders, "Energy conditions in general relativity and quantum field theory", *Class. Quantum Grav.* **37**, 193001 (2020). arXiv:2003.01815v2 (2020-06-05; v1 2020-03-03). DOI 10.1088/1361-6382/ab8fcf.
- **Result:** Quoted from the abstract: "all pointwise energy conditions are systematically violated by quantum fields and also by some rather simple classical fields". QEIs and averaged conditions "have a larger range of validity". The achronal ANEC "is expected to be a universal property of the dynamics of all gravitating physical matter".
- **Table 3 of the review (text read):**
  - A state-independent QWEI, QNEI (along timelike worldlines) and QSEI hold for all Hadamard states of the massless minimally coupled Klein–Gordon field.
  - The massive minimally coupled field has a state-independent QWEI and QNEI. Its QSEI is state-dependent only.
  - The non-minimally coupled Klein–Gordon field (ξ ≠ 0) admits **only state-dependent** QEIs.
  - Maxwell/Proca and Dirac fields have a QWEI. Their QNEI and QSEI are open.
  - 2D unitary CFTs have a QWEI and a QNEI.
- **The review's two formulations of AANEC validity (text §4.3):**
  - (i) In Minkowski space, ANEC holds for any reasonable QFT whose stress tensor generates translations.
  - (ii) On-shell configurations can violate AANEC only over Planck-scale transverse distances.
  - Graham–Olum's self-consistent form is labelled a conjecture.
- **Status:** Review. It is the reference map for the whole of Areas 1–3.
- **Anchors:** Chapter on energy conditions; the "what holds, where" master table.

**1.2 Curiel (2017). Review / conceptual analysis.**
- **Citation:** E. Curiel, "A Primer on Energy Conditions", in *Towards a Theory of Spacetime Theories*, eds. D. Lehmkuhl, G. Schiemann, E. Scholz, Einstein Studies (Birkhäuser, 2017), ch. 3, pp. 43–104. arXiv:1405.0403v1 (2014-04-30). DOI 10.1007/978-1-4939-3210-8_3.
- **Result:** A detailed technical and conceptual analysis of "all the standard conditions used in physics today". It argues that there is "no clear understanding" of their theoretical or epistemic status.
- **Status:** Review/philosophy of physics.
- **Anchors:** Opening chapter on the logical role of energy conditions as hypotheses.

**1.3 Martín-Moruno & Visser, "Essential core" (2018). Derivation.**
- **Citation:** P. Martín-Moruno, M. Visser, "Essential core of the Hawking–Ellis types", *Class. Quantum Grav.* **35**, 125003 (2018). arXiv:1802.00865v2 (2018-05-11). DOI 10.1088/1361-6382/aac147.
- **Result:** Subtracting type I pieces isolates the cores II₀, III₀ and IV₀. Types I and II₀ have simple classical interpretations. "type IV₀ is known to arise semi-classically". III₀ "has neither a simple classical interpretation, nor even a simple semi-classical interpretation". Under perturbation, "types II and III are definitively unstable, whereas types I and IV are stable".
- **Status:** Derivation (algebraic classification plus a perturbative stability argument).
- **Scope:** The classification is algebraic and pointwise.
- **Anchors:** The Hawking–Ellis (Segre–Plebański) classification as a diagnostic for the stress-energy a designed metric demands.

**1.4 Martín-Moruno & Visser, type III geometry (2018). Derivation with constructed examples.**
- **Citation:** "Hawking–Ellis type III spacetime geometry", *Class. Quantum Grav.* **35**, 185004 (2018). arXiv:1806.02094v1 (2018-06-06). DOI 10.1088/1361-6382/aad473.
- **Result:** Type III "is incompatible with either planar or spherical symmetry". The paper exhibits "several (somewhat unnatural) spacetime geometries with a type III Einstein tensor" and "an explicit but somewhat odd Lagrangian model" in Minkowski space.
- **Status:** Derivation (constructed examples).
- **Anchors:** Symmetry constraints on source type. This bears directly on low-symmetry engineered metrics.

**1.5 Martín-Moruno & Visser, "Ugly Duckling" (2019/2020). Derivation.**
- **Citation:** "The type III stress-energy tensor: Ugly Duckling of the Hawking–Ellis classification", *Class. Quantum Grav.* **37**, 015013 (online 2019-12-06). arXiv:1907.01269v3 (2019-11-13). DOI 10.1088/1361-6382/ab56f6.
- **Result:** Generalizes the gyraton geometries. It gives the first consistent classical bosonic Lagrangian for type III₀, extending Griffiths' massless Weyl spinor work.
- **Status:** Derivation.
- **Anchors:** Same as 1.4.

**1.6 Martín-Moruno & Visser, test fields versus back-reaction (2021). Derivation (general results from symmetry).**
- **Citation:** "Hawking–Ellis classification of stress-energy: test-fields versus back-reaction", *Phys. Rev. D* **103**, 124003 (2021). arXiv:2102.13551v2 (2021-03-05). DOI 10.1103/PhysRevD.103.124003.
- **Test fields:** Type IV arises readily from vacuum polarization. The abstract's example is the Unruh vacuum for a massless scalar on Schwarzschild.
- **With Einstein back-reaction, type I is forced in each of these cases:**
  - (1) any static spacetime, in the domain of outer communication and on any horizon;
  - (2) any stationary axisymmetric spacetime, on any horizon;
  - (3) any Killing horizon extendable to a bifurcation 2-surface;
  - (4) the axis of any stationary axisymmetric spacetime;
  - (5) all Bianchi I cosmologies, all FLRW cosmologies and all single-mode Bianchi cosmologies.
- **Text §2 (read):**
  - Roman (1986) first argued for type IV near the apparent horizon of an evaporating black hole.
  - Abdolrahimi, Page & Tzounis (item 4.14) showed that the massless conformal scalar in the Unruh state "is Type IV everywhere outside the horizon".
  - In (1+1) dimensions, their Eq. (B.5) gives Γ = (ρ+p)² − 4f² ∝ (1−3z²)(4−3z²)/(1−z), with z = 2m/r. Working from that equation, the exterior is type IV for 2m < r < 2√3·m and type I for r ≥ 2√3·m. The interval statement itself extracted garbled from the PDF, so this reading is derived from Eq. (B.5).
- **Status:** Derivation (general results from symmetry).
- **Scope:** Type IV is a *test-field* phenomenon. Back-reaction restores type I in highly symmetric settings.
- **Anchors:** Semiclassical source typing; the cost of dropping symmetry.

**1.7 Martín-Moruno & Visser, classical and semi-classical energy conditions (2017). Review chapter.**
- **Citation:** "Classical and semi-classical energy conditions", arXiv:1702.05915v3 (2017-03-29). Published as a chapter of Lobo (ed.) 2017, pp. 193–213 (Springer table of contents verified, item 7.2).
- **Result:** Standard energy conditions are mostly linear in T and tied to geodesic focusing, and semiclassical effects violate them. Non-linear conditions behave better semiclassically "at the cost of a less direct applicability to geodesic focussing".
- **Status:** Review.
- **Anchors:** Non-linear energy conditions.

**1.8 Martín-Moruno & Visser, semiclassical energy conditions for vacuum states (2013). Proposals with examples.**
- **Citation:** "Semiclassical energy conditions for quantum vacuum states", *JHEP* **09** (2013) 050. arXiv:1306.2076v3 (2013-09-12). DOI 10.1007/JHEP09(2013)050.
- **Result:** Introduces the flux (FEC), trace-of-square (TOSEC) and determinant (DETEC) energy conditions. These behave "much better than the classical linear energy conditions" under semiclassical effects.
- **Status:** Proposals, tested on examples.
- **Anchors:** Non-linear energy conditions.

**1.9 Barceló & Visser (2002). Essay/review.**
- **Citation:** C. Barceló, M. Visser, "Twilight for the energy conditions?", *Int. J. Mod. Phys. D* **11**, 1553–1560 (2002). arXiv:gr-qc/0205066v1 (2002-05-16). DOI 10.1142/S0218271802002888. Gravity Research Foundation honourable mention.
- **Title correction:** The exact title is "Twilight **for** the energy conditions?".
- **Result:** There are "serious problems of deep and fundamental principle at the semi-classical level", and certain classical systems "exhibit seriously pathological behaviour".
- **Status:** Essay/review.
- **Anchors:** History and motivation.

**1.10 Banerjee, Faraoni, Vanderwee & Giusti (2023). Derivation.**
- **Citation:** "Realisations of type III stress-energy tensors of the Hawking–Ellis classification in scalar-tensor gravity", arXiv:2307.13846v2 (2023-10-03). The comments say "to appear in Phys. Rev. D"; the journal reference is **UNVERIFIED**.
- **Result:** Gives a class of type III realisations of *effective* stress-energy tensors in first-generation scalar-tensor and Horndeski gravity.
- **Status:** Derivation.
- **Anchors:** Modified-gravity sources can reach source types that Einstein-frame matter struggles to reach. See also 8.20.

**1.11 Epstein, Glaser & Jaffe (1965). Theorem.**
- **Citation:** H. Epstein, V. Glaser, A. Jaffe, "Nonpositivity of the energy density in quantized field theories", *Il Nuovo Cimento* **36**, 1016–1022 (1965). DOI 10.1007/BF02749799. The Springer abstract was read.
- **Result:** Quoted from the abstract: "a positive definite local energy density is incompatible with the usual postulates of local field theory. The question whether it can be bounded below is briefly discussed but not solved."
- **Status:** Theorem (Wightman framework).
- **Anchors:** Why pointwise conditions fail for every QFT. This is the starting point of the QEI programme.

**1.12 Hawking & Ellis (1973). Monograph.**
- **Citation:** S. W. Hawking, G. F. R. Ellis, *The Large Scale Structure of Space-Time* (Cambridge University Press, 1973). DOI 10.1017/CBO9780511524646.
- **PARTIAL (metadata only):** The content (energy conditions, types I–IV) was not re-read in this pass.
- **Anchors:** Canonical definitions.

---

## Area 2. Quantum inequalities (quantum energy inequalities)

**2.1 Ford (1978). PARTIAL (metadata only).**
- **Citation:** L. H. Ford, "Quantum coherence effects and the second law of thermodynamics", *Proc. R. Soc. Lond. A* **364**, 227–236 (1978). DOI 10.1098/rspa.1978.0197.
- **Check:** Crossref metadata only; the publisher page returned 403. Fewster's lecture notes (2.17) identify it as "the original pioneering work of Ford in 1978".
- **Anchors:** History of QEIs.

**2.2 Ford & Roman (1995). Derivation (free field).**
- **Citation:** L. H. Ford, T. A. Roman, "Averaged energy conditions and quantum inequalities", *Phys. Rev. D* **51**, 4277–4286 (1995). arXiv:gr-qc/9410043v1 (1994-10-29). DOI 10.1103/PhysRevD.51.4277.
- **Result:** For free massless scalars, the paper derives:
  - QIs in 2D compactified Minkowski;
  - QIs along timelike and null geodesics that reduce to AWEC and ANEC in 2D Minkowski;
  - a 4D inertial bound: "any inertial observer in flat spacetime cannot see an arbitrarily large negative energy density which lasts for an arbitrarily long period of time".
- **Status:** Derivation for the free field. Rigorous generalizations followed in 2.12–2.14.
- **Anchors:** The QI concept; the 2D null QI.

**2.3 Ford & Roman (1997). Derivation.**
- **Citation:** "Restrictions on negative energy density in flat spacetime", *Phys. Rev. D* **55**, 2082–2089 (1997). arXiv:gr-qc/9607003v2 (1997-01-24). DOI 10.1103/PhysRevD.55.2082.
- **Result (text eq. 1 and eq. 48):** For the free massless scalar in 4D Minkowski, with Lorentzian sampling of width t₀ and ħ = c = 1:
  - ρ̂ ≡ (t₀/π)∫⟨T₀₀⟩dt/(t²+t₀²) ≥ −3/(32π²t₀⁴);
  - the electromagnetic field gives −3/(16π²t₀⁴), which is two polarizations times the scalar bound.
- **Also covered:** Massive scalar in 2D and 4D.
- **Status:** Derivation.
- **Anchors:** Worked QI formulas.

**2.4 Ford & Roman (1996), wormholes. Derivation, conditional on a locality assumption.**
- **Citation:** "Quantum field theory constrains traversable wormhole geometries", *Phys. Rev. D* **53**, 5496–5507 (1996). arXiv:gr-qc/9510071v1 (1995-10-31). DOI 10.1103/PhysRevD.53.5496.
- **Assumption:** The flat-space QI "should hold in regions small compared to the minimum local characteristic radius of curvature or the distance to any boundaries".
- **Result:** A static traversable wormhole must either be "only a little larger than Planck size" or have "a large discrepancy in the length scales". In the second case the negative energy is "concentrated in a thin band many orders of magnitude smaller than the throat size".
- **Status:** Derivation, conditional on the locality assumption.
- **Anchors:** Applying QIs to designed geometries; the template for a QI audit of any engineered metric.

**2.5 Ford & Roman (1996), evaporating black holes. Derivation.**
- **Citation:** "Averaged energy conditions and evaporating black holes", *Phys. Rev. D* **53**, 1988 (1996). arXiv:gr-qc/9506052v2 (1995-12-12). DOI 10.1103/PhysRevD.53.1988.
- **Result:** Examines AWEC and ANEC over half-geodesics in 2D and 4D evaporating black holes. "In all cases where these conditions fail, there appear to be quantum inequalities which bound the magnitude and extent of the negative energy."
- **Status:** Derivation.
- **Anchors:** Averaged conditions near horizons.

**2.6 Pfenning & Ford (1997), warp drive. Derivation, conditional on the flat-QI assumption.**
- **Citation:** "The unphysical nature of 'Warp Drive'", *Class. Quantum Grav.* **14**, 1743–1751 (1997). arXiv:gr-qc/9702026v3 (2001-03-15; this version corrects a sign in Eq. 3). DOI 10.1088/0264-9381/14/7/011.
- **Result:** Applying the QI to Alcubierre's metric gives a "bubble wall thickness … on the order of only a few hundred Planck lengths". The total integrated energy for such walls is "physically unattainable".
- **Status:** Derivation, conditional on the flat-QI assumption.
- **Anchors:** A worked QI audit of an engineered metric.

**2.7 Pfenning (1998), dissertation. Derivation, extended in a thesis.**
- **Citation:** M. J. Pfenning (arXiv lists L. H. Ford as co-author), "Quantum Inequality Restrictions on Negative Energy Densities in Curved Spacetimes", doctoral dissertation, arXiv:gr-qc/9805037v1 (1998-05-11).
- **Result:** Derives QIs in *static* curved spacetimes. In the short-sampling limit "the QI … reduces to the flat space form with subdominant correction terms which depend on the spacetime geometry". Applied to Alcubierre, the total negative energy "exceeds the total mass of the visible universe by a hundred billion times".
- **Journal version:** The companion PRD paper was not fetched and is **UNVERIFIED**.
- **Status:** Derivation (thesis).
- **Anchors:** The curvature-corrected QI, justifying 2.4 and 2.6 in static cases.

**2.8 Ford & Roman (1999), quantum interest. Theorem for the model.**
- **Citation:** "The quantum interest conjecture", *Phys. Rev. D* **60**, 104018 (1999). arXiv:gr-qc/9901074v1 (1999-01-26). DOI 10.1103/PhysRevD.60.104018.
- **Result:** A negative δ-pulse must be overcompensated by a positive pulse, by an amount that increases monotonically with pulse separation. This is proved for massless scalars in flat 2D and 4D and "implied by the quantum inequalities".
- **Status:** Theorem for the model (δ-pulse pairs).
- **Anchors:** Quantum interest, and the scheduling cost of negative energy for any design that sequences negative-energy pulses in time.

**2.9 Fewster & Teo (2000). Theorem for the models.**
- **Citation:** C. J. Fewster, E. Teo, "Quantum inequalities and 'quantum interest' as eigenvalue problems", *Phys. Rev. D* **61**, 084012 (2000). arXiv:gr-qc/9908073v2 (2000-01-11). DOI 10.1103/PhysRevD.61.084012.
- **Result:** QIs for massless scalars in even-dimensional Minkowski space become the positivity of a Schrödinger-type operator. The paper gives optimal quantum-interest bounds. Quoted from the abstract: "in four dimensions — it is impossible for a positive delta-function pulse of any magnitude to compensate for a negative delta-function pulse, no matter how close together they occur."
- **Status:** Theorem for the models.
- **Anchors:** Quantum interest; the eigenvalue method.

**2.10 Teo & Wong (2002). Theorem (2D).**
- **Citation:** E. Teo, K. F. Wong, "Quantum interest in two dimensions", *Phys. Rev. D* **66**, 064007 (2002). arXiv:gr-qc/0206066v2 (2002-07-23). DOI 10.1103/PhysRevD.66.064007.
- **Result:** A proof of the quantum interest conjecture for massless scalars in 2D, "valid for general energy distributions".
- **Status:** Theorem (2D).

**2.11 Flanagan (1997). Theorem (2D massless).**
- **Citation:** É. É. Flanagan, "Quantum inequalities in two dimensional Minkowski spacetime", *Phys. Rev. D* **56**, 4922–4926 (1997). arXiv:gr-qc/9706006v2 (1997-07-16). DOI 10.1103/PhysRevD.56.4922.
- **Result:** The optimal 2D lower bound for arbitrary smooth positive weights. It differs by a factor of three from Ford–Roman's bound for their sampling function.
- **Status:** Theorem (2D massless).

**2.12 Fewster & Eveson (1998). Theorem.**
- **Citation:** C. J. Fewster, S. P. Eveson, "Bounds on negative energy densities in flat spacetime", *Phys. Rev. D* **58**, 084010 (1998). arXiv:gr-qc/9805024v2 (1998-07-08). DOI 10.1103/PhysRevD.58.084010.
- **Result:** QIs in d-dimensional Minkowski space (d ≥ 2) for the free real scalar of mass m ≥ 0. They hold for smooth, even, non-negative sampling functions that are compactly supported or rapidly decaying.
- **Status:** Theorem.

**2.13 Fewster (2000), general worldline QI. Theorem (microlocal analysis).**
- **Citation:** C. J. Fewster, "A general worldline quantum inequality", *Class. Quantum Grav.* **17**, 1897–1911 (2000). arXiv:gr-qc/9910060v2 (2000-02-21). DOI 10.1088/0264-9381/17/9/302.
- **Result:** A worldline QI for the real linear scalar field on an *arbitrary globally hyperbolic spacetime*. It holds for any smooth timelike trajectory, any smooth compactly supported weight and any Hadamard state. Normal ordering is taken relative to a Hadamard reference state, which makes it a "difference" QEI.
- **Status:** Theorem (microlocal analysis).
- **Anchors:** Curved-space QEIs.

**2.14 Fewster & Smith (2008), absolute QEI. Theorem.**
- **Citation:** C. J. Fewster, C. J. Smith, "Absolute quantum energy inequalities in curved spacetime", *Ann. Henri Poincaré* **9**, 425–455 (2008). arXiv:gr-qc/0702056v3 (2007-12-20). DOI 10.1007/s00023-008-0361-0.
- **Result:** The first *absolute* QEI for the minimally coupled massive Klein–Gordon field on 4D globally hyperbolic spacetimes. The bound "depends only on the local geometry".
- **Status:** Theorem.
- **Anchors:** The state-independent curved-space bound a design audit can actually evaluate.

**2.15 Fewster & Roman (2003), null energy conditions in QFT. Theorem (both halves).**
- **Citation:** C. J. Fewster, T. A. Roman, "Null energy conditions in quantum field theory", *Phys. Rev. D* **67**, 044003 (2003). arXiv:gr-qc/0209036v2 (2002-11-26). DOI 10.1103/PhysRevD.67.044003. **The full text was read.**
- **Theorem II.1 (null geodesics: no bound):** Take the massless minimally coupled real scalar in *4D Minkowski*. Weighted averages of ⟨T_ab ℓ^a ℓ^b⟩ along a *null geodesic* are **unbounded below** on Hadamard states. The construction uses vacuum plus multimode two-particle superpositions and "generalise[s] directly to the massive case". There are therefore "no null-worldline QNEIs" in 4D Minkowski, whereas 2D has them. The states used obey ANEC.
- **Theorem III.1 (timelike worldlines: bound exists):** In *any globally hyperbolic spacetime*, for the Klein–Gordon field of mass m ≥ 0, a smooth null vector field ℓ on a tube around a smooth *timelike* curve and a smooth compactly supported real g, the average ∫dτ⟨:T_ab:ℓ^aℓ^b⟩g(τ)² **is bounded below**. The bound is state-independent relative to a Hadamard reference.
- **Explicit form, Eq. (III.10):** For an inertial worldline with 4-velocity v in the Minkowski vacuum reference (massless), ∫dτ⟨:T_ab:ℓ^aℓ^b⟩g² ≥ −((v·ℓ)²/12π²)∫g''(τ)²dτ.
- **Conclusion section:**
  - An argument of Buchholz and Verch (no nontrivial observables on bounded null segments in d > 2 algebraic QFT) suggests that null-worldline QNEIs fail "even for interacting field theories".
  - A null-worldline QNEI cannot replace NEC or ANEC in a Penrose-type singularity theorem.
  - Large negative null energy on one null geodesic "must be compensated by large positive energy densities on neighbouring null geodesics".
- **Status:** Theorem (both halves).
- **Scope:** Free Klein–Gordon field. The null-geodesic nonexistence is proved in flat 4D.
- **Correction to the brief:** The brief states that "the null-contracted stress along timelike worldlines has no lower bound in 4D". The paper proves the opposite. The unbounded case is averaging *along null geodesics*. Along timelike worldlines the null-contracted stress *is* bounded below.
- **Anchors:** Null QEIs; why NEC-type audits must smear along timelike worldlines or over volumes.

**2.16 Ford, Helfer & Roman (2002). Theorem by counterexample.**
- **Citation:** L. H. Ford, A. D. Helfer, T. A. Roman, "Spatially averaged quantum inequalities do not exist in four-dimensional spacetime", *Phys. Rev. D* **66**, 124012 (2002). arXiv:gr-qc/0208045v2 (2002-10-24). DOI 10.1103/PhysRevD.66.124012.
- **Result:** Vacuum plus multimode two-particle states "can produce an arbitrarily large amount of negative energy in a given region of space at a fixed time".
- **Status:** Theorem by counterexample.
- **Anchors:** Only temporal or spacetime smearing constrains negative energy in 4D.

**2.17 Fewster (2012), lecture notes. Review/lecture notes.**
- **Citation:** C. J. Fewster, "Lectures on quantum energy inequalities", arXiv:1208.5399v1 (2012-08-27). Lectures given at AEI Golm, 50 pp.
- **Related chapter:** "Quantum Energy Inequalities" in Lobo (ed.) 2017, pp. 215–254 (Springer table of contents verified). Whether the chapter matches the arXiv notes is **UNVERIFIED**.
- **Result:** Rigorous QEIs via microlocal and algebraic QFT, with free-field examples. The notes also derive QEIs for unitary positive-energy 2D CFTs.
- **Status:** Review/lecture notes.
- **Anchors:** Textbook-grade derivations of QEIs.

**2.18 Fewster & Hollands (2005). Theorem.**
- **Citation:** C. J. Fewster, S. Hollands, "Quantum energy inequalities in two-dimensional conformal field theory", *Rev. Math. Phys.* **17**, 577–612 (2005). arXiv:math-ph/0412028v2 (2005-04-29). DOI 10.1142/S0129055X05002406.
- **Result:** Rigorous state-independent QEIs for *interacting* unitary positive-energy 2D CFTs, along timelike, null and spacelike curves and over volumes. As quoted in Kontou–Sanders eq. (73), a chiral CFT gives ∫G T₀₀ ≥ −(c/12π)∫(d√G/dt)².
- **Status:** Theorem.
- **Anchors:** The main rigorous interacting-theory QEI.

**2.19 Freivogel & Krommydas (2018), SNEC. Conjecture.**
- **Citation:** B. Freivogel, D. Krommydas, "The Smeared Null Energy Condition", *JHEP* **12** (2018) 067. arXiv:1807.03808v4 (2021-04-19). DOI 10.1007/JHEP12(2018)067.
- **Result (text eq. 4):** A proposed bound on null energy smeared over affine length τ along a null geodesic: ⟨T_kk⟩ₛ ≥ −B/(G_N τ²).
  - B is an undetermined constant of order one.
  - The bound is claimed wherever perturbative quantum gravity applies and τ is small compared with the curvature scale.
  - The G_N dependence rests on G_N ∼ 1/N for N species.
  - Consequence: "isolated regions of negative energy are forbidden".
- **Status:** **Conjecture/Proposal.**
- **Anchors:** Semi-local null bounds; the link to the species bound (4.21).

**2.20 Freivogel, Kontou & Krommydas (2022). Theorem conditional on SNEC.**
- **Citation:** "The Return of the Singularities: Applications of the Smeared Null Energy Condition", *SciPost Phys.* **13**, 001 (2022). arXiv:2012.11569v2 (2021-11-15). DOI 10.21468/SciPostPhys.13.1.001.
- **Result:** A semiclassical Penrose-type singularity theorem that *assumes* SNEC. The paper applies the bound to evaporating black holes and to the Maldacena–Milekhin–Popov wormhole.
- **Status:** Theorem conditional on SNEC.

**2.21 Fliss & Freivogel (2022). Theorem (free/super-renormalizable, cutoff-dependent).**
- **Citation:** J. R. Fliss, B. Freivogel, "Semi-local bounds on null energy in QFT", *SciPost Phys.* **12**, 084 (2022; Crossref). arXiv:2108.06068v1 (2021-08-13).
- **Result:** Proves a version of SNEC by light-sheet quantization for free and super-renormalizable QFTs *equipped with a UV cutoff*. Squeezed states show that "the SNEC bound cannot be improved by smearing on a light-sheet alone". The paper proposes DSNEC.
- **Status:** Theorem (free/super-renormalizable, cutoff-dependent bound).

**2.22 Fliss, Freivogel & Kontou (2023), DSNEC. Theorem (free fields, Minkowski).**
- **Citation:** "The double smeared null energy condition", *SciPost Phys.* **14**, 024 (2023; Crossref). arXiv:2111.05772v1 (2021-11-10).
- **Result:** Null energy smeared over *two* null directions has a finite lower bound. It is "rigorously derive[d] … from general worldvolume bounds for free quantum fields in Minkowski spacetime".
- **Status:** Theorem (free fields, Minkowski). Curvature corrections are left as future work.
- **Anchors:** The volume-smeared null bound, the right object for engineered null-energy budgets.

**2.23 Fliss, Freivogel, Kontou & Pardo Santos (2024). Derivation under the EFT assumption.**
- **Citation:** "Non-minimal coupling, negative null energy, and effective field theory", *SciPost Phys.* **16**, 119 (2024; Crossref). arXiv:2309.10848v1 (2023-09-19).
- **Result:** Treats non-minimal coupling as an EFT in which the cutoff controls the field value. Under that assumption, ANEC "is obeyed both classically and in the context of quantum field theory". A smeared NEC holds with a "state dependent bound" that depends on the allowed field range.
- **Status:** Derivation under the EFT assumption.
- **Anchors:** Non-minimally coupled scalars as a classical NEC-violating source, and their limits.

**2.24 Fliss, Freivogel, Kontou & Pardo Santos (2025). Derivation/evidence (large-N approximation).**
- **Citation:** "How negative can null energy be in large N CFTs?", *SciPost Phys.* **19**, 087 (2025; Crossref). arXiv:2412.10618v1 (2024-12-13).
- **Result:** Smeared null energy is bounded below for free *minimally* coupled theories. For *conformally* coupled free bosons, states of unbounded negative smeared null energy exist, reached "by increasing the particle number". In large-N CFTs, the negative smeared null energy scales "at worst as the central charge" C_T.
- **Status:** Derivation/evidence (large-N approximation).

**2.25 Fliss & Rolph (2025/2026), preprint. Derivation (preprint, no journal reference at fetch).**
- **Citation:** "Curious QNEIs from QNEC: New Bounds on Null Energy in Quantum Field Theory", arXiv:2510.26247v2 (2026-04-16).
- **Result:** New families of QNEIs derived from QNEC, strong subadditivity and modular Hamiltonians. The abstract calls them "universal, state-independent lower bounds on semi-local integrals of ⟨T_vv⟩", including "the first of this kind for interacting theories in higher dimensions".
- **Check before citing:** The v2 comment says the higher-dimensional inequality was simplified and its "state-dependence" clarified. Read the full text before citing the higher-dimensional bound as state-independent.
- **Status:** Derivation.

**2.26 Kontou (2024). Review plus a new result.**
- **Citation:** E.-A. Kontou, "Wormhole restrictions from quantum energy inequalities", *Universe* **10**(7), 291 (2024). arXiv:2405.05963v2 (2024-07-08). DOI 10.3390/universe10070291.
- **Result:** Reviews how QEIs restrict "short" and "long" wormholes. New result: DSNEC constraints on the Maldacena–Milekhin–Popov long wormhole.
- **Status:** Review plus new result.

**2.27 Fliss (2026), Modave lectures. Lecture notes.**
- **Citation:** J. R. Fliss, "Modave lectures on energy conditions in quantum field theory and semi-classical gravity", arXiv:2605.18964v1 (2026-05-18), 47 pp.
- **Status:** Lecture notes, the most recent pedagogical treatment.

**2.28 Moghtaderi, Hull, Quintin & Geshnizjani (2025). Derivation conditional on SNEC.**
- **Citation:** "How Much NEC Breaking Can the Universe Endure?", *Phys. Rev. D* **111**, 123552 (2025). arXiv:2503.19955v2 (2025-06-29). DOI 10.1103/j6hp-p8hs.
- **Result:** Translates SNEC into bounds on dark-energy w and on bounce duration versus Ḣ.
- **Status:** Derivation conditional on SNEC.

**2.29 Quantum null energy condition (QNEC).**
- **Bousso, Fisher, Leichenauer & Wall, conjecture:** "A Quantum Focussing Conjecture", *Phys. Rev. D* **93**, 064044 (2016). arXiv:1506.02669v1 (2015-06-08). **Conjecture.**
- **Bousso, Fisher, Koeller, Leichenauer & Wall, proof:** "Proof of the Quantum Null Energy Condition", *Phys. Rev. D* **93**, 024017 (2016). arXiv:1509.02542v2 (2015-09-15).
  - Statement: ⟨T_kk(p)⟩ ≥ (ħ/2π) lim_{A→0} S''_out/A.
  - Proved "for free and superrenormalizable bosonic field theories, and to any points that lie on stationary null surfaces".
  - **Status:** Theorem (physics-level).
- **Balakrishnan, Faulkner, Khandker & Wang, general proof:** "A General Proof of the Quantum Null Energy Condition", *JHEP* **09** (2019) 020. arXiv:1706.09432v2 (2019-03-27; v2 fixes an error in §6).
  - Scope: "any relativistic QFT"; the methods are designed around QFTs "with an interacting UV fixed point".
  - Setting: flat space. **Proof (physics-level).**
- **Ceyhan & Faulkner, QNEC from ANEC:** "Recovering the QNEC from the ANEC", *Commun. Math. Phys.* **377**, 999–1045 (2020; Crossref). arXiv:1812.04683v2 (2019-03-21).
  - Formulated as a theorem for half-sided modular inclusions, with the input state of finite averaged null energy.
  - **Status:** Theorem.
- **Anchors:** Entropy-based null energy bounds. QNEC in curved spacetime remains a conjecture through the QFC.

---

## Area 3. The averaged null energy condition

**3.1 Klinkhammer (1991). Derivation/theorem for the free field.**
- **Citation:** G. Klinkhammer, "Averaged energy conditions for free scalar fields in flat spacetime", *Phys. Rev. D* **43**, 2542–2548 (1991). DOI 10.1103/PhysRevD.43.2542. The APS abstract was read.
- **Result:**
  - For the free scalar in Minkowski space, WEC averaged along a complete null geodesic holds for a wide class of states.
  - It fails when averaged along non-geodesic curves.
  - Compactifying one spatial direction produces AWEC violation.
- **Status:** Derivation/theorem for the free field.

**3.2 Wald & Yurtsever (1991). Theorem.**
- **Citation:** R. Wald, U. Yurtsever, "General proof of the averaged null energy condition for a massless scalar field in two-dimensional curved spacetime", *Phys. Rev. D* **44**, 403–416 (1991). DOI 10.1103/PhysRevD.44.403. The APS abstract was read.
- **Result:**
  - For the massless scalar in *any globally hyperbolic 2D spacetime*, ANEC holds for all Hadamard states "along any complete, achronal null geodesic".
  - Extensions, each with restrictions on the states: massive 2D Minkowski and 4D Minkowski.
  - On null generators of a bifurcate Killing horizon, ANEC holds provided a stationary Hadamard state exists. This gives ANEC for massive Klein–Gordon in de Sitter.
  - Per Kontou–Sanders, they also "argued that the ANEC cannot hold for all states of a massless field in all [4D] spacetimes".
- **Status:** Theorem.

**3.3 Verch (2000). Theorem (2D, general QFT).**
- **Citation:** R. Verch, "The averaged null energy condition for general quantum field theories in two dimensions", *J. Math. Phys.* **41**, 206–217 (2000). arXiv:math-ph/9904036v1 (1999-04-29). DOI 10.1063/1.533130.
- **Result:** ANEC holds on a dense, translation-invariant set of vector states in *any* 2D Minkowski QFT that has a mass gap and a stress tensor. The stress tensor must be a Wightman field, local relative to the observables, generating translations, divergence-free and energetically bounded.
- **Status:** Theorem (2D, general QFT).

**3.4 Faulkner, Leigh, Parrikar & Wang (2016). Proof (physics-level; flat spacetime).**
- **Citation:** "Modular Hamiltonians for deformed half-spaces and the averaged null energy condition", *JHEP* **09** (2016) 038. arXiv:1605.08072v1 (2016-05-25). DOI 10.1007/JHEP09(2016)038.
- **Result:** Shape-deformed modular Hamiltonians together with monotonicity of relative entropy "prove the averaged null energy condition in Minkowski space-time". The same argument gives a new proof of the Hofman–Maldacena bounds.
- **Scope, as characterized in Hartman et al.'s introduction (text read):** "Assuming all of the relevant quantities are well defined in the continuum limit, the argument applies to a large (and perhaps dense) set of states in any unitary, Lorentz-invariant QFT."
- **Status:** Proof (physics-level; flat spacetime only).

**3.5 Hartman, Kundu & Tajdini (2017). Proof (physics-level; flat, d > 2).**
- **Citation:** "Averaged Null Energy Condition from Causality", *JHEP* **07** (2017) 066. arXiv:1610.05308v1 (2016-10-17). DOI 10.1007/JHEP07(2017)066.
- **Result:** Microcausality implies ∫du T_uu ≥ 0 for interacting theories in d > 2. The text states the scope: "any unitary, Lorentz-invariant QFT with an interacting conformal fixed point in the UV must obey the ANEC".
- **Assumptions:**
  - no higher-spin symmetry at the UV fixed point;
  - therefore d > 2;
  - the result does "not immediately apply to free (or asymptotically free) theories".
- **Also derived:** An infinite family of constraints ∫du X_{uu…u} ≥ 0.
- **Status:** Proof (physics-level; flat, d > 2).

**3.6 Visser (1995), scale anomalies. Derivation (test field).**
- **Citation:** M. Visser, "Scale anomalies imply violation of the averaged null energy condition", *Phys. Lett. B* **349**, 443–447 (1995). arXiv:gr-qc/9409043v1 (1994-09-20). DOI 10.1016/0370-2693(95)00303-3.
- **Result:** Characterizes "a broad class of spacetimes in which the ANEC is guaranteed to be violated" for conformal fields with a scale anomaly.
- **Graham–Olum's analysis (text §III read):** The required rescaling is Ω ∼ exp(2880π²). Contraction pushes curvature radii below the Planck length. Dilation makes T negligible compared with G. Neither route produces a self-consistent achronal violation.
- **Status:** Derivation (test field).

**3.7 Visser (1996–1997), gravitational vacuum polarization I–IV. Numerical and semi-analytic (test-field limit).**
- **Setting:** Conformally coupled massless scalar on Schwarzschild in the test-field limit.
- **Paper I:** *Phys. Rev. D* **54**, 5103 (1996), arXiv:gr-qc/9604007v1, Hartle–Hawking state. Pointwise violations form "onion-like layers" between the photon orbit and the horizon, in the order DEC, WEC, (NEC+SEC). ANEC is violated on some trapped null geodesics.
- **Paper II:** *Phys. Rev. D* **54**, 5116 (1996), arXiv:gr-qc/9604008v1, Boulware state. All standard pointwise and averaged energy conditions are violated throughout the exterior.
- **Paper III:** *Phys. Rev. D* **54**, 5123 (1996), arXiv:gr-qc/9604009v1, (1+1)-D.
  - NEC holds outside the horizon in the Hartle–Hawking state and fails in the Boulware and Unruh states.
  - DEC is violated everywhere, for any state.
- **Paper IV:** *Phys. Rev. D* **56**, 936–952 (1997), arXiv:gr-qc/9703001v1, Unruh state.
  - All pointwise energy conditions are violated throughout the exterior.
  - ANEC is violated "on all outgoing radial null geodesics".
  - The semi-analytic model reproduces the numerics to within 0.8%.
- **Graham–Olum footnote (text read):** In Schwarzschild the radial null geodesic "is achronal but not complete", and every complete null geodesic is chronal. These violations therefore leave self-consistent achronal ANEC intact.
- **Status:** Numerical and semi-analytic, test-field limit.
- **Anchors:** Vacuum polarization near horizons; the reference case for horizons that form in engineered metrics.

**3.8 Flanagan & Wald (1996). Derivation (second-order perturbation theory).**
- **Citation:** É. É. Flanagan, R. M. Wald, "Does backreaction enforce the averaged null energy condition in semiclassical gravity?", *Phys. Rev. D* **54**, 6233–6283 (1996). arXiv:gr-qc/9602052v2 (1996-07-02). DOI 10.1103/PhysRevD.54.6233.
- **Setting:** A free massless scalar with arbitrary curvature coupling, at second order about flat/vacuum, imposing the semiclassical Einstein equation.
- **Result:** The ANEC integral can be negative. When averaged transverse to the geodesic with Planck-scale smearing, however, it is "strictly positive … in all cases except for the flat spacetime/vacuum solution". Macroscopic traversable wormholes are therefore disfavoured.
- **Assumptions:** reduction of order; incoming scales much larger than the Planck length; no dominant incoming classical gravitational radiation.
- **Status:** Derivation (second-order perturbation theory).

**3.9 Fewster, Olum & Pfenning (2007). Theorem.**
- **Citation:** "Averaged null energy condition in spacetimes with boundaries", *Phys. Rev. D* **75**, 025007 (2007). arXiv:gr-qc/0609007v3 (2007-09-10). DOI 10.1103/PhysRevD.75.025007.
- **Result:** ANEC is never violated by the minimally coupled free scalar along a complete null geodesic surrounded by a *flat* tubular neighbourhood whose intrinsic causal structure matches the one induced from the full spacetime. In particular it holds in Casimir geometries for geodesics that stay a finite distance from the plates.
- **Status:** Theorem.

**3.10 Graham & Olum (2007). Conjecture plus conditional theorems.**
- **Citation:** N. Graham, K. D. Olum, "Achronal averaged null energy condition", *Phys. Rev. D* **76**, 064001 (2007). arXiv:0705.3193v2 (2007-08-27; v2 qualifies the conditions on Theorem 1). DOI 10.1103/PhysRevD.76.064001. **The text was read.**
- **Condition 1:** "There is no self-consistent solution in semiclassical gravity in which ANEC is violated on a complete, achronal null geodesic." The authors write: "We conjecture that all semiclassical systems obey self-consistent achronal ANEC."
- **Lemma 1:** In a spacetime obeying the null generic condition and Condition 1, there are no complete achronal null geodesics.
- **Theorems 1–3, assuming Condition 1 plus the generic condition:**
  - topological censorship;
  - no time machine (Tipler form);
  - no compactly generated Cauchy horizon (Hawking form).
  - The paper also extends the positive-mass result of Penrose–Sorkin–Woolgar (3.15) to the achronal case.
- **Status:** **Conjecture (Condition 1) plus theorems conditional on it.**

**3.11 Wall (2010). Conditional derivation.**
- **Citation:** A. C. Wall, "Proving the achronal averaged null energy condition from the generalized second law", *Phys. Rev. D* **81**, 024038 (2010). arXiv:0910.5751v2 (2010-02-16). DOI 10.1103/PhysRevD.81.024038.
- **Result:** For quantum fields *minimally coupled to semiclassical Einstein gravity*, ANEC on null lines (complete achronal null geodesics) follows from the GSL for causal horizons.
- **Auxiliary assumptions:** CPT, and a suitable renormalization scheme for the generalized entropy.
- **Limitation:** The dependent theorems "fail once the linearized graviton field is quantized", because the renormalized shear-squared term can be negative. Wall proposes a shear-inclusive ANEC.
- **Kontou–Sanders:** Whether the regularization can be made rigorous "is not fully settled".
- **Status:** Conditional derivation.

**3.12 Urban & Olum (2010), conformally flat spacetime. Derivation (explicit counterexample, test field).**
- **Citation:** D. Urban, K. D. Olum, "Averaged null energy condition violation in a conformally flat spacetime", *Phys. Rev. D* **81**, 024039 (2010). arXiv:0910.5925v2 (2010-01-28). DOI 10.1103/PhysRevD.81.024039.
- **Result:** A conformally coupled scalar in a 3+1 conformally flat spacetime violates ANEC. The violation is state-dependent, "can be made as large as desired" and does not come from anomalies. Since every geodesic in a conformally flat spacetime is achronal, "the achronal averaged null energy condition is likewise violated".
- **Scope (Kontou–Sanders):** These counterexamples are known only for test fields; the semiclassical Einstein equation is not imposed.
- **Status:** Derivation (explicit counterexample, test field).

**3.13 Urban & Olum (2010), spacetime averaging. Derivation (counterexamples).**
- **Citation:** "Spacetime averaged null energy condition", *Phys. Rev. D* **81**, 124004 (2010). arXiv:1002.4689v2 (2010-06-13). DOI 10.1103/PhysRevD.81.124004.
- **Result:** For every procedure of additional averaging they consider, including integration over the whole manifold, they give a class of examples that "violate any such averaged condition".
- **Status:** Derivation (counterexamples).

**3.14 Kontou & Olum (2013, 2015). Theorems (conditional in 2013).**
- **2013 citation:** "Averaged null energy condition in a classical curved background", *Phys. Rev. D* **87**, 064009 (2013). arXiv:1212.2290v1 (2012-12-11). DOI 10.1103/PhysRevD.87.064009.
  - *Starting from a conjecture* that flat-space QIs hold with small corrections at small curvature, the paper proves ANEC for a minimally coupled free scalar on an achronal null geodesic. The geodesic must be surrounded by a tube whose curvature comes from a classical source.
  - **Status:** Conditional theorem.
- **2015 citation:** "Proof of the averaged null energy condition in a classical curved spacetime using a null-projected quantum inequality", *Phys. Rev. D* **92**, 124009 (2015). arXiv:1507.00297v2 (2015-10-27). DOI 10.1103/PhysRevD.92.124009.
  - The paper derives a null-projected QI for the massless minimally coupled scalar "to first order of the Riemann tensor and its derivatives".
  - It then proves ANEC on achronal geodesics in a curved background that obeys the null convergence condition.
  - **Status:** Theorem (free field, first order in curvature, classical background).

**3.15 Penrose, Sorkin & Woolgar (1993). Theorem.**
- **Citation:** R. Penrose, R. D. Sorkin, E. Woolgar, "A positive mass theorem based on the focusing and retardation of null geodesics", arXiv:gr-qc/9301015v2 (1993-01-15). The journal venue is **UNVERIFIED**; the arXiv page carries no journal reference.
- **Result:** A 4D causal-structure proof of positive mass. Per Graham–Olum, it needs only conjugate points on complete null geodesics, and it "might allow a generalisation to semi-classical gravity".
- **Status:** Theorem.

**3.16 Ishibashi, Maeda & Mefford (2019). Derivation (holographic; curved boundary fixed).**
- **Citation:** "Achronal ANEC, Weak Cosmic Censorship, and AdS/CFT duality", *Phys. Rev. D* **100**, 066008 (2019). arXiv:1903.11806v1 (2019-03-28). DOI 10.1103/PhysRevD.100.066008.
- **Result:** Holographic strong-coupling CFTs on curved 3+1 and 4+1 boundaries *violate achronal ANEC*.
  - The bulk is an asymptotically AdS vacuum bubble with no causality violation or singularities.
  - The boundary is "causally proper".
  - Conversely, a boundary that fails to be causally proper implies a bulk naked singularity.
- **Scope:** The boundary metric is prescribed, which is the test-field analogue in the boundary theory.
- **Status:** Derivation (holographic).
- **Anchors:** Counterexamples at strong coupling.

---

## Area 4. Semiclassical gravity, vacuum polarization and horizon thermodynamics

**4.1 Capper & Duff (1974). Derivation (perturbative).**
- **Citation:** D. M. Capper, M. J. Duff, "Trace anomalies in dimensional regularization", *Il Nuovo Cimento A* **23**, 173–183 (1974). DOI 10.1007/BF02748300. The Springer abstract was read.
- **Result:** A trace identity that holds in n dimensions can fail for the finite part in four dimensions. Example: the one-loop neutrino contribution to the graviton propagator.
- **Status:** Derivation (perturbative).
- **Anchors:** The discovery of the trace anomaly.

**4.2 Duff (1994). Review.**
- **Citation:** M. J. Duff, "Twenty years of the Weyl anomaly", *Class. Quantum Grav.* **11**, 1387–1404 (1994). arXiv:hep-th/9308075v1 (1993-08-16). DOI 10.1088/0264-9381/11/6/004.
- **Result:** Weyl invariance of classical massless fields coupled to gravity "no longer survives in the quantum theory".
- **Status:** Review.

**4.3 Deser & Schwimmer (1993). Derivation (classification).**
- **Citation:** S. Deser, A. Schwimmer, "Geometric classification of conformal anomalies in arbitrary dimensions", *Phys. Lett. B* **309**, 279–284 (1993). arXiv:hep-th/9302047v1 (1993-02-12). DOI 10.1016/0370-2693(93)90934-A.
- **Result:** Conformal anomalies fall into two classes:
  - type A: proportional to the Euler density, scale-free;
  - type B: Weyl invariants, which require a regularization scale.
- **Status:** Derivation (classification).

**4.4 Christensen & Fulling (1977). Derivation.**
- **Citation:** S. M. Christensen, S. A. Fulling, "Trace anomalies and the Hawking effect", *Phys. Rev. D* **15**, 2088–2104 (1977). DOI 10.1103/PhysRevD.15.2088. The APS abstract was read.
- **Result:**
  - The general static spherically symmetric conserved T in exterior Schwarzschild depends on two constants and two functions, one of which is the trace.
  - For a conformal scalar, the anomalous trace is proportional to the Weyl scalar 48M²r⁻⁶, with coefficient (2880π²)⁻¹.
  - In 2D, the Hawking flux at infinity is directly proportional to the anomalous trace.
- **Status:** Derivation.
- **Anchors:** Anomaly-driven vacuum stress, from which a geometry's quantum response can be estimated.

**4.5 Birrell & Davies (1982); Parker & Toms (2009); Wald (1994). PARTIAL (metadata only; content not re-read).**
- *Quantum Fields in Curved Space* (Cambridge University Press, 1982), DOI 10.1017/CBO9780511622632.
- *Quantum Field Theory in Curved Spacetime* (Cambridge University Press, 2009), DOI 10.1017/CBO9780511813924.
- R. M. Wald, *Quantum Field Theory in Curved Spacetime and Black Hole Thermodynamics* (University of Chicago Press, 1994), ISBN 9780226870274 (Open Library).
- **Anchors:** Standard QFTCS texts.

**4.6 Hollands & Wald (2015). Review (rigorous).**
- **Citation:** S. Hollands, R. M. Wald, "Quantum fields in curved spacetime", *Phys. Rep.* **574**, 1–35 (2015). arXiv:1401.2026v2 (2014-06-10). DOI 10.1016/j.physrep.2015.02.001.
- **Result:** A mathematically precise review. It covers the microlocal spectrum condition, the definition of the stress tensor, full characterization of renormalization ambiguities, the Unruh and Hawking effects, and perturbative interacting fields.
- **Status:** Review (rigorous).
- **Anchors:** Definition of ⟨T_ab⟩ and its ambiguities.

**4.7 Hu & Verdaguer (2008). Review.**
- **Citation:** B. L. Hu, E. Verdaguer, "Stochastic Gravity: Theory and Applications", *Living Rev. Relativity* **11**, 3 (2008). arXiv:0802.0658v1 (2008-02-05). DOI 10.12942/lrr-2008-3.
- **Result:** The Einstein–Langevin equation with a noise kernel. Proves that Minkowski space is a stable solution of semiclassical gravity. Discusses validity criteria for semiclassical gravity.
- **Status:** Review.

**4.8 Page (1982). Derivation (approximation).**
- **Citation:** D. N. Page, "Thermal stress tensors in static Einstein spaces", *Phys. Rev. D* **25**, 1499–1509 (1982). DOI 10.1103/PhysRevD.25.1499. The APS abstract was read.
- **Result:** A Gaussian (Bekenstein–Parker) approximation for the conformal scalar gives closed-form ⟨T_μν⟩ in the Hartle–Hawking state outside static black holes. It is exact in de Sitter and Nariai, and "close to Candelas's values on the bifurcation two-sphere".
- **Status:** Derivation (approximation).

**4.9 Candelas (1980). PARTIAL (metadata only).**
- **Citation:** P. Candelas, "Vacuum polarization in Schwarzschild spacetime", *Phys. Rev. D* **21**, 2185–2202 (1980). DOI 10.1103/PhysRevD.21.2185.

**4.10 Anderson, Hiscock & Samuel (1995). Numerical plus analytic approximation.**
- **Citation:** P. R. Anderson, W. A. Hiscock, D. A. Samuel, "Stress-energy tensor of quantized scalar fields in static spherically symmetric spacetimes", *Phys. Rev. D* **51**, 4337–4358 (1995). DOI 10.1103/PhysRevD.51.4337. The APS abstract was read.
- **Result:** A method for ⟨T⟩ of massless or massive scalars with arbitrary coupling ξ, in vacuum or thermal states. Numerics are given for Schwarzschild and Reissner–Nordström.
- **Status:** Numerical plus analytic approximation.

**4.11 Roman (1986). PARTIAL (metadata only).**
- **Citation:** T. A. Roman, "Quantum stress-energy tensors and the weak energy condition", *Phys. Rev. D* **33**, 3526–3533 (1986). DOI 10.1103/PhysRevD.33.3526.
- **Content:** Checked only secondhand, via Martín-Moruno–Visser 2021 (first argument for type IV near an evaporating apparent horizon).

**4.12 Abdolrahimi, Page & Tzounis (2019). Numerical/semi-analytic.**
- **Citation:** S. Abdolrahimi, D. N. Page, C. Tzounis, "Ingoing Eddington–Finkelstein metric of an evaporating black hole", *Phys. Rev. D* **100**, 124038 (2019). arXiv:1607.05280v4 (2019-12-17). DOI 10.1103/PhysRevD.100.124038.
- **Result:** A linearized back-reacted metric built from the Unruh-state stress tensor.
- **Version comment (read):** "for a conformal massless scalar field, there is no timelike eigenvector anywhere outside the black hole, so the energy flux is outward for all observers of all velocities". That is Hawking–Ellis type IV everywhere outside.
- **Status:** Numerical/semi-analytic.
- **Anchors:** The Unruh-state type IV result.

**4.13 Hawking (1975). Derivation.**
- **Citation:** S. W. Hawking, "Particle creation by black holes", *Commun. Math. Phys.* **43**, 199–220 (1975). DOI 10.1007/BF02345020. The Springer abstract was read.
- **Result:** Quoted from the abstract: black holes emit "as if they were hot bodies with temperature hκ/2πk ≈ 10⁻⁶(M☉/M) °K". The generalized second law holds: "S + 1/4 A never decreases".
- **Status:** Derivation (QFT on a collapse background).

**4.14 Unruh (1976). Derivation.**
- **Citation:** W. G. Unruh, "Notes on black-hole evaporation", *Phys. Rev. D* **14**, 870–892 (1976). DOI 10.1103/PhysRevD.14.870. The APS abstract was read.
- **Result:**
  - "an accelerated detector even in flat spacetime will detect particles in the vacuum".
  - Boundary conditions on the past horizon define the state now named after Unruh.
  - "a geodesic detector near the horizon will not see the Hawking flux".
- **Missing from the abstract:** The formula T = ħa/(2πck_B) does not appear in the abstract. Its primary-source wording is **UNVERIFIED** in this pass; take it from the full text or from Crispino et al. (4.15).
- **Status:** Derivation.

**4.15 Crispino, Higuchi & Matsas (2008). Review.**
- **Citation:** "The Unruh effect and its applications", *Rev. Mod. Phys.* **80**, 787–838 (2008). arXiv:0710.5373v1 (2007-10-29). DOI 10.1103/RevModPhys.80.787.
- **Result:** A review that aims to "clarify what seems to be common misconceptions".
- **Status:** Review.

**4.16 Fulling (1973); Davies (1975). PARTIAL (metadata only).**
- S. A. Fulling, "Nonuniqueness of canonical field quantization in Riemannian space-time", *Phys. Rev. D* **7**, 2850 (1973), DOI 10.1103/PhysRevD.7.2850.
- P. C. W. Davies, "Scalar production in Schwarzschild and Rindler metrics", *J. Phys. A* **8**, 609 (1975), DOI 10.1088/0305-4470/8/4/022. Crossref gives the title as "Scalar production…".

**4.17 Gibbons & Hawking (1977). Derivation.**
- **Citation:** "Cosmological event horizons, thermodynamics, and particle creation", *Phys. Rev. D* **15**, 2738–2751 (1977). DOI 10.1103/PhysRevD.15.2738. The APS abstract was read.
- **Result:** An observer with a particle detector sees thermal radiation from the cosmological event horizon. The horizon area plays the role of entropy.
- **Status:** Derivation.

**4.18 Tolman (1930); Tolman & Ehrenfest (1930). Derivation (static equilibrium).**
- **Tolman:** R. C. Tolman, "On the weight of heat and thermal equilibrium in general relativity", *Phys. Rev.* **35**, 904–924 (1930). DOI 10.1103/PhysRev.35.904. The APS abstract was read.
  - For a static spherical perfect fluid in equilibrium, d ln T₀/dr = −½ dν/dr, with g₄₄ = e^ν.
- **Tolman & Ehrenfest:** R. C. Tolman, P. Ehrenfest, "Temperature equilibrium in a static gravitational field", *Phys. Rev.* **36**, 1791–1798 (1930). DOI 10.1103/PhysRev.36.1791. The APS abstract was read.
  - For a general static field, the proper temperature at equilibrium makes T₀√g₄₄ constant.
  - The radical was lost in the page extraction, so this form is inferred from Tolman's d ln T₀/dr = −½ dν/dr.
- **Status:** Derivation (static equilibrium).
- **Anchors:** Local temperatures in stationary engineered regions.

**4.19 Dvali (2010). Derivation (black-hole arguments; the abstract says "prove").**
- **Citation:** G. Dvali, "Black holes and large N species solution to the hierarchy problem", *Fortsch. Phys.* **58**, 528–536 (2010). arXiv:0706.2050v1 (2007-06-14; the preprint dates from 2007). DOI 10.1002/prop.201000009.
- **Result:** For N Z₂-conserved species of mass Λ, black-hole physics gives a lower bound on the Planck mass, "in large N limit … given by NΛ²". That is, M_P² ≳ NΛ².
- **Status:** Derivation.

**4.20 Dvali & Redi (2008). Derivation.**
- **Citation:** G. Dvali, M. Redi, "Black hole bound on the number of species and quantum gravity at LHC", *Phys. Rev. D* **77**, 045027 (2008). arXiv:0710.4344v1 (2007-10-23). DOI 10.1103/PhysRevD.77.045027.
- **Result:** Species masses are bounded by M_P/√N. The effective gravitational cutoff is Λ_G ≈ M_P/√N. Black holes smaller than Λ_G⁻¹ are no longer semiclassical.
- **Status:** Derivation.
- **Anchors:** Why "many fields" does not multiply negative-energy budgets for free. This connects the linear-in-N scaling of free-field QEI bounds to SNEC's G_N ∼ 1/N (2.19).

**4.21 Hiscock (1997). Derivation (2D reduction).**
- **Citation:** W. A. Hiscock, "Quantum effects in the Alcubierre warp-drive spacetime", *Class. Quantum Grav.* **14**, L183–L188 (1997). arXiv:gr-qc/9707024v1 (1997-07-10). DOI 10.1088/0264-9381/14/11/002.
- **Result:** In a 2D reduction, the conformal-scalar ⟨T⟩ "is found to diverge if the apparent velocity of the spaceship exceeds the speed of light".
- **Status:** Derivation (2D reduction).

**4.22 Finazzi, Liberati & Barceló (2009). Derivation.**
- **Citation:** S. Finazzi, S. Liberati, C. Barceló, "Semiclassical instability of dynamical warp drives", *Phys. Rev. D* **79**, 124017 (2009). arXiv:0904.0141v2 (2009-07-14). DOI 10.1103/PhysRevD.79.124017.
- **Result:** For a superluminal bubble formed from flat space:
  - an observer at the centre sees a thermal Hawking flux, extremely high if the exotic matter obeys QIs;
  - the renormalized stress tensor "will exponentially grow in time close to, and on, the front wall";
  - the geometry is therefore unstable against semiclassical back-reaction.
- **Companion essay:** Barceló, Finazzi & Liberati, arXiv:1001.4960v1 (2010-01-27), FQXi essay, no journal reference.
- **Status:** Derivation.
- **Anchors:** Horizon formation in engineered metrics and semiclassical back-reaction on front and rear horizons of moving geometries.

---

## Area 5. Topology and causality

**5.1 Geroch (1967). PARTIAL.**
- **Citation:** R. P. Geroch, "Topology in General Relativity", *J. Math. Phys.* **8**, 782–786 (1967). DOI 10.1063/1.1705276.
- **Check:** Crossref and OSTI give the metadata. The AIP page returned 403, so no primary abstract page was read. The abstract quoted in web-search snippets says topology change "can occur if and only if the model is acausal" under certain conditions; treat that as **UNVERIFIED from the primary page**.
- **Secondary verification:** Borde (5.3) states that "Geroch's closed-universe argument" gives causality violation with topology change.
- **Status:** Theorem.

**5.2 Tipler (1976, 1977). Theorem.**
- **1976 citation:** F. J. Tipler, "Causality violation in asymptotically flat space-times", *Phys. Rev. Lett.* **37**, 879–882 (1976). DOI 10.1103/PhysRevLett.37.879. The APS abstract was read.
  - Quoted from the abstract: "a region containing closed timelike lines cannot evolve from regular initial data in a singularity-free asymptotically flat space-time".
  - The energy-condition hypothesis does not appear in the abstract and is **UNVERIFIED** here. Graham–Olum §IV restate the theorem with self-consistent achronal ANEC plus the null generic condition (their Theorem 2).
- **1977 citation:** "Singularities and causality violation", *Ann. Phys.* **108**, 1–36 (1977). DOI 10.1016/0003-4916(77)90348-7. **PARTIAL (metadata only).**
- **Status:** Theorem.

**5.3 Borde (1994). Theorem.**
- **Citation:** A. Borde, "Topology change in classical general relativity", arXiv:gr-qc/9406053v1 (1994-06-30). The arXiv page lists no journal reference.
- **Result:**
  - Topology change is kinematically possible with non-singular Lorentz metrics.
  - Causally compact interpolating spacetimes nonetheless carry causality violations, following Geroch's argument.
  - In dimensions ≥ 3, causally compact topology-changing spacetimes cannot satisfy Einstein's equation with a reasonable source, even allowing geodesic incompleteness.
- **Status:** Theorem.
- **Anchors:** Topology engineering: topology change costs causality violation (kinematics) and is dynamically obstructed in dimension ≥ 3.

**5.4 Morris & Thorne (1988); Morris, Thorne & Yurtsever (1988).**
- **Morris & Thorne:** "Wormholes in spacetime and their use for interstellar travel: A tool for teaching general relativity", *Am. J. Phys.* **56**, 395–412 (1988). DOI 10.1119/1.15620. **PARTIAL (metadata only).**
- **Morris, Thorne & Yurtsever:** "Wormholes, time machines, and the weak energy condition", *Phys. Rev. Lett.* **61**, 1446–1449 (1988). DOI 10.1103/PhysRevLett.61.1446. The APS abstract was read: a maintainable wormhole "can be converted into a time machine".
- **Status:** Derivation.
- **Anchors:** The founding "engineering" papers.

**5.5 Friedman, Schleich & Witt (1993), topological censorship. Theorem.**
- **Citation:** J. L. Friedman, K. Schleich, D. M. Witt, "Topological censorship", *Phys. Rev. Lett.* **71**, 1486–1489 (1993). Erratum: *Phys. Rev. Lett.* **75**, 1872 (1995). arXiv:gr-qc/9305017v2 (1995-06-09).
- **Result (text Theorem 1 read):** "If an asymptotically flat, globally hyperbolic spacetime satisfies the **averaged** null energy condition, then every causal curve from ℐ⁻ to ℐ⁺ is deformable to γ₀." The ANEC used there is "nonnegative along every inextendible null geodesic".
- **Abstract versus theorem:** The abstract says "null energy condition", but the theorem uses ANEC.
- **Erratum:** A secondary "passive topological censorship" claim was false (Burnett); the main theorem is unaffected.
- **Status:** Theorem.

**5.6 Galloway, Schleich, Witt & Woolgar (1999). Theorem.**
- **Citation:** "Topological censorship and higher genus black holes", *Phys. Rev. D* **60**, 104039 (1999). arXiv:gr-qc/9902061v2 (1999-06-19). DOI 10.1103/PhysRevD.60.104039.
- **Result:** Topological censorship for timelike scri (asymptotically AdS). The genera of horizon cross-sections are bounded by the genus of the cut of scri.
- **Status:** Theorem.

**5.7 Friedman & Higuchi (2006). Review.**
- **Citation:** J. L. Friedman, A. Higuchi, "Topological censorship and chronology protection", *Annalen Phys.* **15**, 109–128 (2006). arXiv:0801.0735v2 (2008-06-03). DOI 10.1002/andp.200510172.
- **Status:** Review.

**5.8 Hawking (1992), chronology protection. Theorem plus conjecture.**
- **Citation:** S. W. Hawking, "Chronology protection conjecture", *Phys. Rev. D* **46**, 603–611 (1992). DOI 10.1103/PhysRevD.46.603. The APS abstract was read in full.
- **Result:**
  - A causality violation in a finite, singularity-free region gives a compactly generated Cauchy horizon, generally containing incomplete closed null geodesics.
  - "If the causality violation developed from a noncompact initial surface, the averaged weak energy condition must be violated on the Cauchy horizon."
  - Back-reaction "would prevent closed timelike curves from appearing".
  - The conjecture: "The laws of physics do not allow the appearance of closed timelike curves."
- **Status:** Theorem (the AWEC violation) plus conjecture (chronology protection).

**5.9 Kim & Thorne (1991). Derivation.**
- **Citation:** S.-W. Kim, K. S. Thorne, "Do vacuum fluctuations prevent the creation of closed timelike curves?", *Phys. Rev. D* **43**, 3929–3947 (1991). DOI 10.1103/PhysRevD.43.3929. The APS abstract was read.
- **Result:** The renormalized stress tensor diverges at the Cauchy horizon but "extremely weak[ly]": δg ∼ (l_P/D)(l_P/Δt). The authors conjecture a quantum-gravity cutoff; Hawking's counter-conjecture is contrasted.
- **Status:** Derivation plus competing conjectures.

**5.10 Kay, Radzikowski & Wald (1997). Theorem (linear scalar).**
- **Citation:** B. S. Kay, M. J. Radzikowski, R. M. Wald, "Quantum field theory on spacetimes with a compactly generated Cauchy horizon", *Commun. Math. Phys.* **183**, 533–556 (1997). arXiv:gr-qc/9603012v2 (1997-05-08). DOI 10.1007/s002200050042.
- **Theorems:** The field algebra has no F-local extension at "base points". The Hadamard two-point distribution is singular at every base point, so ⟨φ²⟩ and ⟨T_ab⟩ are "necessarily ill-defined or singular at any base point".
- **Status:** Theorem (linear scalar).

**5.11 Visser (2002/2003). Review.**
- **Citation:** M. Visser, "The quantum physics of chronology protection", arXiv:gr-qc/0204022v2 (2002-04-17). It is a contribution to the Hawking 60th-birthday conference volume; the published venue is **UNVERIFIED**.
- **Status:** Review.

**5.12 Everett & Roman (1997), Krasnikov tube. Derivation.**
- **Citation:** A. E. Everett, T. A. Roman, "Superluminal subway: The Krasnikov tube", *Phys. Rev. D* **56**, 2100–2108 (1997). arXiv:gr-qc/9702049v1 (1997-02-25). DOI 10.1103/PhysRevD.56.2100.
- **Result:**
  - A 4D Krasnikov tube is built along the outbound path.
  - A single tube has no CTCs, but "a time machine can be constructed with a system of two non-overlapping tubes".
  - The construction needs "unphysically thin layers of negative energy density" and large total negative energies.
- **Status:** Derivation.
- **Anchors:** Route-following geometries prepared ahead of time along the path; the classical precedent for route-extended designs.

**5.13 Krasnikov (1998). Derivation under stated assumptions.**
- **Citation:** S. V. Krasnikov, "Hyperfast interstellar travel in general relativity", *Phys. Rev. D* **57**, 4760–4766 (1998). arXiv:gr-qc/9511068v6 (1998-03-09). DOI 10.1103/PhysRevD.57.4760.
- **Result:** "under some reasonable assumptions in globally hyperbolic spacetimes the traveller cannot hasten reaching the destination". An arbitrarily short round trip, as seen from Earth, may still be possible.
- **Status:** Derivation under stated assumptions.

**5.14 Shoshany & Snodgrass (2024). Derivation (explicit construction).**
- **Citation:** B. Shoshany, B. Snodgrass, "Warp drives and closed timelike curves", *Class. Quantum Grav.* **41**, 205005 (2024). arXiv:2309.10072v3 (2024-09-16). DOI 10.1088/1361-6382/ad74d1.
- **Result:** Warp metrics with non-unit lapse and compact support. Gluing two of them gives a closed timelike geodesic. The paper discusses WEC violation.
- **Status:** Derivation (explicit construction).
- **Anchors:** The causal-safety discipline for any FTL design, and why lapse choice matters.

**5.15 Olum (1998). Theorem.**
- **Citation:** K. D. Olum, "Superluminal travel requires negative energies", *Phys. Rev. Lett.* **81**, 3567–3570 (1998). arXiv:gr-qc/9805003v2 (1998-10-14). DOI 10.1103/PhysRevLett.81.3567.
- **Definition used:** Superluminal travel means that the path reaches a destination surface earlier than any neighbouring path.
- **Result:** "With this definition (and assuming the generic condition) I prove that superluminal travel requires weak-energy-condition violation."
- **Status:** Theorem.

**5.16 Visser, Bassett & Liberati (2000). Derivation (perturbative).**
- **Citation:** M. Visser, B. Bassett, S. Liberati, "Superluminal censorship", *Nucl. Phys. Proc. Suppl.* **88**, 267–270 (2000). arXiv:gr-qc/9810026v2 (1999-12-15). DOI 10.1016/S0920-5632(00)00782-9.
- **Result:** In linearized gravity about Minkowski, NEC makes light cones narrow. Shapiro delay is "always a delay … never an advance".
- **Scope:** The v2 comment notes that the non-perturbative null-infinity analysis was abandoned.
- **Status:** Derivation (perturbative).

**5.17 Gao & Wald (2000). Theorem.**
- **Citation:** S. Gao, R. M. Wald, "Theorems on gravitational time delay and related issues", *Class. Quantum Grav.* **17**, 4999–5008 (2000). arXiv:gr-qc/0007021v2 (2000-07-28). DOI 10.1088/0264-9381/17/24/305.
- **Hypotheses:** NEC plus the null generic condition.
- **Result:**
  - (1) In null-geodesically complete spacetimes, fastest null geodesics between distant points avoid any given compact set.
  - (2) With a timelike conformal boundary, fastest null geodesics between boundary points lie in the boundary.
- **Status:** Theorem.

**5.18 Alcubierre (1994). Derivation.**
- **Citation:** M. Alcubierre, "The warp drive: hyper-fast travel within general relativity", *Class. Quantum Grav.* **11**, L73–L77 (1994). arXiv:gr-qc/0009013v1 (2000-09-05; posted after publication). DOI 10.1088/0264-9381/11/5/001.
- **Result:** Local expansion behind and contraction ahead of the ship allow arbitrarily large speed. "exotic matter will be needed".
- **Status:** Derivation.

**5.19 Santiago, Schuster & Visser (2022). Theorem-level general argument.**
- **Citation:** J. Santiago, S. Schuster, M. Visser, "Generic warp drives violate the null energy condition", *Phys. Rev. D* **105**, 064038 (2022). arXiv:2105.03079v2 (2022-02-25). DOI 10.1103/PhysRevD.105.064038.
- **Result:** "all physically reasonable warp drives will violate the null energy condition". They therefore violate WEC, SEC and DEC as well. In modified gravity they violate the null convergence condition.
- **Critique of positive-energy claims:** The positive-energy claims check only Eulerian observers.
- **Status:** Theorem-level general argument. The authors' 2023 GRG paper calls it "fully general, but implicit".

**5.20 Barzegar, Buchert & Vigneron (2026). Theorems and critique (preprint).**
- **Citation:** H. Barzegar, T. Buchert, Q. Vigneron, "General formalism, classification, and demystification of the current warp-drive spacetimes", arXiv:2602.16495v1 (2026-02-18). Preprint, no journal reference at fetch.
- **Result:** Classifies warp models, proves "several new no-go theorems" and identifies errors in physicality claims.
- **Status:** Theorems and critique (preprint).

---

## Area 6. The 3+1 formalism and numerical-relativity textbooks

**6.1 Arnowitt, Deser & Misner (1962; republished 2008). Foundational derivation.**
- **Citation:** R. Arnowitt, S. Deser, C. W. Misner, "The Dynamics of General Relativity", ch. 7 (pp. 227–265) in *Gravitation: an introduction to current research*, ed. L. Witten (Wiley, 1962). Republished in *Gen. Relativ. Gravit.* **40**, 1997–2027 (2008), DOI 10.1007/s10714-008-0661-1. arXiv:gr-qc/0405109v1 (2004-05-19).
- **Status:** Foundational derivation (Hamiltonian formulation; lapse and shift).

**6.2 Gourgoulhon (2007 notes; 2012 book). Lecture notes and textbook.**
- **Notes:** E. Gourgoulhon, "3+1 Formalism and Bases of Numerical Relativity", arXiv:gr-qc/0703035v1 (2007-03-06), 220 pp.
  - Contents, from the abstract: geometry of hypersurfaces and foliations; 3+1 Einstein equations; matter; conformal decomposition; asymptotic flatness and global quantities; the initial data problem; foliation and coordinate choice; evolution schemes.
- **Book:** *3+1 Formalism in General Relativity*, Lecture Notes in Physics **846** (Springer, 2012), DOI 10.1007/978-3-642-24525-1 (Crossref).
  - The subtitle "Bases of Numerical Relativity" is **UNVERIFIED** from the Crossref record.
- **Anchors:** The kinematics of designed metrics (lapse, shift, extrinsic curvature, Eulerian energy).

**6.3 Alcubierre (2008). Textbook.**
- **Citation:** M. Alcubierre, *Introduction to 3+1 Numerical Relativity* (Oxford University Press, 2008). DOI 10.1093/acprof:oso/9780199205677.001.0001 (Crossref).
- **Check:** The series and volume (International Series of Monographs on Physics) and the contents are **UNVERIFIED**.
- **Status:** Textbook.

**6.4 Baumgarte & Shapiro (2010, 2021). Textbooks.**
- *Numerical Relativity* (Cambridge University Press, 2010), DOI 10.1017/CBO9781139193344. Crossref gives only the main title; the subtitle "Solving Einstein's Equations on the Computer" is **UNVERIFIED** from metadata.
- *Numerical Relativity: Starting from Scratch* (Cambridge University Press, 2021), DOI 10.1017/9781108933445.
- **Status:** Textbooks.

**6.5 Shibata. Textbook.**
- **Citation:** M. Shibata, *Numerical Relativity* (World Scientific, "100 Years of General Relativity" series). DOI 10.1142/9692. Crossref issue date is 2015-05-11; the year printed on the book is **UNVERIFIED**.
- **Status:** Textbook.

**6.6 Cauchy problem and kinematics. PARTIAL (metadata only).**
- Y. Fourès-Bruhat, "Théorème d'existence pour certains systèmes d'équations aux dérivées partielles non linéaires", *Acta Math.* **88**, 141–225 (1952), DOI 10.1007/BF02392131.
- Y. Choquet-Bruhat, R. Geroch, "Global aspects of the Cauchy problem in general relativity", *Commun. Math. Phys.* **14**, 329–335 (1969), DOI 10.1007/BF01645389.
- L. Smarr, J. W. York, "Kinematical conditions in the construction of spacetime", *Phys. Rev. D* **17**, 2529–2551 (1978), DOI 10.1103/PhysRevD.17.2529.
- **Anchors:** Well-posedness; what "prescribing" a metric means dynamically.

**6.7 Helmerich et al. (2024), Warp Factory. Numerical toolkit.**
- **Citation:** C. Helmerich, J. Fuchs, A. Bobrick, L. Sellers, B. Melcher, G. Martire, "Analyzing warp drive spacetimes with Warp Factory", *Class. Quantum Grav.* **41**, 095009 (2024). arXiv:2404.03095v2 (2024-04-10). DOI 10.1088/1361-6382/ad2e42.
- **Result:** A numerical toolkit that evaluates the Einstein equations and energy conditions for general warp metrics. It post-processes prescribed metrics.
- **Status:** Numerical toolkit.
- **Anchors:** The prior art for verification pipelines.

**6.8 Clough, Dietrich & Khan (2024). Numerical (full GR evolution).**
- **Citation:** K. Clough, T. Dietrich, S. Khan, "What no one has seen before: gravitational waveforms from warp drive collapse", *Open J. Astrophys.* **7** (2024). arXiv:2406.02466v2 (2024-07-24). DOI 10.33232/001c.121868.
- **Result:** A time evolution of a warp drive with a stiff-equation-of-state fluid. It gives the gravitational-wave signal from "containment failure" and bears on the "dynamical evolution and stability of spacetimes that violate the null energy condition".
- **Status:** Numerical (full GR evolution).
- **Anchors:** Coupled dynamics, as distinct from prescribed-geometry audits.

---

## Area 7. Existing monographs and textbook-like treatments

**7.1 Visser (1995). Monograph.**
- **Citation:** M. Visser, *Lorentzian Wormholes: From Einstein to Hawking* (AIP Press, 1995).
- **Check:** ISBNs 1-56396-394-9 and 1-56396-653-0 and a median length of 412 pp come from the Open Library catalogue. The contents were not read: **PARTIAL**. It predates rigorous curved-space QEIs, the ANEC proofs of 2016–17, QNEC, SNEC and DSNEC, and all numerical warp work.

**7.2 Lobo (ed.) (2017). Edited collection.**
- **Citation:** F. S. N. Lobo (ed.), *Wormholes, Warp Drives and Energy Conditions*, Fundamental Theories of Physics **189** (Springer, 2017). ISBN 978-3-319-55181-4 (hardcover), 978-3-319-55182-1 (eBook). DOI 10.1007/978-3-319-55182-1.
- **Table of contents (from the Springer page, read):**
  - **Part I, wormholes:**
    - Lobo, "Wormhole Basics";
    - Kleihaus & Kunz, "Rotating Wormholes";
    - Harko, Kovács & Lobo, accretion-disk signatures;
    - Sushkov, "Horndeski Wormholes";
    - Garattini & Lobo, "Self-Sustained Traversable Wormholes";
    - Bronnikov, "Trapped Ghosts…";
    - Olmo & Rubiera-Garcia, "Geons in Palatini Theories".
  - **Part II, energy conditions:**
    - Martín-Moruno & Visser, pp. 193–213;
    - Fewster, "Quantum Energy Inequalities", pp. 215–254.
  - **Part III, warp drives:**
    - Alcubierre & Lobo, "Warp Drive Basics", pp. 257–279 (arXiv:2103.05610v1);
    - Barceló & Liberati, "Probing Faster than Light Travel and Chronology Protection with Superluminal Warp Drives", pp. 281–300.
- **Character:** A research collection. It has no unified pedagogy and does not cover 3+1 numerics.

**7.3 Everett & Roman. Popular science.**
- **Citation:** A. Everett, T. Roman, *Time Travel and Warp Drives: A Scientific Guide to Shortcuts through Time and Space* (University of Chicago Press), 280 pp.
- **Year:** The publisher page lists **2011**; the book is commonly cited as 2012. **Resolve before citing.**
- **Check:** The table of contents was read (14 chapters, including "'Don't Be So Negative': Exotic Matter").
- **Level:** "no math beyond high school algebra".

**7.4 Krasnikov (2018). Research monograph.**
- **Citation:** S. Krasnikov, *Back-in-Time and Faster-than-Light Travel in General Relativity*, Fundamental Theories of Physics **193** (Springer, 2018). ISBN 978-3-319-72753-0. DOI 10.1007/978-3-319-72754-7.
- **Check:** The Springer table of contents was read.
  - Classical part: geometry; physical predilections; shortcuts; time machines; a no-go theorem for the artificial time machine; paradoxes.
  - Semiclassical part: quantum corrections; WEC-related quantum restrictions; primordial wormhole; beyond the horizon.
- **Character:** A research monograph on causality and FTL. It has no design or verification methodology.

**7.5 Earman (1995). Philosophy of physics. PARTIAL.**
- **Citation:** J. Earman, *Bangs, Crunches, Whimpers, and Shrieks: Singularities and Acausalities in Relativistic Spacetimes* (Oxford University Press, 1995), 257 pp (Open Library).
- **Check:** The contents were not read.

**7.6 Frontiers of Propulsion Science (2009). PARTIAL.**
- **Citation:** *Frontiers of Propulsion Science* (AIAA, 2009). DOI 10.2514/4.479953.
- **Check:** The editors (commonly Millis & Davis) do not appear in the Crossref metadata; editors and chapter list are **UNVERIFIED**.

**7.7 Review chapters and lecture notes that function as textbook material.**
- Lobo 2008, arXiv:0710.4474v1 (2007-10-24), a 52-pp review chapter in *Classical and Quantum Gravity Research* (Nova). The Nova volume details are from the arXiv journal reference only.
- Kontou–Sanders 2020 (1.1); Fewster 2012 (2.17); Fliss 2026 (2.27); Hollands–Wald 2015 (4.6); Friedman–Higuchi 2006 (5.7).

**7.8 Research-level engineered-metric papers the book must engage.**
- **Natário 2002:** "Warp drive with zero expansion", *Class. Quantum Grav.* **19**, 1157 (2002), arXiv:gr-qc/0110086v3. Expansion and contraction are "a marginal consequence of the choice made by Alcubierre".
- **Van Den Broeck 1999:** *Class. Quantum Grav.* **16**, 3973 (1999), arXiv:gr-qc/9905084v5. The total negative mass drops to "a few solar masses", and the geometry "satisfies the quantum inequality".
- **Lentz 2021:** *Class. Quantum Grav.* **38**, 075015 (2021, Crossref), arXiv:2006.07125v2. Claims superluminal solitons with purely positive energy density.
- **Bobrick & Martire 2021:** *Class. Quantum Grav.* **38**, 105009, arXiv:2102.06824v2.
  - Presents a general warp model and subluminal positive-energy spherically symmetric drives.
  - Argues "any warp drive requires propulsion".
- **Fell & Heisenberg 2021:** *Class. Quantum Grav.* **38**, 155020, arXiv:2104.06488v4. Positive semi-definite Eulerian energy.
- **Fuchs et al. 2024:** *Class. Quantum Grav.* **41**, 095013, arXiv:2405.02709v1. A constant-velocity **subluminal** warp drive that satisfies all energy conditions, obtained by adding a regular matter shell with positive ADM mass.
- **Schuster, Santiago & Visser 2023:** *Gen. Relativ. Gravit.* **55** (2023), arXiv:2205.15950v2. Mass in Natário warp drives; NEC, WEC, SEC and DEC are violated.
- **Critiques:** Santiago–Schuster–Visser 2022 (5.19) and Barzegar et al. 2026 (5.20) dispute the superluminal positive-energy claims.

**Gap assessment, based on the searches run in this pass (no exhaustive bibliographic survey).**
- **What the searches returned:** No graduate textbook on the design of engineered metrics. Monographs cover wormholes (Visser, pre-2000 constraints), causality and FTL (Krasnikov) or popular exposition (Everett–Roman). There is one edited research collection (Lobo 2017). Numerical-relativity texts treat 3+1 evolution for sources that obey the energy conditions.
- **What no single book combines:**
  - (i) the 3+1 *inverse problem*: prescribe lapse and shift, then read off Eulerian and all-observer stress-energy;
  - (ii) Hawking–Ellis typing of the required source, including symmetry obstructions;
  - (iii) pointwise, averaged, QEI, QNEC, SNEC and DSNEC constraints with their exact scopes;
  - (iv) semiclassical response: anomaly-driven vacuum polarization, horizon formation and instabilities, and Hawking/Unruh/Tolman temperatures;
  - (v) causality and topology theorems as design constraints;
  - (vi) candidate NEC-violating source theories (Horndeski and beyond) with their stability status;
  - (vii) verification methodology: constraint residuals, energy-condition sampling over all observers, and full nonlinear evolution;
  - (viii) crewed-transit observables (proper time, tidal tensors, acceleration).
- **Post-2016 results absent from every book located:** ANEC proofs, QNEC proofs, SNEC and DSNEC, the 2021–2026 warp positivity debate and no-go theorems, and numerical warp evolution.

---

## Area 8. Higher-derivative NEC-violating theories: the open source class

**8.1 Horndeski (1974). Theorem.**
- **Citation:** G. W. Horndeski, "Second-order scalar-tensor field equations in a four-dimensional space", *Int. J. Theor. Phys.* **10**, 363–384 (1974). DOI 10.1007/BF01807638. The Springer abstract was read.
- **Result:** Constructs the most general second-order Euler–Lagrange tensors from Lagrangians of metric, scalar and derivatives of arbitrary order in 4D. They derive from a Lagrangian at most second order in derivatives.
- **Status:** Theorem.

**8.2 Dubovsky, Grégoire, Nicolis & Rattazzi (2006). Theorem-level in a class, plus counterexamples.**
- **Citation:** "Null energy condition and superluminal propagation", *JHEP* **03** (2006) 025. arXiv:hep-th/0512260v2 (2006-04-19). DOI 10.1088/1126-6708/2006/03/025.
- **Result:** NEC violation implies instability "in a large class of situations, including isotropic solids and fluids". Consistent effective field theories with stable NEC-violating backgrounds exist; they need "lack of isotropy of the background and the presence of superluminal modes".
- **Status:** Theorem-level within a class, plus counterexamples.

**8.3 Creminelli, Luty, Nicolis & Senatore (2006). Derivation (EFT).**
- **Citation:** "Starting the universe: stable violation of the null energy condition and non-standard cosmologies", *JHEP* **12** (2006) 080. arXiv:hep-th/0606090v2 (2006-12-08). DOI 10.1088/1126-6708/2006/12/080.
- **Result:** A ghost condensate with softly broken shift symmetry violates NEC "without developing any instabilities". Stability requires dH/dt ≲ H².
- **Status:** Derivation (EFT).

**8.4 Adams, Arkani-Hamed, Dubovsky, Nicolis & Rattazzi (2006). Derivation.**
- **Citation:** "Causality, analyticity and an IR obstruction to UV completion", *JHEP* **10** (2006) 014. arXiv:hep-th/0602178v2 (2006-03-31). DOI 10.1088/1126-6708/2006/10/014.
- **Result:** Wrong-sign leading irrelevant operators give superluminal fluctuations around backgrounds. Such theories cannot be embedded in UV theories with standard S-matrix analyticity.
- **Status:** Derivation.
- **Anchors:** The superluminality objection to NEC-violating EFTs.

**8.5 Deffayet, Pujolàs, Sawicki & Vikman (2010). Derivation.**
- **Citation:** "Imperfect Dark Energy from Kinetic Gravity Braiding", *JCAP* **10** (2010) 026. arXiv:1008.0048v2 (2010-09-24). DOI 10.1088/1475-7516/2010/10/026.
- **Result:** Second-derivative scalar interactions without extra degrees of freedom ("kinetic braiding") make the scalar stress tensor imperfect. The scalar can "cross the phantom divide with neither ghosts nor gradient instabilities".
- **Status:** Derivation.

**8.6 Creminelli, Nicolis & Trincherini (2010). Derivation.**
- **Citation:** "Galilean Genesis: an alternative to inflation", *JCAP* **11** (2010) 021. arXiv:1007.0027v2 (2010-10-21). DOI 10.1088/1475-7516/2010/11/021.
- **Result:** A drastic NEC violation, Ḣ ≫ H², based on Galileons, "without instabilities".
- **Status:** Derivation.

**8.7 Rubakov (2014). Review.**
- **Citation:** V. A. Rubakov, "The null energy condition and its violation", *Phys. Usp.* **57**, 128–142 (2014). arXiv:1401.4024v2 (2014-02-25). DOI 10.3367/UFNe.0184.201402b.0137.
- **Result:** Second-derivative Lagrangians with second-order field equations admit NEC-violating solutions "having no obvious pathologies". Applications include cosmology and "the creation of a universe in the laboratory".
- **Status:** Review.

**8.8 Libanov, Mironov & Rubakov (2016). Theorem within the class.**
- **Citation:** "Generalized Galileons: instabilities of bouncing and Genesis cosmologies and modified Genesis", *JCAP* **08** (2016) 037. arXiv:1605.05992v2 (2016-08-16). DOI 10.1088/1475-7516/2016/08/037.
- **Result:** In "a popular class of generalized Galileon theories", spatially flat *bouncing* cosmologies "either are plagued with these instabilities or have singularities". The same holds for Genesis models with a → const as t → −∞. Added NEC-obeying matter coupled only gravitationally does not change this. A modified Genesis *evades* the no-go.
- **Status:** Theorem within the class.

**8.9 Kobayashi (2016). Theorem.**
- **Citation:** T. Kobayashi, "Generic instabilities of nonsingular cosmologies in Horndeski theory: A no-go theorem", *Phys. Rev. D* **94**, 043511 (2016). arXiv:1606.05831v2 (2016-08-09). DOI 10.1103/PhysRevD.94.043511.
- **Result:** Extends 8.8 to *full* Horndeski. Non-singular spatially flat models suffer gradient instabilities or a tensor-sector pathology; "one must go beyond the Horndeski theory".
- **Status:** Theorem.

**8.10 Creminelli, Pirtskhalava, Santoni & Trincherini (2016). Derivation (EFT of perturbations).**
- **Citation:** "Stability of geodesically complete cosmologies", *JCAP* **11** (2016) 047. arXiv:1610.04207v2 (2016-11-29). DOI 10.1088/1475-7516/2016/11/047.
- **Result:** The gradient instability is avoidable only if the operator ⁽³⁾R δN is present *and its coefficient changes sign*. That operator is characteristic of beyond-Horndeski theories.
- **Status:** Derivation (EFT of perturbations).

**8.11 Ijjas & Steinhardt (2017). Derivation.**
- **Citation:** A. Ijjas, P. J. Steinhardt, "Fully stable cosmological solutions with a non-singular classical bounce", *Phys. Lett. B* **764**, 289–294 (2017). arXiv:1609.01253v5 (2020-11-18). DOI 10.1016/j.physletb.2016.11.047.
- **Result:** Using the L₄ Galileon, non-singular bounces "non-pathological for all times".
- **Relation to 8.9:** How this evades the Kobayashi no-go was not examined in this pass and is **UNVERIFIED**.
- **Status:** Derivation.

**8.12 Kolevatov, Mironov, Sukhov & Volkova (2017). Derivation (explicit construction).**
- **Citation:** "Cosmological bounce and Genesis beyond Horndeski", *JCAP* **08** (2017) 038. arXiv:1705.06626v2 (2017-06-05). DOI 10.1088/1475-7516/2017/08/038.
- **Result:** A spatially flat bounce in beyond-Horndeski theory that is "non-singular and stable throughout the whole evolution".
- **Status:** Derivation (explicit construction).

**8.13 Kobayashi (2019). Review.**
- **Citation:** T. Kobayashi, "Horndeski theory and beyond: a review", *Rep. Prog. Phys.* **82**, 086901 (2019). arXiv:1901.07183v2 (2019-07-19). DOI 10.1088/1361-6633/ab2429.
- **Coverage:** NEC-violating cosmology, DHOST theories and their status after GW170817, the Vainshtein mechanism, and hairy black holes.
- **Status:** Review.

**8.14 Rubakov (2016), Galileon wormholes. Derivation.**
- **Citation:** V. A. Rubakov, "Can Galileons support Lorentzian wormholes?", *Theor. Math. Phys.* **187**, 743–752 (2016). arXiv:1509.08808v3 (2015-12-18). DOI 10.1134/S004057791605010X.
- **Result:** ANEC violation and perturbative stability pull against each other. The tension rules out such wormholes in 3D; in 4D any wormholes "must have fairly contrived shapes".
- **Status:** Derivation.

**8.15 Evseev & Melichev (2018). Theorem (linear stability).**
- **Citation:** O. A. Evseev, O. I. Melichev, "No static spherically symmetric wormholes in Horndeski theory", *Phys. Rev. D* **97**, 124040 (2018). arXiv:1711.04152v1 (2017-11-11; the arXiv title misspells "sphericaly"). DOI 10.1103/PhysRevD.97.124040.
- **Result:** 4D Horndeski "does not admit stable, static, spherically symmetric, asymptotically flat, Lorentzian wormholes".
- **Status:** Theorem (linear stability).

**8.16 Franciolini, Hui, Penco, Santoni & Trincherini (2019). Derivation (EFT of perturbations).**
- **Citation:** "Stable wormholes in scalar-tensor theories", *JHEP* **01** (2019) 221. arXiv:1811.05481v2 (2019-01-29). DOI 10.1007/JHEP01(2019)221.
- **Result:** Beyond-Horndeski theories "can have wormhole solutions that are free of ghost and gradient instabilities". Horndeski forbids them.
- **Status:** Derivation (EFT of perturbations).

**8.17 Mironov, Rubakov & Volkova (2019, 2023). Derivation.**
- **2019:** "More about stable wormholes in beyond Horndeski theory", *Class. Quantum Grav.* **36**, 135008 (2019). arXiv:1812.07022v2 (2019-06-05).
  - The no-go proof "does not go through beyond Horndeski". The paper gives an example, but its stability analysis is incomplete.
- **2023:** "In hot pursuit of a stable wormhole in beyond Horndeski theory", *Phys. Rev. D* **107**, 104061 (2023). arXiv:2212.05969v1 (2022-12-12). DOI 10.1103/PhysRevD.107.104061.
  - An example that meets all stability constraints for high-energy modes. "Slow" tachyonic instabilities remain unconstrained.
- **Status:** Derivation.

**8.18 Mironov & Volkova (2024). Derivation.**
- **Citation:** "Complete stability for spherically symmetric backgrounds in beyond Horndeski theory", arXiv:2404.06297v2 (2025-01-17). The comments place it in the IJMPA ICNFP2022 special issue; volume and page are **UNVERIFIED**.
- **Result:** A full set of conditions ruling out ghosts, gradient instabilities, tachyons and superluminal modes for static spherically symmetric quadratic beyond-Horndeski backgrounds.
- **Status:** Derivation.

**8.19 Gergely (2026). Derivation (algebraic classification).**
- **Citation:** L. Á. Gergely, "Fluid interpretation, Hawking–Ellis classification, and energy conditions of the proper kinetic gravity braiding stress tensor", arXiv:2608.15228v1 (2026-08-15). The comments say "Accepted for publication in Physical Review D"; volume and article number are **UNVERIFIED** as of 2026-09-26.
- **Method:** A 2+1+1 decomposition adapted to the scalar gradient.
- **Result:**
  - Braiding generates heat fluxes and anisotropic stresses, unlike k-essence.
  - For open-region null gradients the braiding stress tensor has null-dust form.
  - Hawking–Ellis types:
    - timelike sector: type I (positive discriminant), type II (on the discriminant hypersurface), type IV (negative discriminant);
    - spacelike sector: the same generic branches plus type II/III degeneracies;
    - null open-region sector: type II.
  - NEC "excludes Types III and IV". For spacelike gradients it excludes every nonzero radial heat flux or mixed anisotropy.
  - Quoted from the abstract: "admissible spacelike proper braiding is diagonal", while in the timelike sector the energy conditions bound the total heat flux.
- **Status:** Derivation (algebraic classification).
- **Anchors:** Typing and screening candidate braiding sources for a designed metric. Links to 1.3–1.6 and 8.5.

**8.20 Cross-references.** Banerjee et al. 2023 (1.10) give type III effective stress tensors in Horndeski theory. Fliss et al. 2024 (2.23) cover non-minimally coupled scalars under EFT control.

---

## Results commonly overstated (checked against the sources above)

1. **Null-contracted QEIs (Fewster–Roman 2003).**
   - There is no lower bound for averages along **null geodesics** in 4D Minkowski (free scalar, Theorem II.1).
   - There **is** a state-independent lower bound for null-contracted stress averaged along **timelike worldlines**, in any globally hyperbolic spacetime and for any mass m ≥ 0 (Theorem III.1, Eq. III.10).
   - The brief's lead reverses this.
2. **Achronal ANEC is unproven for interacting fields in curved spacetime.**
   - Proofs exist in these settings:
     - Minkowski space: Faulkner et al. (continuum assumptions); Hartman et al. (interacting UV fixed point, d > 2).
     - 2D: Verch; Wald–Yurtsever for curved 2D with a massless free field.
     - Free fields in restricted curved settings: Kontou–Olum 2015 (first order in curvature, null convergence condition); Fewster–Olum–Pfenning (flat tubes).
   - Test-field counterexamples to *achronal* ANEC exist: Urban–Olum (conformal scalar, conformally flat) and Ishibashi–Maeda–Mefford (holographic).
   - The *self-consistent* achronal form is a conjecture (Graham–Olum). Wall's derivation of it assumes the GSL and fails once gravitons are quantized.
3. **"QIs forbid wormholes and warp drives."**
   - Ford–Roman and Pfenning–Ford assume that flat-space QIs hold in regions small compared with the curvature radius. They bound scale ratios and wall thicknesses.
   - Van Den Broeck's geometry is stated to satisfy the QI.
   - State-independent QEIs are established only for specific free fields. The non-minimally coupled scalar has only state-dependent QEIs, and conformally coupled free bosons have unbounded smeared null energy (Fliss et al. 2025).
   - For interacting theories QEIs are largely open; the exceptions are 2D CFTs and the Ising model.
4. **SNEC is a conjecture.** Its constant B is undetermined and it rests on G_N ∼ 1/N. The proved relatives are narrower: a cutoff-dependent SNEC for free and super-renormalizable theories (Fliss–Freivogel) and DSNEC for free fields in Minkowski. Curved-space and interacting versions remain open.
5. **QNEC.** It is proved in flat space: for free and super-renormalizable theories (Bousso et al.) and for QFTs with an interacting UV fixed point (Balakrishnan et al.). In curved space it rests on the Quantum Focussing Conjecture.
6. **Topological censorship assumes ANEC**, even though the FSW abstract says NEC. Graham–Olum weaken the hypothesis to self-consistent achronal ANEC plus the generic condition.
7. **Chronology protection is a conjecture.** Hawking proves AWEC violation on a compactly generated Cauchy horizon. Kay–Radzikowski–Wald prove that ⟨T⟩ is singular at base points. Kim–Thorne found the divergence weak and argued for a quantum-gravity cutoff.
8. **The Horndeski "no-go" results are specific:**
   - to spatially flat nonsingular *cosmologies* over their whole history (Libanov–Mironov–Rubakov in a subclass; Kobayashi in full Horndeski);
   - to static spherically symmetric asymptotically flat *wormholes* (Evseev–Melichev).
   - Stable NEC violation over finite epochs is established: ghost condensate, Galilean Genesis, kinetic-braiding phantom crossing.
   - Beyond-Horndeski theories evade both no-go results. For wormholes, however, the published examples still leave slow tachyonic modes unconstrained (2023).
9. **Unruh-state type IV** is a test-field result. With Einstein back-reaction, type I is forced in static, stationary-axisymmetric and bifurcate-Killing-horizon settings (Martín-Moruno–Visser 2021).
10. **Warp positivity claims.**
    - Only Fuchs et al. 2024 (subluminal, with a regular matter shell) satisfies all energy conditions.
    - The superluminal positive-energy claims (Lentz; Fell–Heisenberg) are disputed by Santiago–Schuster–Visser (Eulerian-only checks) and by Barzegar et al. 2026.
    - Olum 1998 proves that superluminal travel, as he defines it, requires WEC violation under the generic condition.
11. **Bibliographic slips.**
    - The Barceló–Visser title is "Twilight **for** the energy conditions?".
    - Dvali "2010" is the published version of a 2007 preprint.
    - Everett–Roman appears as 2011 on the publisher page and 2012 in common citations.
    - FSW's erratum retracts only the secondary "passive censorship" claim.

---

## Unverified or partially verified items

- **Content not read (metadata only):**
  - papers: Ford 1978; Morris–Thorne 1988 (AJP); Tipler 1977; Candelas 1980; Fulling 1973; Davies 1975; Roman 1986 (content known secondhand); Smarr–York 1978; Fourès-Bruhat 1952; Choquet-Bruhat–Geroch 1969;
  - books: Hawking–Ellis 1973; Birrell–Davies 1982; Parker–Toms 2009; Wald 1994; Earman 1995; Visser 1995; Alcubierre 2008; Baumgarte–Shapiro 2010 and 2021; Shibata.
- **Geroch 1967:** the abstract is seen only in search snippets; the primary page returned 403.
- **Unresolved bibliographic details:**
  - the Unruh temperature formula as worded in Unruh 1976 (not in the abstract);
  - the Gourgoulhon book subtitle, the Alcubierre series number, the Baumgarte–Shapiro 2010 subtitle, and Shibata's printed year;
  - the editors of *Frontiers of Propulsion Science*;
  - the year of Everett–Roman;
  - how Fewster's 2012 notes correspond to his 2017 chapter.
- **Journal details pending:**
  - Banerjee et al. 2023 (PRD);
  - Mironov–Volkova 2024 (IJMPA);
  - Gergely 2026 (accepted in PRD, not yet assigned);
  - Penrose–Sorkin–Woolgar 1993 (venue);
  - Visser 2002 (conference volume);
  - Pfenning–Ford's journal companion to the dissertation.
- **Preprints without peer-reviewed status at fetch:** Fliss–Rolph 2025/26 (also note its v2 state-dependence clarification); Barzegar–Buchert–Vigneron 2026; Fliss 2026 lectures.
- **Not assessed:** how Ijjas–Steinhardt 2017 relates to the Kobayashi no-go.
- **Not located, so excluded:** Deser–Duff–Isham 1976 (nonlocal conformal anomalies); the DOI lookup failed.

---

## Closing table: topic × anchor papers × status × known exceptions

| Topic | Anchor papers (item numbers) | Status | Known exceptions and scope limits |
|---|---|---|---|
| Pointwise energy conditions fail in QFT | EGJ 1965 (1.11); Kontou–Sanders 2020 (1.1); Curiel 2017 (1.2); Barceló–Visser 2002 (1.9) | Theorem (EGJ); review | Also violated by simple classical fields, e.g. non-minimally coupled scalars |
| Hawking–Ellis types and source typing | Hawking–Ellis 1973 (1.12); Martín-Moruno–Visser 2018a (1.3), 2018b (1.4), 2020 (1.5), 2021 (1.6); Banerjee et al. 2023 (1.10); Gergely 2026 (8.19) | Derivation | Type III is incompatible with planar or spherical symmetry; type IV is a test-field effect; back-reaction forces type I in symmetric settings |
| Non-linear energy conditions | Martín-Moruno–Visser 2013 (1.8), 2017 (1.7) | Proposals | Weaker link to geodesic focusing |
| Worldline QEIs (energy density) | Ford–Roman 1995 (2.2), 1997 (2.3); Flanagan 1997 (2.11); Fewster–Eveson 1998 (2.12); Fewster 2000 (2.13); Fewster–Smith 2008 (2.14) | Theorem for free fields | Non-minimal coupling: state-dependent only; interacting theories open except 2D CFTs and Ising; no spatially averaged QI in 4D (Ford–Helfer–Roman 2002, 2.16) |
| Null-contracted QEIs | Fewster–Roman 2003 (2.15); Ford–Roman 1995 (2.2, 2D); Fewster–Hollands 2005 (2.18) | Theorem | Timelike-worldline bound exists in any globally hyperbolic spacetime; no bound along null geodesics in 4D; 2D null QEIs exist |
| Quantum interest | Ford–Roman 1999 (2.8); Fewster–Teo 2000 (2.9); Teo–Wong 2002 (2.10) | Theorem (models) | In 4D a positive δ-pulse cannot compensate a negative δ-pulse; the general 4D conjecture remains open |
| QIs applied to engineered geometries | Ford–Roman 1996 (2.4); Pfenning–Ford 1997 (2.6); Pfenning 1998 (2.7); Van Den Broeck 1999 (7.8); Kontou 2024 (2.26) | Derivation (flat-QI-in-small-region assumption) | Assumption justified in static spacetimes at short sampling (2.7); geometry-dependent loopholes, e.g. Van Den Broeck |
| Smeared null bounds | Freivogel–Krommydas 2018 (2.19); Freivogel–Kontou–Krommydas 2022 (2.20); Fliss–Freivogel 2022 (2.21); Fliss–Freivogel–Kontou 2023 (2.22); Fliss et al. 2024 (2.23), 2025 (2.24); Fliss–Rolph 2025/26 (2.25) | SNEC: conjecture. Free-field SNEC with cutoff and DSNEC: theorem. Large-N: evidence | Conformally coupled free bosons have unbounded smeared null energy; curved space and interacting theories open |
| QNEC | Bousso et al. 2016a (conjecture), 2016b (proof); Balakrishnan et al. 2019; Ceyhan–Faulkner 2020 (all 2.29) | Theorem/proof in flat space | Curved space rests on the QFC conjecture |
| ANEC in Minkowski | Klinkhammer 1991 (3.1); Wald–Yurtsever 1991 (3.2); Verch 2000 (3.3); Faulkner et al. 2016 (3.4); Hartman et al. 2017 (3.5) | Theorem (free fields; 2D); proof (physics-level; d > 2) | Hartman et al. exclude free and asymptotically free theories (covered separately); Faulkner et al. need continuum assumptions |
| ANEC in curved spacetime | Wald–Yurtsever 1991 (3.2); Fewster–Olum–Pfenning 2007 (3.9); Kontou–Olum 2013, 2015 (3.14); Flanagan–Wald 1996 (3.8) | Theorems in restricted settings; derivation (perturbative) | Counterexamples: Visser 1995 (3.6) and 1996–97 (3.7), incomplete or chronal geodesics; Urban–Olum 2010 (3.12, achronal, test field); Ishibashi–Maeda–Mefford 2019 (3.16, holographic); Klinkhammer (compactified, chronal) |
| Self-consistent achronal ANEC | Graham–Olum 2007 (3.10); Wall 2010 (3.11); Kontou–Sanders 2020 (1.1) | Conjecture; conditional derivation | No known self-consistent violation; Wall's argument fails with quantized gravitons |
| Trace anomaly | Capper–Duff 1974 (4.1); Christensen–Fulling 1977 (4.4); Deser–Schwimmer 1993 (4.3); Duff 1994 (4.2) | Derivation (established) | Coefficients depend on field content; renormalization ambiguities (Hollands–Wald 2015, 4.6) |
| Vacuum polarization near horizons | Candelas 1980 (4.9); Page 1982 (4.8); Anderson–Hiscock–Samuel 1995 (4.10); Visser 1996–97 (3.7) | Numerical, semi-analytic | Test-field limit; state-dependent (Boulware, Hartle–Hawking, Unruh) |
| Type IV in the Unruh state | Roman 1986 (4.11); Visser 1997 (3.7); Abdolrahimi–Page–Tzounis 2019 (4.12); Martín-Moruno–Visser 2021 (1.6) | Numerical | Removed by back-reaction in symmetric settings |
| Horizon temperatures | Hawking 1975 (4.13); Unruh 1976 (4.14); Gibbons–Hawking 1977 (4.17); Tolman 1930 and Tolman–Ehrenfest 1930 (4.18); Crispino et al. 2008 (4.15) | Derivation (established) | Tolman needs static equilibrium; Hawking flux depends on the state; geodesic detectors see no Hawking flux near the horizon (Unruh) |
| Species bound | Dvali 2010 (4.19); Dvali–Redi 2008 (4.20) | Derivation | Model-dependent completion near Λ_G |
| Validity of semiclassical gravity | Flanagan–Wald 1996 (3.8); Hu–Verdaguer 2008 (4.7); Hollands–Wald 2015 (4.6) | Derivation, review | Planck-scale transverse structure lies outside its validity |
| Semiclassical instability of engineered horizons | Hiscock 1997 (4.21); Finazzi–Liberati–Barceló 2009 (4.22) | Derivation | Hiscock uses a 2D reduction; Finazzi et al. treat a quantum field on a fixed dynamical geometry |
| Topology change | Geroch 1967 (5.1, partial); Tipler 1976 and 1977 (5.2); Borde 1994 (5.3) | Theorem | Kinematically possible; dynamically obstructed in dimension ≥ 3 for causally compact spacetimes |
| Topological censorship | Friedman–Schleich–Witt 1993 (5.5); Galloway–Schleich–Witt–Woolgar 1999 (5.6); Graham–Olum 2007 (3.10) | Theorem (assumes ANEC) | Curved-space ANEC violations weaken the hypothesis; the achronal self-consistent version is conjectural |
| Chronology protection | Hawking 1992 (5.8); Kim–Thorne 1991 (5.9); Kay–Radzikowski–Wald 1997 (5.10); Visser 2002 (5.11) | AWEC-violation theorem plus conjecture | Kim–Thorne: weak divergence; Kay–Radzikowski–Wald: singular only at base points |
| Faster-than-light travel requires energy-condition violation | Olum 1998 (5.15); Visser–Bassett–Liberati 2000 (5.16); Gao–Wald 2000 (5.17); Krasnikov 1998 (5.13); Santiago–Schuster–Visser 2022 (5.19); Barzegar et al. 2026 (5.20) | Theorem (definition-dependent) | Positive-energy warp claims: subluminal Fuchs et al. 2024 holds; superluminal claims disputed |
| Faster-than-light travel implies CTCs | Morris–Thorne–Yurtsever 1988 (5.4); Everett–Roman 1997 (5.12); Shoshany–Snodgrass 2024 (5.14) | Derivation (constructive) | A single Krasnikov tube has no CTCs; two tubes or two warp drives are required |
| 3+1 formalism and well-posedness | ADM 1962/2008 (6.1); Gourgoulhon 2007/2012 (6.2); Alcubierre 2008 (6.3); Baumgarte–Shapiro 2010, 2021 (6.4); Shibata (6.5); Fourès-Bruhat 1952, Choquet-Bruhat–Geroch 1969 (6.6, partial) | Foundational derivation; theorems | Standard numerical-relativity texts assume sources that obey the energy conditions |
| Numerical analysis of warp spacetimes | Warp Factory 2024 (6.7); Clough–Dietrich–Khan 2024 (6.8) | Numerical | Warp Factory post-processes prescribed metrics; Clough et al. evolve a warp drive with a stiff-equation-of-state fluid |
| Stable NEC violation in EFT | Dubovsky et al. 2006 (8.2); Creminelli–Luty–Nicolis–Senatore 2006 (8.3); Adams et al. 2006 (8.4); Deffayet et al. 2010 (8.5); Creminelli–Nicolis–Trincherini 2010 (8.6); Rubakov 2014 (8.7) | Derivation | Requires anisotropy or superluminal modes (Dubovsky et al.); obstruction to UV completion (Adams et al.) |
| Horndeski cosmological no-go | Libanov–Mironov–Rubakov 2016 (8.8); Kobayashi 2016 (8.9); Creminelli–Pirtskhalava–Santoni–Trincherini 2016 (8.10); Kolevatov et al. 2017 (8.12); Ijjas–Steinhardt 2017 (8.11) | Theorem (within the class) | Evaded beyond Horndeski and by modified Genesis |
| Horndeski wormhole no-go and escapes | Rubakov 2016 (8.14); Evseev–Melichev 2018 (8.15); Franciolini et al. 2019 (8.16); Mironov–Rubakov–Volkova 2019, 2023 (8.17); Mironov–Volkova 2024 (8.18) | Theorem (no-go); derivation (examples beyond Horndeski) | Slow tachyonic modes unconstrained in the published examples |
| Kinetic-braiding stress tensor typing | Gergely 2026 (8.19); Deffayet et al. 2010 (8.5) | Derivation | NEC excludes types III and IV; preprint accepted in PRD |

Evidence files: `lit_foundations_evidence/arxiv_abstract_pages_parsed_2026-09-26.txt` contains all parsed arXiv pages. The same folder holds the thirteen `pdftotext` full-text extractions consulted.
