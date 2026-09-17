# Finite electrical leads and current hosts

Finite electrical leads add stored field energy, carrier inertia, charged
electrodes, and support duties to the capacitor work interface. Four local
reconstructions of the hosted transfer histories admit a finite causal
transmission-line model with these quantities counted. The larger allocation
is about **2.413 C** in the first-location cases; the second-location cases
require about **2.045 C**. These allocations include a provisional fixture
energy budget and fit the inherited M19 energy reserve. Their comparison with
M20 exhausts its first fine history reserve. The existing whole-history
budgets are used for an energy projection; the lead construction uses sampled
local histories with frozen macro support.

Charging the largest sampled allocation, 2.41276535 C, uniformly leaves a
first fine M19 minimum reserve of **1.50752×10⁻⁵** in the inherited ledger
units. The corresponding M20 value is **−3.39788×10⁻⁵**. The other three
histories retain positive projected reserves for both inventories.

The construction retains an explicit electrical pump port. Its power includes
the derivative of the new line and source-capacitor energies. The first local
cases require an additional peak near **0.0266 P\***. The added stress trace
and its derivative are archived separately so they can enter a subsequent
coupled support calculation. Fixture evolution, optical-to-electrical
conversion, and the placement of the added tensor remain physical design
requirements.

## Capacitor and complementary-field terminals

The periodic support cell has two complete fixed-area gaps per sheet. For a
sheet span L, pitch a, complete gap d=a−L, and facet force F, the parallel bank
has Cb=2A/d, charge Q=2√(2AF), and voltage V=Q/Cb in normalized units. Its field
energy is Ue=2Fd. The terminal and mechanical powers satisfy

\[
VI=\dot U_e+2F\dot L.
\]

The four terminal branches are the outer-sheet gaps, angular-sheet gaps,
complementary hoop field, and complementary radial field. The gap fields
occupy the existing Maxwell bias D=0.62 C. Their decomposition is
H_e=U_outer/2+U_angular and B_e=U_outer/2. The complementary energies are
2D/3−H_e and D/3−B_e. Two equal tangential capacitor copies represent the hoop
field and one radial copy represents the radial field. Consequently all four
load-bank energies sum to D, while their terminal powers sum to the sheet
mechanical power. Wiring the variable gaps alone would omit the larger
complementary-field work branch.

The selected pad area is one quarter of the squared support span, with
complementary gap 0.01 times that span. Each electrical lead is one support
span long, 0.00265258 cδ, covering a finite charge-spreading length at its
terminals. The coax outer-to-inner radius ratio is e and the inner radius is
0.01 times the lead length. These dimensions specify the circuit screen;
three-dimensional turns, pad fringing, current spreading, and spatial packing
require a completed field and material geometry.

## Finite flight and retained source states

For a vacuum coax with radius ratio β, the normalized geometric capacitance
and inductance per length are Cg=2π/logβ and Lg=logβ/(2π). Each conductor has
a fixed absolute mobile-charge inventory Λ per length. The two conductor
populations contribute Lk=2χ_mobile/Λ and a retained host rest energy
2χ_hostΛ per length. The effective distributed law is

\[
C_g V_t=-I_z,\qquad (L_g+L_k)I_t=-V_z,
\]
\[
\partial_t\!\left({C_gV^2\over2}+{L_gI^2\over2}
                 +{L_kI^2\over2}\right)+\partial_z(VI)=0.
\]

Positive Lk gives a characteristic speed below c. This is a lossless,
low-drift material-line law. The underlying full electromagnetic and carrier
model must supply its penetration fields, dispersion, binding forces, and
loss law. The geometric coax fields provide the leading Maxwell stresses.
The distinction between geometric and kinetic inductance is established in
transmission-line models; it supplies a modeling component, while material
selection still depends on the rail's required state. The underlying sources
are [Haus and Melcher, section 14.2](https://web.mit.edu/6.013_book/www/chapter14/14.2.html)
and [Boaventura et al., IEEE Transactions on Applied Superconductivity 30,
1500507 (2020)](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=928652).

For prescribed terminal waves a=(V+ZI)/2 and b=(V−ZI)/2, a lead with flight
time τ requires source waves a(t+τ) and b(t−τ). The incoming schedule therefore
uses finite preview. Signed current and power permit recovery. Each source
also has a positive fixed capacitor, sized at 1% of the corresponding initial
load capacitance. Its pump current is I_source+Cs V̇_source. Thus the combined
electrical input is

\[
P_{\rm pump}=P_{\rm mechanical}
       +{d\over dt}(W_{\rm leads}+U_{\rm source}).
\]

All intermediate energy remains in the line or charged states. The pump is
an exposed work port whose physical conversion mechanism is still required.
The prepared DC fields retain their energy and charged hosts when terminal
current vanishes.

## Charge and reaction requirements

The carrier screen enforces a 1% charge-imbalance ceiling and a 1% drift-speed
ceiling. Electrode inventories obey the same charge-imbalance limit: both
oppositely charged electrode sets carry finite neutral host inventories.
Counting only the deposited charge would underprice these hosts by a factor
of 100 under this condition. The selected normalized host coefficient is
χ_host=0.0005; the mobile-to-host mass-per-charge ratio uses the electron/proton
ratio as an explicit benchmark. This ratio specifies an inventory conversion,
with the material's binding and transport properties left open.

The leading coax fields are Er=V/(r logβ) and Bφ=I/(2πr). Their local Maxwell
stress components are Trr=uB−uE, Tφφ=uE−uB, and Tzz=uE+uB. The finite host must
carry both radial surfaces, axial end loads, and the current-return loads.
The integrated axial duty includes carrier pressure 2K. The summed
circumferential duty at both cylinders is
2∫|uE′−uB′| dz/logβ. Absolute values are taken locally before integration.

The allocation reserves twice these necessary stress duties for prospective
fixtures. It also reserves source-capacitor fixtures and separators for the
fixed complementary-field capacitors. The original periodic gap tractions
remain assigned to their existing sheet populations. This fixture allowance
is a finite energy reservation; an evolving constitutive law must establish
the actual strain, momentum, work, and tensor. Its stress cancellation is
therefore left uncredited.

The new unbalanced trace exposed by the model is

\[
\Pi_{\rm added}=U_E+U_B+2K+U_{\rm source},\qquad
\dot\Pi_{\rm added}=P_{\rm source}-P_{\rm load}
                         +\dot K+\dot U_{\rm source}.
\]

The stored carrier rest inventory is separate. The fixture trace and fixture
work require the material law and its spatial attachments. Allocating energy
to those fixtures does not determine their tensor.

## Normalization and physical scale

The source chain constructs geometric stresses from Gμν/(8π). The finite
containment audit multiplies the target by D=ell R², with ell=γb. The resulting
capacities already contain the proper-volume density per radial material
label and solid angle. A physical cell requires its chosen radial-label and
solid-angle measure; multiplying by another D would repeat the volume factor.

Under a global metric length scale Lmetric, the existing dimensionless ledger
capacity Ĉ and proper delay δ̂ give

\[
C_J={c^4\over G}L_{\rm metric}\widehat C
                  \Delta\widehat x\,\Delta\Omega,\qquad
\delta_s={L_{\rm metric}\over c}\widehat\delta,
\]
\[
{C_J\over\delta_s}={c^5\over G}{\widehat C\over\widehat\delta}
                  \Delta\widehat x\,\Delta\Omega.
\]

For an already integrated geometric cell energy the measure is one. Global
enlargement alone leaves C_J/δ_s invariant. Consequently the circuit's
normalized host coefficient depends on the chosen cell measure and the
ledger; it is not an independent rail-scale control.

The charge unit is √(ε₀ C_J cδ_s), and
χ=(m/q)c²√(ε₀ cδ_s/C_J). The audit records the cell measure that would give
χ_host=0.0005 for the proton mass-per-charge benchmark, requiring
C_J/δ_s=9.34732×10²¹ W. The implied Δx̂ ΔΩ is 1.74052×10⁻³⁴ in the first
local context and 4.99326×10⁻³⁴ in the second. Those measures must be
reconciled with lead dimensions, electrode area, packing, and the required
material state. Absolute field magnitudes also depend on the selected metric
length scale. These dependencies preserve the distinction between an energy
allocation region and a realized physical material configuration.

## Reproducibility and scope

[The audit evidence](data/finite_electrical_leads/summary.json) links the four
local parent histories and the inherited prepared transfer budgets. Eight
tests independently check terminal charge/work derivatives, sheet
acceleration, finite characteristic energy transport, Maxwell surface loads,
retained carrier inventories, and homothetic normalization. Spatial
quadratures are divided at the reconstructed terminal knots. Two additional
sampling refinements change the added-energy estimate by less than
1.89×10⁻⁶ C and the pump-power peak by less than 4.32×10⁻⁶ P\*. The largest
quadrature energy-theorem residual is 2.35×10⁻¹⁰ P\*. These refinement
comparisons characterize sampled results; continuous extrema remain open.

The archived ideal requests contain current jumps. A finite-inertia host
requires a bandwidth treatment for those jumps. The lead screen uses a C1
reconstruction on a fixed 1/16 δ time grid, giving continuous current with
bounded piecewise acceleration. Its high-frequency tails and its departure
from the original trace are recorded; the peak trace difference is 0.00722 C
in the first context and 0.00983 C in the second. It is a prescribed local reconstruction
whose incorporation into the coupled dynamics remains a separate step.

The uniform energy projection charges the largest sampled local allocation
to every capacity in all four inherited histories. It preserves the inherited
matched zero-work thermal-relay condition. The sampled electrical histories
provide candidate resource requirements; an all-node hardware envelope, the
new coupled pump/trace response, fixture evolution, attenuation and heat, and
finite optical-to-electrical conversion remain open. This milestone completes
the finite electrical state and requirement accounting used for the next
physical design gate.
