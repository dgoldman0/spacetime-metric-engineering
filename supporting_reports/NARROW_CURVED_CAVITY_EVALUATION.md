# Narrow cavities between finite curved material layers

Date: 9 September 2026.

## Registered source question

This bounded evaluation tests whether a smaller proper gap provides useful
additional opening stress between two finite, smooth material layers. The
standing backbone, angular material and transport keep their separate roles.
The first comparison grants their additional radial-null load the optimistic
value zero. A positive interaction contribution that exceeds the specified
mirrors' own radial-null stress is required before assigning new support loads.

The [earlier continuum comparison](RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md)
already bounds the energy of a planar cavity held by ordinary axial struts.
That energy result and the radius/lapse-weighted rail opening are different
diagnostics. The present test uses the latter and counts the finite mirrors
before choosing struts, hoop support or exchange with the backbone.

## Material and quantum model

The quantum field is one real, minimally coupled scalar in its static vacuum.
Two real canonical material fields provide a positive portal mass

\[
V=g(\chi_1^2+\chi_2^2),\qquad g>0.
\]

Their self-potentials may be nonnegative; the explicit stress comparison uses
\(U_i=\chi_i^4/4\). In proper distance, each finite layer has profile

\[
\chi_i(l)=v\,b((l-l_i)/d),\qquad
b(u)=\begin{cases}\exp[-u^2/(1-u^2)],&|u|<1,\\0,&|u|\geq1.\end{cases}
\]

The inner faces are separated by an empty gap \(a\); each layer has thickness
\(2d\). Their centers are \(l_i=l_c\pm(a/2+d)\). These prescribed smooth
profiles define optical and canonical material tensors. Equilibrium would
add a specified holding sector and the quantum force. The material fields
already contribute \(H_\chi=\sum_i\chi_i'^2\geq0\), independently of their
self-potentials. The gravitational conversion remains
\(\eta=2.4127904527582454\times10^{-5}\).

Disjoint support makes the interaction effective action
\(\Gamma_{12}-\Gamma_1-\Gamma_2+\Gamma_0\) ultraviolet finite. Local bulk and
material counterterms cancel in this combination. The absolute vacuum of
each isolated layer remains a separate contribution. The interaction tensor
includes its change inside both layers as well as in the gap; it supplies the
new enhancement attributable to their proximity.

## Separation, optical strength and counted opening

Write \(s=d/a\) and \(q=g v^2a^2\). The first planar screen registers
81 logarithmic peak strengths \(10^{-4}\leq q\leq10^4\), and
\(s=0.05,0.1,0.2,0.5,1,2\). Portal values \(g=1,4,10\) give three material
costs for each optical profile. The final value is an exploratory stronger
coupling. Any inferred larger coupling is a diagnostic threshold whose
quantum corrections require a separate calculation.

For finite-layer reflection magnitudes \(r_i(\kappa)\), the planar interaction
energy and attractive traction per area follow the scattering expression

\[
E_I=\frac1{4\pi^2}\int_0^\infty\kappa^2
\log(1-r_1r_2e^{-2\kappa a})\,d\kappa,
\qquad F=\frac1{2\pi^2}\int_0^\infty
\frac{\kappa^3r_1r_2e^{-2\kappa a}}{1-r_1r_2e^{-2\kappa a}}\,d\kappa.
\]

Scaling the proper normal metric while holding the scalar fields fixed gives
the complete interaction radial pressure, including its layer contribution.
With \(e=-a^3E_I\), its helpful integrated radial-null coefficient is
\(h_I=4e-2q\partial_qe\). The mirrors' opposing coefficient is
\(h_\chi=2qI/(gs)\), where \(I=\int_{-1}^1[b'(u)]^2du\).
Both scale as \(\eta/a^3\) when optical strength and relative thickness are
preserved. The implied crossing coupling is \(g_*=2qI/(s h_I)\) when
\(h_I>0\).

The selected finite profile is then evaluated on the repaired phase-0.745
native rail, with independent spherical harmonics. Registered negative-branch
centers have areal radii 3, 4.2 and 6.8. Proper gaps 0.5, 0.25 and 0.125 test
the scale trend. The selection minimizes the planar crossing coupling over
the registered optical shapes, giving the material a favorable comparison.

The curved interaction energy follows the radial determinant ratio. Its
opening contribution is obtained by a static metric variation

\[
\delta\log A=\epsilon/(A^2R),\qquad
\delta\log B=-\epsilon/(A^2R),\qquad\delta R=0,
\qquad B_I=-\eta\left.\partial_\epsilon E_I\right|_0.
\]

This is \(-4\pi\eta\int(R/A)(\rho_I+p_{r,I})\,dl\). The explicit canonical
mirror integral uses the same weight. Mesh, frequency, angular and metric
variation controls assess the comparisons. Exact slab reflection, ideal
plate energy and pressure, and a direct determinant calculation provide
independent controls.

The initial computation allowance is 900 seconds per run, at most four
workers and 20 MB of retained numerical evidence. Mode sums and scalar
diagnostics are retained; narrative findings are written manually. Failure
to improve the counted opening ends this specified narrow-gap construction.
An uncomputed isolated-layer vacuum contribution retains its own source
question and is independent of the proximity enhancement measured here.
