# Constitutive joints and optical reaction dynamics

16 September 2026.

A series connection can carry the scheduled material loads with conserved
core and joint inventories, a common transmitted force, and compatible
extensions. All four histories retain positive reserve across their 246,816
sampled states and throughout the prescribed interpolation. The six core
materials preserve their existing reference inventories; ten directional
joint populations receive additional fixed inventories.

An elastic optical ring supplies a complementary dynamical construction.
Its equations include photon energy, elastic strain, radial kinetic energy,
and the energy and momentum crossing its optical ports. Steady operation
has a finite power ceiling. Switching excites additional stress, and a
low-bias resonant drive reaches the boundary of tensile operation. Together,
these results give explicit joint laws and optical operating requirements
for the next assembly calculation.

## A common force through core and joint

The [scheduled reconfiguration](DISTRIBUTED_RECONFIGURATION_AND_JOINT_BUDGET.md)
provides six effective tensile duties. The present construction partitions
each duty between its core material and connections in series. Thus the
connections participate in the existing tensile path and preserve its
total integrated stress. The preceding additional neutral joint package
had a different geometry and inventory accounting.

Let \(M\) be a core's conserved reference energy, \(d=1\) for a string
and \(d=2\) for a sheet, and \(t\) its core tensile energy. With
\(\epsilon=0\) for strings and \(\epsilon=0.1\) for sheets,

\[
E_c=\sqrt{t^2+[(1-\epsilon)M]^2}+\epsilon M,
\qquad
S=\exp\!\left[\frac1d\operatorname{asinh}
                   \frac{t}{(1-\epsilon)M}\right].
\]

This retains the theoretical constitutive family used in the
[material reconfiguration model](MATERIAL_RECONFIGURATION_TEST.md).
Relativistic elastic membrane models and their characteristic-speed
conditions are developed by
[Mourão, Natário and Vicente](https://arxiv.org/html/2409.10602v2).
A physical material realizing the required family remains to be identified.

In each loaded direction, the core's relaxed span is \(\ell_0\), and
the total relaxed connector span is \(\alpha\ell_0\), with
\(\alpha=10^{-4}\). Each directional connector population has fixed
reference energy \(m\) and a rigid-string constitutive law. Writing
\(f=F\ell_0=t/S\), equality of transmitted force gives

\[
j=\left(1-\frac{2\alpha f}{m}\right)^{-1/2},\qquad
t_j=\alpha fj,\qquad T=t+t_j.
\]

The prescribed effective duty is \(T\). Solving the final equation
determines the core and joint extensions together. Their combined span
and energy are

\[
L=\ell_0(S+\alpha j),\qquad
E_{\rm cell}=E_c+d\,\frac m2(j+j^{-1}).
\]

Consequently \(\mathrm dE_{\rm cell}=d\,T\,\mathrm d\ln L\), or
\(\mathrm dE_{\rm cell}/\mathrm dT=d\,T\,\mathrm d\ln L/\mathrm dT\).
A string with equal reference
energy per relaxed length in its core and connector reproduces the
constitutive law of one continuous string with total inventory
\((1+\alpha)M\); this provides an exact control case.

Core force increases with core duty, and \(t\le T\). A sufficient
prepared inventory for a joint stretch ceiling \(j_*=2\) is therefore

\[
m=\max\left[\alpha M,
\frac{2\alpha\max_\tau[T/S(T)]}{1-j_*^{-2}}\right].
\]

The preparation is fixed for the whole history. Unloaded cores and
connections retain their relaxed energies. Sheets count two directional
connector populations, yielding ten populations across the six roles.

The actual connector-to-core span ratio evolves as \(\alpha j/S\).
On the first fine history it ranges from \(2.39\times10^{-6}\) to
\(10^{-4}\); on the second, from \(9.38\times10^{-6}\) to
\(10^{-4}\). Thus a fixed relaxed length fraction produces a changing
loaded geometry. Core stretches still reach 81.47 and 20.77, respectively,
while every prepared connector remains within twice its relaxed length.
The largest total joint reference energies per label are
\(3.04\times10^{-5}\) and \(2.69\times10^{-5}\).

## Continuous work and reserve

Six core ports, six grouped joint ports, four field and photon ports, the
remaining inventory, and the complementary rail port give eighteen exchange
nodes. Each material's power includes its constitutive energy change and
its work against the inherited macro deformation. The combined core and
joint stresses reproduce the prescribed tensile duties, preserving the
finite-interface load accounting and target tensor.

The continuous replay uses the inherited linear effective duties and field
energies, logarithmic macro stretches, and the new implicit series law.
Interval bounds on its derivatives enclose each node's operating power.
For reserve \(r\), panel duration \(\Delta\tau\), and derivative
bounds \(a\le\dot r\le b\), every panel fraction \(u\) obeys

\[
r(u)\ge\max\{r_0+u\Delta\tau a,
                 r_1-(1-u)\Delta\tau b\}.
\]

Minimizing this two-line envelope certifies the continuous reserve. This
derivative construction accommodates the implicit series constitutive law.
Independent quadratures check the energy and pressure-work integrals.

| History | Minimum reserve with constitutive series joints |
| --- | ---: |
| First, coarse | 0.00175415 |
| First, fine | 0.00163245 |
| Second, coarse | 0.00324896 |
| Second, fine | 0.00294539 |

The all-panel lower bounds attain these same minima. This is a local
constitutive and homogenized load-path construction. Spatial tiling,
finite ends, shear and torque transfer, and the moving attachment tensor
remain assembly requirements.

## A ring that carries its optical reaction

The optical model uses a homogeneous elastic ring carrying equal opposed
photon populations. Their angular momenta cancel. Ideal guiding constrains
the light to the ring, and distributed comoving ports inject and extract
energy together with its radial momentum. These are explicit reduced-model
assumptions. Radiation-pressure coupling and dynamical backaction are
standard subjects of
[cavity optomechanics](https://arxiv.org/abs/1303.0733); reflector internal
degrees of freedom are treated separately in
[oscillator-field moving-mirror models](https://arxiv.org/abs/1204.2569).
The ring calculation here supplies its own mechanical model, while a
microscopic reflector and converter remain additional components.

Use the conserved guide reference energy \(M_g\), reference radius
\(R_0\), and \(c=1\). Dimensionless radius, radial momentum, photon
action and time are \(x=R/R_0\), \(y=p/M_g\),
\(z=K/(M_gR_0)\), and \(\hat\tau=\tau/R_0\). Then

\[
e=\tfrac12(x+x^{-1}),\quad
\theta=\tfrac12(x-x^{-1}),\quad w=z/x,
\]
\[
v=y/h,\quad V=e+w,\quad h=\sqrt{y^2+V^2},\quad\gamma=h/V.
\]

Here \(e,\theta,w,h\) are material energy, tensile energy, photon
energy and total Hamiltonian, divided by \(M_g\). For escape optical
depth \(\eta\) per circuit, dimensionless output power is
\(q_{\rm out}=\eta z/(2\pi x^2)\). Defining
\(q=q_{\rm in}-q_{\rm out}\), the equations are

\[
x'=v,\qquad
y'=\frac{w-\theta}{\gamma x}+vq,\qquad
z'=\frac{xq}{\gamma}.
\]

They give the exact identity \(h'=q\). In particular, the comoving
ports carry the radial momentum term \(vq\), and the Hamiltonian
includes \(h-V\), the radial kinetic energy. The integrated pressure
trace is

\[
\Pi/M_g=hv^2+(w-\theta)/\gamma.
\]

Three equally weighted orthogonal ring planes produce an isotropic
averaged pressure \(\Pi/3\). Transient \(\Pi\) becomes an
additional load on the surrounding ensemble. The external transfer paths,
port supports and receiving stores have their own reaction requirements.

For steady input fraction
\(s=q_{\rm in}/q_{\rm crit}\), with
\(q_{\rm crit}=\eta/(4\pi)\), equilibrium requires
\(0\le s<1\), and

\[
x_{\rm eq}=(1-s)^{-1/2},\qquad
z_{\rm eq}=\tfrac12(x_{\rm eq}^2-1),\qquad\Pi_{\rm eq}=0.
\]

At or above the critical power, a finite tensile equilibrium ceases to
exist in this model. In units of the equilibrium radius, the linear radial
characteristic polynomial is

\[
\lambda^3+b\lambda^2+\lambda+b(1-s)=0,
\qquad b=\eta/(2\pi).
\]

All roots have negative real parts for \(\eta>0\) and \(0<s<1\).
At zero bias the mechanical pair is undamped. These statements concern
the homogeneous radial mode; shape modes require a larger model.

## Switched operation and a tensile-boundary failure

The main drive alternates between \(s=0.25\) and \(s=0.40\).
The slow sequence uses four intervals of \(500R_0/c\). The near-resonant
sequence uses 160 intervals of approximately \(3.824R_0/c\), near half
the radial oscillation period. Each starts at its lower-drive equilibrium.

| Drive trial | Radius range \(R/R_0\) | Largest radial speed | Largest sampled \(|\Pi|/M_g\) |
| --- | ---: | ---: | ---: |
| Slow steps, \(\eta=1\) | 1.14958–1.29314 | \(0.02011c\) | 0.01454 |
| Slow steps, \(\eta=0.5\) | 1.15252–1.29174 | \(0.01091c\) | 0.00748 |
| Near resonance, \(\eta=1\) | 1.06199–1.39468 | \(0.13716c\) | 0.16833 |

The near-resonant drive produces about 11.6 times the slow-step pressure
excursion despite stable steady equilibria. Halving the escape depth
reduces radial speed in the slow-step trial. At equal useful power and
geometry, it also doubles the required guide reference inventory, coupling
this response change to an energy cost.

A lower-bias trial alternates between \(s=0.10\) and \(0.40\) near
its corresponding radial period. It reaches \(R=R_0\) during the seventh
drive interval, at \(23.06034R_0/c\), with inward motion. Integration
stops at that tensile boundary. Continued operation would require a
compressive member, a changed drive, or additional control. Thus bias and
switching spectrum are substantive operating parameters.

Halved integration steps and tighter tolerances agree at common output
times. The listed extrema are sampled trajectory extrema; a bound covering
every admissible drive remains a separate control problem. The inherited
fine-history macro panels are at least \(2.03\times10^5R_0/c\) and
\(3.94\times10^5R_0/c\) long under the sizing below. Those timescales
permit slower commands, while the actual coupled optical histories still
require an explicit drive and routing construction.

## Conditional optical energy sizing

For each label, let \(P_*\) be the sum of the eighteen positive node
power bounds, and \(\delta\) the inherited gap-sized path delay.
The reception allowance is \(C=\delta P_*\). Select
\(R_0=\delta/(2\pi\times1.5)\), so a ring with \(x\le1.5\)
has circumference at most the selected gap-sized path scale. Splitting the traffic among nodes
and ring orientations preserves the summed energy accounting.

With \(\eta=1\), bias \(s_b=0.25\), and peak \(s_p=0.40\),
the summed guide reference inventory and recycled bias power are

\[
M_g=\frac{4\pi R_0P_*}{\eta(s_p-s_b)}
   =8.8889C,\qquad
P_b=\frac{s_b}{s_p-s_b}P_*=\frac53P_*.
\]

The successful selected-drive trials fit \(x\le1.5\) and
\(H\le1.30M_g\). Using that tested energy envelope, the initial
receiving-store charge is
\(B_0=C+M_g[1.30-(1-s_b)^{-1/2}]\).
Let \(O\) be useful transfer energy in flight. With local bias recycling,
the equations give \(B+H+O=B_0+H_0\), and \(O\le C\).
Thus the combined prepared guide, receiving store and useful in-flight
energy is \(C+1.30M_g=12.5556C\). Transit energy is counted once.

| History | Largest \(C\) per label | Minimum reserve after this energy projection |
| --- | ---: | ---: |
| First, coarse | \(3.74902\times10^{-5}\) | 0.00128527 |
| First, fine | \(3.78571\times10^{-5}\) | 0.00116049 |
| Second, coarse | \(1.00744\times10^{-5}\) | 0.00316045 |
| Second, fine | \(1.66554\times10^{-5}\) | 0.00273627 |

These values are remaining energy for the selected sizing and trajectory
envelope. The receiving store remains an abstract reversible reservoir.
Transient guide stress, external path radiation pressure, bias-port and
store reactions, optical conversion, and physical routing still require
assembly models and target-tensor matching. The guide trials and this
energy projection consequently have a narrower scope than a coupled
containment solution.

Continuous bias introduces a demanding loss requirement. If a constant
fraction \(\ell\) of recycled bias energy becomes heat retained within
the same budget, its accumulated energy is \(\ell P_b\tau\). The
fine-history sampled energy ceilings are
\(\ell\le1.7946\times10^{-7}\) at the first location and
\(\ell\le5.3879\times10^{-7}\) at the second: approximately 0.18
and 0.54 parts per million. The continuous reserve bounds give sufficient
fractions of \(1.7942\times10^{-7}\) and
\(5.3864\times10^{-7}\) for this energy-only accounting. Heat pressure,
losses in useful traffic, and heat-export hardware require additional
budgets. These figures constrain the chosen continuously biased recycling
scheme; alternative control and heat-export arrangements have different
requirements.

## Remaining assembly requirements and evidence

The joint result supplies conserved material laws, force-compatible local
geometry and reciprocal work. The optical result supplies a radial
Hamiltonian, port momentum exchange, steady power capacity, and tested
switching failure modes. A next coupled construction must match the
transient optical tensor, provide the converters and port supports, and
establish acceptable loss and thermal behavior. Spatial joint assembly and
non-axisymmetric optical modes remain alongside those tasks.

The [independent current-host obstruction](FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md)
also persists: its necessary bound rejects ten samples in the first fine
history for the tested family of separately added hosts. Shared current
paths and end-force transfer remain coupled requirements. The core strain
requirements and physical material identification likewise remain active.

The [constitutive and optical module](../toolkit/adm_harness_cli/adm_harness/constitutive_joints_and_optics.py),
[four-worker audit](../toolkit/adm_harness_cli/scripts/audit_constitutive_joints_and_optics.py),
and [tests](../toolkit/adm_harness_cli/tests/test_constitutive_joints_and_optics.py)
accompany the [numerical summary](data/constitutive_joints_and_optics/summary.json)
and [hash manifest](data/constitutive_joints_and_optics/manifest.json).
Four history archives and six optical trial archives preserve the numerical
states. Executed sources and parent evidence hashes preserve provenance.
The focused suites pass **55 tests**, including the uniform-string
control, virtual work, interval power bounds, optical energy and momentum
exchange, closed-ring conservation, and linear-mode checks.
Across 68 independently integrated history panels, the largest work
integral error is below \(3.9\times10^{-16}\). Maximum tensor and
instantaneous reciprocal-power errors are below \(6.3\times10^{-16}\)
and \(2.5\times10^{-13}\). The optical trials' largest energy-balance
error is below \(1.8\times10^{-12}\), and the integration refinements
agree within \(7.4\times10^{-12}\) at common output times.

Reproduction uses a fresh output directory:

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_constitutive_joints_and_optics.py \
  --workers 4 --output /tmp/constitutive_joint_optical_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_constitutive_joints_and_optics.py \
  toolkit/adm_harness_cli/tests/test_distributed_reconfiguration.py \
  toolkit/adm_harness_cli/tests/test_material_reconfiguration.py \
  toolkit/adm_harness_cli/tests/test_finite_containment.py \
  toolkit/adm_harness_cli/tests/test_containment_ensemble.py
```
