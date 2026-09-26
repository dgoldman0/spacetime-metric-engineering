# Coverage map: evidence inventories mapped to the book structure

Working inventory for the scaffold (not book text). Compiled 2026-09-26 against
`05_STRUCTURE.md` (Chapters 1–32, Appendices A–D). Every evidence item in the
inputs below is either placed in a section packet (Part 1), listed as an orphan
with a proposed home, or listed as a deliberate exclusion with its reason
(Part 2). Part 3 assesses balance; Part 4 checks the reading order.

Inputs:
- `02_SYNTHESIS.md`: design responses §2.1–2.5; practices A1–A11, B1–B7,
  C1–C6, D1–D5; truisms §3.5; dropped items §3.6; corrections §4.
- `vetting/P01_classify_demand_before_sources.md` (cited as P01 §2a–§2i).
- `inventory/knobs_one_space.md` (parts, knobs K1–K27, identities I1–I26,
  complete tensor §3.2, caveats §3.3).
- `inventory/knobs_throat_era.md` (parts, knobs G1–G31, M1–M8, D1–D3, S1–S18,
  identities I1–I28, Q1–Q13, later findings L1–L7, invalidation register §7).
- `inventory/lit_foundations.md`, `inventory/lit_design_strategy.md`
  (Parts A–G), `inventory/lit_engineering_methods.md`.
- `inventory/incidents_may_june.md` and `inventory/incidents_september.md`
  (closing tables, counter-evidence and recurring lessons only).
- The quiz bank `toolkit/active_rail_quiz_system/src/data/questionBank.js`
  (tracks and topic modules only; 200 questions; file dated 25 May 2026).

## Legend

**Source prefixes.**
- Practice IDs A1–A11, B1–B7, C1–C6, D1–D5 are the `02_SYNTHESIS.md` §3 IDs,
  written plain. Verdicts are quoted from §3.
- `P01 §2x`: the P01 vetting file.
- `OS-`: `knobs_one_space.md`. OS-P# parts, OS-K# knobs, OS-I# identities
  (OS-I4c and OS-I5c are its compiler-checked sub-forms), OS-T3.2 the
  complete tensor of class C0 (§3.2), OS-§3.3.n caveat n, OS-§5 gaps.
- `TE-`: `knobs_throat_era.md`. TE-G#, TE-M# and TE-S# knobs, TE-DR# its
  demand-reading knobs D1–D3, TE-I# identities (§5.1–5.3), TE-Q# source
  identities (§5.4), TE-L# later findings (§0.5), TE-§7 invalidation register,
  TE-§8 gaps.
- `LF n.m`: `lit_foundations.md` item. `LDS:Key`: `lit_design_strategy.md`
  entry; `LDS E.x`, `F.x`, `G.x`, `C.7`, `D.13`: its tables and assessments;
  `LDS-E.5`: the lapse-only NEC lemma derived in that survey.
- `LEM`: `lit_engineering_methods.md` items (V, N, T, D, S, A series). The
  prefix keeps them apart from the practice IDs.
- `MJ`: `incidents_may_june.md` codes (I-01…I-20, CE-1…CE-8, P01+).
  `SE`: `incidents_september.md` codes (incidents A1…E18, counter-evidence
  F1…F15, recurring lessons L1…L24). These codes point to evidence only; the
  book states the practice, its physical basis and its failure mode.
- `QB Track / Module (n)`: quiz-bank track and topic module with question count.

**Literature entries.** Authors Year, arXiv identifier with the version pinned
in the inventory, then [status; verification].
- Status, as recorded: `thm` theorem; `proof` physics-level proof; `der`
  derivation; `num` numerical; `conj` conjecture or proposal; `rev` review or
  lecture notes; `claim` asserted or unrefereed claim; `constr` explicit
  construction; `meth` method or toolkit; `std` engineering standard or
  practice source; `emp` experiment or case-study evidence. Where the two
  physics surveys record different statuses, both appear.
- Verification, as recorded: `FT` full text read; `FT-OCR` full text from a
  scan; `TL` text layer of a third-party copy; `AB` abstract only; `AB+`
  abstract plus a targeted text search; `PT` metadata or secondary source
  only; `UV` unverified.
- "(version not recorded)" marks an arXiv identifier that the inventory gives
  without a version.

**Identity tags** (05 vocabulary). `T` theorem with stated assumptions; `D`
derived in the book and symbolically checked; `D*` a derivation exists in the
inventories and still needs the book's written derivation and a symbolic
check; `L` established literature result; `H` heuristic.

**Design labels and markers for measured examples (field d).** Design labels
follow `knobs_one_space.md` §0.3.
- `✓` gate-passing one-space flat-slice design without beta075 heritage:
  D-lap (convex plateau, sheath e¹; the disclosure embodiment), D-cmp (flat
  compartment), D-fr (front elements), D-trim (trimmed reference and its
  speed-scaled variants).
- `βh` one-space design carrying beta075-heritage parameters (service
  schedule or standing support stretch ≈630) on a new, separately gated
  geometry: D-ch and D-cen pass; D-amp (flat support) passes from e⁷; D-1S
  with held support keeps residual Type IV bands, its static-support variant
  passes.
- `βx` D-ax0: the beta075 service transplanted into an axial core whose layer
  carries Type IV at every tested width. Cautionary use only.
- `D-sph` the constant-radius spherical track: beta075-derived service on a
  new geometry that passes the Type IV gate, still two-ended (TE-L4). Usable
  only as a labelled demonstration of an identity.
- `†` rests on the beta075 geometry that failed the Type IV gate (TE-§7.1).
  **Unsuitable** except as an explicit cautionary example.
- `§` rests on the static zero-shift slice of repaired beta075 (blind to
  Type IV and to currents, TE-L6). **Unsuitable** except as a cautionary
  example.
- `2E` pre-beta075 throat-lineage measurement: two-ended geometry (TE-L4),
  type untested, packet readings under TE-L2. **Unsuitable** except as a
  cautionary example or as a data check of an identity.

A dash (—) means the inventories supply nothing for that field.

---

# Part 1. Evidence packets by chapter and section

## Front matter (Preface; How to read this book; Notation and conventions)

- **(a) Literature:** gap assessment LF 7.1–7.8 (monographs located:
  Visser 1995, no arXiv [monograph; PT]; Lobo (ed.) 2017, no arXiv
  [collection; PT, table of contents read]; Everett–Roman 2011/2012, no arXiv
  [popular; PT, year unresolved]; Krasnikov 2018, no arXiv [monograph; PT,
  table of contents read]; Earman 1995 [PT]; *Frontiers of Propulsion
  Science* 2009 [PT, editors UV]; Lobo 2008 review, arXiv:0710.4474v1 [rev;
  AB]; Alcubierre–Lobo "Warp Drive Basics", arXiv:2103.05610v1 [rev; PT]).
  Claim wording: Oreskes–Shrader-Frechette–Belitz 1994, no arXiv (LEM V16)
  [std; AB]; NASA-STD-7009B 2024 (LEM V13) [std; FT].
- **(b) Identities:** conventions of 05 (signature, units, 3+1 split with
  β^z = −v, ρ, j_i, S_ij, null normalization u·k = −1).
- **(c) Practices:** D1 (name results by the check passed; refined) sets the
  claim-tag vocabulary; placement rules of 05.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** 02 §1 states "the gap is confirmed" from searches that LF
  itself calls non-exhaustive; the Preface should state the search basis.
  Standard GR texts named in the conventions (MTW) are absent from every
  inventory.

## Part I. Foundations

### Chapter 1. Spacetime engineering: the inverse problem

#### 1.1 Geometry as the engineered object
- **(a) Literature:** Alcubierre 1994, arXiv:gr-qc/0009013v1 [der; FT];
  Morris–Thorne 1988, no arXiv (AJP 56, 395) [der; FT-OCR in LDS D.1, PT in
  LF 5.4]; Pendry–Schurig–Smith 2006, no arXiv (LEM T1) [meth; AB];
  Leonhardt–Philbin 2006, arXiv:cond-mat/0607418 (version not recorded)
  (LEM T12) [der; FT]; Roache 2002, no arXiv (LEM V5) [std; AB];
  Salari–Knupp 2000, no arXiv (LEM V6) [std; FT]; Le 2026a,
  arXiv:2605.25417v2 (cite v2; v3 is a different paper) [num; FT];
  Barzegar–Buchert–Vigneron 2026, arXiv:2602.16495v1 [thm + critique; FT,
  preprint]; Barceló–Liberati–Visser, *Analogue Gravity*,
  arXiv:gr-qc/0505065v4 (LEM A1) [rev; FT].
- **(b) Identities:** T = G/8π read as a demand [L].
- **(c) Practices:** A7 (the geometry fixes the demand; evidence-backed).
  LEM principal finding 2: metric-first design is the method of manufactured
  solutions run in reverse; calibration differs from validation (LEM V9).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Einstein equation (7); Metric
  basics (8).
- **(f) Open:** the transformation-optics analogy is kinematic only (LEM T12
  note; LEM Area 3 lesson 6). The MMS reading is the survey's own inference.

#### 1.2 A first tour of five canonical geometries
- **(a) Literature:** Morris–Thorne 1988 [der; FT-OCR]; Visser 1989a,
  arXiv:0809.0907v1 [der; FT]; Alcubierre 1994, arXiv:gr-qc/0009013v1 [der;
  FT]; Natário 2002, arXiv:gr-qc/0110086v3 [thm (Thm 1.7) + der; FT];
  Krasnikov 1998, arXiv:gr-qc/9511068v6 (v1–v5 withdrawn) [der under
  assumptions (LF 5.13), Prop. 1 thm (LDS); FT]; Everett–Roman 1997,
  arXiv:gr-qc/9702049v1 [der; FT]; static lapse geometry:
  Bolívar–Abellán–Vasilev 2026, arXiv:2608.15000v1 [thm + constr; FT of
  abstract and quoted sections]; positive-mass shell: Fuchs et al. 2024,
  arXiv:2405.02709v1 [num; FT; disputed].
- **(b) Identities:** TE-I21 Ellis throat in closed form [ultrastatic,
  α = A = 1, β = 0: ρ = p_l = −a²/(8π(l² + a²)²), p_Ω = −ρ] — D*;
  OS-I2 pure-lapse stress [static flat slices, uniform shift] — D;
  LDS-E.5 lapse-only region on flat slices — D.
- **(c) Practices:** A3 (declare topology, ends and exterior for each
  geometry; evidence-backed).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics (10);
  Metric basics (1).
- **(f) Open:** Fuchs et al. 2024 disputed (Le 2026a finds a Type IV
  smoothing tail in 22 of 25 probes; Barzegar–Buchert–Vigneron Error 18: not
  a TOV solution; LDS F.1.2). 05 leaves the "static lapse geometry" example
  unspecified: the flat-slice lapse-only region (NEC fails somewhere,
  LDS-E.5) and the curved-slice released-lapse hollow core (all energy
  conditions on a compactness interval, Bolívar et al.) teach opposite
  lessons.

#### 1.3 The design loop (geometry → demand → tests → supply → verification)
- **(a) Literature:** Molesky et al. 2018, arXiv:1801.06715 (version not
  recorded) (LEM T14) [meth; FT]; Le 2026a, arXiv:2605.25417v2 (source-first
  shells; five-criterion standard) [num; FT]; Oberkampf–Trucano 2002, no
  arXiv (LEM V9) [std; FT]; Browning 2001, no arXiv (LEM D5) [std; FT];
  Helmerich et al. 2024 (Warp Factory), arXiv:2404.03095v2 [meth/num; FT].
- **(b) Identities:** —
- **(c) Practices:** A5 (class-level exclusions and normalized magnitudes
  first; evidence-backed, the central ordering principle); A7; A8; C6
  (supported; imported). Truism: stage-gate ordering (02 §3.5). P01 §2a
  cost asymmetry (a complete classification takes minutes, source work
  takes months).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Modeling discipline (3); QB
  Design review and synthesis / Paper-to-design transfer (1), recast.
- **(f) Open:** the cost-asymmetry figure (186 s against months) comes from
  one project incident; state it as an observed asymmetry.

#### 1.4 What makes it hard
- **(a) Literature:** Santiago–Schuster–Visser 2022, arXiv:2105.03079v2
  [thm-level general argument; FT]; Olum 1998, arXiv:gr-qc/9805003v2 [thm;
  FT]; Gao–Wald 2000, arXiv:gr-qc/0007021v2 [thm; FT]; Kontou–Sanders 2020,
  arXiv:2003.01815v2 [rev; FT]; Pfenning–Ford 1997, arXiv:gr-qc/9702026v3
  [der, conditional on flat-space QI; FT]; Finazzi–Liberati–Barceló 2009,
  arXiv:0904.0141v2 [der (1+1); FT]; Borde 1994, arXiv:gr-qc/9406053v1 [thm;
  AB]; Dubovsky et al. 2006, arXiv:hep-th/0512260v2 [thm-level in a class;
  AB]; Barzegar–Buchert–Vigneron 2026, arXiv:2602.16495v1 [thm; FT].
- **(b) Identities:** SSV ∫ρ = −∫ω²/32π [flat unit-lapse slices, localized
  flow] — L; LDS-E.5 — D.
- **(c) Practices:** A5. LEM Area 3 lesson 6 (a medium's gap is a
  fabrication gap; spacetime's gap is a physics gap).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Energy conditions (10), part.
- **(f) Open:** —

#### 1.5 Performance inside one spacetime
- **(a) Literature:** Krasnikov 1998, arXiv:gr-qc/9511068v6 [FT];
  Everett–Roman 1997, arXiv:gr-qc/9702049v1 [FT]; Gao–Wald 2000,
  arXiv:gr-qc/0007021v2 [thm; FT]; Olum 1998, arXiv:gr-qc/9805003v2 [thm;
  FT]; Low 1999, arXiv:gr-qc/9812067v1 [thm; FT]; NASA Systems Engineering
  Handbook 2016, no arXiv (LEM S2) [std; FT]; Millis 2005, no arXiv
  (LEM S6) [std; FT].
- **(b) Identities:** —
- **(c) Practices:** A4 (evidence-backed); truism: measures of
  effectiveness. Evidence pointers: SE L20, SE E4, MJ I-02, MJ I-03.
- **(d) Measured examples:** OS-K1 mean lead over flat-space light
  0.05/0.55/0.89/1.13 for lanes 1.2/1.5/1.8/2.1c (D-ch, βh, passes).
- **(e) Quiz:** —
- **(f) Open:** duplicates 11.3 (both carry A4).

### Chapter 2. Lorentzian geometry for design

#### 2.1 Causal structure and proper time
- **(a) Literature:** Hawking–Ellis 1973, no arXiv [monograph; PT];
  Penrose–Sorkin–Woolgar 1993, arXiv:gr-qc/9301015v2 [thm; FT; journal
  venue UV].
- **(b) Identities:** OS-I20 radial null rays dℓ/dσ = −β ± α/√γ_ℓℓ keep
  their order; static observers exist iff α > |β| [class C0] — D*;
  TE-I6 packet norm −α² + A(v + β)², dτ/dσ = √(−norm) [radial worldline in
  the spherical warped-product class] — D*.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Causal structure (7); Metric
  basics (8); Geodesics (2).
- **(f) Open:** thin: standard GR textbooks (MTW, Wald 1984) are not in the
  inventories and Hawking–Ellis is metadata only.

#### 2.2 Observers, frames and tetrads
- **(a) Literature:** Santiago–Schuster–Visser 2022, arXiv:2105.03079v2
  [FT]; Helmerich et al. 2024, arXiv:2404.03095v2 (observer sampling)
  [meth; FT]; Le 2026b, arXiv:2602.18023v6 (Eulerian reading misses ≈73% of
  sampled WEC violations in the Rodal wall) [thm + certified num; FT,
  preprint]; Carneiro et al. 2022, arXiv:2201.05684v2 (negative energy as a
  "reference problem"; cautionary) [claim; AB].
- **(b) Identities:** OS-T3.2 orthonormal frame n = (∂_σ − β∂_z)/α, e_z,
  e_r, e_φ [class C0] — D.
- **(c) Practices:** A1 (preview).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Metric basics.
- **(f) Open:** LDS F.1.7 (frame-effect reading) settled: frame choice hides
  negative energy from one observer family only.

#### 2.3 Killing vectors, stationarity and conserved quantities
- **(a) Literature:** Natário 2002, arXiv:gr-qc/0110086v3 (stationarity
  requires |v_s| < 1; E(1 + X·n) = E₀) [der; FT]; Barceló et al. 2022,
  arXiv:2207.06458v1 [der + estimates; FT]; Gao–Wald 2000 [thm; FT].
- **(b) Identities:** OS-I12 Killing energy E = α√(m² + |k|²) − b k_z
  [stationary pattern frame of a steady lane, flat exterior] — D*.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Geodesics (2).
- **(f) Open:** —

#### 2.4 Horizons and surface gravity
- **(a) Literature:** Hawking 1975, no arXiv [der; AB]; Gibbons–Hawking
  1977, no arXiv [der; AB]; Barceló et al. 2022, arXiv:2207.06458v1
  (Cauchy-horizon points only where the transverse derivative of the flow
  vanishes) [der; FT]; Finazzi–Liberati–Barceló 2009, arXiv:0904.0141v2
  [der; FT]; Natário 2002 (Mach-cone horizon) [der; FT];
  Clark–Hiscock–Larson 1999, arXiv:gr-qc/9907019v1 [num; AB].
- **(b) Identities:** OS-I13 Killing-horizon criterion: the surface
  α² = b² is null exactly where its transverse gradient vanishes;
  κ = |∂_ζα| where the shift vanishes [stationary pattern frame of C0] — D*
  (same criterion as Barceló et al. 2022, L); TE-I5 g_σσ ≥ 0 ⇔ |β| ≥ α/√A
  marks an ergo-like region, a horizon only if null rays cannot leave
  [spherical warped products, radial] — D*.
- **(c) Practices:** A9 (preview).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp geodesics
  (9), part.
- **(f) Open:** textbook anchors for Killing horizons and surface gravity
  are absent from the inventories.

#### 2.5 Congruences, expansion and focusing
- **(a) Literature:** Hochberg–Visser 1998 PRL, arXiv:gr-qc/9802048v3
  [thm; FT]; Hochberg–Visser 1998 PRD, arXiv:gr-qc/9802046v2 [thm; AB];
  Graham–Olum 2007, arXiv:0705.3193v2 (generic condition; focusing) [conj +
  conditional thms; FT]; Freivogel–Kontou–Krommydas 2022,
  arXiv:2012.11569v2 [thm conditional on SNEC; FT]; Santiago–Schuster–Visser
  2022 (Raychaudhuri argument for the SEC) [FT]; Borde 1987 focusing
  theorem [UV; cited only through GO07].
- **(b) Identities:** TE-I10 θ₊θ₋ = −(4α²/R²)(∇R)² for the symmetry
  spheres (sign-level proxy) [spherical warped products] — D*; TE-I11 radial
  bundle focusing d(δl)/dσ = (−∂_lβ ± ∂_l(α/√A))δl, independent of the areal
  radius [same class] — D*; OS-I20 ray-family ordering — D*.
- **(c) Practices:** congruences, not single rays (MJ I-14; general, n = 1);
  one sentence.
- **(d) Measured examples:** OS-K20 a fan grazing the cone tip forms a fold
  caustic (width 9×10⁻⁴, 14 crossings), energy bounded (D-trim, ✓);
  TE-G26 bundle widening by β smoothing 1.94×, areal smoothing 0.989×
  (†, cautionary; confirms TE-I11).
- **(e) Quiz:** QB Established foundations / Geodesics (2); Causal
  structure.
- **(f) Open:** Borde 1987 original unread; TE-I10 and TE-I11 are inventory
  derivations.

#### 2.6 Optical geometry of static metrics
- **(a) Literature:** Leonhardt–Philbin 2006, arXiv:cond-mat/0607418
  (version not recorded) (LEM T12) [der; FT]; Gordon 1923, no arXiv [PT];
  Plebański 1960, no arXiv [PT]; Barceló–Liberati–Visser,
  arXiv:gr-qc/0505065v4 (sound speed as lapse, flow as shift) [rev; FT];
  Tolman 1930, no arXiv [der; AB].
- **(b) Identities:** OS-I16 lapse cavity: index 1/α, α|k| conserved, total
  internal reflection outside arcsin(α_in/α_out) [static pure-lapse regions,
  uniform shift] — D*; flat-slice index n = 1/α from Plebański's relations
  (LEM T12 derivation, "mine") — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 compartment escape cone 1.05° at 2.1c,
  0.22° at 10c (D-trim, ✓); OS-P15 hole boundary as a lapse cavity (✓).
- **(e) Quiz:** —
- **(f) Open:** uses the lapse before Chapter 3 defines it (Part 4).

### Chapter 3. The 3+1 split

#### 3.1 Foliations, lapse and shift
- **(a) Literature:** Arnowitt–Deser–Misner 1962/2008, arXiv:gr-qc/0405109v1
  [foundational der; AB]; Gourgoulhon 2007 notes, arXiv:gr-qc/0703035v1
  [rev; AB]; Gourgoulhon 2012 book, no arXiv [PT, subtitle UV];
  Alcubierre 2008 book [PT]; Baumgarte–Shapiro 2010, 2021 [PT]; Shibata
  [PT, year UV]; Smarr–York 1978, no arXiv [PT].
- **(b) Identities:** 05 conventions (line element; carriage at speed v has
  β^z = −v) — L.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / ADM split (7).
- **(f) Open:** the 3+1 textbooks are metadata-only in the inventories.

#### 3.2 Extrinsic curvature
- **(a) Literature:** Natário 2002 (K = ½(∂_iX_j + ∂_jX_i); expansion a free
  choice) [der; FT]; Santiago–Schuster–Visser 2022 [FT]; Gourgoulhon 2007
  [rev; AB].
- **(b) Identities:** in class C0, K_ẑẑ = β_z/α and K_ẑr̂ = β_r/2α (step of
  OS-I1) — D; OS-T3.2 notation 𝒦 = β_z/α, n(f) = α⁻¹(∂_σ − β∂_z)f — D.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / ADM split.
- **(f) Open:** —

#### 3.3 The constraints read as demand
- **(a) Literature:** ADM 1962/2008 [AB]; Gourgoulhon 2007 [AB];
  Santiago–Schuster–Visser 2022 (Eulerian flux f = ∇×(∇×v)/16π) [FT];
  Le 2026b, arXiv:2602.18023v6, Lemma 2 (8π|j| = ½|∇×(∇×β)|) [thm; FT];
  Santos-Pereira–Abreu–Ribeiro series (arXiv:2008.06560v1,
  2101.11467v2, 2108.10960v1, 2111.01298v1, 2512.12541v1, 2510.11836v3;
  thesis 2508.20348v1) [der; AB] (a shift along the motion couples
  off-diagonal components).
- **(b) Identities:** 16πρ = ³R + K² − K_ijK^ij and
  8πj_i = D_jK^j_i − D_iK [general 3+1] — L; flat slices 16πρ = K² −
  K_ijK^ij (OS-I1 step) — D; OS-I10 static: 16πρ = ³R = −2Δ⊥A/A [static,
  zero shift, spatial metric dr² + r²dφ² + A²dz²] — D*.
- **(c) Practices:** A7.
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / ADM constraints (6).
- **(f) Open:** uses ρ and j before 4.1 formalizes observer components.

#### 3.4 Evolution equations and stresses
- **(a) Literature:** Gourgoulhon 2007 [AB]; ADM [AB]; Alcubierre 2008
  [PT]; Shoshany–Snodgrass 2024, arXiv:2309.10072v3 (stresses with ΔN/N,
  eq. 4.25) [constr + thm; FT].
- **(b) Identities:** OS-T3.2 spatial stresses with Q = n(𝒦) − 𝒦² [class
  C0] — D; OS-I2 8πT_ij = (δ_ij D²α − D_iD_jα)/α [static flat slices,
  uniform shift, any α(σ, x)] — D.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / ADM split; ADM constraints.
- **(f) Open:** —

#### 3.5 Worked examples (Morris–Thorne; Alcubierre and Natário; a lapse-only geometry)
- **(a) Literature:** Morris–Thorne 1988 (ρ = b′/(8πr²); the redshift
  function enters only the stresses) [der; FT-OCR]; Hochberg–Visser 1997,
  arXiv:gr-qc/9704082v1 [thm; FT]; Alcubierre 1994, eq. 19 [der; FT];
  Natário 2002 zero-expansion density [der; FT]; Lobo–Visser 2004,
  arXiv:gr-qc/0406083v2, eq. 10 [der; FT]; Rodal 2023 and 2024,
  arXiv:2512.20738v1 and arXiv:2512.19837v1 (four stress layers; Natário
  invariants 35× Alcubierre's) [der + num; AB]; LDS-E.5 lapse-only tensor
  [der, symbolically checked].
- **(b) Identities:** OS-I1 ρ = −(β_r/α)²/32π [class C0: flat static
  slices, A ≡ 1, shift along z depending on (σ, z, r), any lapse] — L at
  unit lapse (Alcubierre eq. 19; Lobo–Visser eq. 10; Barzegar–Buchert
  2025), D for general lapse (compiler-checked); OS-I2 — D; LDS-E.5 tensor
  G₀₀ = 0, 8παS_ij = δ_ij∇²α − ∂_i∂_jα [flat slices, static lapse, zero or
  uniform shift] — D; TE-I21 — D*.
- **(c) Practices:** A8 (identities before numerics; evidence-backed).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics (10).
- **(f) Open:** —

#### 3.6 ADM and Komar masses
- **(a) Literature:** Schuster–Santiago–Visser 2023, arXiv:2205.15950v2
  [der; FT (§2.3, conclusions); disputed]; Barzegar–Buchert–Vigneron 2026,
  Thm IV.19 (R-Warp ADM energy vanishes; ADM momentum generically nonzero)
  [thm; FT]; Lobo–Visser 2004 (zero ADM mass; the warp field must cancel the
  ship's mass) [der; FT]; Bobrick–Martire 2021, arXiv:2102.06824v2
  (truncation forces ∫4πw r²dr = 0) [der; FT]; Clough–Dietrich–Khan 2024,
  arXiv:2406.02466v2 (ADM mass conserved at zero, quasi-local mass rises)
  [num; FT]; Gao–Wald 2000 (DEC and a flat exterior force flatness) [thm;
  FT]; Penrose–Sorkin–Woolgar 1993 [thm; FT].
- **(b) Identities:** OS-I10 static energy and Komar balances:
  ρ√γ = −(1/8π)∂_r(r∂_rA) integrates to zero; 4πα(ρ + Σp_i) = D²α integrates
  to zero (zero Komar mass with an exactly flat exterior); a lapse maximum
  carries negative active mass on its shoulders [static, zero shift] — D*;
  LDS-E.5 Komar branches of the lapse lemma — D.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K11 energy identical for support lapse
  6/60/600 (D-amp, βh, passes at e⁷): confirms OS-I10 on data.
- **(e) Quiz:** —
- **(f) Open:** ADM-mass dispute (Schuster–Santiago–Visser 2023 against
  Barzegar–Buchert–Vigneron Thm IV.19; LDS F.1.3). Bondi mass and momentum
  are needed by 19.6 and 27.4 and have no section (Part 2).

### Chapter 4. Stress-energy and its algebra

#### 4.1 Components and observers
- **(a) Literature:** Kontou–Sanders 2020, arXiv:2003.01815v2 [rev; FT];
  Hawking–Ellis 1973 [PT]; Helmerich et al. 2024 [meth; FT]; Le 2026b
  [FT].
- **(b) Identities:** 05 conventions ρ = T(n, n), j_i, S_ij — L; TE-I3
  rest-frame quantities of a Type I radial block,
  ρ_rest = (ρ − p_l + sgn(ρ + p_l)√Δ)/2 and v = 2j/(ρ + p_l + sgn√Δ) [radial
  block of a spherical warped product] — D*.
- **(c) Practices:** A1 (preview).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Stress-energy basics (8).
- **(f) Open:** —

#### 4.2 Hawking–Ellis types and their scope
- **(a) Literature:** Hawking–Ellis 1973 [PT]; Martín-Moruno–Visser 2018,
  arXiv:1802.00865v2 (cores; types I and IV stable, II and III unstable)
  [der; AB]; Martín-Moruno–Visser 2018, arXiv:1806.02094v1 (Type III
  incompatible with planar or spherical symmetry) [der; AB];
  Martín-Moruno–Visser 2019/2020, arXiv:1907.01269v3 [der; AB];
  Martín-Moruno–Visser 2021, arXiv:2102.13551v2 (Type IV a test-field effect;
  back-reaction forces Type I in static, stationary-axisymmetric-horizon,
  bifurcate-Killing-horizon, axis and Bianchi I/FLRW settings) [der from
  symmetry (LF), thms (LDS); FT]; Abdolrahimi–Page–Tzounis 2019,
  arXiv:1607.05280v4 (Unruh state Type IV outside the horizon) [num; AB];
  Roman 1986, no arXiv [PT]; Banerjee et al. 2023, arXiv:2307.13846v2
  (Type III effective tensors in scalar-tensor theory) [der; AB; journal
  ref UV].
- **(b) Identities:** TE-I3 Δ_rad = (ρ + p_ℓ)² − 4j_ℓ² =
  T(k₊, k₊)T(k₋, k₋): the radial block is Type IV exactly where the two
  radial null energies differ in sign; the verdict is boost invariant
  [radial block, any spherical warped product] — D*.
- **(c) Practices:** correction 02 §4 (Type IV is a test-field effect in the
  Unruh state).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Stress-energy basics.
- **(f) Open:** the exterior interval 2m < r < 2√3 m is LF's reading of
  Martín-Moruno–Visser Eq. (B.5); the text extraction was garbled.

#### 4.3 Type from 3+1 data: zero momentum implies Type I
- **(a) Literature:** Santiago–Schuster–Visser 2022 §5 [FT]; Le 2026b
  Lemmas 2–3 [thm; FT]; Martín-Moruno–Visser 2021 [FT]; Rodal 2025,
  arXiv:2512.18008v1 (irrotational drive globally Type I) [num + der; AB].
- **(b) Identities:** P01 §2c: j_i = 0 makes n an eigenvector, so the tensor
  is Type I; a static metric in static slicing has K_ij = 0 and j = 0; Type
  IV needs 8πj_i = D_jK^j_i − D_iK ≠ 0 [any 3+1 slicing, any lapse] — D
  (the algebraic core; the literature states special cases, LDS E.4);
  OS-I2 [uniform-shift regions, any lapse and history] — D; TE-I22 static
  geometries are Type I in the radial block — D*; TE-I14 lapse-only dynamics
  carry no energy flux [static spatial metric, zero shift] — D.
- **(c) Practices:** A1; B5 (a surrogate can forbid a failure mode;
  evidence-backed).
- **(d) Measured examples:** TE-G5 attribution: static support with moving
  windows and zero shift gives 236 Type IV points, static support with the
  carrying flow and no windows gives 19 (†, cautionary); P01 §2c 4,504
  static control samples all Type I while every active phase carries a
  Type IV witness (†, cautionary).
- **(e) Quiz:** QB Established foundations / Stress-energy basics.
- **(f) Open:** —

#### 4.4 Canonical matter models and their types
- **(a) Literature:** Deffayet–Pujolàs–Sawicki–Vikman 2010,
  arXiv:1008.0048v2 (kinetic braiding makes the scalar stress imperfect)
  [der; AB]; Gergely 2026, arXiv:2608.15228v1 [der (classification); AB+;
  journal volume UV]; Martín-Moruno–Visser 2018 [AB]; Visser 1989a
  (negative-tension strings; field-theoretic strings carry positive
  tension) [der; FT]; Kontou–Sanders 2020 [FT]; Hawking–Ellis 1973 [PT].
- **(b) Identities:** TE-I4 constant areal radius gives an exact string
  cloud ρ = −p_ℓ = 1/(8πR²), invariant under boosts along the string
  [spherical warped products] — D*; TE-Q12 oriented ensembles
  T^Maxwell = u(δ − 2bb), T^sheet = −u(δ − aa), T^string = −u ss,
  H ≤ 2kE_material — D*; TE-I23 static canonical condensate
  (ρ, p_r, p_t) = (K+D+V+E, K+D−V−E, K−D−V+E); a minimally coupled scalar's
  radial block is never Type IV — D*; TE-S3 string-cloud backbone
  Φ/R²(1, −1, 0) and Maxwell ½E²(1, −1, 0, +1) — D*.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Stress-energy basics; Source
  model basics (5).
- **(f) Open:** thin: no string-cloud, perfect-fluid or Maxwell-stress
  textbook anchor in the inventories.

#### 4.5 Pointwise energy conditions; matrix-inequality form
- **(a) Literature:** Le 2026b, Theorem 1 (NEC, WEC and SEC as 4×4 linear
  matrix inequalities through the S-lemma; DEC needs two tests; no type
  classification and no rapidity cutoff) [thm; FT]; Kontou–Sanders 2020
  [rev; FT]; Curiel 2017, arXiv:1405.0403v1 [rev; AB];
  Martín-Moruno–Visser 2017, arXiv:1702.05915v3 [rev; AB];
  Martín-Moruno–Visser 2013, arXiv:1306.2076v3 (flux, trace-of-square and
  determinant conditions) [conj/proposal; AB]; Barceló–Visser 2002,
  arXiv:gr-qc/0205066v1 [essay; AB].
- **(b) Identities:** null energy is additive over components, so
  NEC-satisfying parts only add (basis of A6) — D.
- **(c) Practices:** A1 refinement (LMIs need no classification).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Energy conditions (10).
- **(f) Open:** non-linear energy conditions have no named section (Part 2).

### Chapter 5. Energy conditions and quantum bounds

#### 5.1 Quantum violation of pointwise conditions
- **(a) Literature:** Epstein–Glaser–Jaffe 1965, no arXiv
  (DOI 10.1007/BF02749799) [thm; AB]; Kontou–Sanders 2020,
  arXiv:2003.01815v2 [rev; FT]; Barceló–Visser 2002, arXiv:gr-qc/0205066v1
  [essay; AB]; Ford–Helfer–Roman 2002, arXiv:gr-qc/0208045v2 (no spatially
  averaged QI in 4D) [thm by counterexample; AB]; Olum–Graham 2003,
  arXiv:gr-qc/0205134v3 (static negative energy near a domain wall) [der;
  AB]; Martín-Moruno–Visser 2013, arXiv:1306.2076v3 [proposal; AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / QFT basics (9); Quantum basics
  (11); Quantum vacuum (2).
- **(f) Open:** needs Hadamard states and renormalized ⟨T⟩, which Chapter 7
  introduces (Part 4).

#### 5.2 Worldline QEIs and quantum interest
- **(a) Literature:** Ford 1978, no arXiv [PT]; Ford–Roman 1995,
  arXiv:gr-qc/9410043v1 [der (free field); FT]; Ford–Roman 1997,
  arXiv:gr-qc/9607003v2 (ρ̂ ≥ −3/(32π²t₀⁴) scalar, −3/(16π²t₀⁴)
  electromagnetic) [der; FT]; Flanagan 1997, arXiv:gr-qc/9706006v2 [thm
  (2D massless); AB]; Fewster–Eveson 1998, arXiv:gr-qc/9805024v2 [thm; AB];
  Fewster 2000, arXiv:gr-qc/9910060v2 [thm (microlocal); AB];
  Fewster–Smith 2008, arXiv:gr-qc/0702056v3 (absolute QEI) [thm; AB];
  Pfenning–Ford 1998, arXiv:gr-qc/9710055v1 (static spacetimes) [der; FT];
  Pfenning 1998 thesis, arXiv:gr-qc/9805037v1 [der; AB]; Ford–Roman 1999,
  arXiv:gr-qc/9901074v1 (quantum interest) [thm for the model; AB];
  Fewster–Teo 2000, arXiv:gr-qc/9908073v2 [thm; AB]; Teo–Wong 2002,
  arXiv:gr-qc/0206066v2 [thm (2D); AB]; Fewster–Hollands 2005,
  arXiv:math-ph/0412028v2 [thm; AB]; Fewster 2012 lectures,
  arXiv:1208.5399v1 [rev; AB]; Fliss 2026 lectures, arXiv:2605.18964v1
  [rev; AB]; Olum–Graham 2003 (interacting system violates QIs) [der; AB];
  Palessandro 2026, arXiv:2608.11817v1 [der; AB; new paper]. Kontou–Sanders 2020
  Table 3 (non-minimal coupling admits only state-dependent QEIs) [FT].
- **(b) Identities:** OS-I21 QI requirement N ≥ 64π²dτ₀⁴(L/ℓ_P)² ≡
  Q(L/ℓ_P)² from the Fewster–Roman bound [flat-space form; τ₀ short against
  curvature and inverse acceleration] — D* (an application of L).
- **(c) Practices:** —
- **(d) Measured examples:** OS-K13 staging lowers the QI requirement
  Q from 0.60 to 0.047, because QIs weigh long, weak deficits heavily (D-lap,
  ✓); OS-K27 Q = 0.013 (f = 0.1) and 3×10⁻⁶ (f = 0.01) (D-lap staged, ✓).
- **(e) Quiz:** QB Established foundations / Quantum inequalities (2); QB
  Published warp and wormhole context / Quantum inequalities (4).
- **(f) Open:** Pfenning–Ford 1998 eq. (48) coefficient reconstructed from a
  text layer (LDS G.2); correspondence of Fewster 2012 with the 2017 chapter
  UV; the thesis's journal companion UV; the general 4D quantum-interest
  conjecture open; the QI requirement was computed on D-lap only
  (OS-§5).

#### 5.3 Null-contracted bounds: timelike worldlines versus null geodesics
- **(a) Literature:** Fewster–Roman 2003, arXiv:gr-qc/0209036v2 (Thm II.1:
  no lower bound along null geodesics in 4D Minkowski; Thm III.1: a bound
  along timelike worldlines in any globally hyperbolic spacetime; Eq. III.10)
  [thm, both halves; FT]; Fewster–Hollands 2005 (2D null QEIs) [thm; AB];
  Ford–Roman 1995 (2D null QIs) [der; FT]; Fewster–Roman 2005,
  arXiv:gr-qc/0507013v1 (null-contracted QI applied to lapse-supported
  wormhole stress) [der; FT].
- **(b) Identities:** —
- **(c) Practices:** correction 02 §4 (null QEIs).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Quantum inequalities.
- **(f) Open:** content of the Fewster–Roman erratum (PRD 80, 069903, 2009)
  UV.

#### 5.4 SNEC, DSNEC and QNEC
- **(a) Literature:** Freivogel–Krommydas 2018, arXiv:1807.03808v4 (SNEC)
  [conj; FT]; Freivogel–Kontou–Krommydas 2022, arXiv:2012.11569v2 [thm
  conditional on SNEC; FT]; Fliss–Freivogel 2022, arXiv:2108.06068v1 [thm
  (free or super-renormalizable, with cutoff); AB]; Fliss–Freivogel–Kontou
  2023, arXiv:2111.05772v1 (DSNEC) [thm (free fields, Minkowski); AB];
  Fliss–Freivogel–Kontou–Pardo Santos 2024, arXiv:2309.10848v1 [der under
  EFT assumption; AB]; Fliss–Freivogel–Kontou–Pardo Santos 2025,
  arXiv:2412.10618v1 [der/evidence (large N); AB]; Fliss–Rolph 2025/26,
  arXiv:2510.26247v2 [der (LF), thm (LDS); AB; preprint]; Moghtaderi–Hull–Quintin–Geshnizjani
  2025, arXiv:2503.19955v2 [der conditional on SNEC; AB]; Bousso et al.
  2016a, arXiv:1506.02669v1 [conj; AB]; Bousso et al. 2016b,
  arXiv:1509.02542v2 [proof; AB]; Balakrishnan–Faulkner–Khandker–Wang 2019,
  arXiv:1706.09432v2 [proof; AB]; Ceyhan–Faulkner 2020, arXiv:1812.04683v2
  [thm; AB].
- **(b) Identities:** —
- **(c) Practices:** correction 02 §4 (SNEC is a conjecture; DSNEC and a
  free-field SNEC with cutoff are proven).
- **(d) Measured examples:** TE-DR2 SNEC screen: 0 violations in 175,851
  windows while the finite-domain ANEC total is negative; the harness floor
  −1/(4τ²) is 8π looser than the unit-normalized Freivogel–Krommydas form (†,
  cautionary; "SNEC-clean does not imply ANEC-clean").
- **(e) Quiz:** QB Established foundations / Quantum inequalities, part.
- **(f) Open:** SNEC constant B undetermined; Fliss–Rolph v2 clarifies
  state dependence of the higher-dimensional bound (read the full text);
  QNEC in curved space rests on the quantum focussing conjecture.

#### 5.5 ANEC: proofs, status in curved spacetime, achronality, counterexamples
- **(a) Literature:** Klinkhammer 1991, no arXiv [der/thm (free field); AB];
  Wald–Yurtsever 1991, no arXiv [thm; AB]; Verch 2000,
  arXiv:math-ph/9904036v1 [thm (2D); AB]; Faulkner–Leigh–Parrikar–Wang 2016,
  arXiv:1605.08072v1 [proof (flat); FT]; Hartman–Kundu–Tajdini 2017,
  arXiv:1610.05308v1 [proof (flat, d > 2); FT]; Visser 1995 scale anomalies,
  arXiv:gr-qc/9409043v1 [der (test field); AB]; Visser 1996–97 vacuum
  polarization I–IV, arXiv:gr-qc/9604007v1, gr-qc/9604008v1,
  gr-qc/9604009v1, gr-qc/9703001v1 [num/semi-analytic (test field); AB];
  Flanagan–Wald 1996, arXiv:gr-qc/9602052v2 [der (second order); AB];
  Ford–Roman 1996 (averaged conditions on half-geodesics of evaporating
  black holes), arXiv:gr-qc/9506052v2 [der; AB];
  Fewster–Olum–Pfenning 2007, arXiv:gr-qc/0609007v3 [thm; AB];
  Graham–Olum 2005, arXiv:hep-th/0506136v2 [der; AB]; Graham–Olum 2007,
  arXiv:0705.3193v2 (Condition 1; Lemma 1; Theorems 1–3) [conj + conditional
  thms; FT]; Wall 2010, arXiv:0910.5751v2 [conditional der; FT];
  Urban–Olum 2010, arXiv:0910.5925v2 [der (counterexample, test field); FT];
  Urban–Olum 2010b, arXiv:1002.4689v2 [der; AB]; Kontou–Olum 2013,
  arXiv:1212.2290v1 [conditional thm (LF), der on a conjectured QI (LDS);
  AB]; Kontou–Olum 2015,
  arXiv:1507.00297v2 [thm (free field, first order in curvature); FT];
  Ishibashi–Maeda–Mefford 2019, arXiv:1903.11806v1 [der (holographic); AB];
  Rosso 2020, arXiv:2005.06476v3 (extremal horizons and (A)dS; highly
  symmetric fixed backgrounds) [thm; AB]; Kontou–Sanders 2020
  formulations (i) and (ii) [rev; FT].
- **(b) Identities:** ANEC normalization: ∫T(k, k)dλ scales by c under
  k ↦ ck, so magnitudes carry the affine normalization and only the sign is
  invariant (Le 2026b §3.5) — L.
- **(c) Practices:** correction 02 §4 (achronal ANEC: global leads,
  completeness, generic condition; perturbative proofs; conjecture in
  general); affine parameters for averaged null conditions (MJ I-12, n = 1;
  one sentence).
- **(d) Measured examples:** OS-K2/OS-K4 first-light ANEC −0.0012 on the
  test trip, −202 and −2.2×10⁴ on long lanes (D-trim, ✓; sign only
  invariant); TE-DR2 finite-domain ANEC negative on the demanded total (†,
  cautionary).
- **(e) Quiz:** QB Established foundations / Energy conditions; QB
  Published warp and wormhole context / Quantum inequalities.
- **(f) Open:** self-consistent achronal ANEC is a conjecture; Wall's
  argument fails once gravitons are quantized; Klinkhammer, Wald–Yurtsever,
  Flanagan–Wald and Visser 1995 are cited in LDS only through verified
  papers (LDS G.2).

#### 5.6 Exact scopes for design use
- **(a) Literature:** LF "Results commonly overstated" items 1–11;
  Kontou–Sanders 2020 [FT]; Graham–Olum 2007 [FT]; Fewster–Roman 2003 [FT];
  Huey 2024, arXiv:2311.07193v3 (non-compact membranes outside the no-go
  hypotheses) [der; AB]; Shoshany–Snodgrass 2024 (Olum's generic condition
  fails for Riemann-flat passenger regions) [FT]; LDS F.2.1–F.2.8.
- **(b) Identities:** —
- **(c) Practices:** all eight corrections of 02 §4; A5 refinement (keep
  the exact scope of each exclusion).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** disputes LDS F.2.1–F.2.8.

### Chapter 6. Global structure: topology, causality, chronology

#### 6.1 Topology change
- **(a) Literature:** Geroch 1967, no arXiv [thm; PT, primary abstract UV];
  Tipler 1976, no arXiv [thm; AB, energy-condition hypothesis UV]; Tipler
  1977 [PT]; Borde 1994, arXiv:gr-qc/9406053v1 [thm; AB]; Li–Pendry 2008,
  arXiv:0806.4396 (version not recorded) (LEM T7; a topology choice removed
  singular demand, analogy) [meth; FT].
- **(b) Identities:** TE-I18 flare-out: (R′/A)′ = −(4πR/A)(ρ + p_ℓ); widening
  from R′ = 0 to R′/A = 1 costs an integrated radial null deficit ≥ 1 per
  end; the transition width sets only the peak [static spherical] — D*.
- **(c) Practices:** A3.
- **(d) Measured examples:** OS-K26 end-transition widths 0.75/1.5/3 give
  peak deficits −0.118/−0.058/−0.028 at a fixed opening of 1 per end
  (D-sph; identity demonstration); OS-K26 one-space alternative: the
  transverse layer carries ≈12× the static negative-null content (βx,
  cautionary).
- **(e) Quiz:** QB Published warp and wormhole context / Topological
  censorship (3), part.
- **(f) Open:** Geroch's primary page unread.

#### 6.2 Topological censorship
- **(a) Literature:** Friedman–Schleich–Witt 1993, arXiv:gr-qc/9305017v2
  (Theorem 1 assumes ANEC; erratum retracts only "passive censorship")
  [thm; FT]; Galloway–Schleich–Witt–Woolgar 1999, arXiv:gr-qc/9902061v2
  [thm; AB]; Friedman–Higuchi 2006, arXiv:0801.0735v2 [rev; AB];
  Graham–Olum 2007, Theorem 1 [conditional thm; FT]; Kontou 2024,
  arXiv:2405.05963v2 [rev + new result; FT]; Gao–Jafferis–Wall 2017,
  arXiv:1608.05687v3 (long wormholes) [der; FT];
  Maldacena–Milekhin–Popov 2018/2023, arXiv:1807.04726v3 [der; FT].
- **(b) Identities:** —
- **(c) Practices:** correction 02 §4 (censorship assumes ANEC).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Topological
  censorship (3).
- **(f) Open:** Graham–Olum abstract wording differs between the arXiv page
  and the pinned v2 PDF (LDS G.3).

#### 6.3 Causality conditions and time functions
- **(a) Literature:** Hawking–Ellis 1973 [PT]; Barzegar–Buchert–Vigneron
  2026, Thm IV.7 (a superluminal R-Warp model switched on from rest cannot
  be globally hyperbolic) [thm; FT]; Alcubierre 1994 (global hyperbolicity
  claimed for positive-definite γ_ij) [claim; FT]; Choquet-Bruhat–Geroch
  1969, no arXiv [PT].
- **(b) Identities:** OS-I19 σ is a global time function on one rail
  (g^σσ = −1/α² < 0), which gives stable causality [class C0] — D*; two
  rails in relative motion can close causal curves [analogy, no
  computation] — H.
- **(c) Practices:** correction 02 §4 (a time function gives stable
  causality, weaker than global hyperbolicity); A3 refinement (say which
  causality property a design has).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Causal structure (7).
- **(f) Open:** LDS F.1.11 (eternal against switched-on constructions).

#### 6.4 Faster-than-light theorems and their definitions
- **(a) Literature:** Olum 1998, arXiv:gr-qc/9805003v2 [thm; FT];
  Visser–Bassett–Liberati 2000, arXiv:gr-qc/9810026v2 (v1 non-perturbative
  claim withdrawn) [der (perturbative); FT]; Visser–Bassett–Liberati 1999,
  arXiv:gr-qc/9908023v1 [der; FT]; Low 1999, arXiv:gr-qc/9812067v1 [thm;
  FT]; Gao–Wald 2000, arXiv:gr-qc/0007021v2 [thm; FT];
  Penrose–Sorkin–Woolgar 1993 [thm; FT]; Krasnikov 1998, Prop. 1 [FT];
  Santiago–Schuster–Visser 2022 [FT]; Barzegar–Buchert–Vigneron 2026 [FT];
  Shoshany–Snodgrass 2024 (critique of Olum's definition) [FT]; theorem chain
  of LDS C.7: Gao–Wald Thm 1 in Galloway's null-line form plus Graham–Olum
  Lemma 1 give ANEC < 0 on a null line for a lead that persists between
  distant endpoints.
- **(b) Identities:** OS-I23 "a lead over light needs achronal ANEC
  violation" — L only in the qualified form (global lead, null completeness,
  generic condition); the unqualified project statement is withdrawn from
  use.
- **(c) Practices:** A4.
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Chronology
  concerns, part.
- **(f) Open:** LDS F.1.6, F.2.2, F.2.3 (Olum's definition; whether achronal
  ANEC rules out warp drives); Galloway's null splitting theorem cited only
  through Gao–Wald.

#### 6.5 Chronology and its protection conjecture
- **(a) Literature:** Hawking 1992, no arXiv [thm (AWEC on compactly
  generated Cauchy horizons) + conj; AB plus TL]; Kim–Thorne 1991, no arXiv
  [der + competing conjectures; AB]; Kay–Radzikowski–Wald 1997,
  arXiv:gr-qc/9603012v2 [thm (linear scalar); AB]; Visser 2002,
  arXiv:gr-qc/0204022v2 [rev; AB; venue UV]; Visser 1993,
  arXiv:hep-th/9202090v2 [claim; AB]; Visser 1997 (Roman ring),
  arXiv:gr-qc/9702043v1 [der; AB]; Morris–Thorne–Yurtsever 1988, no arXiv
  [der; FT-OCR]; Everett 1996, no arXiv [der; TL, symbols garbled];
  Everett–Roman 1997 (two tubes make a time machine) [FT];
  Shoshany–Snodgrass 2024 (two glued drives close a timelike geodesic)
  [FT]; Sajeendran–Ralph 2025, arXiv:2407.18993v2 [der; AB];
  González-Díaz 2000, arXiv:gr-qc/9907026v2 [claim (2D); AB]; Graham–Olum
  2007, Theorems 2–3 [FT].
- **(b) Identities:** OS-I19 (one rail has a time function) — D*.
- **(c) Practices:** correction 02 §4 (chronology protection is a
  conjecture).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Chronology
  concerns (10).
- **(f) Open:** LDS F.3.8 (Kim–Thorne against Hawking); Hawking 1992 and
  Kim–Thorne beyond their abstracts UV (LDS G.3).

### Chapter 7. Semiclassical response

#### 7.1 Renormalized stress and the trace anomaly
- **(a) Literature:** Capper–Duff 1974, no arXiv [der (perturbative); AB];
  Christensen–Fulling 1977, no arXiv [der; AB]; Deser–Schwimmer 1993,
  arXiv:hep-th/9302047v1 [der (classification); AB]; Duff 1994,
  arXiv:hep-th/9308075v1 [rev; AB]; Hollands–Wald 2015, arXiv:1401.2026v2
  [rev (rigorous); AB]; Birrell–Davies 1982, Parker–Toms 2009, Wald 1994
  [PT].
- **(b) Identities:** OS-I22 ⟨T^μ_μ⟩ = (cW² − aE)/16π² · ħc/L⁴ for conformal
  fields, R² counterterm omitted; zero in a flat region — L (application
  D*); TE-Q5 T(ℓ₀) = T(1) − 2(ℓ₀ − 1)H: a change of subtraction convention
  supplies no stress [conformal scalar, curvature-squared coupling] — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 photon trace-anomaly peak 1.33 → 6.01
  ħc/L⁴ for v = 2.1 → 10 (D-trim, ✓); OS-K17 the anomaly peak sits on the
  compartment wall and vanishes inside (✓).
- **(e) Quiz:** QB Established foundations / Semiclassical gravity (6); QFT
  basics.
- **(f) Open:** Deser–Duff–Isham 1976 not located; duplicates 24.4.

#### 7.2 Vacuum polarization and states
- **(a) Literature:** Candelas 1980, no arXiv [PT]; Page 1982, no arXiv [der
  (approximation); AB]; Anderson–Hiscock–Samuel 1995, no arXiv [num; AB];
  Visser 1996–97 I–IV [num; AB]; Fulling 1973, Davies 1975 [PT]; Unruh 1976,
  no arXiv [der; AB]; Hollands–Wald 2015 [AB]; Martín-Moruno–Visser 2021
  [FT]; Abdolrahimi–Page–Tzounis 2019 [num; AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Quantum vacuum (2);
  Semiclassical gravity.
- **(f) Open:** —

#### 7.3 Horizon temperatures
- **(a) Literature:** Hawking 1975 [der; AB]; Unruh 1976 [der; AB; the
  temperature formula's wording UV]; Crispino–Higuchi–Matsas 2008,
  arXiv:0710.5373v1 [rev; AB]; Gibbons–Hawking 1977 [der; AB]; Tolman 1930
  and Tolman–Ehrenfest 1930, no arXiv [der (static equilibrium); AB, the
  √g₄₄ form inferred]; Finazzi–Liberati–Barceló 2009 (interior Hawking flux
  at T ~ κ) [der; FT].
- **(b) Identities:** OS-I17 passengers read κ/(2πN), N = √(α² − b²)
  [stationary pattern frame] — D* (Tolman, L); OS-I13 κ = |∂_ζα| — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 rear-horizon κ 7.55 → 57.2 on the axis,
  passenger temperature 2.75 → 20.8 mK at L = 1 m for v = 2.1 → 10 (D-trim,
  ✓); OS-K27 temperature ∝ 1/L (2.75 mK at 1 m, 2.8 μK at 1 km) (✓).
- **(e) Quiz:** QB Established foundations / Semiclassical gravity.
- **(f) Open:** the rear-horizon flux relies on 1+1 results; κ varies
  7.55–8.3 across the disk; no 3+1 renormalized stress (OS-§3.3.12);
  temperature at compartment clocks other than 1 is inferred (OS-§5).

#### 7.4 The species bound
- **(a) Literature:** Dvali 2010 (preprint 2007), arXiv:0706.2050v1 [der;
  AB]; Dvali–Redi 2008, arXiv:0710.4344v1 [der; AB];
  Freivogel–Krommydas 2018 (G_N ∼ 1/N) [conj; FT]; Ford–Roman 1996 and 1997
  (bounds relax as √N; about 10⁶² fields for 1 m) [der; FT].
- **(b) Identities:** OS-I21 species length ℓ* = √Q L [with the QI
  requirement of 5.2] — D*.
- **(c) Practices:** A5 (QI with the species bound); SE L22.
- **(d) Measured examples:** OS-K27 √Q L = 0.12 L equals the sharpest
  curvature radius 0.117 L; L ≤ 0.45 mm (f = 0.1) (D-lap staged, ✓).
- **(e) Quiz:** —
- **(f) Open:** duplicates 24.3.

#### 7.5 Instability of superluminal fronts
- **(a) Literature:** Hiscock 1997, arXiv:gr-qc/9707024v1 [der (2D
  reduction); AB]; Finazzi–Liberati–Barceló 2009, arXiv:0904.0141v2 [der
  (1+1); FT]; Barceló–Finazzi–Liberati 2010, arXiv:1001.4960v1 [claim
  (essay); AB]; Coutant–Finazzi–Liberati–Parentani 2012, arXiv:1111.4356v2
  [der/num (1+1); AB]; Barceló et al. 2022, arXiv:2207.06458v1 [der +
  estimates; FT]; González-Díaz 2000 [claim; AB].
- **(b) Identities:** OS-I13 a front fall with no transverse gradient is a
  white-hole disk; mode energy density grows as e^{2κt} — D*; OS-I14 tip
  shedding rate λ = ½(√(κ² + 4v(−∂²_rα)) − κ) [paraxial estimate] — H.
- **(c) Practices:** A9.
- **(d) Measured examples:** OS-K19/OS-K20 at the cone tip modes rise at
  most 1.6× and leave; a flat front with the same axial lapse grows at 2κ
  (D-fr, ✓).
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.5 (no 3+1 renormalized stress); duplicates 19.5 and
  29.3.

#### 7.6 Validity limits
- **(a) Literature:** Flanagan–Wald 1996 [der; AB]; Hu–Verdaguer 2008,
  arXiv:0802.0658v1 [rev; AB]; Hollands–Wald 2015 [AB]; Kontou–Sanders 2020
  formulation (ii) (violations only over Planck-scale transverse widths)
  [FT]; Graham–Olum 2007 (Condition 1 expected only below Planck curvature)
  [FT]; Dvali–Redi 2008 [AB]; Van Den Broeck 1999, arXiv:gr-qc/9905084v5
  (curvature radii near the Planck length) [num/der; FT];
  Hochberg–Popov–Sushkov 1997, arXiv:gr-qc/9701064v1 [num; FT].
- **(b) Identities:** —
- **(c) Practices:** A11 (semiclassical stress needs more smoothness, d⁻³ at
  sheets; refined); SE L9, SE D13 (at least C⁴ for fourth-derivative
  renormalized stress).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Effective field theory (8),
  part.
- **(f) Open:** the Hochberg–Popov–Sushkov validity statement is the
  survey's inference (LDS G.3).

### Chapter 8. The canonical engineered geometries

#### 8.1 Traversable wormholes
- **(a) Literature:** Morris–Thorne 1988 [der; FT-OCR]; Morris–Thorne–Yurtsever
  1988 [der; FT-OCR]; Visser 1989a, arXiv:0809.0907v1 [der; FT]; Visser
  1989b, arXiv:0809.0927v1 [der; FT]; Hochberg–Visser 1997 [thm; FT];
  Hochberg–Visser 1998 PRL and PRD [thm; FT/AB]; Visser–Kar–Dadhich 2003,
  arXiv:gr-qc/0301003v2 [der; FT]; Kar–Dadhich–Visser 2004,
  arXiv:gr-qc/0405103v1 [der; FT]; Nandi–Zhang–Kumar 2004,
  arXiv:gr-qc/0407079v5 [der; FT]; Fewster–Roman 2005 [der; FT];
  Ford–Roman 1996, arXiv:gr-qc/9510071v1 [der, conditional on locality; FT];
  Gao–Jafferis–Wall 2017, arXiv:1608.05687v3 [der; FT];
  Fu–Grado-White–Marolf 2019a,b, arXiv:1807.07917v3 and arXiv:1908.03273v2
  [der (perturbative); FT]; Maldacena–Milekhin–Popov, arXiv:1807.04726v3
  [der; FT]; Maldacena–Milekhin 2021, arXiv:2008.06618v2 [der; FT];
  Kanai–Maeda–Yoshida 2025, arXiv:2511.21017v1 [thm (perturbative EFT);
  AB]; Garattini 2019, arXiv:1907.03623v1 [der; FT]; Simpson–Visser 2019,
  arXiv:1812.07114v3 [der; FT]; Einstein–Dirac–Maxwell dispute:
  Blázquez-Salcedo–Knoll–Radu 2021, arXiv:2010.07317v2 [num; FT],
  Bolokhov et al. 2021, arXiv:2104.10933v2 [critique; FT], Danielson et al.
  2021, arXiv:2108.13361v2 [thm + der (refutation); FT], Blázquez-Salcedo–Knoll–Radu
  2022, arXiv:2108.12187v1 [num; FT], Konoplya–Zhidenko 2022,
  arXiv:2106.05034v4 (retitled from v1) [num; FT], Kain 2023a,
  arXiv:2305.11217v2 [num; FT], Kain 2023b, arXiv:2308.00049v2 [num; AB];
  Lobo 2008 review, arXiv:0710.4474v1 [rev; AB]; Visser 1995 book [PT].
- **(b) Identities:** TE-I17 at a minimal sphere p_r = −1/(8πR₀²) whatever
  the lapse, shift and stretch; a strict minimum adds ρ + p_r = −R″/(4πR₀)
  [static spherical] — D* (throat tension τ₀ = 1/(8πb₀²), Morris–Thorne,
  L); TE-I18 — D*; TE-I21 — D*.
- **(c) Practices:** A3.
- **(d) Measured examples:** TE-G1 live p_l peak ratio 0.7656 = (1.75/2.0)²
  (2E; usable only as a data check of TE-I17); integrated burdens rising
  with R_th (2E; grid and mask artefact; unsuitable).
- **(e) Quiz:** QB Published warp and wormhole context /
  Warp-wormhole correspondence (3), part; Metric basics.
- **(f) Open:** LDS F.3.1 (volume-quantifier measure), F.3.2
  (Einstein–Dirac–Maxwell), F.3.6; OCR-limited numerics in Morris–Thorne and
  the Casimir prefactor in Morris–Thorne–Yurtsever UV; Maldacena–Milekhin–Popov
  eq. (5.40) prefactor UV; Garattini eq. (26) prefactor UV.

#### 8.2 Warp metrics
- **(a) Literature:** Alcubierre 1994 [der; FT]; Natário 2002 [thm + der;
  FT]; Natário 2006, arXiv:gr-qc/0408085v3 [claim; AB]; Van Den Broeck 1999,
  arXiv:gr-qc/9905084v5 [num/der; FT]; Lobo–Visser 2004,
  arXiv:gr-qc/0406083v2 [der; FT]; Pfenning–Ford 1997 [der; FT];
  Loup–Waite–Halerewicz 2001, arXiv:gr-qc/0107097v2 [claim, unrefereed; AB];
  Santiago–Schuster–Visser 2022 [FT]; Santiago–Schuster–Visser 2021
  (tractor beams), arXiv:2106.05002v1 [der; AB]; Barzegar–Buchert 2025,
  arXiv:2407.00720v2 [der; FT]; Barzegar–Buchert–Vigneron 2026 [FT];
  Santos-Pereira–Abreu–Ribeiro series [der; AB]; Abellán–Bolívar–Vasilev
  2023, arXiv:2302.13826v3 [der; FT] (the EPJC 83, 7 and CQG 41, 105011
  papers: arXiv identifiers UV; 2305.03736v1 and 2512.16109v1 [AB]);
  Mattingly et al. 2021, arXiv:2010.13693v3 [num; AB; disputed]; Rodal 2023
  and 2024 [AB]; White–Vera–Sylvester–Dudzinski 2025, no arXiv
  (CQG 42, 235022) [der/num; AB]; Jusufi–Lobo 2026, arXiv:2609.05554v1 [der;
  AB]; Chowdhury 2025, arXiv:2404.15948v3 [der; AB]; Buchert–Frackowiak 2026,
  arXiv:2605.03653v1 [der; AB]; Pieri 2023, arXiv:2311.12069v2 [claim; AB].
- **(b) Identities:** OS-I1 — L + D; Santiago–Schuster–Visser integral
  identity — L.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics (10);
  Warp geodesics (9).
- **(f) Open:** LDS F.1.8, F.1.10, F.1.13; the abstract-level entries of
  LDS G.1.

#### 8.3 Krasnikov tubes
- **(a) Literature:** Krasnikov 1998, arXiv:gr-qc/9511068v6 [FT];
  Everett–Roman 1997, arXiv:gr-qc/9702049v1 (QI wall ε ≲ 10⁴ l_P; light-cone
  opening η against ε) [der; FT]; Krasnikov 2003, arXiv:gr-qc/0207057v3
  [claim/der; FT; disputed]; Krasnikov 2018 book [PT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Chronology
  concerns, part.
- **(f) Open:** LDS F.1.14, F.2.4 (QI arguments against shortcuts); the
  construction-time statement is a claim (LDS E.2).

#### 8.4 The positive-energy debate, 2021–26
- **(a) Literature:** Lentz 2021, arXiv:2006.07125v2 (companion
  arXiv:2201.00652v1) [claim; AB+; refuted]; Fell–Heisenberg 2021,
  arXiv:2104.06488v4 [claim; AB+; disputed]; Bobrick–Martire 2021,
  arXiv:2102.06824v2 [der; FT]; Santiago–Schuster–Visser 2022 [thm-level;
  FT]; Helmerich et al. 2024 (Warp Factory) [num; FT]; Fuchs et al. 2024,
  arXiv:2405.02709v1 [num; FT; disputed]; Celmaster–Rubin 2025,
  arXiv:2511.18251v1 [der/num; AB]; Rodal 2025, arXiv:2512.18008v1 [num +
  der; AB]; Le 2026a, arXiv:2605.25417v2 (positive geodesic-integrated null
  energy for source-prescribed shells) [num; FT]; Le 2026b [FT];
  Barzegar–Buchert–Vigneron 2026 [thm + critique; FT]; Huey 2024 [der; AB];
  Abellán–Bolívar–Vasilev 2023 [der; FT]; Carneiro et al. 2022 [claim; AB];
  Rodal 2026, arXiv:2603.21352v2 (cite v2; v3 is a different paper) [num,
  exploratory; AB].
- **(b) Identities:** Santiago–Schuster–Visser ∫ρ = −∫ω²/32π [flat unit
  lapse, localized] — L; OS-I1 (ρ ≤ 0 for one-component flat-slice shifts)
  — L + D.
- **(c) Practices:** A1 (the debate is the literature's own case for
  all-observer evaluation).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics.
- **(f) Open:** LDS F.1.1 (settled against the claims within the flat
  unit-lapse class), F.1.2 (Fuchs shell open), F.1.8, F.1.9; the resolution
  uses 10.1, 10.3 and 16.2 (Part 4).

#### 8.5 The warp–wormhole correspondence
- **(a) Literature:** Garattini–Zatrimaylov 2024, arXiv:2401.15136v2 [der;
  AB]; Garattini–Zatrimaylov 2024, arXiv:2408.04495v4 [der; AB];
  Garattini–Zatrimaylov 2025, arXiv:2502.13153v4 [der; AB; which version
  carried the title Le 2026a cites is UV]; Natário 2002 [FT];
  Morris–Thorne 1988 [FT-OCR].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp-wormhole
  correspondence (3).
- **(f) Open:** thin and abstract-level only; LDS F.1.13 (divergence-averaged
  energy conditions).

#### 8.6 Horizons, swept matter and control
- **(a) Literature:** Clark–Hiscock–Larson 1999 [num; AB]; Natário 2002
  [FT]; McMonigal–Lewis–O'Byrne 2012, arXiv:1202.5708v1 [num; FT];
  Everett–Roman 1997 (the crew can neither create nor control a superluminal
  bubble) [FT]; Krasnikov 1998 [FT]; Finazzi–Liberati–Barceló 2009 [FT];
  Barceló et al. 2022 [FT].
- **(b) Identities:** OS-I12 and OS-I13 — D*.
- **(c) Practices:** A9 (evidence-backed).
- **(d) Measured examples:** OS-K4 current front: swept-matter γ of 10²²,
  10⁴⁷ and 10⁷² for trips of 12.6, 25.2 and 37.8 (D-fr, ✓; a front with a
  white-hole horizon, cautionary); OS-K19 shelves hold γ fixed (✓).
- **(e) Quiz:** QB Published warp and wormhole context / Warp geodesics (9).
- **(f) Open:** duplicates 19.2–19.3.

## Part II. Specifying and testing a geometry

### Chapter 9. From geometry to demand

#### 9.1 The geometry fixes the demand (A7)
- **(a) Literature:** Roache 2002 (LEM V5) [std; AB]; Salari–Knupp 2000
  (LEM V6) [std; FT]; Oberkampf–Trucano 2002 (LEM V9: calibration differs
  from validation) [std; FT]; Santiago–Schuster–Visser 2022 App. A and
  Barzegar–Buchert–Vigneron 2026 Error 14 (the Bianchi identity conserves a
  reverse-engineered tensor automatically) [FT]; Bobrick–Martire 2021 §5.2
  (the continuity objection, rejected in LDS F.1.4) [FT];
  Santos-Pereira–Abreu–Ribeiro (dust sources reduce to vacuum) [der; AB].
- **(b) Identities:** T = G/8π — L; TE-I24 the minimal Type I regulator
  max(0, 2|j_l| − |ρ + p_l|) makes |ρ + p_l| = 2|j_l|, so the regulated
  tensor differs from the Einstein demand [radial block] — D*; TE-I15 a
  conservation law ∇·T = J fixes a component tensor only up to
  divergence-free terms, so it leaves the type free — D*.
- **(c) Practices:** A7 (evidence-backed; track the worst residual after
  every fix; the edge-migration test). Evidence pointers: SE L23, SE A2
  (a ledger is not a partition), SE B1, MJ CE-3 (assigning a known tensor
  always succeeds).
- **(d) Measured examples:** TE-G29 coupled reset source: fixing one Type IV
  witness moved Type IV outward into the source plateau and overdrew the
  mass budget (f = −0.61) (†, cautionary); TE-M1 regulator (†, cautionary;
  TE-I24).
- **(e) Quiz:** QB Established foundations / Einstein equation (7).
- **(f) Open:** —

#### 9.2 The demand ledger: region, class, frame, measure
- **(a) Literature:** Visser–Kar–Dadhich 2003, Kar–Dadhich–Visser 2004,
  Nandi–Zhang–Kumar 2004, Fewster–Roman 2005 (volume quantifiers and the
  measure dispute) [der; FT]; Lobo–Visser 2004 (volume integral quantifier)
  [der; FT]; Le 2026b §3.5 (ANEC normalization) [FT]; Kontou–Sanders 2020
  [FT].
- **(b) Identities:** TE-I8 a coordinate-normalized null energy carries α²:
  T_kk±/α² = ρ + p_l ∓ 2j_l, so any lapse knob rescales it at fixed
  orthonormal stress — D*; OS units note (coordinate measure 2πr dr dz
  against proper measure A r dr dz dφ; peak negative energy as the
  instantaneous volume integral of the Eulerian T_n̂n̂ < 0) — definitions.
- **(c) Practices:** C5 (report absolute values alongside fractions; truism
  with a strong domain record); B4 (domain; near truism). Evidence pointers:
  MJ I-09 (fractions improved by moving the denominator), MJ I-04 (relabelling
  changes no metric).
- **(d) Measured examples:** TE-G17 entry gate: live burden falls when points
  are relabelled "pre-entry" and no metric function changes (2E, cautionary);
  TE-G8/TE-G6 live fractions (2E, TE-L2; unsuitable).
- **(e) Quiz:** QB Established foundations / Dimensional analysis (3), part.
- **(f) Open:** LDS F.3.1 (which quantifier is physical) unresolved.

#### 9.3 Functional zoning
- **(a) Literature:** Suh 1990/2001 (LEM D1) [std; PT, content via MIT OCW
  notes]; Jones 2017 (LEM D2) [std; FT]; Browning 2001 (LEM D5) [std; FT].
- **(b) Identities:** —
- **(c) Practices:** C3 (record which knobs decouple and their adjustment
  order; decoupling is a heuristic; zoning must not hide phases; refined,
  with a stated hazard); LEM Area 4 synthesis (zoning raises the design
  parameter count and makes the matrix triangular).
- **(d) Measured examples:** the OS part list (service region, shift
  transition, sheath, outer falls, compartment; OS-P1–P16) as a zoned design
  (D-lap and D-cmp, ✓).
- **(e) Quiz:** —
- **(f) Open:** duplicates 14.5; uses the design-matrix vocabulary of
  Chapter 14 (Part 4).

#### 9.4 Normalization and absolute scale
- **(a) Literature:** Buckingham 1914, no arXiv [std; PT]; Lawson 1957,
  no arXiv (LEM S5) [std; PT]; Wurzel–Hsu 2022, arXiv:2105.10954 (version
  not recorded) (LEM S5) [emp; FT]; Hashemi et al. 2010,
  arXiv:1003.5934 (version not recorded) (LEM T11: bounds tighten with size)
  [der; FT].
- **(b) Identities:** OS-I25 at fixed shape, stresses ∝ 1/L², energies and
  contents ∝ L, energy per unit length ∝ c²/G × shape factor — D (L:
  Pfenning–Ford; Lobo–Visser E ∝ v²R²/Δ); 05 SI conversion (energy × c⁴L/G,
  stress × c⁴/(GL²)); TE-Q13 C_J/δ_s ∝ c⁵/G independent of L — D*.
- **(c) Practices:** A5 (fix the absolute scale); truism: dimensional
  analysis. Evidence pointers: SE D7, SE D8 (normalize before structure).
- **(d) Measured examples:** OS-K27 D-lap peak stress 3.5×10⁴⁴ Pa at
  L = 1 m; energy per unit length scale-free (✓).
- **(e) Quiz:** QB Established foundations / Dimensional analysis (3).
- **(f) Open:** duplicates 22.3 and Appendix C.

### Chapter 10. Testing the demand

#### 10.1 Complete tensor, all observers (A1)
- **(a) Literature:** Santiago–Schuster–Visser 2022 [FT]; Helmerich et al.
  2024 [num; FT]; Le 2026b (the Eulerian reading misses ≈73% of WEC and ≈74%
  of DEC violations sampled in the Rodal wall) [FT]; Le 2026a [FT];
  Carneiro et al. 2022 [claim; AB; cautionary]; Lentz 2021 (Eulerian-only
  claims) [claim; AB+]; Rodal 2023 and 2024 (curvature invariants; Petrov
  type I for Natário) [AB]; Mattingly et al. 2021 (invariant maps; reported
  plotting errors of 8–21 orders) [num; AB; disputed].
- **(b) Identities:** —
- **(c) Practices:** A1 (evidence-backed; energy conditions as 4×4 LMIs;
  interval certificates); P01 §2b.
- **(d) Measured examples:** P01 §2b the complete demand of beta075 carries
  3,843 dense Type IV points after a component-level fix (†, cautionary).
- **(e) Quiz:** QB Established foundations / Energy conditions.
- **(f) Open:** curvature invariants as frame-free diagnostics have no named
  home (Part 2).

#### 10.2 Time dependence and the blindness of static checks
- **(a) Literature:** Martín-Moruno–Visser 2021 [FT]; Le 2026b Lemmas 2–3
  [FT]; Rodal 2025 [AB].
- **(b) Identities:** zero momentum ⇒ Type I (P01 §2c) — D; TE-I22 — D*;
  TE-I3 combined with TE-I2: Type IV demand requires time dependence acting
  where the areal radius varies [spherical warped products; necessary
  condition only] — D*; TE-I9 uniform slowdown σ = κt: j_κ = κj₁ and, at a
  zero of the static enthalpy, Δ_κ = κ²(κ²h₂² − 4j₁²), so the static limit can
  be Type I while every evolving member carries Type IV [uniform-rate family
  of any metric in the class] — D*.
- **(c) Practices:** A1; B5.
- **(d) Measured examples:** TE-G5 slowdown κ = 1 → 1/64: all 28 roots keep
  Type IV at every resolution, |Δ| ∝ κ², layer width ∝ κ; ordinary grids show
  the slow cases as Type I (†, cautionary; confirms TE-I9); SE D1 a gate's
  control slice became the design geometry (§, cautionary); OS-K24 a carve
  carried the speed advantage and the residual bands together (D-1S, βh
  held support).
- **(e) Quiz:** —
- **(f) Open:** TE-§8.3 whether every time-dependent stretch acting where R
  varies must produce Type IV.

#### 10.3 Transitions to vacuum
- **(a) Literature:** Le 2026a (failures localize at the smooth source–vacuum
  transition; a Type I DEC deficit independent of v₀; Type IV onset linear
  in tilt; no admissible configuration in a 600-point scan) [num; FT];
  Bolívar–Abellán–Vasilev 2026 (unit-lapse radial Painlevé–Gullstrand: a
  regular density rising out of a cavity violates the transverse NEC; onset
  budget) [thm; FT]; Fuchs et al. 2024 (Type IV smoothing tail per Le) [FT].
- **(b) Identities:** OS-I6 shear identity (Type IV where a shift begins to
  vary) — D*.
- **(c) Practices:** A1 ("through the transition to vacuum"); P01 §2d (well
  supported for smooth shells and layers; open for other classes).
- **(d) Measured examples:** OS-K8 removing the sheath gives 92,247 Type IV
  points (D-lap, ✓); OS-K25 Type IV persists at 16–21% of layer points for
  every layer width (βx, cautionary).
- **(e) Quiz:** QB Established foundations / Boundary conditions (3), part.
- **(f) Open:** validity across design classes open (P01 §2d).

#### 10.4 Matrix inequalities and certified bounds between samples (B1)
- **(a) Literature:** Le 2026b (interval evaluation gives pointwise
  certificates and global bounds between samples) [thm + certified num; FT];
  Tucker 2011, no arXiv (LEM V15) [std; PT]; Moore–Kearfott–Cloud 2009
  (LEM V15) [std; PT].
- **(b) Identities:** —
- **(c) Practices:** B1 (evidence-backed; the project's root-finding is
  superseded by interval certification); P01 §2e. Evidence pointers: SE L4,
  SE E8.
- **(d) Measured examples:** OS-K9 nodes are Type I from e⁵ upward while
  resolved bands persist to e^6.5; band width shrinks about e^(−1.5) per
  unit φ (D-amp, βh, passes at e⁷).
- **(e) Quiz:** —
- **(f) Open:** counts of sampled points in a sign set have no observed order
  (LEM V2 note).

#### 10.5 Degenerate tensors (B3)
- **(a) Literature:** Martín-Moruno–Visser 2018 (type cores) [der; AB];
  Salari–Knupp 2000 (blind tests with planted mistakes, LEM V6) [std; FT].
- **(b) Identities:** TE-I3 rest-frame formulas and their sign branch — D*;
  TE-I4 string cloud as a degenerate fixture — D*; TE-I21 Ellis tensor as a
  fixture — D*.
- **(c) Practices:** B3 (exact evaluators and scale-aware tolerances;
  evidence-backed; brief). Evidence pointers: SE A1 (a classifier validated
  on 19 analytic fixtures), SE E17, SE L10.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** thin literature; the analytic fixture set is project-internal
  and could be published in Appendix D.

#### 10.6 Type as a match to source families (A2)
- **(a) Literature:** Gergely 2026, arXiv:2608.15228v1 (braiding reaches
  Type IV only where the NEC fails) [der; AB+]; Martín-Moruno–Visser 2018
  [AB] and 2021 [FT]; Abdolrahimi–Page–Tzounis 2019 [AB]; Zhang et al. 2011,
  arXiv:1012.2238 (version not recorded) (LEM T10: match the transformation
  to a natural material) [emp; FT]; Li–Pendry 2008 (LEM T7) [FT].
- **(b) Identities:** TE-I23 a minimally coupled scalar is never Type IV —
  D*; TE-I25 heat-mode speed v_q = 2j_l/|ρ + p_l| and D = (ρ + p_l)²(1 − v_q²):
  a medium realizing a near-Type II block has a near-luminal heat
  characteristic — D*; TE-I26 boosting infrastructure preserves the radial
  discriminant — D*.
- **(c) Practices:** A2 (evidence-backed; replaces "Type I required");
  02 §3.6 (drop "admissibility" and "Type I required").
- **(d) Measured examples:** TE-M2 source-class screen: a Type I fluid fails
  because Type IV carries a quarter of the burden (†, cautionary).
- **(e) Quiz:** QB Established foundations / Source model basics (5).
- **(f) Open:** Gergely's journal reference UV; uses the algebraic ranges of
  22.1 and 25.5 (Part 4).

### Chapter 11. Global structure and performance claims

#### 11.1 Declaring topology, ends and exterior (A3)
- **(a) Literature:** Geroch 1967 [thm; PT]; Friedman–Schleich–Witt 1993
  [thm; FT]; Hochberg–Visser 1997 (flare-out; genus bound ∫√g ρ ≤ χ/4G)
  [thm; FT]; Li–Pendry 2008 (LEM T7) [FT]; Olason–Tidman 2010 (LEM T13:
  topology at concept stage) [std; FT].
- **(b) Identities:** TE-I18 — D*; OS-P24 spherical-track parts and their
  ends [class CS].
- **(c) Practices:** A3 (evidence-backed). Evidence pointers: SE L6, MJ
  I-01, SE E5.
- **(d) Measured examples:** OS-K26 (D-sph, identity demonstration;
  βx alternative cautionary); SE B9 an Ellis tail carries 96.7% of the null
  demand outside the throat (§, cautionary).
- **(e) Quiz:** QB Published warp and wormhole context / Topological
  censorship.
- **(f) Open:** —

#### 11.2 The causality class of a design
- **(a) Literature:** Barzegar–Buchert–Vigneron 2026 Thm IV.7 [FT];
  Everett–Roman 1997 [FT]; Shoshany–Snodgrass 2024 [FT]; Everett 1996 [TL];
  Krasnikov 1998 [FT]; Sajeendran–Ralph 2025 [AB].
- **(b) Identities:** OS-I19 — D*; OS-I20 static observers exist iff α > |β|
  — D*.
- **(c) Practices:** A3 refinement; correction 02 §4 (time function).
- **(d) Measured examples:** OS-K16 radius without static frames 2.45 at
  compartment clock 0.1, none from clock 3 upward (D-cmp, ✓).
- **(e) Quiz:** QB Established foundations / Causal structure.
- **(f) Open:** LDS F.1.11.

#### 11.3 Performance inside one spacetime; one occupant worldline (A4)
- **(a) Literature:** Krasnikov 1998 [FT]; Gao–Wald 2000 [FT]; Olum 1998
  [FT]; NASA Systems Engineering Handbook 2016 (LEM S2: one MOE, several
  MOPs) [std; FT]; Millis 2005 (LEM S6) [std; FT]; Hannam et al. 2009,
  arXiv:0901.2437 (version not recorded) (LEM N5: accuracy tied to use)
  [emp; AB].
- **(b) Identities:** TE-I6 packet norm and clock on one worldline — D*.
- **(c) Practices:** A4 (evidence-backed); truism: measures of
  effectiveness. Evidence pointers: SE L19, SE L20, SE E3, MJ I-02.
- **(d) Measured examples:** OS-K2 lead over light on the test trip 1.5 →
  112.5 for v = 1.5 → 20 (D-trim, ✓); TE-L3 service-time ratios 2.569 and
  1.233 are proxies and the geometry defines no arrival lead (cautionary);
  TE-L2 packet windows advancing at unit speed while the norm test used the
  carry speed (cautionary).
- **(e) Quiz:** —
- **(f) Open:** duplicates 1.5.

#### 11.4 Coordination without superluminal signals
- **(a) Literature:** Lamport 1978, no arXiv (LEM S8) [std; FT];
  Krasnikov 1998 ("utter causality") [FT]; Everett–Roman 1997 (the bubble is
  arranged beforehand along the route) [FT]; Low 1999 (decision to arrival;
  construction on demand) [thm; FT]; Krasnikov 2003 (construction time)
  [claim; FT]; Pieri 2023 (superluminal signalling claim) [claim,
  unrefereed; AB].
- **(b) Identities:** —
- **(c) Practices:** truism (Lamport clocks; the domain part is proper time:
  convert each clock rate to the chosen time function).
- **(d) Measured examples:** OS-K21 a forward shelf lets packet signals reach
  18 of 19 route points before the pattern, lead 0.109 per unit distance
  (D-fr, ✓); OS-K8 a standing strong sheath is a superluminal signal channel
  independent of the packet (lead 4.15 against 1.66) (D-ch, βh).
- **(e) Quiz:** QB Published warp and wormhole context / Chronology
  concerns, part.
- **(f) Open:** —

### Chapter 12. Occupants

#### 12.1 Occupant observables (A10)
- **(a) Literature:** Morris–Thorne 1988 (tidal limit g⊕ gives
  v ≲ 60 m/s (b₀/10 m); station gravity −Φ′c²) [der; FT-OCR];
  Maldacena–Milekhin 2021 (a 20g tide forces r_e > 1.5×10⁷ m and a redshift
  contrast ~2×10¹²) [der; FT]; Ford–Roman 1996 (blueshift ~10²³ at the
  plates) [der; FT]; Eiroa–Rubín de Celis–Simeone 2025, arXiv:2511.15001v1
  (a jump of K^t_t at a thin layer gives a radial tide independent of speed)
  [der; FT]; Alcubierre 1994 (the ship is geodesic with no time dilation)
  [FT]; McMonigal et al. 2012 (shielding against blueshifted particles)
  [FT]; NASA SE Handbook (LEM S2) [std; FT]; Tolman 1930 [AB].
- **(b) Identities:** OS-I26 a passenger in a compartment of lapse α_c ages
  α_c/v of light's crossing time per unit distance [class C0, steady lane]
  — D*; OS-I17 — D*; OS-I16 — D*; TE-I6 — D*.
- **(c) Practices:** A10 (truism as practice; the domain list is content:
  clock rate against exterior time and light's crossing time, tides, proper
  acceleration, radiation temperature, swept matter). Evidence pointers:
  SE L7, SE E13, SE B14.
- **(d) Measured examples:** OS-K2 aging 244 → 18 days per light-year for
  v = 1.5 → 20 at clock 1 (D-trim, ✓); OS-K5 D-lap packet clock e⁴ = 55 and
  tides of 3×10¹⁶ m/s² per metre at L = 1 m (✓ for the gate; cautionary for
  occupants); OS-K10 peak clock rate 9,069 → 140 when the support stretch is
  removed (D-cen → D-amp, βh).
- **(e) Quiz:** —
- **(f) Open:** tides quantified for D-lap only and zero in compartments;
  temperature at clocks other than 1 inferred (OS-§5).

#### 12.2 Flat compartments
- **(a) Literature:** Alcubierre 1994 (flat ship region) [FT]; Van Den Broeck
  1999 (uniform-shift pocket) [FT]; White et al. 2025 (interior-flat nacelle
  bubbles) [AB]; Bolívar–Abellán–Vasilev 2026 (flat cavities) [FT];
  Santos-Pereira–Abreu–Ribeiro (Burgers-type shifts are flat) [AB].
- **(b) Identities:** OS-I3 where α = α(σ) and β = β(σ) the metric is
  Minkowski, normal observers are geodesic and a packet carried at β = −v
  ages at rate α [flat slices, spatially uniform lapse and shift] — D*;
  OS-I2 the compartment wall is pure lapse, hence Type I for any profile —
  D.
- **(c) Practices:** A10.
- **(d) Measured examples:** OS-K16 largest compartment Riemann component
  4.4×10⁻¹⁶ at every clock rate (D-cmp, ✓); OS-K17 the wall holds 157 of
  2,286 content units and the trace-anomaly peak (✓).
- **(e) Quiz:** —
- **(f) Open:** project-derived statement dominates; the literature's flat
  interiors should lead (Part 3).

#### 12.3 Choosing the occupant clock
- **(a) Literature:** Bobrick–Martire 2021 (positive-energy spherical drives
  can only slow interior clocks) [der; FT]; Maldacena–Milekhin 2021 [FT];
  Morris–Thorne 1988 [FT-OCR]; Shoshany–Snodgrass 2024 (a large lapse in
  shear regions suppresses total Eulerian energy at an N-fold time-dilation
  cost) [claim within FT].
- **(b) Identities:** OS-I26 — D*; OS-I3 — D*; LDS-E.5 (lapse contrasts sit
  in NEC-violating falls) — D.
- **(c) Practices:** A10.
- **(d) Measured examples:** OS-K16 clock-rate stress curve: peak stress 6.75
  at clock 0.1, 2.91 at 1, saturating at 1.75 from clock 3 (D-cmp, ✓;
  measured-only, 02 §2.3); OS-K5 the 55× D-lap clock (✓; cautionary).
- **(e) Quiz:** —
- **(f) Open:** the stress trend and its saturation are single-design
  results; the clock sweep used a coarser σ spacing (OS-§5).

#### 12.4 Occupants under single-gate optimization
- **(a) Literature:** Suh (LEM D1: coupled requirements under one objective)
  [std; PT]; Monticone–Alù 2013, arXiv:1307.3996 (version not recorded)
  (LEM T11, analogy) [der; FT].
- **(b) Identities:** —
- **(c) Practices:** C4 (carry margins, side effects, occupant and causal
  quantities in the same pass; evidence-backed hazard); P01 §2i. Evidence
  pointers: SE L8, SE E7, MJ I-08 (n = 7).
- **(d) Measured examples:** OS-K9 the gate-passing e⁸ pre-sheath carried
  450× excess energy and a 9,069× clock (D-cen/D-1S, βh; cautionary); OS-K5
  e⁴ plateau → 55× clock (D-lap, ✓; cautionary).
- **(e) Quiz:** —
- **(f) Open:** duplicates 30.4 and uses C4 before 30.4 introduces it.

### Chapter 13. Computing and certifying the demand

#### 13.1 Code verification: manufactured solutions and observed order (B2)
- **(a) Literature:** Roache 2002 (LEM V5) [std; AB]; Salari–Knupp 2000
  (LEM V6) [std; FT]; Roache 1998 (LEM V1) [std; PT];
  Oberkampf–Roy 2010/2025 (LEM V7) [std; PT]; Roy 2005 (LEM V8) [std; PT];
  Roache 1994 GCI (LEM V2) [std; AB, formulas via NASA tutorial]; Celik et
  al. 2008 (LEM V3) [std; PT]; Richardson 1911, Richardson–Gaunt 1927
  (LEM V4) [PT]; Choptuik 1991 (LEM N1) [num; AB]; Alcubierre et al. 2004,
  arXiv:gr-qc/0305023 (version not recorded) (LEM N2) [std; FT];
  Babiuc et al. 2008, arXiv:0709.3559 (version not recorded) (LEM N3) [emp;
  FT]; Löffler et al. 2012, arXiv:1111.3344 (version not recorded)
  (LEM N4) [std; FT]; Helmerich et al. 2024 (LEM N7: exact vacuum benchmark,
  no observed-order test) [meth; FT].
- **(b) Identities:** the contracted Bianchi identity makes ∇_μT^{μν} = 0 a
  free independent residual (LEM Area 1 synthesis, inference) — L.
- **(c) Practices:** B2 (superseded; the book teaches manufactured solutions
  judged by observed order, with the grid convergence index); truism:
  regression is not verification (LEM N4). Evidence pointers: SE F1, SE C10
  (manufactured tests must activate every coupling).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Modeling discipline (3).
- **(f) Open:** arXiv versions unrecorded for LEM N2–N6; Post & Votta defect
  rates UV.

#### 13.2 Solution verification aimed at decisions (B7)
- **(a) Literature:** ASME V&V 40-2018 (LEM V12) [std; AB]; ASME V&V 20-2009
  (LEM V10) [std; PT]; Roache 1994 GCI [std; AB]; Hannam et al. 2009
  (LEM N5) [emp; AB]; Hinder et al. 2014, arXiv:1307.5307 (version not
  recorded) (LEM N6) [emp; AB]; NASA-STD-7009B (LEM V13) [std; FT].
- **(b) Identities:** —
- **(c) Practices:** B7 (aim refinement at quantities that could change a
  decision; refinement of practice). Evidence pointers: SE F3, SE C2.
- **(d) Measured examples:** TE-M7 integrated totals agree within ~1% under
  refinement while extrema keep degrading (†, cautionary); TE-G2 resolution
  moved a packet cliff substantially (2E, cautionary).
- **(e) Quiz:** —
- **(f) Open:** the GCI applies to smooth outputs; sign sets need the
  between-sample methods of 10.4.

#### 13.3 Domains, surrogates and reduced models (B4, B5)
- **(a) Literature:** Alcubierre et al. 2004 (LEM N2: boundary
  inconsistencies; constraints never in isolation) [std; FT];
  Barceló–Liberati–Visser (LEM A1: an analogue realizes a restricted subset
  of metrics) [rev; FT]; Martín-Moruno–Visser 2021 [FT].
- **(b) Identities:** static ⇒ Type I, so a static surrogate cannot see
  Type IV — D.
- **(c) Practices:** B4 (near truism; brief); B5 (evidence-backed; a gate's
  control case is never the design case). Evidence pointers: SE L5, MJ I-13
  (n = 6), SE E6, SE E9, SE E14.
- **(d) Measured examples:** TE-S1–S13 source screens on the static
  surrogate (§, cautionary); OS-K2 3D optical audits (escape cones) (D-trim,
  ✓).
- **(e) Quiz:** —
- **(f) Open:** —

#### 13.4 Solver statuses (B6)
- **(a) Literature:** Tajmar–Neunzig–Weikert 2022 (LEM S7: controls against
  named artefacts) [emp; FT].
- **(b) Identities:** —
- **(c) Practices:** B6 (solver and stop statuses are not physics; textbook
  numerics; brief). Evidence pointers: SE L11, SE C1, SE C5, SE B6.
- **(d) Measured examples:** TE-S17 an apparent heat-engine infeasibility
  came from the solver deleting coefficients below 1e−9 (†, cautionary).
- **(e) Quiz:** —
- **(f) Open:** thin literature.

#### 13.5 Reference solutions for testing
- **(a) Literature:** Alcubierre et al. 2004 and Babiuc et al. 2008 (LEM
  N2, N3: shared testbeds) [FT]; Helmerich et al. 2024 (LEM N7:
  Schwarzschild exterior benchmark) [FT].
- **(b) Identities:** TE-I21 Ellis tensor matches samples within 8.02×10⁻¹¹
  — D*; TE-I16 decomposition checked against flat space, cylinder, Ellis and
  the de Sitter static patch — D*; TE-I1 checked on Ellis, a dust cosmology
  and Painlevé–Gullstrand Schwarzschild — D*.
- **(c) Practices:** B2; LEM N3 transfer (a shared benchmark set of analytic
  metrics with known demand, type and energy-condition verdicts).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** overlaps Appendix D.

## Part III. How the physics responds to design

### Chapter 14. Design matrices

#### 14.1 Design elements and physical channels
- **(a) Literature:** Suh 1990/2001 (LEM D1) [std; PT]; Steward 1981 [PT],
  Browning 2001 [FT], Eppinger–Browning 2012 [PT] (LEM D5, design structure
  matrix); LDS E.1–E.3 (the literature's own knob × relation tables);
  Mattingly et al. 2021 (single-parameter sweeps of speed, skin depth and
  radius) [num; AB]; Le 2026a (compactness × thickness scan) [num; FT];
  Pfenning–Ford 1997 and Lobo–Visser 2004 (E as a function of v, R, Δ)
  [der; FT].
- **(b) Identities:** —
- **(c) Practices:** 02 §2.5 (present the matrix per class, mark identity
  entries, claim decoupling only as a heuristic); C3.
- **(d) Measured examples:** OS coupling matrix §4 (channels E, N, S, Loc,
  Ty, Oc, Ot, Oθ, Ar, Sw, Src; mostly ✓ and βh designs); TE coupling matrix
  §6 (†, §, 2E; cautionary: algebraic type is its emptiest column).
- **(e) Quiz:** —
- **(f) Open:** project matrices dominate unless LDS E.1–E.3 lead (Part 3).

#### 14.2 Identity-backed and measured entries
- **(a) Literature:** Jones 2017 (LEM D2) [std; FT]; Olewnik–Lewis 2003
  (LEM D3) [std; FT].
- **(b) Identities:** evidence tags of the maps (OS: ID, ID-t, ID-c, EST, SW,
  SC; TE: I, I/M, M, 0, 0I).
- **(c) Practices:** 02 §2.3 (measured-only responses appear as labelled
  examples, never as laws); 05 placement rules.
- **(d) Measured examples:** OS-K5 plateau e⁴ → e³ raises the peak negative
  energy by exactly e² = 7.39, the α⁻² law of OS-I1 on data (D-trim, ✓);
  OS-K11 energy unchanged across support lapses (D-amp, βh; OS-I10 on data).
- **(e) Quiz:** —
- **(f) Open:** —

#### 14.3 Coupling, decoupling and adjustment order
- **(a) Literature:** Suh (LEM D1: Theorem 1, fewer parameters than
  requirements forces coupling) [std; PT]; Jones 2017 (LEM D2: mature good
  designs are often coupled) [std; FT]; Weber–Kößler–Paetzold 2015
  (LEM D4) [std; FT]; Browning 2001 (LEM D5) [std; FT].
- **(b) Identities:** the LEM Area 4 design matrix built on OS-I1 and OS-I2
  (carry, energy density in the shift transition, stress in shift-free
  regions; one lapse couples them, two zoned lapse elements make the matrix
  triangular) — the survey's application; identity-backed decouplings of
  TE-§6.4: p_l at a minimal sphere depends on R alone (TE-I17), packet
  kinematics ignore the areal radius (TE-I4, TE-I6), radial focusing ignores
  it (TE-I11), spatially disjoint edits superpose (locality of G_μν), a boost
  preserves the discriminant (TE-I26) — D*.
- **(c) Practices:** C3; 02 §2.5.
- **(d) Measured examples:** OS-K16 the compartment clock leaves the gate and
  the NEC content (±3%) unchanged (D-cmp, ✓); TE-G3 a lapse cushion moved the
  packet's causal margin at fixed radial pressure, an added design parameter
  that decouples two requirements (LEM D1 reading of MJ I-08; the sign
  ∂(−α² + A(v + β)²)/∂α = −2α is general) (2E; cautionary); TE measured-only
  decouplings (G8 footprint, G13 ring, G22 window thickness, G5/G23 lags, G6
  core peak) (2E or †, unsuitable).
- **(e) Quiz:** —
- **(f) Open:** duplicates 18.4.

#### 14.4 Identities before numerics (A8)
- **(a) Literature:** Alcubierre et al. 2004 (LEM N2: exact solutions are the
  most unambiguous tests) [std; FT].
- **(b) Identities:** worked cases: TE-I9 (slowdown scaling), TE-I2/TE-I3
  (the null-Hessian identity that became the constant-radius rule), OS-I11
  (speed scaling), OS-I13 (horizon criterion).
- **(c) Practices:** A8 (evidence-backed; the identities are book content).
  Evidence pointers: SE L3 (n = 12, strength A), SE A5, SE A7, SE E1.
- **(d) Measured examples:** TE-G31 constant areal radius: Type IV 13,587 → 0
  of 141,661 points (D-sph; identity demonstration); TE-G30 a 1,024-point
  search left 780 controls undecided where an onset expansion decided (†,
  cautionary).
- **(e) Quiz:** —
- **(f) Open:** TE-I28 onset obstruction is scoped to the registered source
  families (project-specific).

#### 14.5 Zoning and its hazard (C3)
- **(a) Literature:** Oberkampf–Trucano 2002 (LEM V9: a complete-system tier
  stays necessary) [std; FT]; Suh (LEM D1) [PT]; Browning 2001 (LEM D5) [FT].
- **(b) Identities:** —
- **(c) Practices:** C3 (refined, with a stated hazard: zoning must not hide
  phases). Evidence pointer: MJ CE-7 (n = 1).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** hazard evidence n = 1; duplicates 9.3.

### Chapter 15. The lapse

#### 15.1 Clock, redshift and refractive index
- **(a) Literature:** Morris–Thorne 1988 (redshift function; station
  gravity) [der; FT-OCR]; Leonhardt–Philbin 2006 (LEM T12) [der; FT];
  Gordon 1923 [PT]; Barceló–Liberati–Visser (LEM A1) [rev; FT]; Tolman 1930
  [AB]; Shoshany–Snodgrass 2024 (Eulerian worldlines are geodesic iff
  ∂_iN = 0; a spatially varying lapse switches rest frames) [thm within the
  class; FT]; Visser–Bassett–Liberati 2000 (Shapiro delay under the NEC)
  [der; FT]; Fuchs et al. 2024 (the delay persists with positive mass) [FT].
- **(b) Identities:** OS-I16 — D*; OS-I20 along-track light speed α/A in the
  standing geometry — D*; lapse-maximum dynamics (free particles fall away
  from a lapse maximum) [Newtonian-limit statement, unmeasured,
  OS-§3.3.10] — H.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K8 clocks inside a standing e¹⁶ sheath run
  9×10⁶ × exterior; along-track light α/A ≈ e⁸ (D-1S/D-ch, βh).
- **(e) Quiz:** —
- **(f) Open:** lapse-maximum dynamics unmeasured.

#### 15.2 Stress without energy where the shift is uniform
- **(a) Literature:** Morris–Thorne 1988 [FT-OCR]; Hochberg–Visser 1997
  (ρ carries no redshift function) [thm; FT]; Visser–Kar–Dadhich 2003
  (spatially Schwarzschild wormholes: ρ ≡ 0, all NEC violation
  lapse-supported) [der; FT]; Fewster–Roman 2005 (a null-contracted QI bounds
  lapse-supported violation) [der; FT]; Bolívar–Abellán–Vasilev 2026 [FT];
  Martín-Moruno–Visser 2021 [FT]; Loup–Waite–Halerewicz 2001 [claim; AB;
  the invariant content is N²ρ].
- **(b) Identities:** OS-I2 where the spatial metric is static and flat and
  the shift is spatially uniform, K_ij = 0, ρ = j = 0 and 8πT_ij =
  (δ_ij D²α − D_iD_jα)/α, Type I for any α(σ, x) including time dependence —
  D; OS-I10 — D*; TE-I14 — D; LDS-E.5 tensor — D.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K8 the sheath adds zero energy (6,230 →
  6,230) (D-cen, βh); OS-K11 (D-amp, βh).
- **(e) Quiz:** —
- **(f) Open:** —

#### 15.3 The lapse-only NEC lemma and the Komar balance; lapse maxima and the SEC
- **(a) Literature:** LDS-E.5 (derived in the survey; closest published:
  Bobrick–Martire 2021 §3.1, Barzegar–Buchert–Vigneron 2026 Thm IV.20,
  Martín-Moruno–Visser 2021) [der; symbolically checked]; Bobrick–Martire
  2021 [FT]; Barzegar–Buchert–Vigneron 2026 [FT].
- **(b) Identities:** LDS-E.5 lemma: every non-constant lapse on flat slices
  (time independent, α → 1, zero or uniform shift) violates the NEC
  somewhere; the two cases are the positive and zero Komar-mass branches —
  D (proof written, tensor checked; can be stated as T with these class
  conditions); OS-I10 Komar balance — D*; OS-I18 8πT(n + e, n + e) =
  (Δα − ∂²_eα)/α for any unit direction e; every lapse hill that returns to
  one violates the radial NEC on its fall [pure-lapse regions] — D;
  TE-I19 clock identity (R²A′)′ = 4πR²A(ρ + p_r + 2p_t): an interior lapse
  maximum needs a strong-energy-type violation [static spherical,
  proper-distance gauge] — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K18 the outer falls hold most of the null
  content: 1,334 of 2,286 (D-cmp), 456 of 799 (D-lap staged); the F(φ)R zero
  sits there at r ≈ 10.65 (✓).
- **(e) Quiz:** —
- **(f) Open:** TE-I19 was never checked against a design (TE-§8.1); the net
  ANEC over a whole lapse hill is not established (OS-§3.3.14).

#### 15.4 The lapse in static spherical geometries
- **(a) Literature:** Morris–Thorne 1988 [FT-OCR]; Hochberg–Visser 1997
  [FT]; Visser–Kar–Dadhich 2003 [FT]; Kar–Dadhich–Visser 2004 [FT];
  Fewster–Roman 2005 [FT]; Bolívar–Abellán–Vasilev 2026 (released lapse:
  regular hollow shells with flat cavities and Schwarzschild exteriors
  satisfying NEC, WEC, SEC and DEC on a compactness interval; Theorem 5)
  [thm + constr; FT]; Visser 1989b [FT]; Bobrick–Martire 2021 [FT].
- **(b) Identities:** TE-I16 static decomposition 8π(ρ, p_r, p_t) =
  W(1, −1, 0) + Z(−2, 0, 1) + Y(0, 2, 1) + X(0, 0, 1), with X = A″/A the
  clock curvature and Y the clock–radius overlap [static spherical,
  proper-distance gauge] — D*; TE-I17 — D*; TE-I19 — D*; TE-I20 static
  conservation — L.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** relies on the spherical machinery of 17.3 (Part 4).

#### 15.5 Time staging
- **(a) Literature:** —
- **(b) Identities:** OS-I2 (a lapse that moves or switches where the shift
  vanishes stays Type I and carries no energy) — D.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K13 static against staged sheath: standing
  content 53 → 0, transit content 1,616 → 799, QI requirement 0.60 → 0.047
  (D-lap, ✓); OS-K14 ungated windows: 26,895 Type IV points (D-lap, ✓);
  live-scheduled window: 18,931 → 2,972 (D-1S, βh held support).
- **(e) Quiz:** —
- **(f) Open:** no literature precedent in the inventories; the section rests
  on one identity and one design lineage.

#### 15.6 Measured examples (M)
- **(a) Literature:** —
- **(b) Identities:** —
- **(c) Practices:** 02 §2.3.
- **(d) Measured examples:** OS-K5 plateau thresholds (e⁴ needed in D-lap;
  e³ suffices in D-cmp and D-trim with sheath e¹) (✓); OS-K6 a convexity of
  0.3 replaces at least six e-folds of plateau height (D-lap, ✓); OS-K7 most
  of a 15× stress reduction comes from moving the service cutoff away from
  the plateau edge (D-lap, ✓); OS-K8 sheath thresholds; above threshold the
  amplitude hardly matters (✓); OS-K16 clock-rate stress curve (✓); OS-K18
  trimming (✓).
- **(e) Quiz:** —
- **(f) Open:** every entry is a single-design result; thresholds differ
  between designs.

### Chapter 16. The shift

#### 16.1 Carriage
- **(a) Literature:** Alcubierre 1994 [FT]; Natário 2002 [FT]; Krasnikov
  1998 [FT].
- **(b) Identities:** OS-P2 the packet's coordinate speed equals −β at its
  centre [class C0] — definition; OS-I3 — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K3 rest-to-rest carriage 0 → 2.1c → 0 at zero
  proper acceleration inside a flat compartment (D-cmp, ✓).
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics.
- **(f) Open:** —

#### 16.2 Energy density from shear and vorticity; integral negativity; α⁻² suppression
- **(a) Literature:** Alcubierre 1994 eq. 19 [FT]; Natário 2002 [FT];
  Lobo–Visser 2004 eq. 10 [FT]; Barzegar–Buchert 2025 (8πGε + Λ = −Ω²)
  [der; FT]; Santiago–Schuster–Visser 2022 eqs. 4.3–4.6 and 7.17 [thm; FT];
  Shoshany–Snodgrass 2024 eq. 4.3 and ∫N²ρ ≤ 0 [thm; FT];
  Santos-Pereira–Abreu–Ribeiro [AB]; Abellán–Bolívar–Vasilev 2023 [FT];
  Lentz 2021 [AB+] and Celmaster–Rubin 2025 [AB] (claim and refutation);
  Rodal 2023/2024 [AB]; White et al. 2025 (segmented walls relocate the
  energy) [AB]; Santiago–Schuster–Visser 2021 (tractor beams) [AB].
- **(b) Identities:** OS-I1 ρ = −(β_r/α)²/32π [class C0] — L at unit lapse,
  D for general lapse (Shoshany–Snodgrass eq. 4.3 reduces to it);
  ∫ρ = −∫ω²/32π [flat unit-lapse slices, localized] — L; ∫N²ρ d³x ≤ 0
  [flat slices, any lapse, C², β = O(r^{−1/2})] — L; the α⁻² suppression as
  a design lever — D (the project's addition).
- **(c) Practices:** —
- **(d) Measured examples:** OS-K5 e² ratio of peak negative energy (D-trim,
  ✓); OS-K12 removing all stretch: positive energy vanishes everywhere and
  standing energy 7.5×10⁴ → 0 (D-amp → D-lap).
- **(e) Quiz:** QB Published warp and wormhole context / Warp metrics.
- **(f) Open:** OS-§3.3.2 (the formula written with a stretch factor holds
  only for A = 1); LDS F.1.8 resolved by the identity.

#### 16.3 Momentum and vorticity; irrotational shifts
- **(a) Literature:** Santiago–Schuster–Visser 2022 (flux zero for gradient
  flows) [FT]; Fell–Heisenberg 2021 [AB+]; Le 2026b Lemma 2 (j ≡ 0 exactly for
  a gradient plus a rigid rotation, bounded vorticity on ℝ³) [thm; FT];
  Rodal 2025 [AB]; Barzegar–Buchert–Vigneron 2026 Thms III.15, IV.16, IV.17
  (vorticity-free Alcubierre, shear-free and harmonic-gradient R-Warp models
  are Minkowski) [thm; FT]; Schuster–Santiago–Visser 2023 [FT].
- **(b) Identities:** OS-I5c 8πT_n̂ẑ = −(1/2r)∂_r(rβ_r/α) and
  8πT_n̂r̂ = (1/2α²)∂_z(αβ_r) − (β_z/α)∂_r ln α; fluxes linear in β and
  O(1/α) [class C0] — D; j ≡ 0 iff gradient plus rigid rotation [flat
  unit-lapse slices] — L; TE-G6 structure: at fixed (α, A, B) the radial
  momentum j_l is affine in β with a 1/α prefactor and Δρ is quadratic with
  1/α², and where B′ = Ḃ = 0 a shift produces no j_l [spherical warped
  products; inventory derivation] — D*.
- **(c) Practices:** 02 §2.4 strategy row "irrotational or gradient shift"
  (Type I, still NEC-violating).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.9 (Rodal drive: Type I and energy-condition
  violating).

#### 16.4 Type IV at shear-layer edges
- **(a) Literature:** Le 2026b (walls 81–99% Type IV at v_s = 0.5; Van Den
  Broeck's Type IV fraction crosses 50% at v_s ≈ 0.38) [num; FT]; Le 2026a
  (Type IV onset linear in tilt, slope 1.01 ± 0.01) [num; FT]; Helmerich et
  al. 2024 [FT].
- **(b) Identities:** OS-I6 in a layer with α = A = 1, 8πT(n ± e_z,
  n ± e_z) = −(β_r² ± Δ⊥β): Type IV wherever |Δ⊥β| > β_r², always where a
  shift begins to vary — D*; the general-lapse extension (flux scales with
  the proper shear Aβ_r/α) is stated without derivation (OS-§3.3.1) — open.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K15 ordering probes: shift before stretch 525
  Type IV points, stretch before shift 0 (βx probes; label as an interaction
  example only); OS-K25 layer width (βx, cautionary).
- **(e) Quiz:** —
- **(f) Open:** proper-shear scaling with stretch unproven.

#### 16.5 Speed as a lapse contrast
- **(a) Literature:** Shoshany–Snodgrass 2024 (the lapse moves a drive
  between rest frames; ρ ∝ 1/N²) [FT]; Loup–Waite–Halerewicz 2001 [claim;
  AB]; Bobrick–Martire 2021 [FT]. No paper states the isometry (LDS E.4).
- **(b) Identities:** OS-I11 around the shift the metric depends on α dσ and
  β dσ, so (α, β) → (cα, cβ) with σ → σ/c is an isometry [steady lane; the
  lapse is multiplied wherever the shift is nonzero] — D*; LDS-E.5
  consequence: the contrast sits in NEC-violating falls — D.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 peak negative energy 0.009015 and
  envelope ratio 0.504 at every speed from 1.5 to 20 (D-trim, ✓; the
  identity on data); peak stress grows ≈ ln v (✓, measured-only).
- **(e) Quiz:** —
- **(f) Open:** OS-§3.3.5 (exact only in a steady lane; test tolerance 10⁻³
  against the reported 10⁻⁵); needs the pattern frame of 19.1 (Part 4).

#### 16.6 Energy scaling with speed
- **(a) Literature:** Lobo–Visser 2004 (E ∝ v²R²/Δ; an O(v) NEC term) [der;
  FT]; Le 2026b Lemma 4 (integrated negative Eulerian energy exactly
  quadratic on a fixed domain for shifts linear in speed) [thm; FT];
  Pfenning–Ford 1997 [FT]; Jusufi–Lobo 2026 [AB]; Bobrick–Martire 2021
  (flattening α_X = 1 + v² makes E velocity independent) [der; FT].
- **(b) Identities:** OS-I11 breaks the fixed-profile premise of the v² law
  (LDS E.1) — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 peak content 211 → 1,529 for v = 1.5 → 20,
  cone-dominated above v ≈ 3 (D-trim, ✓, measured-only).
- **(e) Quiz:** —
- **(f) Open:** overlaps 20.2.

### Chapter 17. The spatial geometry

#### 17.1 Curved slices and the ³R channel
- **(a) Literature:** Van Den Broeck 1999 (pocket region: energy through
  spatial curvature under a uniform shift) [num/der; FT]; Chowdhury 2025
  [der; AB]; Barzegar–Buchert–Vigneron 2026 Thm IV.33 [thm; FT];
  Barzegar–Buchert 2025 (tilted flows with spatial curvature, proposal)
  [claim within FT]; Garattini–Zatrimaylov 2024 (a wormhole embedding needs
  curved slices) [AB]; Bolívar–Abellán–Vasilev 2026 Theorem 5 [thm; FT];
  Fuchs et al. 2024 [FT].
- **(b) Identities:** 16πρ = ³R + K² − K_ijK^ij — L; OS-I10 static form — D*.
- **(c) Practices:** 02 §2.4 strategy row "curved slices (pocket)".
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** untested in the project (02 §2.2).

#### 17.2 Stretch and conformal factors
- **(a) Literature:** Van Den Broeck 1999 (conformal pocket factor) [FT].
- **(b) Identities:** OS-I7 for z-independent fields and zero shift,
  8πT(k±, k±) = −∇_{k±}∇_{k±}A/A − ∇_{k±}∇_{k±}C/C; time dependence splits the
  two Hessians and opens Type IV bands [class C0A sub-class] — D*; OS-I9
  where ln α and ln A rise together the radial flux vanishes [requires
  β_r = 0 across the rise] — D*; OS-I10 energy of each sign follows the
  stretch amplitude — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K9 pre-sheath energy ∝ e^φ while bands shrink
  ≈ e^(−1.5φ) (D-cen/D-amp, βh); OS-K10 the heritage support stretch did no
  work for arrival (D-cen → D-amp, βh); OS-K12 stretch against lapse fork
  (D-amp → D-lap).
- **(e) Quiz:** —
- **(f) Open:** OS-§3.3.4, 3.3.8, 3.3.9 (flux-free condition unstated;
  Hessian identity applied beyond its class; log-capacity argument
  underived).

#### 17.3 Spherical warped products: areal-radius Hessian, radial discriminant, string clouds
- **(a) Literature:** Morris–Thorne 1988 [FT-OCR]; Hochberg–Visser 1997,
  1998 [FT/AB]; Visser 1989a [FT].
- **(b) Identities:** TE-I1 G_ab = −(2/R)∇_a∇_bR + g_ab[(2/R)□R +
  ((∇R)² − 1)/R²] — L; TE-I2 every radial null vector obeys
  8πT(k, k) = −(2/R)k^ak^b∇_a∇_bR, so the radial NEC fails exactly where R is
  convex along affine radial null rays — D*; TE-I3 — D*; TE-I4 constant R
  gives an exact string cloud and moves every 2D dynamic into
  p_Ω = −K/8π — D*; TE-I12 areal flux of a radial string cloud (≈1/8π where
  R is nearly constant) — D*; TE-I27 areal-gauge mass relations — L; OS-I24
  (the same identities) — D*.
- **(c) Practices:** A8. Evidence pointer: SE E1.
- **(d) Measured examples:** TE-G31 constant-radius track: Type IV
  13,587 → 0; the angular NEC then fails where K > 1/R_b² (D-sph; identity
  demonstration); OS-K22 on the same track, slowing the decompression lowers
  the integrated angular deficit from 0.373 to 0.0063 with every point Type I
  (D-sph); transferred to the axial core the reduction falls to 60–72% and
  Type IV spreads over more samples (βx, cautionary); TE-G14 and TE-G24 only
  an edit of the areal radius moves the radial null energy directly, as
  TE-I2 predicts (2E and †; cautionary data checks).
- **(e) Quiz:** —
- **(f) Open:** TE-§8.3 (Type IV necessity).

#### 17.4 Throats: flare-out cost, tension, topology
- **(a) Literature:** Morris–Thorne 1988 (τ₀ = 1/(8πb₀²); flare-out τ₀ > ρ₀)
  [der; FT-OCR]; Hochberg–Visser 1997 (flare-out; genus) [thm; FT];
  Hochberg–Visser 1998 PRL and PRD (dynamic throats, anti-trapped surfaces)
  [thm; FT/AB]; Friedman–Schleich–Witt 1993 [FT]; Simpson–Visser 2019 [FT].
- **(b) Identities:** TE-I17 tension and opening are separate duties at the
  same location — D*; TE-I18 — D*; TE-I10 — D*.
- **(c) Practices:** split bulk tension from the null deficit before
  allocating sources (SE B8, one incident).
- **(d) Measured examples:** TE-G1 tension ratio (2E; data check of TE-I17);
  "throat-era radius scaling" (02 §2.3) is no controlled similarity sweep
  (TE-§8.2; unsuitable).
- **(e) Quiz:** —
- **(f) Open:** —

#### 17.5 Thin shells and junctions
- **(a) Literature:** Visser 1989a and 1989b [der; FT]; Poisson–Visser 1995,
  arXiv:gr-qc/9506083v1 (equation of state as the stability knob) [der; FT];
  Garcia–Lobo–Visser 2012, arXiv:1112.2057v3 [der; FT]; Eiroa–Rubín de
  Celis–Simeone 2025 [der; FT]; Liu et al. 2023, arXiv:2004.14267v4 [num; AB]; Huey 2024 (Israel jump in extrinsic curvature) [der; AB].
- **(b) Identities:** TE-I13 a metric function with a d^p cusp has stress
  ∝ d^{p−2}; a slope jump gives an h⁻¹ surface term; C² joins converge at
  first order and C∞ primitives at scheme order — D*; TE-Q10 capacitor-shell
  surface charge σ = (√f_in − √f_out)/(4πr) — D*.
- **(c) Practices:** A11 (set smoothness by the highest derivative the
  analysis uses; refined); read the sign of the surface stress a junction
  demands before choosing the shell material (SE L17).
- **(d) Measured examples:** TE-G28 receiver √ cusp: density −0.064 →
  −107.6 over five step halvings, ×2^{3/2} per halving; repair removed the
  divergence and left Type IV beneath it (†, cautionary; confirms TE-I13).
- **(e) Quiz:** —
- **(f) Open:** no Israel-junction primary source in the inventories;
  Poisson–Visser's admissibility of β₀² < 0 awaits a microphysical model
  (LDS F.3.7).

### Chapter 18. Coupling the elements

#### 18.1 The complete tensor of the flat-slice lapse–shift class
- **(a) Literature:** Santiago–Schuster–Visser 2022 (general flow, unit
  lapse) [FT]; Shoshany–Snodgrass 2024 eq. 4.3 (with lapse) [FT]; Le 2026b
  [FT].
- **(b) Identities:** OS-T3.2 complete orthonormal tensor of class C0
  (ds² = −α²dσ² + (dz + β dσ)² + dr² + r²dφ², α and β functions of σ, z, r):
  energy −s²/4 with s = β_r/α, fluxes linear in β and O(1/α), the lapse
  entering every null sum through its flat-space Hessian divided by α — D
  (compiler-checked; unpublished in this form).
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

#### 18.2 Lapse under a varying shift: exact discriminants and the envelope heuristic
- **(a) Literature:** Le 2026a (Type IV onset linear in tilt) [FT]; Fuchs et
  al. 2024 (the shift is bounded by flux ≤ energy) [FT].
- **(b) Identities:** OS-T3.2 (n, z) block 8π(ρ + p_z) = Δ⊥α/α − (β_r/α)² —
  D; OS-I5c — D; OS-I5 leading-order flux against null term — H; OS-I8
  envelope α > 2r|β_z| — H (Type I observed at ratios up to 1.59; neither
  necessary nor exact).
- **(c) Practices:** —
- **(d) Measured examples:** OS-K1 faster lanes need window gain 3 to meet
  the envelope (D-ch, βh); OS-K14 envelope violations 10 of 1,445 → 0 with a
  live-scheduled window (D-1S, βh); OS-K15 a shorter shift edge raises the
  envelope ratio to 0.66 (D-trim, ✓).
- **(e) Quiz:** —
- **(f) Open:** the envelope's neglected terms (OS-§3.3.3).

#### 18.3 Product regions
- **(a) Literature:** —
- **(b) Identities:** OS-I4 for a product of a 2D Lorentzian service metric
  (curvature K) with a transverse 2D metric (curvature K_Σ),
  T = diag(K_Σ, −K_Σ, −K, −K)/8π and along-track null energies vanish — D*;
  OS-I4c K = −α_zz/α − n(β_z/α) + (β_z/α)², so convex log-lapse drives K < 0
  and p_r > 0 — D; TE-I4 spherical analogue — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K6 convexity 0.3 clears the bands (D-lap, ✓);
  OS-K25 service-region content ∝ area and the string cushion's 72% deficit
  angle (βx, cautionary).
- **(e) Quiz:** —
- **(f) Open:** project-only section.

#### 18.4 Adjustment order
- **(a) Literature:** Suh (LEM D1) [PT]; Jones 2017 (LEM D2) [FT].
- **(b) Identities:** LEM Area 4 order: fix the shift for the carry, set the
  transition lapse for energy suppression, shape the shift-free stress with a
  separate lapse element.
- **(c) Practices:** C3.
- **(d) Measured examples:** OS-K15 ordering rules (the shift must vary where
  the lapse is high and still rising, after any stretch has returned to one)
  (βx probes; label).
- **(e) Quiz:** —
- **(f) Open:** duplicates 14.3.

#### 18.5 The combined design matrix
- **(a) Literature:** LEM D1–D5 [mixed].
- **(b) Identities:** OS coupling matrix codes I, i, M, S.
- **(c) Practices:** 02 §2.5.
- **(d) Measured examples:** OS §4 matrix (✓ and βh rows); TE §6 matrix (†,
  §, 2E; cautionary).
- **(e) Quiz:** —
- **(f) Open:** project-dominated (Part 3).

### Chapter 19. Moving structures

#### 19.1 The pattern frame and Killing energy
- **(a) Literature:** Natário 2002 (E(1 + X·n) = E₀; forward light
  blueshifted by 1 + v_s) [der; FT]; McMonigal–Lewis–O'Byrne 2012 [num; FT].
- **(b) Identities:** OS-I12 conserved Killing energy; where the shift
  vanishes d ln|k|/dσ = −k̂·∇α; kept gain exp(v∫(−∂_ζ ln α)dσ); exit-angle
  law gain = (v − 1)/(v cos θ_f − 1), checked on 20 exits to 3×10⁻⁹
  [stationary pattern frame, flat exterior] — D*.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Published warp and wormhole context / Warp geodesics.
- **(f) Open:** —

#### 19.2 Light surfaces and horizons
- **(a) Literature:** Barceló et al. 2022 [der; FT]; Natário 2002 [FT];
  Clark–Hiscock–Larson 1999 [num; AB]; Finazzi–Liberati–Barceló 2009 (black
  rear and white front horizons) [der; FT]; Hiscock 1997 [AB].
- **(b) Identities:** OS-I13 — D* (L: Barceló et al. 2022); TE-I5 — D*.
- **(c) Practices:** A9 (locate α² = b² surfaces and classify them;
  evidence-backed). Evidence pointers: SE L16, SE E11.
- **(d) Measured examples:** OS-K19 the current front is a white-hole disk
  (κ 9.1–9.7); the cone's surface is timelike wherever r > 0 (D-fr, ✓);
  TE-G27 guards leave g_σσ ≥ 0 regions and rays escape them (†, cautionary).
- **(e) Quiz:** QB Published warp and wormhole context / Warp geodesics.
- **(f) Open:** A9 is unlabelled in 05 (Part 2).

#### 19.3 Overtaken light and matter
- **(a) Literature:** McMonigal–Lewis–O'Byrne 2012 (time-locked particles
  released as a high-energy beam on deceleration) [num; FT]; Natário 2002
  [FT]; Everett–Roman 1997 [FT]; Pieri 2023 [claim; AB].
- **(b) Identities:** OS-I12 shelf law γ′ = (α_s² + v²)/(α_s² − v²), exit
  through a resting terminal at α_sγ′ [1D, α_s > v] — D*; OS-I13 growth
  e^{κt} at a front horizon — D*.
- **(c) Practices:** A9 (account for what is overtaken).
- **(d) Measured examples:** OS-K4 current front γ 1.0×10²², 1.3×10⁴⁷,
  1.7×10⁷²; shelves fixed at 10.8; cone ≤ 5.8 (D-fr, ✓); OS-K2 swept γ ≈ 92
  at v = 10 (D-trim, ✓).
- **(e) Quiz:** QB Published warp and wormhole context / Warp geodesics.
- **(f) Open:** —

#### 19.4 Front design: shelves, cones, the flank criterion
- **(a) Literature:** Natário 2002 (Mach angle sin α = 1/v) [der; FT]; Low
  1999 with the LDS E.2 derivation (sin θ < 1/v ⇔ subluminal normal speed)
  [thm; FT]; Barceló et al. 2022 (a convex bubble has two critical points;
  flat fronts accumulate more) [der; FT].
- **(b) Identities:** OS-I15 a front surface whose normal makes angle θ_c with
  the radius moves along its normal at v sin θ_c; light rides the flank once
  v sin θ_c > 1 [lapse front moving through a flat exterior] — D*; OS-I12
  shelf law — D*; OS-I14 — H.
- **(c) Practices:** A9; keep every front's normal speed below local light
  (SE L16).
- **(d) Measured examples:** OS-K20 near-axis gains 1.0–4.9 at 15°, 10⁶–10¹⁵
  at 45°; a fixed 15° cone traps light above v = 1/sin 15° = 3.9 (D-fr,
  D-trim, ✓); OS-K21 shelf cost 1.58 per unit route length (✓); OS-K19 cone
  +68% peak content (✓) (all measured-only, 02 §2.3).
- **(e) Quiz:** —
- **(f) Open:** the section title names project elements (Part 3); tip rates
  are estimates.

#### 19.5 Semiclassical response at fronts
- **(a) Literature:** Finazzi–Liberati–Barceló 2009 [FT];
  Coutant–Finazzi–Liberati–Parentani 2012 [AB]; Hiscock 1997 [AB]; Barceló et
  al. 2022 [FT]; Barceló–Liberati–Visser (dispersion leaves the Hawking
  spectrum approximately intact) [FT].
- **(b) Identities:** OS-I13, OS-I17 — D*; OS-I14 — H.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 tip κ 0.44 → 1.18 and λ/κ 3.7 → 34.9 for
  v = 1.5 → 20 (D-trim, ✓); OS-K19/K20 tip field evolution (D-fr, ✓).
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.5 (no 3+1 renormalized stress); exterior mixing
  bounded only at the window-edge control (OS-§3.3.13); duplicates 7.5 and
  29.3.

#### 19.6 Momentum and steering
- **(a) Literature:** Le 2026c, arXiv:2606.22531v4 (v1–v3 carry the old
  title) [thm-level argument + der; AB]; Bobrick–Martire 2021 (any drive
  needs propulsion) [claim within FT]; Barzegar–Buchert–Vigneron 2026
  Thm IV.19 [thm; FT]; Clough–Dietrich–Khan 2024 [num; FT];
  Shoshany–Snodgrass 2024 (frame switching) [FT]; LDS F.1.4.
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** Le 2026c read at abstract level only, and v4 narrows the
  scope; duplicates 27.4; Bondi four-momentum is introduced nowhere (Part 2).

### Chapter 20. Scaling laws

#### 20.1 Size
- **(a) Literature:** Pfenning–Ford 1997 [FT]; Lobo–Visser 2004 [FT];
  Jusufi–Lobo 2026 (E = −(15π/1024)v_s² l) [der; AB]; Van Den Broeck 1999
  [FT]; Pieri 2023 [claim; AB].
- **(b) Identities:** OS-I25 — D; TE-Q13 — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K27 stresses ∝ 1/L² (D-lap, ✓); TE-G1 radius
  comparison (2E; no similarity sweep; unsuitable).
- **(e) Quiz:** QB Established foundations / Dimensional analysis.
- **(f) Open:** —

#### 20.2 Speed
- **(a) Literature:** Lobo–Visser 2004 [FT]; Le 2026b Lemma 4 [FT];
  Shoshany–Snodgrass 2024 [FT]; Bobrick–Martire 2021 [FT].
- **(b) Identities:** OS-I11 — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K2 (D-trim, ✓); OS-K1 lead against lane speed
  (D-ch, βh).
- **(e) Quiz:** —
- **(f) Open:** overlaps 16.5 and 16.6.

#### 20.3 Wall thickness under QEIs
- **(a) Literature:** Pfenning–Ford 1997 (Δ ≲ 10² v_b L_P for α = 1/10)
  [der; FT]; Everett–Roman 1997 (ε ≲ 10⁴ l_P) [der; FT]; Ford–Roman 1996
  (a₀ ≲ (r₀/(8f⁴ℓ_P))^{1/3}ℓ_P) [der; FT]; Pfenning 1998 thesis [AB];
  Pfenning–Ford 1998 [FT]; Le 2026b eq. 36 (a static wall observer's
  threshold τ₀ ≃ c(ℓ_P R_b)^{1/2}) [der; FT]; Krasnikov 2003 [FT; disputes];
  Fewster–Roman 2005 [FT]; Kontou–Sanders 2020 §5 [FT]; Van Den Broeck 1999
  (QI met for Eulerian observers) [FT].
- **(b) Identities:** OS-I21 Casimir gap a = 0.58√(ℓ_P L) — D*; shear-layer
  form αw/Δβ ≲ ℓ_P/f² (LDS E.2, "this inventory") — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K27 QI requirement (D-lap staged, ✓).
- **(e) Quiz:** QB Published warp and wormhole context / Quantum
  inequalities (4).
- **(f) Open:** the flat-QI-in-small-regions assumption is argued, not proven;
  LDS F.1.14, F.2.4.

#### 20.4 Shape
- **(a) Literature:** Bobrick–Martire 2021 (flattening; variational optimum
  f̄ = min(r₀/r, 1) saves a factor of about 3) [der; FT]; Van Den Broeck 1999
  [FT]; Natário 2002 and Rodal 2024 (removing expansion keeps or raises the
  shear) [FT/AB]; White et al. 2025 [AB]; Rodal 2025 (irrotational: peak
  deficit 38× below Alcubierre) [AB]; Barceló et al. 2022 (front convexity)
  [FT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** OS-K6/OS-K7 plateau convexity and shape (D-lap,
  ✓); OS-K20 cone shape (✓).
- **(e) Quiz:** —
- **(f) Open:** —

### Chapter 21. Strategies and their price

#### 21.1 The catalogue
- **(a) Literature:** the 02 §2.2 responses: Van Den Broeck 1999 (pocket);
  Pfenning–Ford 1997 (walls under QEIs); Bobrick–Martire 2021 (flattening);
  Fuchs et al. 2024 and Le 2026a (positive-mass shells, Type IV tail);
  Poisson–Visser 1995 (equation of state); Horndeski no-go results and
  beyond-Horndeski escapes (25.3 anchors); Le 2026c (steering); Gao–Jafferis–Wall
  2017, Maldacena–Milekhin–Popov, Kontou 2024 (long and short wormholes).
  Further literature strategies: Natário 2002 (zero expansion); Rodal 2025
  (irrotational); White et al. 2025 (segmentation); Bolívar–Abellán–Vasilev
  2026 (released lapse); Garattini–Zatrimaylov (background flows);
  Simpson–Visser 2019 (black-bounce family); Krasnikov 1998 and
  Everett–Roman 1997 (corridor laid along the route).
- **(b) Identities:** those behind the project rows: OS-I1, OS-I2, OS-I3,
  OS-I6, OS-I11, OS-I15, TE-I4, LDS-E.5.
- **(c) Practices:** 02 §2.4 (each strategy with what it buys, what it costs,
  and the status of both).
- **(d) Measured examples:** cone +68% peak demand (D-fr, ✓); shelf cost
  proportional to route length (✓); a hotter rear horizon at higher speed
  (D-trim, ✓).
- **(e) Quiz:** —
- **(f) Open:** 7 of the 11 rows of 02 §2.4 are project strategies (Part 3).

#### 21.2 Where the NEC violation goes
- **(a) Literature:** Hochberg–Visser 1997, 1998 [FT]; LDS D.13 item 2
  (moving the violation into another sector relabels which term violates
  it); Lobo–Oliveira 2009, arXiv:0909.5539v2 [der; FT];
  Kanti–Kleihaus–Kunz 2011, arXiv:1108.3003v2 [num; AB] and 2012,
  arXiv:1111.4049v3 [der; FT; its stability claim refuted]; Cuyubamba–Konoplya–Zhidenko 2018,
  arXiv:1804.11170v2 [num; FT]; Santiago–Schuster–Visser 2022 (modified
  gravity violates the null convergence condition) [claim/der; FT];
  Rubakov 2016a, arXiv:1509.08808v3 [der (LF), thm (LDS); FT].
- **(b) Identities:** LDS-E.5 — D; OS-I18 (the falls hold the null deficit)
  — D; TE-I17, TE-I18 — D*.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K18 outer falls hold most of the content
  (D-cmp, D-lap, ✓).
- **(e) Quiz:** QB Published warp and wormhole context / Scalar-source
  literature (3).
- **(f) Open:** LDS F.3.4 (effective-stress framing against Hochberg–Visser).

#### 21.3 Class choices
- **(a) Literature:** Santiago–Schuster–Visser 2022 (scope: unit lapse, flat
  slices) [FT]; Shoshany–Snodgrass 2024 [FT]; Barzegar–Buchert–Vigneron 2026
  (R-Warp class theorems) [FT]; Bolívar–Abellán–Vasilev 2026 [FT];
  Bobrick–Martire 2021 [FT].
- **(b) Identities:** LDS-E.5 (flat slices carry a structural lapse cost;
  curved slices escape it) — D.
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

## Part IV. Supplying the demand

### Chapter 22. The supply problem

#### 22.1 Algebraic range of source families
- **(a) Literature:** Gergely 2026, arXiv:2608.15228v1 [der; AB+];
  Martín-Moruno–Visser 2018 [AB] and 2021 [FT]; Banerjee et al. 2023,
  arXiv:2307.13846v2 [der; AB]; Deffayet et al. 2010, arXiv:1008.0048v2 [der;
  AB]; Zhang et al. 2011 (LEM T10) [emp; FT]; Li–Pendry 2008 (LEM T7) [FT].
- **(b) Identities:** TE-I23 static canonical fields give radial and angular
  null stresses 2(K + D) and 2(K + E), so components with non-negative null
  stress cannot reduce the negative null requirement — D*; TE-I25 — D*;
  TE-Q2 anomaly lock ρ_Q − p_{r,Q} = ηc/(48π²R²)(a″ + a′²): a conformal radial
  channel cannot change the sign of ρ − p_r [radial 1+1 conformal channels,
  spherically averaged] — D*; TE-Q5 — D*; TE-S3 tension-carrier algebra (a
  (1, −1, 0) carrier removes tension without touching ρ + p_r) — D*.
- **(c) Practices:** A2; LEM Area 3 lesson 2 ("hard" is relative to the
  source technology).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Source model basics.
- **(f) Open:** —

#### 22.2 Class-level exclusions first (A5)
- **(a) Literature:** the achronal-ANEC chain (Gao–Wald 2000, Graham–Olum
  2007 Lemma 1, Wall 2010, Kontou–Olum 2015) [FT]; QEI with field counts
  (Ford–Roman 1996, 1997 [FT]; Dvali 2010, Dvali–Redi 2008 [AB]); Horndeski
  no-go results (Kobayashi 2016, arXiv:1606.05831v2 [thm; AB];
  Evseev–Melichev 2018, arXiv:1711.04152v1 [thm; FT]; Libanov–Mironov–Rubakov
  2016, arXiv:1605.05992v2 [thm; AB]); Rodal 2025 (metamaterial coupling),
  arXiv:2507.09724v2 [der + experimental bounds; AB]; physical limits on
  cloaking (LEM T11: Hashemi et al. 2010 [FT], Monticone–Alù 2013 [FT] and
  2016 [AB], Miller 2006 [AB], Fano 1950 [PT]); Lawson 1957 and Wurzel–Hsu
  2022 (LEM S5) [PT/FT].
- **(b) Identities:** OS-I21 (QI requirement, species length, Casimir gap,
  F(φ)R bound-state count) — D*; OS-I23 in its qualified form — L.
- **(c) Practices:** A5 (evidence-backed; the central ordering principle;
  keep the exact scope of each exclusion). Evidence pointers: SE L1 (n = 12,
  strength A), SE E15, SE B7, SE D8, MJ I-19.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** the quantum exclusion is conditional (02 §4); applies
  exclusions whose physics sits in 23–25 (Part 4).

#### 22.3 Absolute scale
- **(a) Literature:** Wurzel–Hsu 2022 (LEM S5) [emp; FT]; Buckingham 1914
  [PT]; Pfenning–Ford 1997 (energies in solar masses) [FT].
- **(b) Identities:** OS-I25 — D; TE-S18 E_peak = (5.86×10²⁶ V)/L, so the
  Schwinger field is reached at L ≈ 4.43×10⁸ m; enlarging L lowers the field
  and leaves the dimensionless material-energy ratio unchanged — D* (the
  number rests on beta075 V5 histories, †).
- **(c) Practices:** A5 (fix the absolute scale). Evidence pointer: SE D7
  (scale windows that conflict).
- **(d) Measured examples:** OS-K27 (D-lap, ✓).
- **(e) Quiz:** QB Established foundations / Dimensional analysis.
- **(f) Open:** duplicates 9.4.

#### 22.4 A screening sequence with exact scopes
- **(a) Literature:** Cooper 1990 (LEM S4) [std; FT]; Millis 2005 (LEM S6:
  minimal go/no-go tasks) [std; FT]; Browning 2001 (LEM D5: activity
  sequencing so each step's information exists first) [std; FT].
- **(b) Identities:** —
- **(c) Practices:** A5; truism: stage-gate ordering; P01 §2a (cost
  asymmetry), P01 §2h (passing a gate is necessary, never sufficient).
  Evidence pointer: SE C15 (cheap nodewise screens excluded families early).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** the sequence comes from one project's workflow; state it in
  general form with its scopes.

### Chapter 23. Ordinary matter under relativistic stress

#### 23.1 Strength-to-energy ratios
- **(a) Literature:** —
- **(b) Identities:** TE-S14 sleeve strength k = allowable stress / proper
  energy density (definition); TE-Q11 sleeve virial bound
  E_sleeve ≥ 2E/(3k(1 + πa/L)) — D*; TE-Q12 H ≤ 2kE_material — D*.
- **(c) Practices:** —
- **(d) Measured examples:** TE-S14 "demonstrated materials" (graphene
  k ≈ 6.15×10⁻¹⁰, carbon nanolattices ≈ 4×10⁻¹¹) come from a project report
  whose sources are outside every inventory (UV); required k of 0.74–0.95 (†,
  unsuitable).
- **(e) Quiz:** —
- **(f) Open:** no verified literature anchor for material data.

#### 23.2 Electromagnetic stresses and confinement
- **(a) Literature:** —
- **(b) Identities:** TE-Q11 confinement B²/8π > P_γ + P_e± — D*; TE-Q12
  T^Maxwell = u(δ − 2bb) — D*; TE-Q8 shared-field cross term
  u_E = (Q_L² + Q_R²)/2R⁴ + Q_LQ_R/R⁴ — D*; TE-S3 radial-field Maxwell tensor
  ½E²(1, −1, 0, +1) — D*; TE-S15 jacket pressure relations — D*.
- **(c) Practices:** per-constituent principal stresses (SE D3).
- **(d) Measured examples:** TE-S14/S15 thresholds (†, unsuitable); TE-S16 an
  averaged tensor (1, 1, 0) hides the mechanical difference between a hoop
  field and axial photons (†; the lesson is general, the numbers unsuitable).
- **(e) Quiz:** —
- **(f) Open:** thin literature.

#### 23.3 Strings, sheets and oriented ensembles
- **(a) Literature:** Visser 1989a (field-theoretic strings carry positive
  tension) [der; FT].
- **(b) Identities:** TE-Q12 — D*; TE-I4 — D*; TE-I12 — D*.
- **(c) Practices:** —
- **(d) Measured examples:** TE-S16 (†, cautionary).
- **(e) Quiz:** —
- **(f) Open:** thin literature; no string-cloud primary source.

#### 23.4 Junction stress and charged shells
- **(a) Literature:** Visser 1989a and 1989b [FT]; Poisson–Visser 1995 [FT];
  Garcia–Lobo–Visser 2012 [FT].
- **(b) Identities:** TE-Q10 σ = (√f_in − √f_out)/(4πr) and
  U_E/(M_in + M_out) ≤ 2(b − a)/(b + a) [charged spherical shells] — D*.
- **(c) Practices:** SE L17.
- **(d) Measured examples:** TE-S17 capacitor field-to-wall ratio 0.048 →
  3.27 (†, unsuitable).
- **(e) Quiz:** —
- **(f) Open:** Israel-junction primary source absent.

#### 23.5 Storage limits
- **(a) Literature:** Tolman 1930 (the weight of heat) [der; AB].
- **(b) Identities:** TE-Q10, TE-Q11, TE-Q13 — D*; the Tolman integrating
  factor for pressure columns in a clock gradient — L.
- **(c) Practices:** screen stores by E/Mc² first (SE C6); virial bounds
  before sweeps (SE D4); count GR self-weight (SE C9); count the complete
  ledger (SE C8, SE L14).
- **(d) Measured examples:** TE-S17 storage media (†, unsuitable).
- **(e) Quiz:** —
- **(f) Open:** thin literature.

### Chapter 24. Quantum sources

#### 24.1 Casimir systems and the mirror's energy
- **(a) Literature:** Morris–Thorne–Yurtsever 1988 (plate separation; plate
  models left open) [der; FT-OCR]; Garattini 2019, arXiv:1907.03623v1 [der;
  FT]; Graham–Olum 2005 (plate with a hole obeys ANEC) [der; AB];
  Fewster–Olum–Pfenning 2007 [thm; AB]; Ford–Roman 1996 [FT].
- **(b) Identities:** TE-Q7 planar EM Casimir cells C = ηπ²/(720d⁴);
  independently held cells need holder energy ≥ 3(C_r + 2C_t), complete cells
  ≥ 2(C_r + 2C_t) — D*; TE-Q6 Dirichlet-end response (Δρ, Δp_r, Δp_t) =
  Δb(1/6, 1/2, −1/6) and held-interaction bound d|F|/|E| > 1 — D*; TE-Q9
  scalar-mirror proximity h ∝ η/a³ — D*; TE-Q3 reflector reaction
  F = −4πR²[p_r] — D*; OS-I21 Casimir gap a = 0.58√(ℓ_P L) and ~10⁷ mirror
  overhead — D*.
- **(c) Practices:** A6. Evidence pointers: SE B3, SE E10.
- **(d) Measured examples:** OS-K27 the mirror energy exceeds the deficit by
  ~10⁷ at every gap (D-lap, ✓); TE-S11/S13 (§, cautionary).
- **(e) Quiz:** QB Established foundations / Casimir effect (8); Boundary
  conditions (3).
- **(f) Open:** no verified literature on the energy cost of Casimir mirrors
  or on laboratory Casimir measurements; the Morris–Thorne–Yurtsever
  prefactor is UV.

#### 24.2 States with negative energy density
- **(a) Literature:** Epstein–Glaser–Jaffe 1965 [thm; AB]; Ford–Roman 1995,
  1997 [der; FT]; Ford–Helfer–Roman 2002 [thm; AB]; Fewster–Roman 2003
  (multimode two-particle superpositions) [thm; FT];
  Fliss–Freivogel–Kontou–Pardo Santos 2025 (conformally coupled free bosons
  reach unbounded negative smeared null energy) [der; AB]; Olum–Graham 2003
  [der; AB]; Visser 1996–97 (Boulware and Unruh states) [num; AB];
  Abdolrahimi–Page–Tzounis 2019 [AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Quantum vacuum (2); QFT basics
  (9).
- **(f) Open:** the "laboratory negative-energy modalities" that 05 lists for
  this chapter have no anchor in any inventory.

#### 24.3 Field counts and the species bound
- **(a) Literature:** Ford–Roman 1996, 1997 [FT]; Dvali 2010 [AB];
  Dvali–Redi 2008 [AB]; Freivogel–Krommydas 2018 [FT]; Kontou–Sanders 2020
  [FT].
- **(b) Identities:** OS-I21 N ≥ Q(L/ℓ_P)² and ℓ* = √Q L — D*.
- **(c) Practices:** A5. Evidence pointers: SE L22, SE D9.
- **(d) Measured examples:** OS-K27 (D-lap staged, ✓); TE-S4/S5 central-charge
  inventories of 4.3×10⁶ to 2.8×10⁸ (§, cautionary).
- **(e) Quiz:** —
- **(f) Open:** duplicates 7.4.

#### 24.4 Vacuum polarization and the anomaly
- **(a) Literature:** Capper–Duff 1974, Christensen–Fulling 1977 [der; AB];
  Deser–Schwimmer 1993, Duff 1994 [AB]; Visser 1995 [der; AB];
  Hollands–Wald 2015 [AB]; Page 1982 [AB]; Anderson–Hiscock–Samuel 1995
  [AB]; Candelas 1980 [PT].
- **(b) Identities:** OS-I22 — L (application D*); TE-Q1 radial 1+1
  conformal channels, spherically averaged — D*; TE-Q2 anomaly lock — D*;
  TE-Q5 conformal scalar on a cylinder, ρ ∝ −2 log(R/a₀), angular null energy
  negative for log(R/a₀) > 1/4 — D*.
- **(c) Practices:** anomaly-fixed combinations cannot be tuned; the Wald
  renormalization ambiguity moves stress and supplies none (SE L22, SE D10,
  SE D12).
- **(d) Measured examples:** OS-K2 trace-to-demand ratio 0.74 → 1.64 ×
  (ℓ_P/L)² (D-trim, ✓); OS-K27 ~2×10⁻⁷⁰ at 1 m (✓); TE-S9 curvature-coupling
  outcomes (§, cautionary).
- **(e) Quiz:** QB Established foundations / Semiclassical gravity.
- **(f) Open:** duplicates 7.1.

#### 24.5 Scope of quantum exclusions
- **(a) Literature:** Graham–Olum 2007 [FT]; Wall 2010 [FT]; Kontou–Olum
  2015 [FT]; Urban–Olum 2010 [FT]; Ishibashi–Maeda–Mefford 2019 [AB];
  Faulkner et al. 2016, Hartman et al. 2017 [FT]; Kontou–Sanders 2020 [FT];
  Kontou 2024 [FT]; Gao–Jafferis–Wall 2017, Maldacena–Milekhin–Popov,
  Fu–Grado-White–Marolf 2019a,b [FT]; Kanai–Maeda–Yoshida 2025 [AB];
  LDS C.7 assessment.
- **(b) Identities:** OS-I23 qualified — L (conditional).
- **(c) Practices:** correction 02 §4 (achronal ANEC); A5 refinement.
- **(d) Measured examples:** OS-K2/OS-K4 first-light ANEC signs (D-trim,
  ✓).
- **(e) Quiz:** —
- **(f) Open:** achronality of the complete ray and the transverse width of
  the negative-ANEC bundle remain unmeasured (LDS C.7 qualifications 2–3).

### Chapter 25. Classical NEC-violating fields

#### 25.1 Canonical fields and curvature couplings (bound-state test)
- **(a) Literature:** Barceló–Visser 2000, arXiv:gr-qc/0003025v2 (non-minimal
  scalars need trans-Planckian values; the effective Newton constant changes
  sign) [der; AB]; Fliss et al. 2024 [der; AB]; Bronnikov–Starobinsky 2007,
  arXiv:gr-qc/0612032v1 [thm; AB]; Kontou–Sanders 2020 (non-minimal coupling:
  only state-dependent QEIs) [FT]; ghost and phantom scalars:
  Shinkai–Hayward 2002, arXiv:gr-qc/0205041v2 [num; FT],
  Gonzalez–Guzman–Sarbach 2009a,b, arXiv:0806.0608v2 and
  arXiv:0806.1370v2 [thm/num; FT].
- **(b) Identities:** OS-I21 for F(φ)R theories F″ ≤ 8πT(k, k)F along affinely
  parametrized null geodesics, F vanishes by the first zero of
  ψ″ = 8πT(k, k)ψ, and the zero count is the bound-state count of
  −d²/dλ² + 8πT(k, k), scale-free — D*; TE-I23 — D*.
- **(c) Practices:** audition the simplest source family against the full
  demand pattern cheaply (MJ I-20, n = 2).
- **(d) Measured examples:** TE-DR3 non-minimal scalar screen: best radial-null
  coverage 0.0072, top-20 overlap 0/20 (promoted pair before beta075, type
  untested; cautionary); OS-K18 the F(φ)R zero at r ≈ 10.65 (D-lap, ✓).
- **(e) Quiz:** QB Published warp and wormhole context / Scalar-source
  literature (3).
- **(f) Open:** —

#### 25.2 Higher-derivative scalars
- **(a) Literature:** Horndeski 1974, no arXiv [thm; AB]; Deffayet et al.
  2010 [der; AB]; Creminelli–Luty–Nicolis–Senatore 2006,
  arXiv:hep-th/0606090v2 [der; AB]; Creminelli–Nicolis–Trincherini 2010,
  arXiv:1007.0027v2 [der; AB]; Rubakov 2014, arXiv:1401.4024v2 [rev; AB];
  Kobayashi 2019, arXiv:1901.07183v2 [rev; AB]; Gergely 2026 [AB+];
  Banerjee et al. 2023 [AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Effective field theory (8).
- **(f) Open:** —

#### 25.3 Stability and no-go results with their scopes
- **(a) Literature:** Dubovsky et al. 2006 [thm-level; AB];
  Libanov–Mironov–Rubakov 2016 [thm; AB]; Kobayashi 2016 [thm; AB];
  Creminelli–Pirtskhalava–Santoni–Trincherini 2016, arXiv:1610.04207v2 [der;
  AB]; Ijjas–Steinhardt 2017, arXiv:1609.01253v5 [der; AB];
  Kolevatov–Mironov–Sukhov–Volkova 2017, arXiv:1705.06626v2 [der; AB];
  Rubakov 2016a, arXiv:1509.08808v3 [der (LF), thm (LDS); FT] and 2016b, arXiv:1601.06566v1 [thm; FT];
  Evseev–Melichev 2018 [thm; FT]; Franciolini et al. 2019,
  arXiv:1811.05481v2 [der; FT]; Mironov–Rubakov–Volkova 2018,
  arXiv:1811.05832v1, 2019, arXiv:1812.07022v2, 2023, arXiv:2212.05969v1
  [der; FT]; Mironov–Volkova 2024, arXiv:2404.06297v2 [der; AB; journal UV];
  Bronnikov–Starobinsky 2007 [thm; AB]; wormhole instabilities:
  Bronnikov–Fabris–Zhidenko 2011, arXiv:1109.6576v2 [AB],
  Bronnikov–Konoplya–Zhidenko 2012, arXiv:1205.2224v3 [AB],
  Cremona–Pirotta–Pizzocchero 2019, arXiv:1805.02602v3 [AB];
  Kanti–Kleihaus–Kunz 2011/2012 and Cuyubamba–Konoplya–Zhidenko 2018;
  Liu et al. 2023 [AB]; Gurses–Sisman–Tekin 2020, arXiv:2004.03390v3 [claim; AB].
- **(b) Identities:** —
- **(c) Practices:** correction 02 §4 (Horndeski no-go results are specific
  to their settings).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Stability and perturbations (4).
- **(f) Open:** how Ijjas–Steinhardt evades the Kobayashi no-go is UV; the
  beyond-Horndeski tachyonic sector is open (LDS F.3.3); 4D Einstein–Gauss–Bonnet
  existence disputed (LDS F.3.4).

#### 25.4 Superluminality and UV completion
- **(a) Literature:** Adams et al. 2006, arXiv:hep-th/0602178v2 [der; AB];
  Dubovsky et al. 2006 [AB]; Mironov–Rubakov–Volkova 2023 (superluminal
  angular propagation in the explicit example) [FT];
  Coutant–Finazzi–Liberati–Parentani 2012 (modified dispersion) [AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Effective field theory.
- **(f) Open:** UV completion of beyond-Horndeski wormholes open (LDS F.3.3).

#### 25.5 Algebraic range
- **(a) Literature:** Gergely 2026 (timelike sector Types I, II, IV; the NEC
  excludes III and IV; admissible spacelike braiding is diagonal) [der; AB+];
  Deffayet et al. 2010 [AB]; Banerjee et al. 2023 [AB]; Rodal 2026
  (birefringent vacuum screening, exploratory) [num; AB].
- **(b) Identities:** —
- **(c) Practices:** A2.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

### Chapter 26. Net supply

#### 26.1 NEC-satisfying parts only add to the deficit (A6)
- **(a) Literature:** —
- **(b) Identities:** additivity of null energy over components — D; TE-I23 —
  D*.
- **(c) Practices:** A6 (evidence-backed). Evidence pointers: SE L2 (strength
  A; 12 instances), SE B2, SE C4 (null projection with its Doppler weight
  before dynamics), SE B8.
- **(d) Measured examples:** — (all instances are † or §).
- **(e) Quiz:** —
- **(f) Open:** 02 §3.1 cites "Lit (Casimir mirror cost)" for A6; no verified
  paper on mirror energy exists in the inventories.

#### 26.2 Accounting boundaries and gain chains
- **(a) Literature:** LEM S5: Wurzel–Hsu 2022 [emp; FT];
  Abu-Shawareb et al. 2024 [emp; AB]; Tillack et al. 2009 [PT; the 2008
  presentation read]; Lawson 1957 [PT].
- **(b) Identities:** —
- **(c) Practices:** A6 refinement (name the accounting boundary at each
  gain). Evidence pointers: SE L14, SE C8.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

#### 26.3 Holding costs
- **(a) Literature:** Morris–Thorne–Yurtsever 1988 (plate models left open)
  [FT-OCR].
- **(b) Identities:** TE-Q6 E_int + d|F_int| > 0 for a DEC-obeying direct
  static support — D*; TE-Q7 holder bounds; a directly held static
  negative-energy cell costs more positive holding energy than it supplies
  (TE-S13) — D*; TE-Q3 outer end loads grow as the square of the compartment
  count — D*.
- **(c) Practices:** SE B3, SE E10.
- **(d) Measured examples:** TE-S8 end loads 9.03 → ≈1.51×10⁶ (§,
  cautionary).
- **(e) Quiz:** —
- **(f) Open:** thin literature.

### Chapter 27. Assemblies

#### 27.1 Component tensors on one shared geometry
- **(a) Literature:** Oberkampf–Trucano 2002 (LEM V9: coupled tier required)
  [std; FT].
- **(b) Identities:** TE-I15 — D*; TE-Q8 — D*; the nonlinearity of the
  Einstein equations (standard) — L.
- **(c) Practices:** A7 (assigning a known tensor to components always
  succeeds). Evidence pointers: SE A2, SE L14, SE D3.
- **(d) Measured examples:** TE-S1 separated modules against a connected
  control: charge inventory ×2 and support energy +77% (§, cautionary);
  TE-S2 overlap placements (§, cautionary).
- **(e) Quiz:** —
- **(f) Open:** thin literature; the C1 architecture itself is excluded
  (02 §3.6).

#### 27.2 Interaction contracts and recoil
- **(a) Literature:** NASA SE Handbook (LEM S2: interface control documents)
  [std; FT]; Browning 2001 (LEM D5) [FT]; Barzegar–Buchert–Vigneron 2026
  Thm IV.19 [FT]; Le 2026c [AB].
- **(b) Identities:** —
- **(c) Practices:** truism: interface contracts.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** thin literature.

#### 27.3 Function and physical realization
- **(a) Literature:** Suh (LEM D1: functional and physical domains) [std;
  PT].
- **(b) Identities:** —
- **(c) Practices:** 02 §3.6 (the function–realization distinction survives
  as a general point); LEM closing table row P11 (supported as the FR/DP
  distinction).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** thin; the section risks carrying the project's architecture.

#### 27.4 Momentum exchange by radiation
- **(a) Literature:** Le 2026c (Bondi four-momentum changes only by radiation;
  −ṁ ≥ 3m|a| in v1–v3; m_f/m_i = e^{−3L} in v4; surface DEC for
  2m/R < 24/25) [thm-level + der; AB]; Bobrick–Martire 2021 [FT];
  Clough–Dietrich–Khan 2024 [FT]; Barzegar–Buchert–Vigneron 2026 [FT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** duplicates 19.6; abstract-level only; Bondi concepts absent
  from Part I.

### Chapter 28. Realizability as a design objective

#### 28.1 Spending design freedom on sourceability (C6)
- **(a) Literature:** Li–Pendry 2008 (LEM T7) [meth; FT]; Zhang et al. 2011
  and Chen et al. 2011 (LEM T10) [emp; FT/AB]; Pendry–Schurig–Smith 2006
  (LEM T1) [AB]; Leonhardt 2006, arXiv:physics/0602092 (version not
  recorded) (LEM T2) [der; AB]; Schurig et al. 2006 (LEM T3), Cai et al. 2007
  (LEM T5), Liu et al. 2009 and Valentine et al. 2009 (LEM T8) [emp; AB].
- **(b) Identities:** —
- **(c) Practices:** C6 (supported; imported); LEM Area 3 lessons 1–2.
- **(d) Measured examples:** TE-G31 as the in-field instance: among
  geometries with the same service, holding the areal radius constant removed
  the Type IV demand (D-sph; identity demonstration).
- **(e) Quiz:** QB Design review and synthesis / Paper-to-design transfer
  (1), recast.
- **(f) Open:** —

#### 28.2 Forward checks of simplified designs
- **(a) Literature:** Cummer et al. 2006 (LEM T4) [num; AB];
  Yan–Ruan–Qiu 2007, arXiv:0706.0655 (version not recorded) (LEM T6) [der;
  FT]; Zhang–Chan–Wu 2010, arXiv:1004.2551 (version not recorded) (LEM T9)
  [der; AB].
- **(b) Identities:** —
- **(c) Practices:** C6 (forward-check the simplified source on every service
  observable); keep a ledger of relaxations (SE F8; D4).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

#### 28.3 Realizability inside the design loop
- **(a) Literature:** Bendsøe–Kikuchi 1988 [PT], Bendsøe–Sigmund 2003 [PT],
  Sigmund 2001 [FT], Sigmund–Petersson 1998 [PT], Wang–Lazarov–Sigmund 2011
  [AB], Olason–Tidman 2010 [FT] (LEM T13); Molesky et al. 2018 (LEM T14)
  [FT]; Bobrick–Martire 2021 (variational profile optimum) [FT]; Warp
  Factory toolkit paper, arXiv:2404.10855v1 (perturbative optimizer) [meth;
  companion, not read in full]; Fuchs et al. 2024 (1D profile optimization as
  future work) [FT]; LDS E.1 gap statement (no paper optimizes a warp
  geometry against certified all-observer margins).
- **(b) Identities:** —
- **(c) Practices:** put the second law, passivity and regularity inside
  inverse source optimization (SE L18, SE C13, SE D14).
- **(d) Measured examples:** TE-S5/S6 LP allocations (§, cautionary).
- **(e) Quiz:** —
- **(f) Open:** optimization against certified margins is an open gap.

## Part V. Dynamics

### Chapter 29. Dynamics, back-reaction and stability

#### 29.1 Prescribed metrics and solutions
- **(a) Literature:** Fourès-Bruhat 1952, Choquet-Bruhat–Geroch 1969,
  Smarr–York 1978, no arXiv [PT]; ADM 1962/2008 [AB];
  Barzegar–Buchert–Vigneron 2026 Errors 19–20 (a proper 3+1 initial-value
  formulation is missing from much warp work) [critique; FT];
  Barzegar–Buchert 2025 [FT]; Santos-Pereira–Abreu–Ribeiro [AB]; Fuchs et
  al. 2024 (not a TOV solution per Barzegar–Buchert–Vigneron) [FT].
- **(b) Identities:** T = G/8π as a prescription; the method of manufactured
  solutions run in reverse (LEM Area 1) — L.
- **(c) Practices:** A7; calibration differs from validation (LEM V9).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Einstein equation.
- **(f) Open:** —

#### 29.2 Evolving warp spacetimes with matter
- **(a) Literature:** Clough–Dietrich–Khan 2024, arXiv:2406.02466v2 (full
  numerical relativity, stiff fluid; containment failure radiates a burst at
  frequency ~1/R; matter flux exceeds the GW flux) [num; FT];
  Buchert–Frackowiak 2026, arXiv:2605.03653v1 (generic instability of a
  geodesically determined realization) [der; AB];
  Santos-Pereira–Abreu–Ribeiro (Burgers dynamics) [AB];
  Abellán–Bolívar–Vasilev 2023, arXiv:2305.03736v1 [num; AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** — (coupled dynamics are open in the project;
  TE-M8's "3+1 backreaction" proxy is invalidated, †).
- **(e) Quiz:** —
- **(f) Open:** one full evolution in the inventories.

#### 29.3 Semiclassical back-reaction
- **(a) Literature:** Finazzi–Liberati–Barceló 2009 [FT]; Hiscock 1997 [AB];
  Flanagan–Wald 1996 [AB]; Hochberg–Popov–Sushkov 1997 [num; FT];
  Kim–Thorne 1991 [AB]; Hawking 1992 [AB + TL]; Hu–Verdaguer 2008 [AB];
  Martín-Moruno–Visser 2021 (back-reaction forces Type I in symmetric
  settings) [FT]; Kain 2023b [AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Semiclassical gravity.
- **(f) Open:** no 3+1 renormalized stress for any engineered front
  (LDS F.1.5).

#### 29.4 Stability of NEC-violating sources
- **(a) Literature:** Poisson–Visser 1995 (a₀ > 3M stable only for β₀² < 0)
  [der; FT]; Garcia–Lobo–Visser 2012 [der; FT]; Shinkai–Hayward 2002 [num;
  FT]; Gonzalez–Guzman–Sarbach 2009a,b (one unstable mode, growth time
  0.59–0.85 r_throat/c) [thm/num; FT]; Bronnikov–Fabris–Zhidenko 2011,
  Bronnikov–Konoplya–Zhidenko 2012, Cremona–Pirotta–Pizzocchero 2019 [AB];
  Azad et al. 2023, arXiv:2301.05243v2 [num; FT]; Khoo et al. 2024,
  arXiv:2401.02898v2 [num; AB]; Azad et al. 2025, arXiv:2509.22118v1 [der;
  AB]; Kanti–Kleihaus–Kunz 2012 [der; FT] and Cuyubamba–Konoplya–Zhidenko 2018
  (refutation) [FT]; Mironov–Rubakov–Volkova 2019, 2023 [FT]; Dubovsky et al.
  2006 [AB]; Le 2026c (radiating equilibrium linearly unstable; self-similar
  shells have growing modes) [AB]; Kain 2023a (Einstein–Dirac–Maxwell
  wormholes evolve to black holes) [num; FT]; Buchert–Frackowiak 2026 [AB];
  Fu–Grado-White–Marolf 2019 and Maldacena–Milekhin–Popov (fragile
  configurations) [FT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Stability and perturbations (4).
- **(f) Open:** rotation as stabilizer (LDS F.3.5; the Azad et al. PRD 109,
  124051 follow-up UV); stability of a lapse maximum is open (OS-§5).

#### 29.5 Fields on engineered backgrounds
- **(a) Literature:** Finazzi–Liberati–Barceló 2009 [FT];
  Coutant–Finazzi–Liberati–Parentani 2012 [AB]; Barceló et al. 2022 [FT];
  McMonigal–Lewis–O'Byrne 2012 (test particles) [FT]; Clark–Hiscock–Larson
  1999 [AB]; Barceló–Liberati–Visser (LEM A1) [FT].
- **(b) Identities:** OS-I12, OS-I13 — D*; OS-I14 — H.
- **(c) Practices:** —
- **(d) Measured examples:** OS-K19 tip field evolution: modes rise at most
  1.6× and leave, while a flat front grows at 2κ (D-fr, ✓).
- **(e) Quiz:** —
- **(f) Open:** 3+1 renormalized stress, emission rates, fields through
  acceleration and off-meridian rays remain open (OS-§5).

## Part VI. Method and frontier

### Chapter 30. Design studies

#### 30.1 Attribution and sensitivity maps (C1)
- **(a) Literature:** Saltelli et al. 2019 (LEM D6) [std; FT]; Saltelli et
  al. 2008 *Primer*, Sobol′ 2001, Saltelli–Annoni 2010, Lo Piano et al. 2021
  (LEM D6) [PT]; Morris 1991 (LEM D7) [std; FT]; Fisher 1935, Box–Hunter–Hunter
  2005, Czitrom 1999, Sacks et al. 1989 (LEM D8) [std; FT];
  Tajmar–Neunzig–Weikert 2022 (LEM S7) [emp; FT].
- **(b) Identities:** —
- **(c) Practices:** C1 (superseded for maps by global sensitivity; supported
  for attribution at a base point); attribute failures to term families
  before adding knobs (MJ I-15); ablation of inherited elements (SE L15;
  truism, one sentence).
- **(d) Measured examples:** OS-K15 ordering interaction (525 against 0 Type
  IV points), the non-additivity that one-at-a-time studies miss (βx probes;
  label); TE-G20 a comparison that changed lead and width together with no
  matched control (2E, cautionary).
- **(e) Quiz:** QB Design review and synthesis / Failure analysis (2),
  recast.
- **(f) Open:** —

#### 30.2 Matched comparisons
- **(a) Literature:** Sacks et al. 1989 (LEM D8: in deterministic codes
  discretization bias replaces noise, so matched controls must match
  resolution and domain) [std; FT]; Tajmar et al. 2022 (LEM S7) [emp; FT].
- **(b) Identities:** —
- **(c) Practices:** truism: matched controls; C1 (compare at matched
  effective strength).
- **(d) Measured examples:** TE-G21 matched-strength shell shapes (2E;
  illustrative only).
- **(e) Quiz:** —
- **(f) Open:** —

#### 30.3 Forks and set-based exploration (C2)
- **(a) Literature:** Sobek–Ward–Liker 1999 (LEM D9) [std; PT]; Toche et al.
  2020 (LEM D9) [std; FT]; Millis 2005 (LEM S6: portfolio diversity) [std;
  FT]; Zhang et al. 2011 and Li–Pendry 2008 (LEM T10, T7: each map family won
  in a different technology) [FT].
- **(b) Identities:** —
- **(c) Practices:** C2 (run every branch of a fork through the same checks
  and record it; supported). Evidence pointer: SE F15 (a provisional
  preference that needs evidence to change and none to keep).
- **(d) Measured examples:** OS-K19 front fork (current front, running shelf,
  static shelf, cone) recorded with outcomes (D-fr, ✓); OS-K12 stretch against
  lapse fork (D-amp → D-lap).
- **(e) Quiz:** —
- **(f) Open:** —

#### 30.4 Single-gate distortion (C4)
- **(a) Literature:** Suh (LEM D1) [PT]; Monticone–Alù 2013 (LEM T11,
  analogy) [FT]; topology-optimization practice (LEM T13) [mixed].
- **(b) Identities:** —
- **(c) Practices:** C4 (evidence-backed hazard); P01 §2i. Evidence pointers:
  SE L8, MJ I-06 (a cost-only objective selected a null component), MJ I-08.
- **(d) Measured examples:** OS-K9 (βh; cautionary); OS-K5 (✓; cautionary).
- **(e) Quiz:** —
- **(f) Open:** duplicates 12.4.

#### 30.5 Absolute and relative figures of merit (C5)
- **(a) Literature:** Lawson 1957 and Wurzel–Hsu 2022 (LEM S5: an absolute
  threshold) [PT/FT]; Millis 2005 (LEM S6: incumbent metrics mislead) [std;
  FT].
- **(b) Identities:** —
- **(c) Practices:** C5 (truism with a strong domain record). Evidence
  pointers: SE F7 (a relative merit steered about 90 commits), MJ I-09.
- **(d) Measured examples:** TE-G8 live fractions improved by moving
  denominators (2E, cautionary).
- **(e) Quiz:** —
- **(f) Open:** —

### Chapter 31. Credibility and claim scope

#### 31.1 Naming results by the check passed (D1)
- **(a) Literature:** Oreskes–Shrader-Frechette–Belitz 1994 (LEM V16) [std;
  AB]; NASA-STD-7009B (LEM V13: best estimate, uncertainty, credibility,
  caveats, risk) [std; FT].
- **(b) Identities:** —
- **(c) Practices:** D1 (refined; the claim ladder kept as one axis). Evidence
  pointers: MJ I-17 (label inflation, n = 4); 02 §3.6 ("admissibility" names
  a check that establishes algebraic compatibility with a source class).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Established foundations / Claim classification (2); QB
  Design review and synthesis / Claim classification (5), recast;
  Evidence sufficiency (6), recast.
- **(f) Open:** —

#### 31.2 Multi-axis credibility and readiness
- **(a) Literature:** PCMM, Oberkampf–Trucano–Pilch 2007 (LEM V14) [std;
  AB]; NASA-STD-7009B (LEM V13) [std; FT]; ASME V&V 40 (LEM V12) [std; AB];
  Mankins 1995 (LEM S1) [std; FT]; NASA SE Handbook (LEM S2: AD2) [std; FT];
  GAO-20-48G (LEM S3) [std; AB]; Millis 2005 (LEM S6: Applied Science
  Readiness Levels) [std; FT]; Le 2026a five-criterion standard [FT].
- **(b) Identities:** —
- **(c) Practices:** D1 (analytic work sits below TRL 1 on the readiness
  scale); LEM comparison table (claim ladder against V&V tiers, fusion gains
  and readiness scales).
- **(d) Measured examples:** —
- **(e) Quiz:** QB Design review and synthesis / Evidence sufficiency (6),
  recast.
- **(f) Open:** —

#### 31.3 Kinematic and sourcing claims
- **(a) Literature:** Barceló–Liberati–Visser, arXiv:gr-qc/0505065v4
  (LEM A1: laboratory Hawking experiments are purely kinematic) [rev; FT];
  Weinfurtner et al. 2011, arXiv:1008.1911; Steinhauer 2016,
  arXiv:1510.00621; Philbin et al. 2008, arXiv:0711.4796 (versions not
  recorded) (LEM A3) [emp; AB]; Leonhardt–Philbin 2006 (LEM T12:
  transformation optics uses kinematics only) [FT].
- **(b) Identities:** —
- **(c) Practices:** D1 (separate kinematic claims, which analogue
  experiments can test, from sourcing claims, which they cannot); the
  distinct scopes of spectral checks, algebraic targets, supplied stress,
  finite closure and coupled dynamics, stated in general form.
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** —

#### 31.4 Program hazards (D2–D5)
- **(a) Literature:** Cooper 1990 (LEM S4: gatekeepers, Go/Kill/Hold/Recycle)
  [std; FT]; Millis 2005 (LEM S6: publish regardless of outcome) [std; FT];
  Oberkampf–Trucano 2002 (LEM V9: verification cannot detect a wrong
  conceptual model) [std; FT]; NASA-STD-7009B (LEM V13: reviewer
  independence) [std; FT]; Löffler et al. 2012 (LEM N4) [FT].
- **(b) Identities:** —
- **(c) Practices:** D2 (frame review separate from process review;
  evidence-backed, one strong episode); D3 (stopping rules at two levels;
  heuristic, labelled); D4 (live ledger of negative verdicts and relaxations;
  governance); D5 (freezes stop tuning and carry no confidence; governance);
  truisms: supersession map; stage-gate ordering. Evidence pointers: MJ CE-1,
  CE-2, CE-4, CE-5; SE A8, A9, F4, F6, F8, F13, F14; SE L12, L13.
- **(d) Measured examples:** —
- **(e) Quiz:** QB Design review and synthesis / Project-state handling (5):
  excluded (project state).
- **(f) Open:** governance sidebar; small n for D2–D3.

### Chapter 32. The frontier

#### 32.1 Open sourcing classes
- **(a) Literature:** Mironov–Rubakov–Volkova 2023 and Franciolini et al.
  2019 (beyond Horndeski) [FT]; Gergely 2026 [AB+]; Rodal 2026 (birefringent
  screening) [AB]; Huey 2024 (membranes) [AB]; Fuchs et al. 2024 [FT];
  Einstein–Dirac–Maxwell papers [FT/AB]; Kanai–Maeda–Yoshida 2025 [AB].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.2, F.1.12, F.3.2, F.3.3.

#### 32.2 Dynamics and stability
- **(a) Literature:** Clough–Dietrich–Khan 2024 [FT]; Buchert–Frackowiak 2026
  [AB]; Le 2026c [AB]; Azad et al. 2023/2025, Khoo et al. 2024.
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.5, F.3.5; OS-§5 (coupled dynamics, back-reaction,
  stability of a lapse maximum); TE-§8.

#### 32.3 Quantum questions
- **(a) Literature:** Graham–Olum 2007 (self-consistent achronal ANEC) [FT];
  Wall 2010 (quantized gravitons; shear-inclusive ANEC) [FT];
  Freivogel–Krommydas 2018 (SNEC constant) [FT]; Bousso et al. 2016 (quantum
  focussing conjecture) [AB]; Fliss–Rolph 2025/26 [AB]; Fewster–Teo 2000 and
  Ford–Roman 1999 (quantum interest in 4D) [AB]; Kontou–Sanders 2020
  formulation (ii) [FT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** LDS F.2.5–F.2.8; a 3+1 renormalized stress at engineered
  fronts (LDS F.1.5).

#### 32.4 Global questions
- **(a) Literature:** Hawking 1992 and Kim–Thorne 1991 [AB]; Borde 1994
  [AB]; Barzegar–Buchert–Vigneron 2026 Thm IV.7 [FT]; Schuster–Santiago–Visser
  2023 against Barzegar–Buchert–Vigneron Thm IV.19 [FT];
  Shoshany–Snodgrass 2024 on Olum's definition [FT].
- **(b) Identities:** —
- **(c) Practices:** —
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** LDS F.1.3, F.1.6, F.1.11, F.2.1–F.2.3, F.3.8.

## Appendices

### A. Laboratory analogues and experiments
- **(a) Literature:** Barceló–Liberati–Visser, *Analogue Gravity*, Living
  Rev. 2005, 2011 and 2026 editions, arXiv:gr-qc/0505065v4 (LEM A1) [rev;
  FT; identity of v4 with the 2026 edition unchecked]; Unruh 1981, no arXiv
  (LEM A2) [PT]; Weinfurtner et al. 2011, Steinhauer 2016, Philbin et al.
  2008 (LEM A3) [emp; AB]; Leonhardt–Philbin 2006 (LEM T12) [FT].
- **(b) Identities:** acoustic metric: lapse set by the sound speed, shift by
  the flow; at most three degrees of freedom per point (LEM A1) — L.
- **(c) Practices:** D1 (kinematic claims only).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** no laboratory negative-energy or Casimir experiment is in any
  inventory; the "experiments" half of the appendix is unsupported.

### B. Computational companion
- **(a) Literature:** Helmerich et al. 2024 (Warp Factory) and its toolkit
  paper arXiv:2404.10855v1 [meth; FT/companion]; Le 2026b (warpax, JAX)
  [meth; FT]; Löffler et al. 2012 (Einstein Toolkit, LEM N4) [std; FT];
  Clough–Dietrich–Khan 2024 (GRChombo evolution) [FT]; LEM Area 1 synthesis
  (a manufactured-metric test suite with every coupling switched on).
- **(b) Identities:** the symbolic scripts behind OS-T3.2
  (`verify_identities.py`, `verify_compact.py`) as a template for
  metric-to-tensor checks.
- **(c) Practices:** B2, B6; truisms: commit discipline, supersession map,
  regression tests separate from verification (one sentence each).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** the project toolkit itself is outside the book; only general
  modules would enter.

### C. Units, scales and conversions
- **(a) Literature:** Buckingham 1914 [PT]; Pfenning–Ford 1997 and
  Morris–Thorne 1988 (worked magnitudes) [FT].
- **(b) Identities:** OS-I25 — D; 05 SI conversions; ℓ_P = (ħG/c³)^{1/2};
  TE-Q13 — D*; TE-S18 Schwinger-field scale — D*.
- **(c) Practices:** truism: dimensional analysis; A5 (absolute scale).
- **(d) Measured examples:** OS-K27 conversion table (L from 204 ℓ_P to
  1 km) (D-lap, ✓).
- **(e) Quiz:** QB Established foundations / Dimensional analysis (3).
- **(f) Open:** —

### D. Reference solutions and their stress tensors
- **(a) Literature:** Morris–Thorne 1988 [FT-OCR]; Ellis form (TE-I21);
  Alcubierre 1994 [FT]; Natário 2002 [FT]; Van Den Broeck 1999 [FT];
  Krasnikov 1998 and Everett–Roman 1997 [FT]; Visser 1989a (polyhedral
  thin-shell wormholes) [FT]; Simpson–Visser 2019 [FT];
  Bolívar–Abellán–Vasilev 2026 (hollow core family) [FT]; Rodal 2025
  (irrotational drive) [AB]; Fuchs et al. 2024 (disputed) [FT].
- **(b) Identities:** TE-I21 — D*; TE-I16 checks (flat space, cylinder,
  Ellis, de Sitter static patch) — D*; TE-I1 checks (Ellis, dust cosmology,
  Painlevé–Gullstrand Schwarzschild) — D*; TE-I4 string cloud — D*; OS-T3.2
  the complete tensor of class C0 — D; LDS-E.5 lapse-only tensor — D.
- **(c) Practices:** B2, B3 (analytic fixtures for degenerate tensors).
- **(d) Measured examples:** —
- **(e) Quiz:** —
- **(f) Open:** the project's 19 analytic classifier fixtures are unpublished;
  Lentz 2021 and Fuchs et al. 2024 enter only with their disputes.

### Quiz-bank summary (all tracks and modules)

| Track (n) | Module (n) | Placement |
|---|---|---|
| Established foundations (125) | Metric basics (8); Causal structure (7); Geodesics (2) | 2.1–2.5, 6.3 |
| | ADM split (7); ADM constraints (6); Einstein equation (7) | 3.1–3.4, 9.1, 29.1 |
| | Stress-energy basics (8); Source model basics (5) | 4.1–4.4, 10.6, 22.1 |
| | Energy conditions (10); Quantum inequalities (2) | 4.5, 5.2–5.5, 10.1 |
| | QFT basics (9); Quantum basics (11); Quantum vacuum (2) | QFT primer before Ch 5; 7.2; 24.2 |
| | Casimir effect (8); Boundary conditions (3) | 24.1 (boundary items also 10.3; check content) |
| | Semiclassical gravity (6) | 7.1–7.3, 24.4, 29.3 |
| | Effective field theory (8); Stability and perturbations (4) | 25.2–25.4, 29.4, 7.6 |
| | Dimensional analysis (3) | 9.4, 20.1, App C |
| | Modeling discipline (3); Claim classification (2) | 13.1, 31.1 |
| | String theory context (4) | excluded (no home in the structure) |
| Published warp and wormhole context (43) | Warp metrics (10); Metric basics (1) | 8.2, 16.2, 1.2 |
| | Warp geodesics (9) | 8.6, 19.1–19.3 |
| | Chronology concerns (10); Topological censorship (3) | 6.2, 6.5, 8.3, 11.1 |
| | Quantum inequalities (4) | 5.2, 20.3 |
| | Scalar-source literature (3) | 21.2, 25.1 |
| | Warp-wormhole correspondence (3) | 8.5 |
| Design review and synthesis (19) | Claim classification (5); Evidence sufficiency (6); Failure analysis (2); Paper-to-design transfer (1) | 31.1–31.2, 30.1, 28.1, after removing project content |
| | Project-state handling (5) | excluded (project state) |
| Active-rail architecture (13) | Architecture overview (2); Packet versus plant (1); Plant diagnostics (1); Service chronology (5); Source ledger (3); Symbol roles (1) | excluded (throat-era project architecture) |

The bank was built on 23–25 May 2026, before the September corrections and
the 02 §4 scope corrections. Every reused item needs a check against 02 §4
and against the taxonomy flags (`revision_sensitive`, `open_question`,
`project_material`, `project_state`).

---

# Part 2. Orphans and deliberate exclusions

## 2.1 Orphans: items with book value and no home in 05

| # | Item and evidence | Book value | Proposed placement |
|---|---|---|---|
| O1 | **A11, smoothness class of a prescription.** 02 §3.1 A11 (refined); TE-I13 (a d^p cusp gives stress ∝ d^{p−2}); TE-G28 (†) and TE-G16 (2E: transition width matters more than smoothness order, consistent with G being linear in second derivatives, ∝ 1/Δ²); SE A3, B4, D13, L9; LEM V6 (smooth manufactured solutions), T6 (a regularized inner boundary changes the result), T11 (adiabatic transitions), T13 (length scales), N7 (sharp transitions give spurious violations); Danielson et al. 2021 (a non-C³ metric is no solution). 05 names no section for A11. | A general rule with an identity behind it, and a verification requirement | New 9.5 "Smoothness class of a prescription (A11)", cross-referenced from 7.6 and 17.5 |
| O2 | **A9 is unlabelled.** Its content sits in 19.2–19.4. | Traceability of the practice | Label 19.2 "(A9)" |
| O3 | **Bondi mass and four-momentum; radiation balance.** Le 2026c; Barzegar–Buchert–Vigneron Thm IV.19; Clough–Dietrich–Khan 2024. Used by 19.6 and 27.4, introduced nowhere. | Steering and recoil need it | Extend 3.6 to "ADM, Komar and Bondi masses"; acquire a Bondi–Sachs primary source |
| O4 | **Curvature invariants and Petrov type as frame-free diagnostics.** Mattingly et al. 2021; Rodal 2023, 2024 (Petrov type I for Natário; reported plotting errors of 8–21 orders). | A second frame-free check beside the energy conditions | 10.1, with the plotting dispute as a verification example in 13.2 |
| O5 | **Non-linear energy conditions** (flux, trace-of-square, determinant). Martín-Moruno–Visser 2013, 2017. | Better semiclassical behaviour, weaker link to focusing | 4.5 (definitions), 5.1 (semiclassical behaviour) |
| O6 | **Quantifying exotic matter: volume integrals and their measure.** Visser–Kar–Dadhich 2003; Kar–Dadhich–Visser 2004; Nandi–Zhang–Kumar 2004; Fewster–Roman 2005; LDS F.3.1. | The "measure" column of the demand ledger | 9.2, with a pointer from 8.1 |
| O7 | **Rest-frame transitions by a spatially varying lapse.** Shoshany–Snodgrass 2024 (Eulerian worldlines are geodesic iff ∂_iN = 0). | Links the lapse to frame changes and to the CTC construction | 15.1, cited from 6.5 and 19.6 |
| O8 | **Coupling engineering.** Rodal 2025 (a prescribed κ(x) violates the Bianchi identity; a dynamical κ is a scalar–tensor theory excluded by PPN bounds). | A class-level exclusion | 22.2 |
| O9 | **Higher-curvature gravity sectors.** Lobo–Oliveira 2009; Kanti–Kleihaus–Kunz 2011, 2012; Cuyubamba–Konoplya–Zhidenko 2018; Liu et al. 2023; Gurses–Sisman–Tekin 2020; Eiroa–Rubín de Celis–Simeone 2025; the null-convergence statement of Santiago–Schuster–Visser 2022. Chapter 25 covers matter fields only. | "Moving the violation into the gravitational sector" is a strategy with its own record | New 25.6 "Curvature sectors of modified gravity" (21.2 points to it) |
| O10 | **Quantum-sourced wormholes and the long–short dichotomy.** Gao–Jafferis–Wall 2017; Fu–Grado-White–Marolf 2019a,b; Maldacena–Milekhin–Popov; Maldacena–Milekhin 2021; Kanai–Maeda–Yoshida 2025; Kontou 2024. Now spread over 6.2, 8.1 and 24.5. | The only quantum-sourced constructions with derivations | One home in 24.5, or a new 24.6 |
| O11 | **Einstein–Dirac–Maxwell wormhole dispute** (seven papers). Held in 8.1 for now. | A case study in claimed solutions (smoothness, dynamics) | 8.1 for the geometry; its lessons in O1 (9.5) and 29.4 |
| O12 | **Information-destroying reductions hide diagnostics.** MJ P01+ (a minimum over branches); TE-§0.4 (the radial-null count takes either branch, so it never separates Type I NEC violation from Type IV). | A ledger-design rule | 9.2 |
| O13 | **Symmetry-guaranteed gates carry no evidential weight.** TE-§8.4; TE-M3 (J_⊥ = 0 is forced by spherical symmetry); ADM re-projection at 10⁻¹⁷. | Guards against counting trivially passed checks | 13.3 |
| O14 | **Proxy promotions and one-sided metrics.** TE-§8.4 (one-sided transfer metrics disagree in sign with raw changes; promotion on proxies; fits with normalized L1 > 1 called passes). | Claim-hygiene examples | 31.1 (with 30.5) |
| O15 | **Minor engineering items.** LEM V11 (ASME V&V 10, terminology; PT); LEM T15 (Chen–Chan–Sheng review; PT, used for no verdict). | Background | 31.2 and 28.1 respectively |

**Evidence pointers without a named packet entry** (all map to practices
already placed): MJ I-05 (relax a failed criterion only by a dated
decision → D5, 31.4); MJ I-07 (sign boundaries move under refinement → 13.2);
MJ I-10 (energy-condition verdicts on the complete tensor → 10.1); MJ I-11
(out-of-sample tests for fitted closures → 9.1, 13.2); MJ I-16 (nested
parameterizations reproduce the reference → 13.1); MJ CE-6 (non-claim
language does not test the frame → D2, 31.4); MJ CE-8 (sample size is no
evidence against a structurally different failure → 5.4, 13.2); SE B10
(state what a surrogate can represent → B5, 13.3); SE B11 (compute the
dimensionless threshold first → 22.3, 24.1); SE B15 (resolution-sensitive
classification → 13.2); SE C7 (keep the tightest cheap bound → 22.4);
SE C11, C12 (budgets over intervals → B1, 10.4); SE D5 (failed necessary
conditions persist → D4, 31.4); SE D11 (dense residual tracking after each
fix → A7, 9.1); SE E12 (a fix tuned at one speed failed at higher speed →
19.4 with OS-K20); SE F2 (precision on the wrong premises → D2, 31.4); SE F5
(scope qualifications ignored downstream → 31.1); SE F9 (reproduction carried
errors forward → 13.1); SE F11 (a single gate as design driver → C4, 30.4).

**Parts of the knob maps and their disposition.** OS-P1–P8, P11–P21, P23,
P24 enter through the knobs and identities cited in Part 1. OS-P9 (standing
support), OS-P10 (carve) and OS-P25 (decompression) are heritage elements;
their lessons enter through OS-K10, OS-K24 and TE-G5. OS-P22 (track cutoff)
enters through OS-K7. TE §1.1 geometry parts enter through TE-G1–G31 and
TE-I1–I28 as cited; TE §1.2 source-architecture parts enter only through the
source laws TE-Q1–Q13.

## 2.2 Items deliberately excluded

**Project-specific (architecture, vocabulary, process).**
- The C1 build architecture as a rule (02 §3.6; TE-S1–S2 architecture):
  the choice is the project's; only the function–realization distinction
  survives (27.3).
- "Preserve specialized components" (02 §3.6): in the record it made
  exclusions non-cumulative (SE F13).
- "Admissibility" as a name and "Type I required" (02 §3.6; P01 §2g).
- Throat-era project constructs as design facts: beta075, the service factor
  V, carve, receiver, collar, support-shell overlay, release fade, entry
  gate, S0 scaffold, packet tube (TE §1.1; magnitudes of TE-G2–G27).
- TE-G4, G7, G9–G12, G15, G18, G19 magnitudes (2E: two-ended, type untested,
  packet readings under TE-L2). Their general content is placed through
  TE-I6 (G7), TE-I8 (G9) and the locality of G_μν (G11, G25).
- TE-I7 re-match algebra: a design-specific collar with trivial algebra.
- TE-Q4 and TE-S10: a project-specific 1+1 supply bound with a Gaussian
  weight.
- TE-M3, M4, M6 (source-model choices on †); only TE-I24 and TE-I25 survive
  as placed. The convex-kernel bound and positive upwind transport of TE-M4
  are correct linear-positivity statements with no book use.
- TE-DR1 oracle role partition (accounting; "live residual 0" by
  construction); its lesson is A7 and MJ CE-3.
- TE-S5, S7, S12 magnitudes (§).
- OS-K23 extended carry: a two-ended track whose arrival readings of that era
  are proxies.
- Governance: commit discipline beyond one sentence (SE D2); disclosure and
  running-log rules (SE A9, B13, F6); locking the design record (SE L21,
  E16); worker-count and array-commit rules (SE F12); append-only reports
  (SE F10); the user corrections of SE Part G; the report-writing rules of
  the repository; every item of `04_PROJECT_FINDINGS.md` (claim wording,
  citation pins, solver settings, uncommitted work).
- Quiz tracks Active-rail architecture (13) and Project-state handling (5);
  module String theory context (4), which has no home in the structure.

**Invalidated.**
- TE-M1–M8 as source realizations (†; TE-L1, TE-L5; TE-§7.1).
- Every packet-norm verdict and cliff of the throat era (TE-L2; the
  w_th 0.569/0.570 and V ≈ 10.01 cliffs are single mask-edge nodes).
- Service-time ratios 2.569/1.233 and their extrapolations (TE-L3).
- "Relax throat" readings and end-transition deficits read as rail costs
  (TE-L4).
- Legacy classifier labels and May rest-frame energy-condition columns
  (TE-L5).
- Storage, capacitor and magnetic-containment thresholds (TE-S14–S17, †);
  C1, cavity and longitudinal-gate magnitudes (TE-S1–S13, §).
- The 3+1 "backreaction" proxy (TE-M8).
- "No evidence of a new curvature blow-up caused by the receiver"
  (contradicted by the September refinement; TE-§7.1).
- Throat-era radius scaling as a law (no similarity sweep; TE-§8.2).
- D-ax0 numbers except as cautionary examples (βx).
- TE-DR2 harness verdicts read as physical SNEC tests (normalization
  unverified).
- The unqualified project statements "no semiclassical quantum sector
  supplies the demand at any size" and "quantum fields supply the rail below
  0.45 mm"; 24.5 carries the qualified form (LDS C.7).
- The energy formula written with a stretch factor (OS-§3.3.2; valid only for
  A = 1).

**Truisms (one sentence each, with their placement).** Stage-gate ordering
(1.3, 22.4); dimensional analysis (9.4, App C); interface contracts (27.2);
matched controls (30.2); commit discipline (App B); a supersession map
(31.4, App B); regression is not verification (13.1); measures of
effectiveness (1.5, 11.3); clock coordination without signals (11.4, with
proper time as the domain content). Demoted September items: a repair must
overlap its defect (SE A4; 9.1); test edge cases (SE L10; 10.5); ablation
(SE L15, E2; 30.1); envelope testing (SE E12; 19.4); settle mechanism and
topology before subsystem optimization (SE L24, D6, E18; 1.3, with the
non-additivity of placement in GR as its content). Excluded outright:
search the archive (SE B12); march along the characteristic direction
(SE C14); check perturbative control at extremes (SE D15); check the
receiving matter's kinematics first (SE C3, a heuristic from one incident).

## 2.3 Unverified items (no weight until verified)

- LDS G.1: Abellán–Bolívar–Vasilev EPJC 83, 7 and CQG 41, 105011 (arXiv
  identifiers unidentified); Bolívar et al. Ann. Phys. 481 (search summary
  only); Chowdhury's journal volume; White et al. full text; the Garattini–
  Zatrimaylov title version; Lentz energy estimates; Harold White's earlier
  reports (not surveyed).
- LDS G.2: Fewster–Roman erratum content; Krasnikov 1998 construction time,
  Borde 1987, Galloway's splitting theorem, Tipler 1976/77, Flanagan–Wald
  1996, Wald–Yurtsever 1991 and Visser 1995 read only through citing papers;
  Pfenning–Ford 1998 eq. (48) coefficient; the Freivogel–Kontou–Krommydas
  "B ≪ 1" relation.
- LDS G.3: Hawking 1992 and Kim–Thorne 1991 beyond abstracts; OCR-limited
  prefactors in Morris–Thorne and Morris–Thorne–Yurtsever; Maldacena–
  Milekhin–Popov eq. (5.40); Garattini eq. (26); the Azad et al. PRD 109,
  124051 follow-up; 2019–2026 f(R,T), f(Q), f(R,L_m) wormhole papers (titles
  only).
- LF: metadata-only books and papers (Hawking–Ellis, Birrell–Davies,
  Parker–Toms, Wald 1994, Visser 1995, the 3+1 textbooks, Candelas, Fulling,
  Davies, Roman 1986, Tipler 1977, Smarr–York, Fourès-Bruhat,
  Choquet-Bruhat–Geroch); Geroch 1967 primary abstract; the Unruh
  temperature's primary wording; journal details of Banerjee et al.,
  Mironov–Volkova, Gergely, Penrose–Sorkin–Woolgar, Visser 2002; Deser–Duff–Isham
  1976 (not located); the wrong-ID records arXiv:0911.3380 and gr-qc/9903038.
- LEM: "Chen, Liang & Alù" (no such paper found); Post & Votta; the ASME V&V
  10-2006 history; Olewnik–Lewis 2005; Suh 1998; Ward et al. 1995;
  de Neufville–Scholtes 2011; NPR 7123.1; Hord 1985; Tajmar et al. 2019;
  Leonhardt–Philbin 2009; Kildishev et al. 2008; Jensen–Sigmund 2011;
  Cassier–Milton 2017; Gundlach et al. 2005; the NIF wall-plug energy.
- TE-S14 material strength data (graphene, carbon nanolattices): taken from
  a project report whose sources are outside every inventory.
- arXiv identifiers recorded without a version (pin before citing): LEM N2
  gr-qc/0305023, N3 0709.3559, N4 1111.3344, N5 0901.2437, N6 1307.5307,
  T2 physics/0602092, T6 0706.0655, T7 0806.4396, T9 1004.2551, T10
  1012.2238, T11 1003.5934, 1307.3996, 1306.5835, T12 cond-mat/0607418, T14
  1801.06715, S5 2105.10954, A3 1008.1911, 1510.00621, 0711.4796.

---

# Part 3. Balance

## 3.1 Thin chapters and sections

Counts are literature anchors placed in the packets (full-text or abstract);
engineering standards count for the method chapters.

| Chapter or section | Anchors | Problem | Remedy |
|---|---:|---|---|
| **23** Ordinary matter | ≈5, none in 23.1–23.2 | Every identity comes from † or § source work; every number is unsuitable | Acquire Israel junctions, string-cloud and Maxwell-stress sources and primary material data, or fold 23 into 26 |
| **26** Net supply | ≈5 | A6's "Casimir mirror cost" has no paper in the inventories; 26.1 rests on an identity plus incidents | Acquire QFT models of Casimir plates and their energy; otherwise merge 26 with 27 |
| **27** Assemblies | ≈8 | 27.1–27.3 rest on engineering sources and the project's architecture; 27.4 is abstract-level only | Merge with 26; acquire Bondi–Sachs and photon-rocket sources |
| **18** Coupling the elements | 5 physics anchors, all cited again in 8.4 and 16 | Built on class C0 identities; 18.3 has no literature | Lead with Santiago–Schuster–Visser and Shoshany–Snodgrass tensors; keep project identities as D statements |
| 15.5 Time staging | 0 | One identity plus one design lineage | Keep as a D statement with an M box |
| 24.2 and App A | 0 laboratory sources | 05's change 4 lists "laboratory negative-energy modalities"; no inventory holds any | Acquire (squeezed states, Casimir measurements) or drop the claim from 05 |
| 2.1, 2.4, Ch 3, 4.4 | textbooks metadata-only | MTW, Wald 1984, the 3+1 texts and Hawking–Ellis were never read | Read the standard texts for the definitions the book relies on |
| 17.5, 23.4 | no junction primary | Israel's formalism is used without an anchor | Acquire |
| 10.5, 13.4 | 1–2 | Degenerate tensors and solver statuses have no domain literature | Brief sections, as 02 already rates them |
| 8.5 | 3, abstract-level | Garattini–Zatrimaylov only | Keep short |

## 3.2 Overloaded chapters

| Chapter | Anchors | Load | Remedy |
|---|---:|---|---|
| **8** Canonical geometries | ≈85 (8.1 alone ≈35) | Wormhole foundations, quantity measures, stability, quantum-sourced wormholes, the Einstein–Dirac–Maxwell dispute and the whole warp literature | Split into warp/shortcut and wormhole/shell chapters, or move stability to 29.4, modified gravity to 25.6 (O9) and quantum-sourced wormholes to 24.5/24.6 (O10) |
| **5** Energy bounds | ≈60 (5.2 ≈20, 5.5 ≈25) | QEIs, quantum interest, null bounds, SNEC family, QNEC, ANEC in flat and curved space | Keep, with 5.6 as the scope table; move the prerequisites of Part 4 ahead |
| **25** NEC-violating fields | ≈45 (25.3 ≈30) | Cosmological no-go results and wormhole instabilities together | Move wormhole instabilities to 29.4 |
| **7** and **24** | ≈35 each | 7.1/24.4 and 7.4/24.3 duplicate | Physics in 7, source use in 24 |
| **6** Global structure | ≈40 (6.5 ≈15) | Chronology literature is large | Acceptable |
| 29.4 | ≈20 | Thin-shell, ghost-scalar, rotation and beyond-Horndeski stability | Acceptable once 25.3 hands over |

## 3.3 Duplicated coverage

1.5 ↔ 11.3 (A4); 7.1 ↔ 24.4; 7.4 ↔ 24.3; 7.5 ↔ 19.5 ↔ 29.3; 8.6 ↔ 19.2–19.3;
9.3 ↔ 14.5 (zoning); 9.4 ↔ 22.3 ↔ App C (scale); 12.4 ↔ 30.4 (C4);
14.3 ↔ 18.4 (adjustment order); 16.5–16.6 ↔ 20.2 (speed); 19.6 ↔ 27.4
(momentum by radiation); 13.5 ↔ App D; 5.6 ↔ 22.2 ↔ 24.5 (scope of
exclusions).

## 3.4 Where project-derived material dominates

The book must not be organized around the project. These sections draw most
of their evidence from the project's identities or measurements:

- **12.2 Flat compartments, 12.3 Choosing the occupant clock, 12.4 Occupants
  under single-gate optimization.** Literature exists for flat interiors
  (Alcubierre, Van Den Broeck, White et al., Bolívar et al.) and for interior
  clocks (Bobrick–Martire, Maldacena–Milekhin); it should lead.
- **15.5 Time staging, 15.6 Measured examples, 16.5 Speed as a lapse
  contrast, 17.2 Stretch and conformal factors.** Project identities (OS-I2,
  OS-I9, OS-I10, OS-I11) with one literature anchor (Van Den Broeck) or none.
- **Chapter 18 in full** (OS-T3.2, OS-I4, OS-I8, the OS coupling matrix).
- **19.4 Front design: shelves, cones, the flank criterion.** Shelves and
  cones are project elements; Natário, Low and Barceló et al. give the
  general criterion.
- **21.1 The catalogue.** 7 of the 11 rows of 02 §2.4 are project strategies;
  02 §2.2 and LDS E.1 hold at least 12 literature strategies.
- **14.1 and 18.5 (worked matrices).** The only complete matrices are the
  project's; LDS E.1–E.3 give literature matrices.
- **22.4 A screening sequence** (from the project's workflow), **26** and
  **27** (source-architecture work).
- **Section titles naming project constructs:** 12.2 "Flat compartments",
  15.5 "Time staging", 16.5 "Speed as a lapse contrast", 18.3 "Product
  regions" (the service region), 19.4 "shelves, cones".

The element-by-element plan of Part III itself is general: the split into
lapse, shift and spatial geometry is the ADM split, and the literature
attributes responses the same way (Morris–Thorne shape and redshift functions;
Santiago–Schuster–Visser and Shoshany–Snodgrass for shift energy; Van Den
Broeck for ³R). The risk lies in the section-level content listed above.

---

# Part 4. Dependency check

## 4.1 Prerequisites and forward references by chapter

| Ch | Prerequisites | Concepts used before their introduction (flags) |
|---|---|---|
| 1 | — (roadmap) | 1.2 uses lapse, shift and stress-energy (Ch 3–4); acceptable as a tour with pointers. 1.5 duplicates 11.3 |
| 2 | first-course GR | **2.6 uses the lapse (3.1).** Write the static metric as −V²dt² + h and identify V with the lapse in 3.1, or move 2.6 after 3.1 |
| 3 | 2 | 3.3 uses ρ and j, formalized in 4.1 (minor). 3.6 lacks the Bondi quantities that 19.6 and 27.4 need |
| 4 | 3 | — |
| 5 | 2, 4, QFT | **5.1–5.5 use Hadamard states and renormalized ⟨T⟩ (7.1–7.2), the trace anomaly (7.1: Visser's scale-anomaly counterexample in 5.5) and field counts (7.4: SNEC's G_N ∼ 1/N; the √N relaxation of QIs)** |
| 6 | 2, 5 | **6.1–6.2 use causality conditions and global hyperbolicity that 6.3 defines; 6.5 uses Hadamard singularities (Kay–Radzikowski–Wald) and renormalized-stress divergence (Kim–Thorne) from Ch 7** |
| 7 | 2, 5 | **7.5 uses superluminal warp fronts and their white horizons (8.2, 8.6, 19.2)** |
| 8 | 3–7 | 8.1 uses flare-out and throat tension (17.4); **8.4 resolves the debate with the integral identity of 16.2, all-observer testing (10.1) and transitions to vacuum (10.3)**; 8.6 anticipates 19.2–19.3 |
| 9 | 3, 4 | 9.3 uses the design-matrix vocabulary of 14.1–14.3 |
| 10 | 4, 5 | 10.4 uses interval certification (placed with verification in 13); 10.6 uses the algebraic ranges of 22.1 and 25.5 (by design) |
| 11 | 6 | 11.3 duplicates 1.5 |
| 12 | 2.4, 7.3 | **12.1 uses light surfaces with N = √(α² − b²) (19.2) and swept matter (19.3); 12.2–12.3 use lapse and shift design (15–16) and speed as a lapse contrast (16.5); 12.4 uses C4 (30.4)** |
| 13 | 9, 10 | — |
| 14 | 13 | 14.5 duplicates 9.3 |
| 15 | 3, 14 | **15.4 uses the static spherical decomposition of 17.3 (TE-I16)**; 15.5 motivates staging by shift transitions (16) |
| 16 | 15 | **16.5 is exact only in the stationary pattern frame (19.1)** |
| 17 | 4 (string clouds), 6.1 | 17.5 introduces junction conditions with no primary anchor |
| 18 | 15–17 | 18.4 duplicates 14.3 |
| 19 | 2.3–2.4, 7, 15–16 | 19.5 duplicates 7.5; **19.6 needs Bondi momentum (introduced nowhere)** |
| 20 | 5.2, 16 | 20.2 duplicates 16.5–16.6 |
| 21 | 15–20 | 21.2 points ahead to 25 (by design) |
| 22 | 5, 7 | **22.2 applies exclusions whose physics sits in 23.5 (E/Mc²), 24.1 (mirror energy) and 25.3 (Horndeski no-go results); 22.4 screens families not yet described** |
| 23 | 4, 17.5 | — |
| 24 | 5, 7 | duplicates 7.1 and 7.4 |
| 25 | 4, 5 | — |
| 26 | 4.5, 23–25 | — |
| 27 | 26 | **27.4 needs Bondi momentum** |
| 28 | 13, 22–27 | — |
| 29 | 3, 7, 25 | — |
| 30 | 13, 14 | C4 was already used in 12.4 |
| 31 | 13 | — |
| 32 | all | — |
| A | 2.6, 7.3 | — |
| B | 13 | — |
| C | — | — |
| D | 3, 4 | — |

## 4.2 Proposed structure changes

1. **Quantum-field groundwork before the bounds.** Move 7.1 (renormalized
   stress and the anomaly), 7.2 (states) and 7.4 (the species bound) ahead of
   Chapter 5, as a new chapter or by swapping Chapters 5 and 7 and keeping
   7.3, 7.5 and 7.6 after the bounds.
2. **Chapter 6 order.** Put 6.3 (causality conditions and time functions)
   first.
3. **Fronts in one place.** Move 7.5 into 19.5; keep 29.3 for back-reaction
   and a pointer in Chapter 7.
4. **Merge duplicates:** 1.5 into 11.3 (keep a one-paragraph preview); 9.3
   into 14.5; 18.4 into 14.3; 12.4 into 30.4; 16.6 into 20.2; 27.4 into 19.6;
   24.3 into 7.4 and 24.4 into 7.1, each with a source-use paragraph in 24;
   one treatment of scale for 9.4, 22.3 and Appendix C.
5. **Add** Bondi quantities to 3.6 (O3), a section 9.5 on the smoothness
   class of a prescription (O1), a section 25.6 on curvature sectors (O9),
   and the label A9 on 19.2 (O2).
6. **Spherical lapse after spherical geometry.** Move 15.4 into Chapter 17
   after 17.3, or place Chapter 17 before Chapter 15.
7. **Speed after the pattern frame.** Move 16.5 after 19.1, or introduce the
   pattern frame in 16.1.
8. **Relieve Chapter 8.** Split it into warp/shortcut and wormhole/shell
   chapters, or move wormhole stability to 29.4, modified-gravity wormholes to
   25.6 and quantum-sourced wormholes to 24.5 or 24.6. Present 8.4's
   resolution after 10.1, 10.3 and 16.2, or state it there with forward
   references.
9. **Occupant chapter placement.** Keep 12.1 in Part II; move 12.2–12.3 into
   Part III after Chapter 16, where their lapse and shift are developed.
10. **Retitle project-named sections:** 12.2 → "Flat interior regions";
    15.5 → "Scheduling lapse elements in time"; 16.5 → "Speed and the lapse:
    the steady-lane rescaling"; 18.3 → "Translation-invariant service regions
    (product metrics)"; 19.4 → "Front shape and normal speed".
11. **Rebuild 21.1** on the literature strategies of 02 §2.2 and LDS E.1, with
    the project strategies as labelled rows.
12. **Thin Part IV chapters.** Merge 26 and 27 ("Net supply and assemblies")
    unless the missing literature is acquired; fold 23 into it if its anchors
    stay absent.
13. **Screening after the families.** Keep 22.1–22.3 as framing; move 22.4 to
    the end of Part IV.
14. **Appendix A and 05's change 4.** Restrict Appendix A to analogue
    kinematics, or acquire laboratory negative-energy sources; correct the
    evidence claim in 05's change 4.
15. **Exercises.** 05 has no exercise appendix; the quiz mapping in Part 1
    gives per-section sources: 164 foundations and literature items (the
    String theory module excluded) plus 14 review items that can be recast,
    each to be checked against 02 §4.
