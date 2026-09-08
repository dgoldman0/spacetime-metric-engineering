# Coupled Reset Source Attempt

Date: 8 September 2026.

## Registered candidate and stopping sequence

This attempt tests one explicit source prescription inspired by Le's separation
of supporting matter and momentum transfer. It replaces part of the standing
radial string support with a tangential material body and two directed null
streams. The source enters radial Einstein constraints, allowing the mass,
radial metric, and lapse to respond. The inner mass is inherited from the rail;
the outer mass is free to change.

The local domain is the negative-side endpoint annulus
\(\ell\in[-6,-0.5]\). Its inner boundary excludes the areal-radius minimum,
where a single polar-areal chart would fail. The intended reset begins at the
release onset \(s=0.745\), passes through release, receiver fade, and geometry
decompression, and approaches the retained static endpoint at \(s=15\).

Three necessary conditions precede spacetime evolution:

1. The complete prescribed source must be free of Type IV stress throughout
   the handoff. Regular null transfer sectors are assessed by their explicit
   null structure; their individual Type II character is permitted.
2. The radial Einstein equations must admit a positive-lapse metric with
   timelike stationary material observers throughout the annulus.
3. On any surviving time-dependent family, the momentum and angular Einstein
   equations, source exchanges, and matching to the retained rail must agree.

A refinement-stable failure of either of the first two conditions stops this
candidate before constructing an inconsistent time evolution. The attempt has
one material-density ratio, one tangential-pressure ratio, and one handoff
profile. These are specified below and receive no outcome-driven tuning.

## Source prescription

At each phase the combined C2 rail candidate supplies a matched static control
\(T_b=(E_b,P_b,0,P_{tb})\) and the active demanded current. The former is an
explicit effective background prescription for this trial; a microscopic
realization of its signed stresses remains an independent project requirement.
The latter calibrates the requested transfer waveform in the new source's
orthonormal frame. Agreement with the new geometric demand is a subsequent
equation, rather than an assumed frame identity.

Write \(r=\sqrt{\gamma_\Omega}\). A C2 window \(W\) is one across the central
annulus and reaches zero through the first and last 3% of its areal extent.
The released radial string density is
\[
B=\frac{0.039783\,W}{r^2},
\]
using the existing body-only constant-flux fit. Removing its radial pair
changes the retained infrastructure to
\((E_b-B,P_b+B,0,P_{tb})\). This grants the candidate an explicit energy
reassignment from radial support.

For the outward current command \(J=-Wj_{\ell,\mathrm{reference}}\), define
\[
F=\sqrt{J^2+\epsilon^2W^2},\qquad
\epsilon=0.01\max_\ell|j_{\ell,\mathrm{reference}}|,
\qquad \mu_\pm=\tfrac12(F\pm J).
\]
The two nonnegative null streams carry
\((E,P_r,J,P_t)=(F,F,J,0)\) in total. The small counterstream reserve makes
the signed-current handoff smooth within each phase.

The tangential material body has density \(F\), radial pressure zero, and
\(P_t=F/4\). Its state is partitioned between endpoint and outer reservoir by
one fixed C2 weight. This partition adds no tensor and double-counts no stored
energy. The complete prescribed source is
\[
\boxed{(E,P_r,J,P_t)
=(E_b-B+2F,\;P_b+B+F,\;J,\;P_{tb}+F/4).}
\]
The ordinary material and both transfer streams individually satisfy their
algebraic dominant-energy bounds. The signed infrastructure background makes
classification of the complete sum essential.

## Radial Einstein response

The local material body is stationary in the areal frame,
\[
ds^2=-\alpha^2dt^2+\frac{dr^2}{f}+r^2d\Omega^2,
\qquad f=1-2m/r.
\]
For the matched static background,
\(m_b=\tfrac r2[1-(\partial_\ell r)^2/\gamma_{\ell\ell}]\).
The Hamiltonian equation fixes the changed mass directly:
\[
m=m_b+4\pi\int_{r_{\rm in}}^r(2F-B)\,\bar r^2\,d\bar r.
\]
Thus the radial metric responds to both released string energy and the full
energy cost of the material/transfer pair. A surviving radial domain then
determines its lapse from
\[
\partial_r\log\alpha
=\frac{m+4\pi r^3P_r}{r(r-2m)},
\]
with the outer reference lapse as its clock anchor. The momentum equation
requires
\(\partial_t m=-4\pi r^2\alpha\sqrt f\,J\).
It supplies a compatibility condition for a time history; the radial solves
alone provide no time-evolution certificate.

The criterion \(f>0\) is required by the stationary material frame of this
candidate. A violation excludes this ansatz and its matching prescription;
more general moving-matter geometries remain a different construction.

## Numerical design

The nine sampled phases cover release onset and completion, the reference
worst-DEC phase, receiver fade onset and completion, reset decompression,
completion of the geometry command, and late controls at \(s=5,15\).
Each phase uses 129, 257, and 513 uniformly spaced annular points, augmented
by six fixed locations from the preceding boundary diagnostics. The geometric
derivative steps are \(h_s=h_\ell=0.00125,0.000625,0.0003125\), respectively.
Each location receives fresh active and matched-static Einstein tensors.

The complete prescribed source receives a full mixed-tensor eigensystem
certificate at every sample. Component matrices are retained separately, and
the radial mass integral is evaluated on each refinement grid. A matched-static
lapse reconstruction supplies a quadrature control. The calculation uses four
independent worker processes with one BLAS thread per worker.

The implementation has passed the 285-test harness suite. An integration
smoke run has exercised reference extraction, component assembly, radial
constraints, eigensystem storage, and the diagnostic figure. The full candidate
run follows this registered design.

## Source references

- [Stage 2 radial string crosswalk](STAGE2_RADIAL_STRING_CLOUD_ENDPOINT_CROSSWALK.md)
  supplies the body-only string flux used in the energy reassignment.
- [Bounded metric repair](LE_BOUNDED_METRIC_REPAIR.md) supplies the combined
  C2 background and the fixed radial witness locations.
- Le, [On the boundary cost of source-consistent warp shells](https://arxiv.org/html/2605.25417v2),
  motivates checking the complete source alongside its geometric realization.
- Le, [Steering a warp drive without exotic matter](https://arxiv.org/html/2606.22531),
  supplies the constructive separation into tangential support and explicit
  transfer channels. The annular source prescription above is specific to this
  rail trial.
