# Magnetic load balancing for the cold reservoir

Test date: 16 September 2026.

A slender closed magnetic loop admits the prescribed cold-bank heat receipts
within the sampled rail tensor budget, with compression work, return fields,
and current-carrier energy included. Its straight-section containment requires
an unusually strong material. In the fixed-energy sleeve comparison, the
minimum allowable stress divided by total proper energy density is 0.7767 at
the first location and 0.9746 at the second. These values use favorable sharing
of the already counted phase field and freely adjustable sleeve axial stress.
Bend supports and a material constitutive law remain to be supplied.

The result identifies a conditional tensor allocation and a severe mechanical
requirement. The tested loop supplies no completed thermal-storage device.
The investigation follows the
[storage-containment literature review](STORAGE_CONTAINMENT_LITERATURE_REVIEW.md)
and retains the connected, evolving architecture of the
[composite capacitor comparison](COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md).
Its mechanical conclusions concern this specified loop and sleeve family.

## Geometry and retained obligations

Each capsule-shaped flux tube has two straight legs of initial length \(L\)
and two semicircular bends of radius \(a\). An interacting ultrarelativistic
plasma occupies the complete tube, including its return leg and bends, with
\(p=E/(3V)\). The model presumes sufficient coupling between radiation and
charged matter; opacity and finite-temperature composition require a separate
material calculation.

The registered geometry carries the tube through the local deformation
\(F=\operatorname{diag}(\lambda_r,\lambda_t,\lambda_t)\), where
\(\lambda_r=\ell/\ell_0\), \(\lambda_t=R/R_0\), and
\(J=\det F=D/D_0\). The magnetic field follows the solenoidal affine form
\(B=F B_0/J\), with a controlled common amplitude. Opposite tilts and an
azimuthal ensemble cancel the averaged mixed stresses. The selected loop has
\(a/L=0.01\), radial straight legs, tube radius \(0.1a\), and a 10% volume
fill fraction. Its full radial span occupies half the registered cell width.

The field is sized so \(p/(B^2/2)\leq1\) everywhere along the loop, in
\(c=\mu_0=1\) units. The complete magnetic energy includes both straight
legs and both bends. With \(\delta=\pi a/L\), initial pitch \(\theta\), and
\(w_r=(\cos^2\theta+\delta/2)/(1+\delta)\), the integrated components are

\[
U_r=\frac{E}{3}\frac{w_r\lambda_r^2}
 {\min(\lambda_r^2,\lambda_t^2)},\qquad
U_t=\frac{E}{3}\frac{(1-w_r)\lambda_t^2}
 {\min(\lambda_r^2,\lambda_t^2)}.
\]

Their diagonal tensor is \((U_r+U_t,U_t-U_r,U_r)/D\). Magnetic pressure
matching alone leaves the tube's mechanical boundary unresolved. For the
assumed zero exterior loop field, the current-bearing sidewall experiences
outward pressure \(p+B^2/2\).

The hot receiver, fixed phase tensor, fluid, photon histories, guide
requirement, and interface duties retain their archived values. The cold
receiver's assigned enclosure credit, \(\max_t E_{c,\mathrm{old}}/3\), is
released; the unused remainder of the original enclosure rating stays counted.
This credit comes from the repository's existing three-dimensional trace
allowance. The spherical thin-wall benchmark in the literature has its own
geometry and coefficient.

The remaining radial-field, photon, membrane, and pressureless components can
repartition to carry the new loads. Up to half the phase energy density is
available as already counted radial magnetic field. Field overlap with that
component is granted at the averaged tensor level. A spatial realization of
the shared phase and loop fields is an additional requirement. Consequently,
the permitted sleeve energy is measured against the reallocated composite
tensor, beyond the earlier comparison that added material to a fixed backing.

## Heat, currents, and sleeve accounting

The original positive cold heat receipts are retained panel by panel. With
constant receipt rate inside each panel, the radiation first law gives

\[
d(E D^{1/3})=D^{1/3}\,dQ.
\]

Integrating this relation counts the energy supplied by compression. The
geometric factor is evaluated with independent four- and eight-point Gaussian
quadratures across the registered geometry knots. The entropy proxy
\(E^{3/4}J^{1/4}\) increases at every sampled step.

Both the surface current \(|K|=|B|\) and the distributed bend current are
included. Oppositely charged, oppositely drifting carriers cancel net charge
and momentum. Each current family keeps a fixed particle rest inventory
\(\sqrt{2}\,\chi\max_t\int|\mathbf j|\,dV\), with
\(\chi=m/|q|\). This construction keeps drift speed at or below
\(1/\sqrt{2}\); the full Lorentz-factor energy and anisotropic kinetic
pressures enter the tensor. Carrier redistribution, host stresses, and the
electric field required by induction remain separate requirements.

The numerical \(\chi\) uses the same normalized electromagnetic stress units
as the archive. It has no assigned particle species or SI conversion. The
tested values, \(2.54415\times10^{-8}\) and \(1.20001\times10^{-8}\), are
half the respective joint current-coefficient limits: the allocation must
pass both with and without a unit-strength straight sleeve. They define
controlled comparisons at the two locations, within that additional
restriction.

For both straight legs, the transverse virial balance requires hoop energy
\(H_{\mathrm{int}}=2(p+B^2/2)V_{\mathrm{straight}}\). Let
\(k\) denote allowable stress divided by total proper energy density. The
sleeve requires \(E_s\geq H_{\mathrm{int}}/k\), together with
\(|P_{s,\parallel}|\leq k E_s\). The hoop contribution and an independently
adjustable axial stress are inserted into all three residual tensor
inequalities. The two bend sleeves, junction reactions, and finite-thickness
corrections are omitted favorably.

The main comparison keeps one sleeve energy \(M\) per material label across
the whole history, so its density is \(M/D\). Eliminating the free axial
stress gives an exact common interval for \(M\). This is a fixed-energy
comparison: mechanical exchange is needed to hold \(M\) constant. A passive
elastic sleeve would require its own evolving energy and stress law. The
reported threshold optimizes the permitted inventory for each \(k\); the
retained example allocation uses \(k=1\).

## Measured results

The fine histories sample 32 radial labels at each location and respectively
4,113 and 2,057 times. Energies below are per material label in the archived
normalization; ranges run across labels.

| Quantity | First location, near \(x=-2\) | Second location, near \(x=-1.975\) |
| --- | ---: | ---: |
| Final reference cold energy | 0.09799–0.11462 | 0.08926–0.10894 |
| Final cold energy with compression | 0.13039–0.14786 | 0.11797–0.15008 |
| Maximum compression addition | 0.03380 | 0.04114 |
| Final complete-loop magnetic energy | 0.05123–0.05811 | 0.04754–0.06051 |
| Counted current-carrier rest inventory | 0.01464–0.01557 | 0.00599–0.00674 |
| Selected fixed straight-sleeve energy, \(k=1\) | 0.25626–0.27751 | 0.15473–0.19669 |
| Minimum sleeve \(k\), zero carrier cost | 0.73860 | 0.95050 |
| Minimum sleeve \(k\), counted carriers | **0.77668** | **0.97462** |
| Minimum remaining density margin, selected \(k=1\) allocation | \(3.8126\times10^{-4}\) | \(7.5829\times10^{-5}\) |

At \(k=0.5\), every label fails the common-inventory sleeve comparison at
both locations. At \(k=0.9\), the first location passes and the second has
failing labels. A \(k=0.99\) sleeve passes both necessary comparisons. The
unit-strength example also uses substantial axial compression: the largest
axial pressure divided by sleeve energy density is about 0.905 and 0.987.
Its supporting material therefore needs both the stated hoop response and a
very large axial load capacity. No material law has been identified for these
requirements.

The geometric sweep optimizes one common initial pitch across every sample
for each aspect ratio. At the second location, the shared-field comparison
passes for \(a/L=0.005,0.01,0.025\) before carrier and sleeve costs. It fails
at \(0.05,0.1,0.2\), with minimum possible density shortfalls of
\(0.001287\), \(0.005050\), and \(0.010398\). Compression makes the
transverse bend field expensive. The first location passes this preliminary
field comparison at all six tested aspect ratios. The sleeve results above
apply specifically to the selected \(a/L=0.01\) radial construction.

Unshared phase-field controls also admit a preliminary field-only tensor at
\(a/L=0.01\), at optimized pitches of about 38.49° and 10.18°. Their material
closure is outside the selected shared-field sleeve result. Fixed-energy hot
and combined hot/cold replacement controls fail their preliminary tensor
comparison at this aspect ratio, which favors investigating the cold bank
first within this family.

The controlled field needs a complete-loop electrical transfer. Integrating
\(dU_B=\delta W_B+\delta W_{\mathrm{electrical}}\) gives input of
0.07934–0.08677 at the first location and 0.07179–0.09598 at the second.
These are full-loop transfers; assigning the portion belonging to the
already counted phase field to existing ports is a separate ledger task.
Holding the selected sleeve energy fixed requires input of
0.00120–0.00133 and 0.00216–0.00404, while exporting mechanical work of
0.03214–0.03911 and 0.02474–0.05509. The changed transfer network still needs
an explicit routing and replay.

Compression also changes the caloric comparison. Write the effective laws
as \(T_{\mathrm{old}}^4=b_{\mathrm{old}}C\) and
\(T_{\mathrm{new}}^4=b_{\mathrm{new}}E/J\), with the initial physical
volume absorbed into \(b\). Preserving or lowering every sampled reference
cold temperature requires an effective coefficient ratio
\(b_{\mathrm{new}}/b_{\mathrm{old}}\leq0.20469\) or \(0.18539\).
That adjustment changes the physical packing or material normalization.
The present calculations supply a mechanical and energy screen; opacity,
temperature normalization, contact exchange, and release remain material
design requirements.

## Verification and retained evidence

Four independent jobs used four workers, covering both locations at two
spatial/time resolutions. The original full-tensor shortfall reconstructed
exactly. The fine-hierarchy sleeve thresholds changed from 0.776569 to
0.776677 and from 0.974104 to 0.974621. This agreement supports the sampled
conclusion; a continuous-time bound remains open.

Increasing the current quadrature from order 32 to 64 changed its tensor by
at most \(1.36\times10^{-7}\) relative to its maximum magnitude, and the
admitted current coefficient by at most \(2.43\times10^{-7}\) relatively.
Radiation quadratures agreed within \(5.56\times10^{-17}\). The retained
component decomposition reconstructed the residual tensor within
\(4.17\times10^{-17}\). The focused suite passed all 45 tests, including
independent linear-program comparisons of the component cone, common pitch,
straight sleeve, and common sleeve-inventory interval, plus analytic heat,
flux, current, and work controls.

The [execution manifest](data/magnetic_load_balance/manifest.json) records
authenticated input hashes, inherited historical-source checks, runtime
source hashes, execution source snapshots, and output hashes. The
[combined summary](data/magnetic_load_balance/summary.json) and four state
archives retain the parameter sweep and selected allocations. Computation is
implemented in
[magnetic_load_balance.py](../toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py),
with its
[runner](../toolkit/adm_harness_cli/scripts/evaluate_magnetic_load_balance.py)
and [tests](../toolkit/adm_harness_cli/tests/test_magnetic_load_balance.py).

Reproduction from the repository root uses a fresh output directory:

```bash
PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/evaluate_magnetic_load_balance.py \
  --output-name magnetic_load_balance_reproduction --workers 4 --current-order 32

PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  pytest -q toolkit/adm_harness_cli/tests/test_magnetic_load_balance.py \
  toolkit/adm_harness_cli/tests/test_field_membrane_support.py \
  toolkit/adm_harness_cli/tests/test_virtual_cell_material_bank.py \
  toolkit/adm_harness_cli/tests/test_virtual_cell_thermal_replay.py
```

The useful continuation is a spatial field-and-support construction that
reduces the required material stress fraction while supplying the bend
reactions. It must include the phase-field placement, current hosts, induction
field, and electrical and mechanical ports. That calculation can determine
whether shared rail loads turn the conditional allocation into a material
advantage. The current technical disclosure remains at its established
design scope.

The subsequent [exterior-jacket comparison](MAGNETIC_GEOMETRY_COMPARISON.md)
adds the mechanical hoop reaction of the circulating carriers to both
geometries. Its corresponding original-loop thresholds are 0.8115 and 0.9952.
A shared jacket geometry lowers them to 0.8065 and 0.6542, with the separate
boundary inventories counted and bend mechanical equilibrium still open.
