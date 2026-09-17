# Fermionic string material candidate

A finite-width Abelian–Higgs vortex carrying two balanced fermion
populations supplies a field-theory candidate for the rigid string law.
The classical vortex calculation reaches the illustrative rotor carrier
threshold at \(\beta=5.83701\times10^{-11}\). Its scalar and energy
profiles extend far beyond the magnetic-flux core. Geometry, occupied
carrier backreaction and the quantum-corrected potential therefore remain
separate material requirements. The calculation concerns a microscopic
field theory; realization as an available material remains open.

The [finite-radius carrier comparison](FINITE_RADIUS_CARRIER_REQUIREMENTS.md)
retains this conservative threshold and also examines longer-lived loop
modes above the bulk mass, including the rotor's forward energy shift and
the geometry required by all six rotor copies.

## Field and occupation normalization

The bosonic action follows [Ringeval, Eqs. (2), (3), (10)](https://arxiv.org/pdf/hep-ph/0007015):

\[
\mathcal L_b=\tfrac12|D\Phi|^2-\tfrac14H_{\mu\nu}H^{\mu\nu}
 -\frac{\lambda_H}{8}(|\Phi|^2-\eta^2)^2.
\]

With \(e=qc_\Phi\), define \(\rho=e\eta r\),
\(\beta=\lambda_H/e^2\), and a unit vortex
\(\Phi=\eta f(\rho)e^{i\theta}\), with gauge profile
\(a(0)=0\), \(a(\infty)=1\). The masses are
\(m_V=e\eta\), \(m_H=e\eta\sqrt\beta\), and the bulk Yukawa
mass is \(m_f=g\eta\). The equations solved here are

\[
f''+\frac{f'}\rho-\frac{(1-a)^2f}{\rho^2}
 -\frac\beta2 f(f^2-1)=0,\qquad
a''-\frac{a'}\rho+f^2(1-a)=0.
\]

Their integrated bare tension is \(\mu=\pi\eta^2B\), where

\[
B=\int_0^\infty\rho\left[
 f'^2+\frac{(1-a)^2f^2}{\rho^2}+\frac{a'^2}{\rho^2}
 +\frac\beta4(1-f^2)^2\right]d\rho.
\]

At \(\beta=1\), the first-order equations
\(f'=(1-a)f/\rho\) and \(a'/\rho=(1-f^2)/2\) give \(B=1\).

For the carrier screen, each of two opposite chiral branches contains
\(N\) particles, with equal populations cancelling longitudinal momentum.
One state per \(dk/(2\pi)\) gives
\(N/L=k_F/(2\pi)\) and branch energy density \(k_F^2/(4\pi)\).
This counting also appears with explicit multiplicity in
[Ibe et al., Eqs. (4.1)–(4.2)](https://arxiv.org/pdf/2102.05412).
Thus

\[
E(L)=\mu L+\frac{2\pi N^2}{L}
 =\frac M2(\lambda+\lambda^{-1}),\qquad
L=\lambda L_0,\quad M=2\mu L_0.
\]

The corresponding line energy and tension are
\(U=\mu(1+\lambda^{-2})\) and
\(\mathcal T=\mu(1-\lambda^{-2})\).
The relation \(U+\mathcal T=2\mu\), with longitudinal sound speed
\(c_L=1\), agrees with the zero-mode approximation of
[Peter and Ringeval, Eqs. (19), (25)](https://arxiv.org/pdf/hep-ph/0011308).

There is a numerical normalization caveat. For equal particle-only
populations, Ringeval's printed Eqs. (113), (119) give twice the carrier
energy of the explicit one-state-per-momentum count above. The archive
keeps `canonical_two_branches` and `printed_ringeval_two_branches` as
separate sensitivity cases. The canonical case sets the threshold and
numbers below; the printed case halves the required \(g^2\).

## Component duties and the carrier threshold

The rotor begins at proper stretch 2.3349; the material screen also uses
the proposed operating floor 1.17 and the relaxed state 1. Each role has
a different carrier load:

| String duty | Stretch | Carrier energy / bare energy | \(\mathcal T/U\) | \(k_F/\sqrt\mu\) |
| --- | ---: | ---: | ---: | ---: |
| Initial rotor | 2.3349 | 0.183427 | 0.690007 | 1.073548 |
| Rotor floor | 1.17 | 0.730514 | 0.155726 | 2.142417 |
| Relaxed core or joint limit | 1 | 1 | 0 | 2.506628 |

The last row has vanishing string tension and transverse wave speed
\(c_T=\sqrt{\mathcal T/U}\). A sheet additionally requires two
in-plane load directions and its separate shear response. A construction
from string populations would need a counted network and junction law
to supply those sheet duties.

Let \(z=k_F/m_f\) and \(\ell_g=g^2/(16\pi^2)\). Canonical
occupation gives the exact screening tradeoff

\[
z^2\ell_g=\frac{B}{8\lambda^2}.
\]

The illustrative cuts \(z\le0.3\) and \(\ell_g\le0.1\) at
\(\lambda=1.17\) require \(B\le0.0985608\). The computed
crossing is \(\beta=5.83700556\times10^{-11}\); at
\(\beta=10^{-12}\), \(B=0.08329151381\). By comparison,
\(B(10^{-6})=0.17103490984\).

At the crossing, \(g=3.973835\) meets both selected cuts. Holding
that coupling fixed gives \(z=0.150328\) at the initial rotor
stretch and \(z=0.351\) at stretch one. The relaxed-state cuts
require \(B\le0.072\); the retained scan reaches a minimum
required \(\ell_g=0.115683\) for \(z=0.3\) in that role.

## Finite width and quantum diagnostics

At fixed bare tension, the radius conversion is

\[
r\sqrt\mu=\frac{\rho\sqrt{\pi B}}e.
\]

Scalar amplitude, enclosed energy and enclosed flux define distinct
widths. The table gives \(e r\sqrt\mu\); divide each entry by
the selected gauge coupling to obtain \(r\sqrt\mu\).

| Profile | Scalar \(f=0.9\) | 90% energy | 90% flux | 99% energy |
| --- | ---: | ---: | ---: | ---: |
| Rotor threshold | 33,038.1 | 27,712.9 | 13.4178 | 106,653.0 |
| \(\beta=10^{-12}\) | 186,462.7 | 159,946.4 | 14.4884 | 704,829.9 |

For \(z=0.3\) at stretch 1.17, the latter profile requires
\(g=3.653071\) and \(\ell_g=0.084508\). Lower tension factor
improves these two carrier diagnostics while increasing the scalar
extent substantially.

The unit-coefficient quartic loop-size diagnostic is
\(\delta\lambda_H\sim g^4/(16\pi^2)\), compared with
\(\lambda_H=\beta e^2\). At the crossing this gives
\(\delta\lambda_H/\lambda_H\sim2.70539\times10^{10}/e^2\);
at \(\beta=10^{-12}\), it gives
\(1.12775\times10^{12}/e^2\). A renormalized potential and its
parameter dependence determine the actual quantum correction.

The occupied gauge and Higgs sources also require calculation.
[Ringeval's Eqs. (150)–(151)](https://arxiv.org/pdf/hep-ph/0007015)
give distinct conditions for perturbing the vortex background and its
zero modes. The present calculation resolves the unoccupied classical
background and applies occupation energetics; the sourced profiles,
massive carrier spectrum and leakage rates remain open.

## Numerical evidence

The [retained evidence](data/fermionic_string_material/summary.json)
contains 25 values from \(\beta=10^{-12}\) through 1, with three
resolutions and domains per value, plus a refined threshold and two
stronger domain checks. The BPS case gives
\(B=0.999999999999954\). Maximum relative virial residual
\(|B_{\rm magnetic}-B_{\rm potential}|/B\) is
\(1.01\times10^{-12}\); maximum square-completion error is
\(1.25\times10^{-13}\).

For \(t=\log\rho\), \(p=df/dt\), \(q=da/dt\), the
completion check integrates

\[
[p-(1-a)f]^2+q^2/\rho^2-q(1-f^2)
 +\beta\rho^2(1-f^2)^2/4
\]

and adds the topological boundary term. Combining the gauge square and
potential correction before integration removes cancellation between
terms of order \(1/\beta\). The original unexpanded diagnostic
is retained alongside it, and the absolute acceptance tolerance remains
\(2\times10^{-8}\).

The stronger checks use inner radius \(10^{-7}\), outer radius
\(50/\sqrt\beta\), and collocation tolerance \(2\times10^{-10}\).
At the threshold and smallest beta, they change \(B\) by less than
\(6.7\times10^{-14}\) and every recorded width by less than
\(9.3\times10^{-11}\) relatively. Eight tests cover normalization,
variational stationarity, small-beta cancellation, carrier counting,
thresholds and physical-radius conversion.

## Next finite-radius and carrier calculation

First, express the rotor's minimum curvature radius and component
clearance in the same units as these profiles. A single loop with
\(L_0=2\pi R_0\) and relaxed inventory \(M\) has
\(\mu=M/(4\pi R_0)\). Specifying the energy-length scale relative
to \(\hbar c\) fixes \(R_{\min}\sqrt\mu\). The archived
99% energy and scalar widths then give a quantitative fit and curvature
parameter for each \((\beta,e)\), with an explicit tail allowance.

Next, solve the normalized transverse Dirac spectrum on these finite
profiles for a specified pair of chiral charge assignments and Yukawa
coupling. The first massive bound-state threshold, localization widths
and bulk continuum must be compared with the occupied \(k_F\).
Filling accessible modes at fixed conserved populations supplies the
scalar and gauge sources for the coupled Higgs, azimuthal, temporal and
longitudinal gauge equations. Their integrated stress gives the change
in \(U\), \(\mathcal T\), and the rigid-law residual. Curvature
and junction perturbations then supply the relevant leakage calculation;
[Ibe et al.](https://arxiv.org/pdf/2102.05412) demonstrate the importance
of curvature in their specified axion-string decay model.

## Reproduction

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_fermionic_string_material.py \
  --workers 4 --minimum-log10-beta -12 --beta-samples 25 \
  --output /tmp/fermionic_string_material_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_fermionic_string_material.py
```

The [manifest](data/fermionic_string_material/manifest.json) records
implementation, test and output hashes. This report was manually authored.
