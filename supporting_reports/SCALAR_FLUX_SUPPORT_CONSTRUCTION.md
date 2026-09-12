# Scalar potential and flux-tube support

Scalar potential energy supplies the correlated stress missing from the
previous electromagnetic/radiation/angular-membrane comparison. Its local
addition admits the retained active-rail backing target. A conserved radial
population of equilibrium flux tubes has a stronger restriction: its tension
per solid angle stays fixed. That specialization fails both on the retained
target and after reoptimizing the registered support family. Stable causal
elastic excitations about a fixed tube ground state remain inside the same
excluded stress envelope.

The calculation concerns the scheduled backing patch `-2.1 <= x <= -0.5`,
its pressure link, and its standing-support connections. It uses the active
geometry and counted electrode, fluid, work-route, and receiver loads from the
[joint construction review](JOINT_SUPPORT_CONSTRUCTION_REVIEW.md). The
capacitor keeps its electrical role, while the support carries the combined
mechanical reaction. The standing substrate's allocated tensor remains a
construction target with a separately required physical realization.

## Local stress supplied by the extra field sector

Write the rest-frame tensor as `(rho,p_r,p_t)`. Here `rho` is energy density,
including rest energy. The candidate basis contains radial Maxwell energy
`E`, scalar potential energy `V`, radial waves `W`, angular waves `H`, an
angular tensile membrane `M`, and rest inventory `I`:

| Energy | Tensor per positive unit energy |
| --- | --- |
| `E` | `(1,-1,1)` |
| `V` | `(1,-1,-1)` |
| `W` | `(1,1,0)` |
| `H` | `(1,0,1/2)` |
| `M` | `(1,0,-1)` |
| `I` | `(1,0,0)` |

Minimizing their summed energy at fixed pressures gives

```
rho_min = max(p_r+2p_t, p_r-p_t, -p_r, -p_t).
```

In particular, `E=V=1/2` supplies `(1,-1,0)`. The earlier Maxwell field plus
purely angular membrane needed energy 2 for the same unit radial tension.
The scalar potential contributes radial tension while supplying the
transverse reaction. This is the relevant change in stress correlation.

[Ishihara and Ogawa](https://arxiv.org/html/2103.13732v1) give a canonical
scalar/gauge model whose potential-dominated interior has positive energy
and equal negative pressures. Their full tensor also contains scalar kinetic
and gradient energies. A local allocation of `V` leaves those field
equations, gradients, and exchanges to the material construction.

For a general target, the allowed potential interval is

```
max(0,(-2p_r-rho-p_t)/2) <= V
V <= min((rho-p_r-2p_t)/4, rho-p_r+p_t).
```

At each allowed `V`, the field energy satisfies
`max(0,-p_r-V) <= E <= (rho-p_r+p_t-V)/3`. The remaining positive weights
then reconstruct the target tensor. Independent linear programs verify the
closed-form energy bound and the component reconstruction.

## Equilibrium tubes impose a conserved amplitude

An isolated straight static relativistic vortex has equal energy and tension
per unit length. For fixed tube count, a radial bundle therefore supplies

```
(rho_v,p_r_v,p_t_v) = (A/R^2,-A/R^2,0).
```

The amplitude `A` is constant along an uninterrupted bundle and through time.
This tensor is exactly conserved on the registered active metric. Its
equality of longitudinal energy and tension also holds for a resolved
equilibrium core; the expression uses the integrated transverse equilibrium
stress, with the usual small-core approximation relative to the rail scale.

Subtracting this tensor and requiring the remaining fields, radiation,
angular membrane, and rest inventory to carry positive energy gives

```
A >= max(0, R^2*(-2p_r-p_t-rho)),
A <= R^2*min((rho-p_r-2p_t)/2, (rho-p_r+p_t)/2).
```

The final `f=0.99` generic target admits this decomposition independently at
every original node. A common amplitude instead requires `A >= 2.02361`
near `(t,x)=(1.24986,-1.15)` and `A <= 0.00237834` near
`(0.0727832,-2.0)`. The two bounds differ by a factor of about 851. At
`x=-2.0` alone, the maximum lower bound through time exceeds the minimum
upper bound by a factor of about 119. Even independently grading the tube
population at each position leaves a temporal conflict in this target.

The upper-bound witness is a region of radial compression. Maintaining a
large permanent tension there consumes energy in both the tension carrier
and its opposing compressive load. The later tensile region needs much
more of the same permanent population. This explains the conflict in terms
of the assembly's changing load distribution.

## Reoptimizing the scheduled support

The comparison reuses the conservative response bases at 128 cells / 258
times and 256 cells / 515 times. All 27 material controls have unrestricted
amplitudes, both work-direction fractions range over `[0,1]`, and the
conserved bundle amplitude ranges over `[0,infinity)`. The bundle is
subtracted from the total backing response before testing the residual
component mixture. Thus its energy and stress belong to the same counted
backing tensor.

| Representation | Freely varying potential energy | Conserved bundle plus earlier components |
| --- | --- | --- |
| 128 cells | Nodal material null peak `0.663599` | Infeasible subset of 2601 constraints |
| 256 cells | Nodal material null peak `0.690092` | Infeasible subset of 2602 constraints |

The refined potential case satisfies all 1,455,905 original inequalities to
`1.25e-13` after replacing the sampled angular maximum with the analytic
maximum. Its initial support inventory is 10,133.7, final inventory 978.53,
and charging feed fraction from the left 0.25134. Recovery remains rightward.
For comparison, the earlier generic `f=0.99` target had material null peak
1.76512 and initial support inventory 7914.71. The lower peak therefore
coexists with increased prepared energy.

These peaks cover the backing and pressure medium in the existing comparison.
The changed route's full tensor, physical field dynamics, and complete quantum
source remain separate entries in the construction. The nodal potentials
provide an algebraic response target. Independent work reconstruction and
between-node admissibility determine its numerical continuation.

The conserved-bundle result is a finite-family numerical infeasibility
result, obtained on both representations. The local interval contradiction
above independently excludes that realization of the retained target.

## Why ordinary elastic or current excitations stay within this gate

[Hartmann, Michel, and Peter](https://arxiv.org/pdf/1710.00738) relate the
longitudinal and transverse squared characteristic speeds of an elastic
string to `-dT/dU` and `T/U`. Consider an aligned equilibrium branch connected
to a common ground state `U=T=mu`, with `U>=mu`, `T>=0`, and causal stable
longitudinal response `0<=-dT/dU<=1`. Integrating this last inequality gives

```
T <= mu,              U+T >= 2mu.
```

Its diagonal stress has the exact positive decomposition

```
(U,-T,0) = mu*(1,-1,0)
         + (mu-T)*(1,1,0)
         + (U+T-2mu)*(1,0,0).
```

The last two terms already belong to the radial-wave and rest-inventory
basis used by the conserved-bundle test. Consequently those causal elastic
branches, including the transonic law `UT=mu^2`, fit inside its more generous
component envelope. Adding their currents or waves preserves the finite-family
obstruction. This implication is derived here from the characteristic-speed
condition; the cited work studies microscopic string models and also shows
that macroscopic stability can coexist with microscopic instability in excited
branches.

The implication assumes a fixed ground state, radial orientation, conserved
bundle count, and the stated equilibrium branch. A changing condensate phase,
resolved transverse dynamics, tube redistribution, or additional interaction
stress introduces different material equations and counted exchanges.

## Literature and physical construction boundary

[Bolognesi and colleagues](https://arxiv.org/html/1408.1572v3) provide an
explicit large-flux vortex limit in which magnetic energy balances scalar
potential energy inside a tube. At fixed flux, increasing the cross section
reduces magnetic energy and increases potential energy. This gives a useful
finite-dimensional check before attempting a general field evolution.

These gauge/scalar actions supply theoretical constitutive candidates.
Their mapping to available matter remains a physical requirement. In
particular, the Standard Model embedding has its own stability problem:
[Forgacs and Lukacs](https://arxiv.org/abs/1909.07447) find their electroweak
strings with an added dark condensate become unstable as the mixing angle
approaches its physical value. A laboratory condensate analogue likewise
requires its host's rest energy and mechanical tensor in the gravitational
accounting.

The positive local result identifies a useful stress correlation. The
conserved-bundle and elastic-envelope results identify the material response
that this realization lacks. The ongoing independent audit addresses
conserved work, finite-load witnesses, and the leading-volume tube invariant.
Those results belong to this supporting record; the technical disclosure
retains its established design content.

## Evidence and validation

The [response-family results](data/scalar_flux_response_family/summary.json)
contain both resolutions and both constitutive envelopes. Their manifest
records source and result hashes. Seven focused tests compare the local cone
with independent component programs, verify conserved expanding and squeezed
tube controls, check product bounds, and test the elastic-envelope inclusion.
Independent cases run in parallel with a configurable worker count.
