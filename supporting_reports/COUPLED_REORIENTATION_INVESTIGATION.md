# Coupled support reorientation and construction gates

Date: 9 September 2026.

Restoring the rail's component roles gives a consistent static target
allocation with a separately counted radial backbone, the saved condensate,
independent radial and angular quantum targets, and a pressure-bounded host.
The throat's large radial tension can belong to the backbone and host while
the quantum target supplies a small negative null correction. Across the
retained transition, the quantum and mechanical requirements remain larger.
This distinction separates an improved source allocation from a supplied
field construction.

The calculation follows the
[component cross-reference](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
and uses the same smooth static geometry and relaxed material as the
[allocation audit](COUPLED_SOURCE_ROLE_AUDIT.md). The active current,
startup, and reservoir evolution remain separate duties in the joint system.

## A counted standing allocation

The source comparison is

\[
T_{\rm demanded}=T_{S_0}+T_{\rm condensate}+T_Q+T_{\rm host}.
\]

All tensors use geometric source units, with the saved material multiplied
by \(\eta v^4\). The registered values are
\(\eta=2.4127904528\times10^{-5}\), \(v=12/6.8\), and
\(\omega=0.8528237074\). The material tensor already includes its scalar,
Higgs, and gauge contributions.

The additional backbone has

\[
(\rho,p_r,p_t)_{S_0}=\frac{\Phi(x)}{R^2}(1,-1,0),\qquad
\Phi(x)=\frac{f}{8\pi}w(x).
\]

The window equals one through \(|x|=1\), tapers with a quintic smoothstep,
and reaches zero at \(|x|=3\). The tested throat-tension shares are
\(f=0,0.5,0.95\). These are declared allocation comparisons. The finite
backbone requires the explicit static radial force density

\[
(\nabla_a T_{S_0}^{a\hat l})=-\frac{\Phi'(l)}{R^2}.
\]

The opposing force belongs to its coupled host or termination material. The
area-weighted integral on either half equals \(\mp f/2\), with the sign
following the increasing proper-distance direction. The 95% case reaches
a local force magnitude of \(1.58607\times10^{-3}\). This is the force
required by the parameterized backbone; a material interaction law still
has to supply it.

The quantum comparison retains both ideal planar electromagnetic orientations,

\[
(\rho,p_r,p_t)_Q=(-C_r-2C_t,-3C_r+2C_t,C_r-2C_t).
\]

Thus its radial and angular null stresses are \(-4C_r\) and \(-4C_t\).
The existing exact two-variable optimization minimizes \(C_r+2C_t\) while
requiring \(\rho_{\rm host}\geq |p_{r,\rm host}|,|p_{t,\rm host}|\).
These weights describe a target tensor. Physical intersecting cavities,
material boundaries, and their absolute quantum state require a common
field calculation.

At the throat, the 95% allocation gives:

| Contribution | Energy density | Radial pressure | Angular pressure |
| --- | ---: | ---: | ---: |
| Demanded total | 0.00956354 | −0.00956491 | 0.0000326418 |
| Backbone | 0.00908666 | −0.00908666 | 0 |
| Saved condensate | 0.0000585000 | −0.0000584981 | −0.0000585000 |
| Ideal quantum target | −0.000000341474 | −0.00000102442 | 0.000000341474 |
| Fitted host | 0.000418723 | −0.000418723 | 0.0000908004 |

The backbone carries 95% of the demanded throat tension, and the saved material
carries 0.611591%. The remaining host carries most of the balance. The ideal
radial quantum weight is \(3.4147434\times10^{-7}\), with zero angular weight
at this point. Its negative energy and tension differ substantially from the
large positive-density remainder assigned to the single scalar in the earlier
restricted allocation.

The finite-volume proper energies below use
\(4\pi\int_{x=-40}^{40}R^2\rho\,dl\). They are geometric source integrals;
the measure differs from ADM mass and from the earlier reset annulus.

| Backbone throat share | Backbone | Condensate | Ideal quantum target | Fitted host |
| --- | ---: | ---: | ---: | ---: |
| 0% | 0 | 2.69006 | −23.38925 | 137.25975 |
| 50% | 58.40579 | 2.69006 | −25.13640 | 80.60112 |
| 95% | 110.97100 | 2.69006 | −27.78549 | 30.68499 |

Each row sums to the demanded 116.56057. Increasing this backbone allocation
reduces the host's bulk energy requirement while increasing the optimized
quantum magnitude by about 18.8% across the interval. The same added
positive-energy radial tension supplies zero radial null stress and adds
positive angular null stress. Its role in the throat and its effect on the
transition therefore differ.

## The angular response adds a distinct cost

Requiring only nonnegative host null stresses gives the weaker bounds

\[
C_r\geq\max[0,-H_{r,\rm remainder}/4],\qquad
C_t\geq\max[0,-H_{t,\rm remainder}/4].
\]

For the 95% allocation, their minimum integrated quantum magnitude is 2.88833,
compared with 27.78549 when the host also obeys the dominant energy condition.
The weaker comparison relaxes the host's energy and pressure constraints;
it supplies a lower bound on the quantum target, with material realization
left open.

This difference identifies an additional constitutive burden. At \(x=0.5\),
the geometry asks for \(p_t\simeq0.01889\) with
\(\rho\simeq0.00777\). A host whose pressure magnitude is bounded by its
energy must carry substantial energy to produce that angular pressure. The
quantum target then compensates the added energy and radial null stress.
Near \(x=\pm2.5\), the full optimized host reaches
\(p_r=p_t=\rho\simeq0.055\), while the quantum radial weight is about 0.0324.
Independent angular response therefore includes an energy cost as well as
an adjustable pressure channel.

For scale comparison, the flat ideal electromagnetic relation
\(C=\eta\pi^2/(720d^4)\) maps the radial targets to
\(d\simeq0.992\) at the throat and \(d\simeq0.0565\) near
\(|x|=2.5\), in the existing rail length units. The angular comparison gap
near the latter location is about 0.0672. These are inverse stress scales
under an ideal planar formula. They leave finite material thickness, curved
space stress, and holder energy to be supplied.

## A mechanical realization gate

The previously established
[independently held planar-cell bound](RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md)
applies when each cell carries its own ordinary struts: holder energy is at
least \(3(C_r+2C_t)\), and the complete cell energy is at least
\(2(C_r+2C_t)\). Even allowing all ordinary energy in the allocation to
serve as holding energy leaves a positive deficit in the retained transition.
The maximum local deficit in the 95% case is 0.139277.

Consequently the algebraic match cannot be implemented by homogenizing those
complete, independently supported planar cells. A curved extended field with
spatially separated supports has a different mechanical balance. Its signed
stress and its support tensor would have to be calculated together. This gate
retains that scope and the earlier finite-condensate result.

## Allocation evidence and verification

The [allocation runner](../toolkit/adm_harness_cli/scripts/reorient_coupled_support.py)
uses four available workers for three independent backbone shares. It checks
the saved material hash, reconstructs each full tensor, and retains the actual
backbone force. The source reconstruction error is at most
\(1.05\times10^{-17}\), with host energy-condition margins at roundoff.
The area-weighted force check agrees within \(1.49\times10^{-9}\).
The 80,001/160,001-point proper-energy comparisons change by at most
\(3.30\times10^{-6}\). Six existing vacuum-allocation tests pass, including
independent linear-program comparisons.

The numerical record comprises
[allocation.json](data/coupled_reorientation/allocation/allocation.json) and
[witnesses.csv](data/coupled_reorientation/allocation/witnesses.csv).
This report is written manually.
