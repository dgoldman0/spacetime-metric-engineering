# Material-confined fermions: occupied-state evaluation

Date: 9 September 2026.

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

The first state catalog includes every resolved positive-frequency bound
mode below `0.9 y v`, with both spherical parities. A fully occupied angular
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
