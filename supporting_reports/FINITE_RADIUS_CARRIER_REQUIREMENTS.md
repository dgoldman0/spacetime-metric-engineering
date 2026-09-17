# Finite-radius carrier requirements

A finite-radius escape screen admits much less extreme field parameters
than the earlier illustrative \(k_F/m_f\le0.3\) cut. For example,
\(\beta=1,\ e=g=1\) reaches an exterior tunneling-action diagnostic of
100 at \(R\sqrt\mu=11803.4\), including the forward Doppler shift and
an instantaneous radial-speed envelope.
Its unit-coefficient quartic-loop diagnostic is 0.00633, compared with
\(2.71\times10^{10}\) at the earlier small-\(\beta\) threshold.
These numbers define geometric requirements for candidate field theories.
The occupied curved string still needs a lifetime and constitutive-law
calculation using its actual spectrum, sources and interactions.

## Exterior escape diagnostic

[Harigaya et al., JHEP 03 (2025) 063](https://arxiv.org/html/2412.12259v1)
distinguish exact bound states from long-lived loop modes. Their global-string
analysis gives escape suppression proportional to
\(\exp[-2m_f^3R/(3E^2)]\) in its large-mode limit; curvature-dependent decay
and scattering channels also matter. Their carrier model differs from the
present two-branch local vortex. The result motivates a radius-dependent
diagnostic in place of a universal bulk-mass cutoff.

Here the exterior angular-momentum barrier is integrated directly. For
laboratory energy \(E>m_o\), orbital angular momentum \(n\), and constant
exterior mass \(m_o\), define \(k=\sqrt{E^2-m_o^2}\), \(R_o=R+w\), and
\(z=kR_o/n\). If \(z<1\), twice the radial forbidden-region action is

\[
\mathcal B
=2\int_{R_o}^{n/k}\sqrt{\frac{n^2}{r^2}-k^2}\,dr
=2n\left[\operatorname{arccosh}\frac1z-\sqrt{1-z^2}\right].
\]

For a frozen radius, \(n=ER\). At zero core width, \(\zeta=E/m_o\) gives
\(\mathcal B=2ER[\operatorname{atanh}(1/\zeta)-1/\zeta]\).
Its high-energy expansion is \(2m_oR/(3\zeta^2)\), matching the
large-loop exponential form above. Finite \(w\) removes the inner part of
the exterior barrier. For \(E\le m_o\), this free-particle channel is
energetically closed.

The screen uses the classical vortex's scalar \(f=0.99\) radius for \(w\),
\(m_o=0.99m_f\), and requires \(w/R\le0.01\), \(n\ge100\), and
\(\mathcal B\ge100\) where the channel is open. The exponent target is
selected for comparison. Operating life also depends on the rate prefactor,
competing channels and exposure time. The curved exterior profile and the
WKB approximation for the local two-branch model remain assumptions.

## Rotor frame and replicated inventory

The exterior comparison uses laboratory energy and orbital momentum as
separate inputs. Proper carrier
momentum \(k_F/\sqrt\mu=\sqrt{2\pi}/\lambda\), with
\(\lambda=x/\sqrt{1-j^2}\), becomes

\[
\frac{E_{\rm radial}}{\sqrt\mu}=\frac{\sqrt{2\pi}(1+j)}x,\qquad
E_{\rm lab}=\gamma_rE_{\rm radial},\qquad
n=R E_{\rm radial}.
\]

The coupled domain has \(h\le1.32\), \(|x-h|\le0.01140\), and \(b\ge0\).
Writing the lab energy using the rotor energy identity gives

\[
\frac{E_{\rm lab}}{\sqrt{2\pi\mu}}
=\frac{2h(1+j)}{x^2+1+j^2+2b}.
\]

For fixed \(h,x\), the derivative with respect to \(j\) has the sign of
\(x^2+1+2b-2j-j^2\), which is positive on this domain. The largest
allowed spin and smallest heat occur at \(b=0,\gamma_r=1\), where
\(j^2=h^2-(x-h)^2-1\). Maximizing over the remaining rectangle gives
\(E_{\rm lab}/\sqrt\mu\le3.565807922\), attained at the boundary
rectangle at \(h=1.32,\ x=1.3086,\ j=0.861551\).
The radius screen then uses this energy bound together with
\(\gamma_{\max}=(1-0.00905^2)^{-1/2}\) and
\(n=E_{\max}R/\gamma_{\max}\). At fixed radial Lorentz factor,
the exterior-action integrand decreases with energy because
\((R/(\gamma_r r))^2-1\le0\). Increasing \(\gamma_r\) also decreases
the action. The independent bounds therefore enclose these instantaneous
scalar-barrier comparisons. Time-dependent tunneling and acceleration
channels require the moving-background field equations. The archive also
keeps a separate stationary relaxed-string screen.

The microscopic layout counts six equal rotor copies: two opposed spins
for each of three orientations. For total node inventory \(MC\), each
copy has \(\mu=MC/(4\pi N_{\rm copy}R_0)\), with \(R_0=r_0\delta\).
Taking \(R_{\min}=x_{\min}R_0\) gives

\[
\frac{C\delta}{\hbar}\ge
\frac{4\pi N_{\rm copy}(R_{\min}\sqrt\mu)^2}{x_{\min}^2Mr_0},
\quad N_{\rm copy}=6,\ M=19,\ r_0=\frac1{12\pi},\ x_{\min}=1.068.
\]

Natural units use \(c=1\). The inherited capacities already contain
\(D=\ell R^2\) and are energies per radial material label and solid angle.
A physical cell uses the corresponding label and solid-angle measure.
The [physical normalization](RAIL_STORAGE_AND_INTERFACE_STATUS.md#physical-normalization)
relates that cell energy and proper delay to one metric length scale.
The audit's action requirement is applied through this common conversion.

## Candidate comparison

All rows use \(e=1\), the forward rotor energy bound, and the same
width and exponent criteria, and the radial-speed envelope.

| \(\beta\) | \(g\) | Required \(R\sqrt\mu\) | Forward \(E/m_f\) | \(g^2/(16\pi^2)\) | Quartic loop/tree diagnostic |
|---|---:|---:|---:|---:|---:|
| 0.1 | 1 | 6785.34 | 5.05227 | 0.006333 | 0.06333 |
| 1 | 0.3 | 439815 | 21.0674 | 0.000570 | 0.00005129 |
| 1 | 1 | 11803.4 | 6.32023 | 0.006333 | 0.006333 |
| 1 | 2 | 1514.96 | 3.16011 | 0.025330 | 0.10132 |
| \(5.83701\times10^{-11}\) | 3.973835 | \(1.54727\times10^7\) | 0.499316 | 0.1 | \(2.70539\times10^{10}\) |

In the final row the selected exterior channel is closed and scalar width
sets the radius. For \(\beta=1,\ g=1\), the scalar radius is
\(6.86738\times10^{-4}\) of the loop radius. The corresponding node
action is \(C\delta/\hbar\ge1.82729\times10^{10}\), including all six
copies.

The weakest first-fine receiving node has normalized \(C_i\delta_i\)
of \(1.98883\times10^{-23}\). Applying this independent-cell layout
to every active node requires a common energy-time unit of
\(9.18775\times10^{32}\hbar\) for \(\beta=1,\ g=1\), or
\(3.03628\times10^{32}\hbar\) for \(\beta=0.1,\ g=1\).
These are dimensional conversion requirements. For a homothetic rail,
the cell measure and metric length determine the energy and time units
together. Shared microscopic hosts need a corresponding revision of the
cell construction.

## Material conditions and evidence

The comparison separates loop escape from vacuum coupling strength, width
and the desired elastic law. Accessible massive modes, two-branch collisions,
current backreaction, curvature corrections and driven interfaces can alter
the occupied stress tensor. For example,
[Ringeval's massive-mode calculation](https://arxiv.org/abs/hep-ph/0106179)
finds that massive occupations change the zero-mode equation of state.
A favorable escape exponent therefore leaves the rigid law as an independent
material calculation.

The subsequent [charge-symmetric host calculation](NEUTRAL_FERMIONIC_HOSTS_AND_OCCUPATION.md)
supplies explicit carrier profiles and evaluates opposite-branch escape,
counted flavor multiplicity and the full homogeneous fermion-loop
coefficient for its specified tree normalization.

Six tests compare the action with direct quadrature, recover its
high-energy limit, check finite width, verify six-copy dimensional scaling,
and independently bound the boosted rotor energy and the radial-motion
envelope. A four-worker audit
evaluates 300 parameter/role combinations and four history scale requirements.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_fermionic_loop_screen.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_fermionic_loop_screen.py -q
~~~

The [retained evidence](data/fermionic_loop_screen/) includes numerical
tables, source snapshots and provenance.
