# Material-confined fermions: occupied-state evaluation

Date: 9 September 2026.

The evaluated scalar mass well supports a resolved bound spectrum, but every
occupied multiplet opposes the rail's integrated opening requirement. Across
three Yukawa couplings, the final catalogs contain 74, 302 and 1,222 multiplets.
Their best independently selected occupation supplies zero opening, while the
confining scalar adds an opposing contribution. This closes the proposed repair
through stationary particle occupation in this model. The absolute fermion
vacuum and the coupled material equilibrium remain separate calculations.

## Registered component question

This evaluation asks whether occupied, physically normalized fermion states
can supply a useful radial-null contribution on the retained repaired rail.
The scalar material supplies confinement; the standing backbone, angular
response and transport retain their separate roles. The absolute fermion
vacuum is an additional source with its own renormalization and force. The
occupied-state calculation measures the finite change from that vacuum.

The static geometry is the phase-0.745 native reference in the
[archived comparison](ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md), with its
unit-lapse tails. The gravitational conversion remains
`eta = 2.4127904527582454e-5`. A new real, neutral scalar confines a neutral
Dirac field through `m = y chi`. This defines a conventional Yukawa interaction.
The existing condensate's vacuum amplitude `v = 12/6.8` supplies the comparison
scale; the neutral scalar has its own counted tensor.

## Action, material and state

With canonical kinetic terms, the scalar potential is

\[
U(\chi)=\frac{\lambda}{4}\chi^2(\chi-v)^2,
\qquad \lambda=\frac{8}{v^2d^2}.
\]

Two smooth interfaces enclose the rail at areal radius 6.8 on its two sides.
In proper distance, their starting profile is

\[
\chi(l)=v\left[1+\frac12\tanh\frac{l-l_+}{d}
                  -\frac12\tanh\frac{l-l_-}{d}\right].
\]

The initial width is `d = 1`; the Yukawa couplings are `y = 1, 2, 4`, with
one Dirac species per calculation. Each isolated flat interface satisfies
its scalar equation. Curved equilibrium includes the geometrical force and
the fermion scalar density. The starting profile's scalar equation residual
is retained in the evidence. Its tensor is

\[
T_\chi=\eta\left(\tfrac12\chi'^2+U,
                 \tfrac12\chi'^2-U,-\tfrac12\chi'^2-U\right),
\qquad H_\chi=\eta\chi'^2.
\]

The initial state catalog includes every resolved positive-frequency bound
mode below `0.9 y v`, with both spherical parities. The final extension takes
the ceiling to the continuum threshold `y v` and retains the resolved roots
below it. A fully occupied angular
multiplet has `2 |K|` particles, where `|K| = j+1/2`. Individual occupations
obey Pauli statistics. Optimizing the opening contribution also allows
independent fractional multiplet occupations between zero and one, a larger
class than equilibrium Fermi filling.

## Radial spectrum and supplied stress

For optical distance `dz = dl/A`, write `M = A m`, `W = K A/R` and
`Q = -d/dz + W`. The radial Hamiltonian and normalization are

\[
H_D=\begin{pmatrix}M&Q^\dagger\\Q&-M\end{pmatrix},
\qquad \int(F^2+G^2)\,dz=1.
\]

Positive frequencies reduce to

\[
\left[Q^\dagger(\omega+M)^{-1}Q+M\right]F=\omega F.
\]

The left-hand eigenvalues decrease with frequency. Their crossings enumerate
the positive spectrum below the specified ceiling. A staggered discretization
gives a symmetric tridiagonal Schur operator. The spherical mode and stress
conventions follow [Kain's equations (19)–(28) and (58)](https://arxiv.org/html/2308.00049v2);
positive-frequency and bound-state restrictions are informed by
[Weinbaum's analysis](https://arxiv.org/html/2607.28738v1).

For `S = F^2+G^2`, `D = F^2-G^2`, `P = 2FG` and
`C = eta 2|K|/(4 pi A^2 R^2)`, the occupied multiplet supplies

\[
\rho_F=C\omega S,\qquad
p_{r,F}=C(\omega S-AmD-WP),\qquad
p_{t,F}=\tfrac12 CWP.
\]

The Yukawa mass appears once in this tensor. Its exchange with the scalar
obeys

\[
p_{r,F}'+\frac{A'}A(\rho_F+p_{r,F})+
2\frac{R'}R(p_{r,F}-p_{t,F})=-m'\eta\langle\bar\psi\psi\rangle_{\rm occ}.
\]

In particular, the occupied density is nonnegative. Regions of demanded
negative density continue to require an absolute vacuum contribution or
another specified signed source.

## Necessary gates and numerical controls

The component's integrated opening contribution is

\[
B_F=-4\pi\int R(\rho_F+p_{r,F})\,dz,
\qquad B_{\rm required}=\left[\frac{R'}A\right]_-^+.
\]

The best arbitrary occupation sums the positive `B_F` values. Every negative
mode contribution opposes opening. A separate optimistic envelope keeps only
negative local radial-null stress, even within a mode. Both are compared with
the scalar's opposing contribution and the geometric requirement.

At the frequency ceiling, put `a = 1/(omega+M)` and `w = A/R`. Expansion of
the Schur quadratic form gives a potential
`M-omega+K^2 a w^2+K (a w)'`, with primes here denoting optical distance.
Its pointwise lower bound for both parities provides an angular truncation
condition. The calculation samples its sufficient envelope, adds a margin,
and includes both parity sectors through that margin. Finer meshes check
the envelope and the spectrum. This supplies a numerical angular audit.

Four independent sector workers are allowed, with a 900-second initial run
and 20 MB retained-output allowance. The initial optical spacing is `1/128`
and the native-coordinate ends are at `+-64`. Resolution, outer boundaries
and occupation ceiling receive targeted follow-ups when they affect the
conclusion. Positive source evidence requires resolved energy normalization,
small boundary amplitude, stress-force conservation and numerical convergence.
A useful occupied contribution would precede material relaxation and an
absolute fermion-vacuum calculation. An adverse occupied contribution ends
this proposed repair through particle occupation.

The four initial tests check exact product-space energies, the mass
Hellmann–Feynman relation, stress conservation and trace, scalar-wall energy
and equilibrium, and parity pairing in a symmetric mass well.

## Supplied opening and occupation result

The final calculation uses optical spacing `1/256` and ends at native
coordinate `+-96`. Each table row is a separate one-species model. A positive
opening contribution would help the demanded balance.

| Yukawa coupling | Resolved angular/radial multiplets | Multiplets helping opening | Opening with every multiplet filled | Best arbitrary occupation |
| --- | ---: | ---: | ---: | ---: |
| 1 | 74 | 0 | −0.004496899 | 0 |
| 2 | 302 | 0 | −0.069770540 | 0 |
| 4 | 1,222 | 0 | −1.101717275 | 0 |

The geometry requires `B = 1.999667780` on that interval. The scalar supplies
`B_chi = −0.004281489`, common to all three couplings. Consequently the
opening-maximizing choice empties every evaluated particle mode and still
leaves the scalar's additional load. Multiplying these occupied spectra by
positive species counts increases the opposing contribution. Optimistically
keeping only the helpful local pieces inside every mode yields at most
`1.93e-15` in the strongest coupling, a negligible tail contribution.

The occupied density is positive and the computed radial-null stress is
overwhelmingly positive. Coarse saved probes place the probability peaks in
outer regions of the retained geometry, with some probability extending into
the central region. Thus the scalar well resolves the availability of bound
states while their supplied tensor adds pressure and opening burden. The
standing backbone, angular material and transport keep their assigned roles;
allowing their combined radial-null burden to vanish still leaves this
occupied-state result adverse.

## Numerical evidence

Six bounded runs separate resolution, occupation range and outer-boundary
effects. The angular limits at the continuum ceiling are `|K| = 15, 26, 48`;
the sampled sufficient angular bound lies below each limit with positive
potential margin. Both parity sectors are included throughout.

| Evidence directory | Couplings | Optical spacing | Coordinate extent | Ceiling / `y v` | Multiplets by coupling | Elapsed seconds |
| --- | --- | --- | ---: | ---: | --- | ---: |
| `initial` | 1, 2, 4 | 1/128 | 64 | 0.90 | 52, 224, 906 | 25.5 |
| `refined` | 1, 2, 4 | 1/256 | 64 | 0.90 | 52, 224, 906 | 51.0 |
| `higher_ceiling` | 4 | 1/256 | 64 | 0.98 | 1,140 | 52.3 |
| `far_boundary` | 4 | 1/256 | 96 | 0.98 | 1,140 | 73.8 |
| `complete_band` | 1, 2, 4 | 1/256 | 64 | 1.00 | 74, 302, 1,222 | 75.2 |
| `complete_band_far` | 1, 2, 4 | 1/256 | 96 | 1.00 | 74, 302, 1,222 | 203.8 |

The [independent audit](data/confined_fermion/audit/audit.json) gives the
following checks:

- The four analytic tests pass. They test a known spectrum and tensor,
  physical normalization, material action and parity pairing.
- Doubling resolution preserves all 1,182 initial multiplets and every
  opening sign. The largest relative frequency change is `5.58e-5`; the
  largest relative opening change is `1.71e-4`. The maximum weighted
  stress-exchange residual decreases by approximately a factor of four.
- Increasing the final outer extent from 64 to 96 preserves all 1,598
  continuum-ceiling multiplets. The largest relative frequency change is
  `1.28e-10`, and the largest relative opening change is `6.50e-7`.
  The final maximum boundary probability-density fraction is `5.54e-13`.
- The final maximum relative Killing-energy error is `4.51e-5`, the maximum
  weighted stress-exchange residual is `5.00e-4`, and the integrated geometric
  opening identity agrees to `7.67e-9` relative error.
- A separate full first-order Dirac collocation solve reproduces the lowest
  `y = 1`, `K = 1` frequency to `3.25e-7` relative agreement and its opening
  contribution to `7.56e-7`. Its normalization is unity to `3.82e-11`.
- The same tensor code reproduces Weinbaum's actual negative-ANEC example,
  equations (112)–(113). Three successive meshes approach frequency
  `111.88352` and ANEC `−3.59047` in the paper's normalization, consistent
  with its rounded `111.88` and `−3.59`. This control explicitly exercises
  the sign needed by the proposed source.

The last control uses the paper's highly structured prescribed metric. Its
negative averaged null stress and the rail's radius-weighted opening integral
are distinct diagnostics. Reproducing the former validates the ability to
compute signed fermion stress; the rail conclusion comes from the latter.

## Scope and continuation decision

This result covers stationary, diagonal occupations of the resolved
positive-frequency spherical modes in the specified real, nonnegative
Yukawa mass well, at the retained static construction phase. The finite-box
and sampled angular checks support the resolved catalog; they supply a
numerical bound-state audit with the stated resolution. The initial
90-percent band receives the direct mesh comparison, while the added upper
band receives the stress residual and outer-boundary checks.

The canonical scalar profile remains a seed for curved material equilibrium.
Its stress and equation residual are counted, and an eventual equilibrium
requires the fermion scalar density and the vacuum force. An optimistic
zero additional positive material burden already fails the occupied opening
gate on this seed. A coupled relaxation would therefore need an identified
mechanism that changes the sign-bearing state or its geometry.

The computed fermion tensor is a finite occupied-state increment. Absolute
vacuum polarization, scattering states, coherent time-dependent states,
different confining interactions and changed geometries require their own
calculations. A vacuum-based continuation needs a specified spectrum and
enhancement mechanism beyond these occupied states. The present result
provides a stopping point before a full semiclassical solve. The complete
An–T–Le source construction remains open.

## Reproduction and storage

The model and initial protocol were committed as `b4fe60d`. The common
Dirac/material implementation stays unchanged across all six runs. Later
runner changes allow a ceiling equal to the continuum threshold and store
the common background once. Each run's `summary.json` retains source and
input SHA-256 hashes, model parameters, every mode's diagnostics and aggregate
results. The audit preserves the original independent-control source hashes
when reusing those controls after changes confined to audit orchestration.
The [original control script](data/confined_fermion/audit/control_source.py.txt)
is retained with its matching recorded hash.

From the repository root, an independent final-catalog reproduction is:

```bash
export PYTHONPATH=toolkit/adm_harness_cli
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python3 toolkit/adm_harness_cli/scripts/evaluate_confined_fermion.py \
  --output /tmp/rail-confined-fermion-check \
  --spacing 0.00390625 --extent 96 --cutoff-fraction 1 --workers 2
```

The other rows follow by changing the listed parameters, with a fresh output
directory for each run and `--yukawa 4` for the two single-coupling rows. Those
five runs used four workers each. The largest measured worker resident set
was 247,044 KiB, approximately 241 MiB. Each run stayed below its 20 MB output
allowance and 900-second wall-clock allowance.

The six numerical summaries, final background and tensor probes, refined
tensor probes and audit occupy approximately **28.95 MB**. Redundant arrays
were removed after their comparisons; the
[retention manifest](data/confined_fermion/array_retention.json) records their
hashes and the 51.19 MB recovered. The native probe arrays sample the tensor
at 257 points; the integrated diagnostics use the full optical mesh.

```bash
pytest -q toolkit/adm_harness_cli/tests/test_confined_fermion.py
python3 toolkit/adm_harness_cli/scripts/audit_confined_fermion.py
```

The audit command repeats the independent controls and reconstructs the
comparison tables from the retained summaries and refined probes.
