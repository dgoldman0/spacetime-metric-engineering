# Containment ensemble: constituent laws, shared loads and remaining construction

16 September 2026.

An ensemble of the existing ideal field, membrane and string primitives
admits pointwise stress allocations at every saved sample of both containment
histories. The original magnetic geometry, heat history, current-carrier
energy and centrifugal hoop loads remain counted. Each constituent supplies
its own directional stresses, and the two sleeve boundaries receive their
respective loads. The resulting allocation has positive energy reserve at
both resolutions.

This result reopens the existing component approach. The earlier
[scalar-wall test](CURRENT_CARRYING_WALL_MATERIAL_TEST.md) correctly rejects
its specified wall duties and support basis. The present ensemble supplies
those duties through several constituents with distinct orientations and
normal stresses. Its physical realization requires a finite arrangement,
additional current hosts, interface forces, and a common evolving state.

The [component architecture](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
already distinguishes source roles, physical constituents, and their state
variables. The containment calculation now carries that distinction into
its mechanical equations. A field law belongs to its constituent; the
assembly must satisfy the summed tensor and the actual load-transfer
conditions.

| Requirement or earlier assumption | Scope in the revised test |
| --- | --- |
| Stored radiation, prescribed geometry and existing magnetic field | Retained operating inputs. |
| Existing current-carrier energy and mechanical reaction | Retained in full; the new ensemble receives zero credit for replacing those carriers. |
| Scalar-wall relation \(p_z=-u\) | Applies to the relevant longitudinal sheet, with other constituents supplying their own axial stresses. |
| Pure canonical-scalar joint-stress bound | Retains its stated field-content and normal-stress assumptions. The oriented Maxwell constituent below has a different local identity. |
| Zero integrated normal stress | Enforced on each complete boundary assembly; constituents may carry opposing normal stresses. |
| Hoop restraint | Shared among explicitly identified constituents, with each contribution counted once. |
| Fixed sleeve-energy inventory | A previous construction choice. This test supplies pointwise allocations and records the exchanges required to connect them. |
| Material strength fraction | Applied to the specified constituent. The assembly has several independent responses and budgets. |

The loss of local directional information was consequential. In the
original averaged support basis, a transverse Maxwell field and opposed
axial photons both have tensor \((u,p_z,p_\perp)=(1,1,0)\) per unit energy.
Their hoop and normal stresses differ. Assigning mechanical duties requires
retaining those directions before the cylindrical average.

Use local axes \((z,\theta,n)\) for tube axis, hoop and normal. The ideal
assembly has the following constituent tensors, per unit proper energy:

| Constituent | \(p_z\) | \(p_\theta\) | \(p_n\) | Assigned contribution |
| --- | ---: | ---: | ---: | --- |
| Longitudinal sheet, spanning axis and hoop | −1 | −1 | 0 | Axial tension and hoop restraint. |
| Hoop strings | 0 | −1 | 0 | Hoop restraint with an independent axial response. |
| Transverse sheet, spanning hoop and normal | 0 | −1 | −1 | Tensile hoop and normal stresses. |
| Hoop-directed Maxwell field | +1 | −1 | +1 | Axial pressure, hoop tension and opposing normal stress. |
| Pressureless host allowance | 0 | 0 | 0 | An explicitly counted energy-cost sensitivity. |

The zero-current canonical wall supplies an example of the ideal sheet
stress law. The previously considered current-carrying wall derives from
[Peter's scalar-field action](https://arxiv.org/abs/hep-ph/9503408); its
additional current-dependent relation belongs to that branch. The present
test retains the old carrier model separately. All material primitives in
the table describe ideal relativistic responses whose realizable scale,
constitutive evolution and preparation remain to be supplied.

The local tensors follow directly from the spatial projectors
\(T^{\rm Maxwell}_{ij}=u(\delta_{ij}-2b_i b_j)\),
\(T^{\rm sheet}_{ij}=-u(\delta_{ij}-a_i a_j)\), and
\(T^{\rm string}_{ij}=-u s_i s_j\), for unit field direction \(b\), sheet
normal \(a\), and string direction \(s\). Cylindrical averaging maps each
local tensor to \((u,p_z,(p_\theta+p_n)/2)\).

For example, a transverse sheet of energy one plus a hoop field of energy
one gives

\[
(u,p_z,p_\theta,p_n)=(2,1,-2,0).
\]

Its normal stresses cancel while axial pressure and hoop tension coexist.
The combination has \(p_z+H=3>u=2\), with \(H=-p_\theta\). Thus the
canonical-scalar-only inequality used in the previous screen leaves this
ensemble available. Every energy contribution is positive and explicitly
included.

The allocation uses energies \(W,S,M,b\) for longitudinal sheet, hoop
strings, transverse sheet and added hoop field. Let \(k_M\) be the
transverse sheet's own stress fraction, leaving the other ideal laws as
listed. Normal and hoop balance give

\[
k_M M=b,\qquad W+S+2b=H,\qquad z=b-W.
\]

A pressureless host cost \(\beta b\) yields

\[
u=H+\left(k_M^{-1}-1+\beta\right)b.
\]

For a specified axial pressure \(-H\leq z\leq H/2\), a minimum-energy
choice is
\(b=\max(z,0)\), \(W=\max(-z,0)\), and
\(S=H-W-2b\). These relations expose the responsibilities of each member
and preserve the energy cost of the normal-stress partner.

The implementation combines this assembly with the five existing auxiliary
support primitives. It maximizes the remaining pressureless inventory
subject to the three averaged tensor equations, the required hoop load,
normal-stress cancellation, and the host-cost equation. An independent
linear program uses all ten component energies directly. Equal-average
controls replace the hoop field by either a normal field or axial photons.
Both substitutions fail at the earlier worst joint-stress samples, while
the correctly oriented field passes. This control checks the mechanical
distinction that disappears in the three-component averaged tensor.

The saved jacket still has internal magnetic pressure \(0.1p\), annular
pressure \(1.1p\), and radius ratio 1.01. The added hoop field belongs to
the proposed support assembly; its energy is included in the table above.
Its finite routing and current sources are construction requirements.
The original fields and their current costs remain untouched. The calculated
component fractions are split between the inner and outer boundaries using
their actual, separately retained hoop loads.

| Sampled history | Samples | Minimum integrated energy reserve, ideal ensemble | Maximum pressureless host cost / added-field energy |
| --- | ---: | ---: | ---: |
| First, coarse | 2,057 × 16 | 0.00488856 | 0.223806 |
| First, fine | 4,113 × 32 | 0.00471315 | 0.215777 |
| Second, coarse | 1,029 × 16 | 0.0156885 | 0.332394 |
| Second, fine | 2,057 × 32 | 0.0140901 | 0.326806 |

All four ideal allocations pass every sampled point. Energy values use the
existing ledger normalization. The host allowance is a conditional
pressureless-energy test; an actual current host needs its own current,
stress and force equations. The added field reaches energies of 0.0620775
and 0.0580190 per label on the fine histories, with a separately counted
transverse-sheet partner of equal energy in the ideal case.

Constituent-specific sensitivities retain positive reserve in several useful
cases:

| Constituent assumptions | First fine history | Second fine history |
| --- | ---: | ---: |
| Ideal tensile constituents; host energy \(0.1b\) | Pass; reserve 0.00252888 | Pass; reserve 0.0102394 |
| Transverse-sheet strength 0.85; zero host surcharge | Pass; reserve 0.000858551 | Pass; reserve 0.00701417 |
| Transverse-sheet strength 0.85; host energy \(0.1b\) | 7 violating samples | Pass; reserve 0.00234850 |
| Ideal tensile constituents; host energy \(b\) | 12 violating samples | 176 violating samples |

The last row recovers the earlier additive joint-stress gaps. For this
ensemble, the finite gain comes from the oriented field and its counted
normal-stress partner. With ideal remaining constituents and zero host
surcharge, the minimum allowable transverse-sheet strengths are approximately
0.822520 and 0.753690. These are separate constituent requirements;
the longitudinal sheets and hoop strings retain their unit-strength ideal
laws in that comparison.

A broader material bound also survives the scope correction. Suppose all
tensile materials obey \(|p_i|\leq k\rho\), while the remaining positive
energy components obey \(|p_i|\leq\rho\) and
\(p_\theta+p_n\geq0\), as Maxwell fields, radiation and dust do. For total
normal stress zero and hoop tension \(H\),

\[
H\leq2kE_{\rm material},\qquad
H\leq kE_{\rm material}+E_{\rm other},\qquad
E_{\rm total}\geq\frac{H(1+k)}{2k}.
\]

Granting the assembly every available residual-energy unit therefore gives
\(k\geq H/(2\rho_{\rm available}-H)\). The fine-history maxima are
0.0217143 and 0.0890055. These are favorable necessary bounds for the stated
closed load path, including internal normal-stress cancellation. They
preserve a substantial tensile-energy requirement while avoiding the
earlier single-sleeve restriction. Materials with higher permitted stress,
different signed field sectors, or an explicitly supplied external load path
have their respective accounting.

Pointwise allocation leaves an evolution requirement. For each constituent
the archive records the panel exchange implied by

\[
\Delta Q_i=\Delta E_i+
 \overline{P_{z,i}}\,\Delta\ln\lambda_z+
 \overline{P_{\theta,i}+P_{n,i}}\,\Delta\ln\lambda_\perp,
\]

where \(P_i\) is the volume-integrated pressure and the bars denote the
trapezoidal panel average. These exchanges sum to the required exchange of
the whole allocated group. Their individual positive receipts can include
internal transfers; their sum is a component-activity diagnostic. A physical
state law and reciprocal interactions must supply the recorded histories.
The calculation grants pointwise changes of component allocation, whose
realization includes material strain, flux control and preparation.

Similarly, integrated normal cancellation and hoop matching specify the
load target for a finite construction. Spatial Maxwell equations, boundary
tractions, the ends of transverse sheets, current returns, bend reactions,
thermal interfaces and coupled perturbations remain explicit physical
requirements. The existing 1% magnetic gap and retained affine geometry
must accommodate that construction or receive a separately evaluated
geometric revision. The present result establishes an ensemble allocation
worth constructing before changing the underlying phenomenological families.

Verification covers 1,975 independent ensemble linear programs, including
the weakest samples and seeded points throughout each history, plus the
restricted-class and orientation controls. Their energy reserves agree with
the analytic allocation within \(1.2\times10^{-15}\). Full tensor
reconstruction is accurate to \(4.2\times10^{-17}\); separate boundary load
checks reach \(8.7\times10^{-19}\); and component exchange sums agree within
\(1.4\times10^{-15}\). The new and related test suites pass 49 tests.

The implementation is
[containment_ensemble.py](../toolkit/adm_harness_cli/adm_harness/containment_ensemble.py),
with a [four-worker audit](../toolkit/adm_harness_cli/scripts/audit_containment_ensemble.py)
and [independent tests](../toolkit/adm_harness_cli/tests/test_containment_ensemble.py).
The [summary](data/containment_ensemble/summary.json), state archives, and
[manifest](data/containment_ensemble/manifest.json) retain all component
energies, boundary assignments, required exchanges, input hashes and
execution sources. Reproduction from the repository root uses a fresh
output directory:

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_containment_ensemble.py \
  --workers 4 --output /tmp/containment_ensemble_replay
```
