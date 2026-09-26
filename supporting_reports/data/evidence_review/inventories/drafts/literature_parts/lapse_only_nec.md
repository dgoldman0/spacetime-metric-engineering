### E.5 Derived here: the energy-condition cost of a lapse-only region on flat slices

Status: **derivation** made during this survey, with the Einstein tensor checked symbolically (sympy, metric −α(x)²dt² + δ_ij dx^i dx^j). No paper read for this inventory states it in this form; the closest published statements are Bobrick & Martire 2021 §3.1 (a positive-energy spherical shell can only slow interior clocks), Barzegar, Buchert & Vigneron 2026 Thm IV.20 (DEC forces an asymptotically flat R-Warp model to be Minkowski) and the static Type I theorem of Martín-Moruno & Visser 2021.

**Setting.** Flat spatial slices, a time-independent lapse α(x) → 1 at infinity, and zero shift (a spatially uniform, time-independent shift gives the same K_ij = 0 and the same result).

**Tensor.** G_00 = 0, so the Eulerian energy density vanishes identically; the Eulerian momentum vanishes (K_ij = 0), so the tensor is Hawking–Ellis Type I; the stresses are

  8π α S_ij = δ_ij ∇²α − ∂_i∂_j α,  with trace S = ∇²α / (4π α).

This is the precise content of project result (b): the lapse carries stress and no energy.

**Lemma.** Every non-constant such lapse violates the NEC somewhere.

- *Case 1: a 1/r tail, α = 1 − M/r + …, M ≠ 0.* Outside the source ∇²α = 0 and S_ij = −∂_i∂_jα/(8πα). The Hessian of −M/r has eigenvalues −2M/r³ (radial) and +M/r³ (twice, tangential). For M > 0 the tangential principal stress is −M/(8παr³) < 0 while ρ = 0, so ρ + p_⊥ < 0; for M < 0 the radial stress is negative.
- *Case 2: faster fall-off (M = 0).* ∫ α S d³x = (1/4π)∮ ∇α·dA → 0, so S = ∇²α/(4πα) changes sign unless ∇²α ≡ 0; a bounded harmonic α with α → 1 and no 1/r term is constant. Where S < 0 at least one principal stress is negative with ρ = 0, which violates the NEC.

**Reading.** The flux (1/4π)∮∇α·dA is the Komar mass of the lapse region, so Case 1 and Case 2 are the "positive Komar mass" and "zero Komar mass" branches. A lapse-only region on flat slices is therefore always Type I and always NEC-violating somewhere. Curved slices remove the obstruction: the Bolívar, Abellán & Vasilev 2026 lapse family and the Morris–Thorne redshift function both carry energy through the spatial curvature (mass function) while the lapse supplies the stress balance.

**Consequences for the project identities.**
- (b) holds as stated and gains a qualifier: the lapse's stress carries a mandatory NEC deficit somewhere whenever the slices are flat.
- (d) Speed as a lapse contrast places the whole contrast in regions where the lapse returns to one. On flat slices those regions are Type I, as the project states, and by the lemma each of them violates the NEC somewhere. This is the flat-slice counterpart of Bobrick & Martire's result that a faster interior clock needs negative energy.
