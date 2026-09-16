# Finite containment: current paths, interfaces and material evolution

16 September 2026.

A finite coaxial construction supplies the added hoop field's current paths
and radial interface equations. Following that construction through the
saved histories exposes separate current-host, end-reaction and material
inventory requirements. The second location admits pointwise allocations
with the new particle costs included. A fixed ensemble of ideal sheets,
strings and pressure-control photons exceeds the available energy along
both histories, including a sensitivity that grants every current host for
free. Physical containment remains an open construction requirement.

The [ensemble role audit](CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md) established a
positive pointwise allocation through several constituents. This calculation
retains that component distinction. It tests one spatial arrangement and
two explicit material evolution laws, while preserving the heat history,
original magnetic fields, original carrier tensors, original centrifugal
reactions and the support field floor. Shared current populations and
material reconfiguration remain distinct constructions with their own
state and exchange equations.

## A finite field and its interfaces

Each original straight leg receives a coaxial cartridge in its existing
annulus, with inner radius \(r\), outer radius \(\eta r\), length \(L\),
and \(\eta=1.01\). There are two cartridges per capsule. In units
\(c=\mu_0=1\), the added field is

\[
B_\theta(s)=C/s,\qquad r<s<\eta r,\quad |z|<L/2,
\]

with zero added field outside the cartridge. Its currents occupy all four
faces: \(K_z=C/r\) on the inner cylinder, \(K_z=-C/(\eta r)\) on the
outer cylinder, and opposite radial currents \(K_s=\pm C/s\) on the
annular ends. The circulating current is \(I=2\pi C\). Each face carries
the same charge flux through a transverse cut, closing the circuit.

```mermaid
flowchart LR
    A[Inner cylindrical current] --> B[Far annular return]
    B --> C[Outer cylindrical current]
    C --> D[Near annular return]
    D --> A
```

The coaxial field and its energy integral follow the usual
[Ampère-law and inductance construction](https://farside.ph.utexas.edu/teaching/em/lectures/node86.html).
The sharp interfaces here define an ideal magnetostatic solution; a finite
conductor and a changing current require thickness, induction fields and
propagation dynamics.

Let \(V_s\) be the total straight core volume per label, \(B_i=C/r\), and
\(U\) the added field energy over both legs and all capsules in that label.
Direct integration gives

\[
U=V_s B_i^2\ln\eta,\qquad
J_z=\int |K_z|\,dA=\frac4r\sqrt{\frac{UV_s}{\ln\eta}},\qquad
J_s=J_z\frac{(\eta-1)r}{L}.
\]

Both cylindrical sheets and both annular returns are included. The maximum
return-to-axial current-integral ratios are \(3.57\times10^{-5}\) and
\(3.84\times10^{-5}\) at the two locations.

A stack of transverse tensile sheets spans the annulus. Choose its net
tensile density \(m=B_i^2/2\), constant across the gap. With
\(b(s)=C^2/(2s^2)\), the combined radial and hoop stresses are

\[
p_s=b(s)-m,\qquad p_\theta=-b(s)-m,
\qquad \frac{dp_s}{ds}+\frac{p_s-p_\theta}{s}=0.
\]

Thus the added radial traction vanishes at the inner boundary. At the outer
boundary it equals \(B_i^2(\eta^{-2}-1)/2\). The integrated transverse
tension is

\[
M=R_\eta U,\qquad
R_\eta=\frac{\eta^2-1}{2\ln\eta}=1.010033\ldots .
\]

If the original inner and outer integrated hoop loads are \(H_i,H_o\),
the remaining surface duties become \(H_i\) and \(H_o-2M\). Tensile outer
supports require \(U\le H_o/(2R_\eta)\). Their total transverse stress,
including the bulk sheet and field, is exactly \(-(H_i+H_o)\).

This finite arrangement has integrated normal stress \(U-M\). The earlier
algebraic arrangement imposed zero integrated normal stress. Here the local
radial equilibrium equation and the separate interface tractions determine
the normal stress. The resulting load allocation is recomputed for the
finite arrangement.

The ends add independent duties. Summed over the cartridges, the added
magnetic axial force at either end set is \(U/L\). Moreover, the retained
axial background field \(B_z\) produces the shear stress
\(T_{z\theta}=-B_zB_\theta\) and opposite end torques of magnitude

\[
\mathcal T=\frac{V_s}{L}(\eta^2-1)rB_iB_z.
\]

These follow from the local
[Maxwell momentum flux](https://farside.ph.utexas.edu/teaching/em/lectures/node91.html).
Azimuthal averaging removes the shear from the rail's diagonal tensor;
the end interfaces still require torque transmission. Opposite cartridge
orientations can cancel the net torque while retaining the connecting
member's local load.

## Current hosts and end reactions

The explicit host trial uses additional opposed charged populations,
retaining the original carrier allocation. With
\(\chi=m/|q|\), absolute charge inventory \(N\), and current integral
\(J=Nv\), the particle energy and longitudinal pressure are

\[
E=\chi N(1-v^2)^{-1/2},\qquad P=Ev^2.
\]

The return populations contribute radial kinetic pressure. A favorable
ideal radial-string reaction is charged energy equal to that pressure.
Binding matter, finite junctions and shear fixtures remain additional
costs. The coefficients retain their previous normalized values; a physical
particle species and dimensional scale have yet to be assigned.

Applying the new current integral directly to the previous maximizing
field witness gives peak minimum particle energies of 0.326909 and
0.141227 per label. Those values alone give an incomplete test because
the carrier pressure can assist an axial duty. The calculation therefore
reallocates the surface sheets and strings using the full particle tensor
and searches the field amplitude and drift speed.

An independent continuous bound also checks every subluminal velocity
distribution. Write \(E=P+Q\). Cauchy–Schwarz gives
\(PQ\ge(\chi J_z)^2\), including mixtures of speeds. The three remaining
support facets bound \(Q\) and \(E\) at each allowed field amplitude.
The bound grants free return currents, end supports and torque fixtures.
A violation therefore rejects the specified independent-host construction
even with those favorable allowances.

| History | Samples | Samples rejected by the all-speed host bound | Samples failing the explicit pointwise search |
| --- | ---: | ---: | ---: |
| First, coarse | 2,057 × 16 | 4 | 4 |
| First, fine | 4,113 × 32 | 10 | 10 |
| Second, coarse | 1,029 × 16 | 0 | 0 |
| Second, fine | 2,057 × 32 | 0 | 0 |

The first-location violations occur at saved time 0.5. Its fine-history
necessary coefficient ceiling is \(1.31305\times10^{-8}\), compared with
the retained \(2.54415\times10^{-8}\). The second ceiling is
\(1.34171\times10^{-8}\), above its retained
\(1.20001\times10^{-8}\). These are necessary ceilings for this geometry
and host arrangement. The explicit second-location witnesses use drift
speeds between approximately \(0.9733c\) and \(0.9867c\) wherever the new
field is activated.

The pointwise witnesses still require end reactions. Even granting all
remaining radial-Maxwell tension to the new end load leaves insufficient
capacity at two otherwise passing first-location fine samples and 176
second-location fine samples. Reserving the existing field floor for its
previous duties gives the same failure counts. These capacity checks apply
to the constructed allocations; a jointly redesigned rail connection has
its own reaction assignment.

Closing the cartridge's axial load entirely with its own ideal tensile
members also has a necessary budget obstruction: 12 first-location and 172
second-location fine samples violate the bound before carrier or torque
costs. The construction therefore calls for a different shared reaction
path at those samples.

For a time history, the charged population remains present when its current
vanishes. Replaying the searched field with fixed axial and return charge
inventories fails at both locations for the tested peak speeds
\(c/\sqrt2\), \(0.98c\), and \(0.999c\). At peak speed \(0.98c\), the
fine-history maximum energy shortfalls are 0.129920 and 0.0651782. These
are three conserved-inventory trials of that waveform.

The pointwise search also creates sharp current switching. Its proper-time
rate diagnostic, one leg's light-crossing time multiplied by current change
rate divided by peak current, reaches 3.48 and 0.602 on the fine histories.
Doubling time resolution approximately doubles these maxima. Those searched
waveforms require a resolved electromagnetic transient before they can
serve as physical trajectories.

## Fixed materials and controlled energy exchange

The material construction keeps separate populations for inner and outer
longitudinal sheets, inner and outer hoop strings, and transverse sheets.
For the inherited affine stretches \(\lambda_z,\lambda_\perp\), their
passive ideal laws are

\[
W_j=W_{j0}\lambda_z\lambda_\perp,\qquad
K_j=K_{j0}\lambda_\perp,\qquad
A=A_0\lambda_\perp^2.
\]

An unmodified transverse population would require \(M=A=R_\eta U\).
Its initial inventory must simultaneously exceed the later required
tension and respect the initially small outer load. This fails for 12 of
32 first-location labels and every second-location label on the fine
histories. The maximum required initial energies are 0.0183815 and
0.0322627; the allowed initial inventories are only approximately
\(0.9\text{–}1.1\times10^{-4}\) and
\(0.46\text{–}0.73\times10^{-4}\), respectively.

An active ensemble then adds independently counted photon populations to
adjust tension while keeping the five material populations fixed. Opposed
hoop photons of energy \(e_j\) reduce each boundary's net hoop tension:

\[
e_i=W_i+K_i-H_i,\qquad
e_o=W_o+K_o-H_o+2R_\eta U,\qquad 0\le e_j\le K_j.
\]

Isotropic in-plane photons of energy
\(e_T=2(A-R_\eta U)\ge0\) reduce the transverse sheet's two tensions
equally. This preserves the radial equilibrium construction. Its total
energy, axial pressure and transverse trace, before new carrier costs, are

\[
E_{\rm assembly}=2(W_i+W_o)+2(K_i+K_o)+3A-H_i-H_o+U,
\]
\[
P_z=U-W_i-W_o,\qquad P_\theta+P_s=-H_i-H_o.
\]

Thus the field amplitude and three photon populations can change while the
material population identities stay fixed. A whole-history linear program
optimizes all five initial populations, retaining every sampled time and
the separate boundary duties. It grants free new current hosts, lossless
photon control and free end fixtures. The objective is the smallest constant
extra energy allowance per label needed to satisfy every tensor constraint.
Positive values measure the missing budget for this material family.

| History | Range of minimum extra energy allowance across labels | Rejected labels | Worst allowance with **all** current hosts and their centrifugal reactions free |
| --- | ---: | ---: | ---: |
| First, coarse | 0.152285–0.170782 | 16 / 16 | 0.113396 |
| First, fine | 0.151935–0.171272 | 32 / 32 | 0.113888 |
| Second, coarse | 0.0970681–0.127513 | 16 / 16 | 0.102815 |
| Second, fine | 0.0969403–0.127818 | 32 / 32 | 0.103084 |

All energies use the existing integrated ledger normalization. The free
current-host sensitivity also removes the original host tensor and its
centrifugal loads, then solves the entire material program again. It
isolates the fixed-material cost from the choice to retain separate current
populations.

The strongest fine-history deficits occur at saved time 0.0451758. The
assembly must already contain material sized for subsequent loading, while
its early low-tension state requires positive photon energy to offset the
prepared tensile stress. At the worst first-location label, the prepared
transverse sheet has initial energy 0.0545815 and the initial compensating
photons have energy 0.109163. Their energy remains counted throughout the
change in duty.

The evolution archive records each component's mechanical work and required
exchange:

\[
\Delta Q_i=\Delta E_i+
\overline{P_{z,i}}\,\Delta\ln\lambda_z+
\overline{P_{\theta,i}+P_{s,i}}\,\Delta\ln\lambda_\perp.
\]

The fixed material populations satisfy their passive work laws to the panel
quadrature accuracy. The field and photon populations exchange energy with
an explicit candidate control store. Assigning the store
\(\Delta E_{\rm store}=-\sum_i\Delta Q_i\) makes the exchanges reciprocal,
consistent with the electromagnetic
[energy-balance requirement](https://farside.ph.utexas.edu/teaching/em/lectures/node89.html).
With cumulative demand \(C(t)\) and available pressureless reserve \(S(t)\),
a counted store requires an initial energy in the interval

\[
\max_t C(t)\ \le E_{\rm store,0}\ \le\min_t[C(t)+S(t)].
\]

That interval is empty for every constructed history label. The minimum
distance between its endpoints ranges from 0.156152 to 0.193679 at the
first fine history and from 0.0983934 to 0.161772 at the second. The states
already have tensor-budget deficits; this store calculation records the
consequences for the same constructed trajectory. Its deficit is separate
from, and overlaps with, the tensor deficit. The two values should not be
added. Lossless unlimited-rate transfer is a favorable capacity assumption;
finite power, entropy disposal and control hardware require further states.

## Consequences for the next construction

The finite calculation identifies actual places where forces and energy
must pass: two cylindrical current hosts, two end returns, transverse
tensile elements, outer hoop members, axial end connections, torque
connections, and a reciprocal control-energy store. It also preserves a
useful distinction between a pointwise allocation and a common material
history.

The next material model needs an internal configuration variable, such as
sheet orientation, deployment or transfer between duties, together with its
energy, forces and evolution law. This directly addresses the cost of
carrying the prepared fixed ensemble through the early low-load state.
For the electrical construction, shared helical current populations and
their shear stresses deserve joint treatment with the original hosts.
Those changes can then be tested against the same retained tensor and
exchange budgets. The existing results continue to constrain their assigned
constituents and load paths.

## Evidence and reproduction

The [implementation](../toolkit/adm_harness_cli/adm_harness/finite_containment.py)
and [four-worker audit](../toolkit/adm_harness_cli/scripts/audit_finite_containment.py)
produce a [numerical summary](data/finite_containment/summary.json), four
state archives and an [evidence manifest](data/finite_containment/manifest.json).
The archives retain current demands, field and drift witnesses, separate
interface data, fixed-population trajectories, exchanges, control-store
states and primal/dual material-program values. Parent hashes and executed
source snapshots accompany the numerical results.

The [new tests](../toolkit/adm_harness_cli/tests/test_finite_containment.py)
check field and current integrals by quadrature, current closure, radial
stress divergence, both boundary reactions, end force and torque, charge
conservation, the all-speed particle inequality, fixed-material work and
reciprocal storage. An independent linear program retains every field
amplitude explicitly and agrees with the eliminated history formulation.
The new and ensemble suites pass 22 tests.

Across the saved histories, the fixed-material programs have maximum
primal/dual objective disagreement below \(6\times10^{-17}\), and maximum
dual stationarity residual below \(6\times10^{-16}\). Their maximum
constraint violation is below \(3\times10^{-17}\). Component exchange
sums agree within \(8\times10^{-17}\), and reciprocal store exchanges
within \(7\times10^{-18}\). The two resolutions retain the same failure
classification and similar energy deficits.

Reproduction from the repository root uses a fresh output directory:

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_finite_containment.py \
  --workers 4 --output /tmp/finite_containment_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_finite_containment.py \
  toolkit/adm_harness_cli/tests/test_containment_ensemble.py
```

This supporting construction study leaves the technical disclosure at its
established design scope.
