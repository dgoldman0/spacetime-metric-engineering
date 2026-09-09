# Matched Wall Masses and the Remaining Support Cost

Date: 9 September 2026.

## Registered questions

The [moving-boundary investigation](QUANTUM_MOVING_BOUNDARY_ATTEMPT.md)
produces negative gap radial enthalpy with positive primitive kinetic
terms. Its one-wall field dressing and local energy depend on the cutoff.
This follow-up separates the physical wall masses from the finite
interaction energy and tests the holding contribution across an extended
family of optical responses. A second comparison uses the retained rail
slice to determine what the complete-cell sign test implies for spatially
extended boundary placement.

The scalar interaction is specified by two disjoint sheets,
\(V=\lambda_1\delta(z)+\lambda_2\delta(z-a)\), with positive couplings.
This thin-sheet specialization changes the preceding Gaussian shape;
the empty gap and its continuum scattering problem are exact. Each
isolated sheet has a specified measured mass per area \(M_i\). Its
isolated field self-energy is included in \(M_i\). The finite binding
energy and its boundary contribution remain in the two-sheet calculation.
The optical couplings and measured masses remain fixed when differentiating
the separation. A microscopic material that realizes both parameters
would supply additional constitutive input.

The scattering expression follows equation 3.10 of
[Milton and Wagner](https://arxiv.org/abs/0712.3811). The isolated-mass
prescription and the distinction between bulk and surface energies follow
equations 1.23 and 4.4–4.5 of
[Milton, Shajesh, Fulling, and Parashar](https://arxiv.org/abs/1401.0784).
The canonical stress uses \(\xi=0\), as in the preceding model. A
\(\xi=1/6\) control explicitly changes the scalar's curvature coupling;
its local tensor and surface partition are recorded separately.

The response grid combines 81 equal-coupling pairs over
\(\lambda_i a=10^{-4}\) through \(10^4\), an independent nine-by-nine
decade grid of unequal pairs, and the preceding nominal coupling 8.
Duplicate pairs are removed. Three logarithmic quadratures use 128, 256,
and 512 nodes. An independent adaptive integral checks the finest values.
Interior stress profiles for couplings 0.01, 1, 8, and 100 retain isolated
sheet polarization tails and avoid the singular sheet locations.

The static assembly screen includes measured wall masses 0.25 and 1 per
wall, together with an optimistic zero-wall-mass holding bound. The
released zero-energy mass threshold is recorded as an accounting
condition. This calculation tests initial source requirements and static
holding cost. The preceding field-and-wall trajectories remain a separate
finite-cutoff dynamical result.

For the second comparison, the frozen initial rail profile is sampled at
513, 1,025, and 2,049 points. Coordinate mass, proper energy, lapse-weighted
slice energy, radial enthalpy, and the locations of positive energy are
retained. The lapse-weighted integral describes this slice; the evolving
rail has no assumed globally conserved Killing energy.

Four independent worker processes, single-thread numerical libraries,
1,536 MiB address space per worker, a 300-second main allowance, and an
8 MB evidence allowance bound these comparisons. All narrative findings
are written manually after the computations and independent checks.

## Finite interaction and the analytic holding bound

For imaginary wave number \(\kappa\), the reflection magnitudes are
\(r_i=\lambda_i/(2\kappa+\lambda_i)\). With
\(t=r_1r_2e^{-2\kappa a}\),
\[
E_C=\frac{1}{4\pi^2}\int_0^\infty
\kappa^2\log(1-t)\,d\kappa,
\qquad
P=-\frac{1}{2\pi^2}\int_0^\infty
\frac{\kappa^3t}{1-t}\,d\kappa.
\]
The gap makes both integrals ultraviolet finite. Let \(e=-E_C>0\),
\(f=-P>0\), and let \(D\) denote the derivative of \(e\) when both
dimensionless optical couplings increase by the same logarithmic amount.
Dimensional scaling gives \(af+D=3e\).

An independent pointwise inequality bounds \(D\). Its integrand relative
to the logarithm is \((2-r_1-r_2)t/(1-t)\). Since
\(r_1+r_2\geq2\sqrt{r_1r_2}\geq2\sqrt t\),
\[
0<\frac{(2-r_1-r_2)t}{1-t}
\leq\frac{2t}{1+\sqrt t}
<2[-\log(1-t)].
\]
Consequently \(0<D<2e\) and \(1<af/e<3\) for finite positive
couplings. An ordinary axial holding structure satisfying the dominant
energy condition has energy per area at least \(af\): the material's
energy density is at least the magnitude of its axial stress, integrated
over the gap. Therefore
\[
E_\mathrm{held}\geq M_1+M_2+af-e
=M_1+M_2+(af/e-1)e>0.
\]
This bound applies to the specified static planar family at every positive
optical coupling, including unequal sheets. The positive assembly result
survives the isolated-mass prescription. Its assumptions overlap the
equilibrium support conditions examined by
[Costa and Matsas](https://arxiv.org/abs/2112.08881); the inequality here is
derived for the finite-transparency scalar sheets above.

The finite surface contribution is also retained. For curvature coupling
\(\xi\), it is \(E_\mathrm{surface}=-(1-4\xi)D\), while the bulk
interaction energy across the gap and exterior is
\(aP/3-4(\xi-1/6)D\). Their sum equals \(E_C\).
The canonical bulk profile includes the finite vacuum polarization from
each isolated sheet at every interior point. Absorbing a sheet's total
self-energy into its measured mass preserves those exterior tails.
