# Connected pressure paths for distributed electrothermal storage

The short confined-fluid couplings in the [graded-storage study](GRADED_ELECTROTHERMAL_ASSEMBLY.md)
leave loaded pressure ends and a thermal exchange. This investigation connects
the pressure-bearing material across the tested storage patch and includes its
thermal pressure in the coupled conservation equations. The calculation keeps
the active geometry, fitted endpoint heat/current tensor, and scheduled protected
packet. It addresses the late patch, from preparation at s=0 to carrying-flow
fade at s=1.285, with a reset extension conditional on the first result.

The standing support and receiver/reset plant already have mechanical and
thermal interfaces in component cards 002, 005, and 006. Their physical load
capacity remains an explicit construction requirement. Consequently, the first
comparison records the two end tractions. A stronger control balances the
fluid and field radial pressures at both ends, removing their net traction
from the patch's external mechanical ports.

## Registered construction

The radial electric field retains H=R^4 u_E and stress
(u_E,-u_E,0,u_E). A connected material phase carries conserved rest mass n
and isotropic thermal pressure p, with rest energy density rho=n+3p. This
gamma-law model represents a pressure-bearing thermal constituent and cold
inertia at a common velocity. It supplies a concrete thermal-pressure response;
an actual mixture requires its own opacity, charge-carrier, and transport laws.
The adiabatic sound speed is c_s^2=4p/[3(n+4p)], bounded by 1/3.

The model follows the usual relativistic ideal-fluid stress construction and
gamma-law thermodynamics; finite charge-current and heat-current dynamics
require additional constitutive equations. Relevant primary frameworks are
[Pandya, Most, and Pretorius](https://arxiv.org/abs/2209.09265) and
[Andersson's charged multifluid construction](https://arxiv.org/abs/1204.2695).
Their existence motivates these constitutive choices; the numerical rail
results below come from the repository's active metric and endpoint tensor.

With prescribed coordinate-fixed material motion,

    v = B beta/alpha, Gamma = (1-v^2)^(-1/2), N_lapse = alpha/Gamma,
    D = Gamma B R^2, N_mass = D n, U = 3D p, lambda = partial_s ln D,

N_mass is conserved on each worldline. The coupled equations are

    U_s + lambda U/3 + (Gamma B/R^2) H_s = S,
    H_x - R^4 p_x - R^2 a_s [N_mass + 4U/3]
        - (4/3)(v R^2/N_lapse) U_s = B R^4 F_endpoint,
    S = -alpha Gamma B R^2 (P_endpoint-v F_endpoint).

These equations include the fluid's compression heating, inertia, pressure
gradient, and the electromagnetic work. Every interior momentum equation is
retained. The field and fluid may exchange force locally along the full path;
their tensor sum supplies the reaction that the previous construction exposed
at three internal contacts. There is no independent adjustable thermal sink
in this first completion test. Net heat exchange is exactly the complementary
exchange with the archived endpoint medium. The receiver/reset export path
remains a distinct possible extension.

The new initial thermal energy first equals the earlier allocated buffer heat.
A preparation control allows extra positive initial heat and optimizes its
profile. Both controls preserve the same rest-mass profile. Field energy stays
positive, decreases passively, and has proper reduced discharge rate at most
one in the principal comparison. The rate is a registered response comparison,
with the unit conversion set by the eventual physical length scale.

The objective minimizes the largest supplied null projection over all null
directions. A secondary energy objective selects among equally good peak
solutions when its bounded solver completes. Exposed-end and balanced-end
variants distinguish interior pressure transmission from external reaction.
Balanced ends require p=u_E; their individual material and electromagnetic
interfaces still require physical charge carriers and containment.

## Bounded decision and verification

The first round compares fixed and adjustable preparation with exposed or
balanced end tractions. A successful low-burden candidate receives separate
space and time refinement, an independent full-tensor divergence audit, and
the remaining-source diagnostic against G/(8 pi). A failed class receives a
bounded relaxation or force-balance witness sufficient to identify its cause.
An unresolved solver result remains a numerical outcome.

The strongest completion would supply positive material/field histories,
finite rates, internal force closure, tolerable quantified end reactions, and
a source burden comparable to the earlier local coupling estimate. A large
pressure-transmission cost or incompatible joint energy history would identify
the limitation of a continuous, co-moving pressure link. The study retains the
separate remaining quantum-source, material stability, earlier preparation,
and full-cycle gates of the rail assembly.

Independent computations run in four processes, each with one BLAS thread.
Tests compare the scalar fluid and field equations to covariant tensor
divergence on a time-dependent metric, check manufactured flat-space pressure
transmission and closed-end force obstruction, and verify compression work.
Reports are written manually at the numerical milestones.

## First round: the cost appears along the connection

The initial four 32-cell cases establish one feasible joint history: extra
thermal preparation with exposed end tractions. It has initial slice energy
68,073.78 and peak supplied null stress 8.73223. Its remaining negative null
requirements are 8.20130 at startup and 8.72294 at fade. The retained initial
heat profile and both balanced-end cases are infeasible in this discretization.
The feasible case's independent tensor residuals are 0.201% for energy and
0.363% for force, measured against the sums of equation-term magnitudes.

A separate extension of the archived short couplings makes the load-path
mechanism explicit. For the rho=3p fluid on a slice with partial_s p=0,

    p_x + 4 Gamma B a_s p = Gamma B F_required.

The minimum positive solution connects all three archived force contacts
through the full patch. Its two end pressures remain measured loads. At
startup it requires peak pressure 221,216.7 and slice energy 30,913,090; at
fade, peak pressure 56.4225 and slice energy 7,015.13. The earlier isolated
pieces at those phases cost 158.34 and 16.69 in slice energy. The pressure
link transmits each contact's load and also supports the intervening fluid.
The integrating factor accumulates that self-weight across the large clock
gradient. The 513-to-1025-point comparison changes pressure by at most
0.0034% and energy by at most 0.0080%.

Thus the earlier small local coupling cost supplies a component estimate;
completing it as a continuous pressure column introduces a substantial new
cost. Joint redistribution of field and thermal energy reduces the raw
column cost, while its first solution still requires much more source stress
than the local construction. The next bounded checks refine that joint
solution and derive the balanced-end force obstruction with the time and
shift terms retained.
