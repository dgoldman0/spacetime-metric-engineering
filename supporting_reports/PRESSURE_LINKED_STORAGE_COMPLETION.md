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

## Refinement and the reaction requirement

The 64- and 128-cell refinements, with 128 and 256 time intervals, are all
infeasible at the principal discharge rate. Thus the first coarse history
supplies no converged candidate at that rate. Allowing unrestricted passive
discharge restores a 32-cell history even with the original thermal allocation,
at peak supplied null stress 11.63855 and maximum interval-averaged reduced
discharge rate 290.775. Its initial slice energy is 90,902.04. These results
motivate a final rate control at finer resolution and an optimistic reversible
field-charging control. The latter tests the significance of passive discharge;
its conversion entropy and charge-current laws remain additional requirements.

The balanced-end obstruction has an independent integrated form that retains
the active time dependence. Put q=p-u_E, b=4v/(3N_lapse R^2),
r=-H_s/H, and C=4 Gamma B a_s-b lambda D. The coupled equations give

    q_x + C q + [C-4(ln R)_x+b D r] u_E
        = -B F_endpoint-Gamma B a_s n-b S.

For passive conversion with reduced conductivity at most sigma,
0 <= r <= 2 sigma N_lapse. With W=exp(integral C dx), integration yields

    W_right q_right - q_left = I - integral W K u_E dx,
    I = integral W [-B F_endpoint-Gamma B a_s n-b S] dx.

At fade, the 2049-point evaluation gives I=-2.1946573 and a positive minimum
K=0.4446935 over the allowed rate interval, for both sigma=1 and sigma=10.
The 1025-to-2049 refinement changes I by 0.00037%; the positive coefficient
margin persists. Therefore balanced q=0 ends conflict with the integrated
force equation in this constitutive class. Field energy is nonnegative, so
its contribution strengthens the required boundary reaction. The finite
shift terms enter the displayed identity and numerical witness.

The obstruction identifies a reaction-bearing role. Fluid pressure and field
redistribution can transmit internal loads, while this co-moving assembly
still needs a supplied external reaction. Additional divisions of the same
fluid and field leave the summed force balance intact. A physical wall or
support adds its own tensor and can change that balance; its capacity is
precisely the remaining construction requirement.

## Bidirectional conversion changes the interior result

The final rate controls recover 64-cell passive histories at peak supplied
null stress 7.24840 for rate ten and 7.11498 with unrestricted discharge.
The 128-cell, 256-interval rate-ten control remains infeasible. Increasing
the discharge rate therefore supplies no converged low-burden passive history.

In contrast, permitting both charging and discharging produces a 64-cell
history with peak supplied null stress 0.0913135, initial slice energy 625.359,
and fade slice energy 43.9036. The remaining negative-null requirement at fade
is 0.102688. The left and right peak terminal-traction magnitudes are 0.010383
and 0.043245. The fluid carries its actual thermal pressure, and all interior
force equations are present. Its sampled speed remains the prescribed
coordinate-fixed target, at most 0.202141c.

This control identifies a useful constitutive distinction: a field that can
recharge locally has substantially more freedom to match the changing fluid
pressure and geometry than a passively discharging store. Its unconstrained
interval-averaged charging and discharge rates reach 228 and 423. The next
comparison imposes finite rates in both directions and refines the grid.

Local charging also has a thermodynamic requirement. Define C=H_s/(N_lapse R^4)
and E=-Gamma(P_endpoint-v F_endpoint). Positive C stores work in the electric
field; the fluid receives E-C as nonmechanical energy. Directly assigning
incoming endpoint energy to electrical work requires C <= max(E,0).
Where E<0, the endpoint can instead be a heat-dump port for a heat engine:
heat extracted from the fluid is C-E, electrical work is C, and dump heat
is -E. The required efficiency is C/(C-E). Its physical temperature ratio
and entropy balance still require the endpoint medium's constitutive law.

Two additional inverse controls isolate this requirement. The direct-work
control limits charging to incoming endpoint energy. The optimistic heat-engine
control also allows fluid heat extraction where the endpoint exports energy,
while requiring direct work elsewhere. Both controls grant all incoming endpoint
energy as usable work, so they remain generous physical screens. A charging
history that draws fluid heat while possessing no assigned heat-dump port
requires an additional free-energy store, a work-transfer current, or a changed
thermal exchange. Its tensor and reciprocal exchange must enter the assembly.

## Coefficient-retention audit

The finite bidirectional comparison converges to a small supplied-null peak:
0.0938878 at 64 cells and 0.0937354 at 128 cells with twice as many time
intervals. The refined initial slice energy is 632.965; the independent force
residual is 0.0529% of the summed equation-term magnitudes.

However, the first heat-engine solver status conflicts with the feasible-set
ordering: its constraints include every direct-work history, and a direct-work
history succeeds on the same grid. Direct substitution of that accepted history
into the heat-engine problem gives maximum scaled equality residual
9.45e-9 and inequality violation 1.29e-14. This warrants a numerical audit of
the infeasibility statuses before they support a physical conclusion.

HiGHS deletes coefficients at or below 1e-9 by default, as documented in its
[matrix-size options](https://ergo-code.github.io/HiGHS/dev/options/definitions/#small_matrix_value).
The large volume-weighted stores can give small shift coefficients a measurable
product. The audit therefore uses the supported 1e-12 retention threshold for
both optimization stages and checks the original matrices after solving.
A manufactured regression verifies a small coefficient multiplying a large
store. Earlier infeasibility labels remain archived solver outcomes; the
retained-coefficient rerun determines the final comparison.
