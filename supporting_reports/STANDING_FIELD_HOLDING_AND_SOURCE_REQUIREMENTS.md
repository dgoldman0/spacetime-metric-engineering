# Standing-field holding and source requirements

17 September 2026.

The rail's original pressure fields carry a continuous holding duty in
addition to their scheduled exchanges with material cores, joints and the
complementary rail port. Separating these duties gives a concrete
confinement requirement. With the existing transfer-loss allowance and
shared-reaction state cost charged, the tightest first-fine photon
population requires a \(1/e\) energy lifetime about **2,408 times its
full service duration**. The corresponding second-fine requirement is
about **96.5 service durations**. These are allocations of the remaining
energy budget; physical field hosts and the resulting operating dynamics
retain separate equations.

The four-component field basis also admits an exact conversion between
photon pressure and Maxwell pressure. This preserves integrated energy,
stress and aggregate reversible work, while changing the current paths,
individual work ports and holding mechanisms. Thus the next source
construction can compare photon confinement, electromagnetic holding and
mixtures within the existing backbone and jacket.

## Distinct infrastructure duties

The [rail infrastructure study](RAIL_INFRASTRUCTURE_TRANSFER_AND_REACTIONS.md)
tracks the packet corridor and service interfaces, conserved material
populations, current returns, force-matched joints, local stores, field
populations, receiver memory and support reservoir. The field populations
already participate in the common tensor and energy ledger. Their
reversible work ports take the form

\[
P_i=\dot E_i+p_iD_z+2q_iD_a.
\]

The [scheduled-transfer calculation](SCHEDULED_TRANSFER_AND_MECHANICAL_HOLDING.md)
uses these port demands to construct receipt, guide, converter and local
storage traffic. A separate residence exposure describes energy that
continues to occupy a pressure field between exchanges:

\[
I_i(\tau)=\int_0^\tau E_i(s)\,ds.
\]

Consequently a low work-port duty factor and a large standing-field
inventory can occur together. The original photon populations reach
97.57% of total local allocated energy at individual first-fine samples,
and 90.78% at individual second-fine samples. These maxima describe local
states in the inherited tensor allocation.

| Duty | Population or interface | Quantity entering the loss account |
| --- | --- | --- |
| Scheduled useful exchange | Work ports, transfer guides, splitter/converter paths | Integrated optical throughput and finite-flight inventory |
| Mechanical holding | Counterrotating stores and their thermal populations | Rotational drag, local heat and spin depletion |
| Standing positive pressure | Original radial and angular photon populations | Energy-time exposure and confinement attenuation |
| Electromagnetic support | Original and substituted hoop/radial Maxwell fields | Energy-time exposure, current-carrier dissipation, induction and return paths |
| Shared reaction support | Existing sheets and joints, field bias and reaction work branch | Additional state energy, reciprocal power, branch propagation and recoil |
| Whole service | Packet interfaces, receiver, support reservoir and control | The inherited service tensor and remaining source/interface allocations |

## Continuous panel loss budget

The archived field populations are piecewise linear in proper time. For
panel \(k\), their residence integrals therefore follow exactly from

\[
I_{i,k}=\sum_{m\le k}\frac{\Delta\tau_m}{2}
 (E_{i,m}+E_{i,m+1}).
\]

Define the available panel reserve after the inherited transfer exposure
\(O_k\) and shared-reaction ceiling by

\[
R_k=R_k^{\rm scheduled}
 -\frac{\alpha O_k}{1-\alpha/j_{\min}}-3\Pi_*,
\qquad \alpha=0.62\times10^{-6},\quad j_{\min}=0.3.
\]

Here \(\Pi_*\) is the summed guide/store trace bound at the material
label. For constant fractional energy-decay rates \(\Gamma_i\),
maintaining the prescribed field energies requires replacement powers
\(\Gamma_i E_i\). The separate rates share the constraints

\[
f\sum_i\Gamma_i I_{i,k}\le R_k
\quad\hbox{for every panel and label},\qquad
f=\frac1{1-\alpha/j_{\min}}.
\]

The factor \(f\) allows the previous converter's optical replacement
loss in the energy account. It remains conditional on that work-port
model. Charging the cumulative exposure through a panel's end against
the reserve lower bound throughout the panel covers every interior time.

These inequalities price loss replacement along the prescribed field
histories. Supplying that replacement changes individual node demands;
receipt peaks, loop schedules, retained heat and the new reaction work
therefore require a combined dynamical calculation.

For the original photon populations with one common decay rate,
\(\Gamma_{\rm ph}\), the allocation boundary is

\[
\Gamma_{{\rm ph},\max}
 =\min_{k,j}\frac{R_{kj}}{f(I_{r,kj}+I_{a,kj})}.
\]

The following values use a Maxwell representation of the small new
isotropic reaction bias. The photon channel receives the remaining
budget in this comparison; concurrent magnetic, mechanical and interface
losses reduce its allowance.

| History | Common photon decay ceiling, per proper-time unit | Tightest required energy lifetime / full service duration | Tightest required circuit period / local transfer delay at 0.62 ppm per circuit |
| --- | ---: | ---: | ---: |
| First, 16 labels | \(1.64571\times10^{-4}\) | 1,194.50 | 148,354 |
| First, 32 labels | \(8.16179\times10^{-5}\) | 2,408.46 | 299,122 |
| Second, 16 labels | \(2.37723\times10^{-3}\) | 74.37 | 8,912 |
| Second, 32 labels | \(1.83208\times10^{-3}\) | 96.54 | 11,571 |

The finer histories tighten the first-location allowance by about a
factor of two. In the first-fine case the limiting panel ends at proper
time 2.621861 and material label \(-2.0001953125\), inside a longer
service history. Its remaining reserve is 0.000139974 and its cumulative
original-photon exposure is 1.714988. The second-fine limiting panel ends
at proper time 5.352446 and label \(-1.9749921875\).

For an equivalent continuous attenuation model, a passive circuit losing
fraction \(\epsilon\) over proper circuit time \(T_c\) has
\(\Gamma=-\log(1-\epsilon)/T_c\). The final table column applies
this relation at the assigned 0.62 ppm benchmark. The actual standing
field geometry determines \(T_c\); the existing local transfer delay
is a comparison scale. Consequently reusing that short delay as the
standing-field circuit period would exhaust the available photon budget.
Larger paths, lower encounter loss, distinct confinement mechanisms and
field mixtures provide separate design variables.

A photon representation of the new reaction bias adds the constant
energy \(3B=\Pi_*\) to residence exposure. It changes the fine
decay ceilings by less than 0.002%. The original standing populations
dominate this holding duty.

## Equal-tensor electromagnetic alternatives

Write the four populations as hoop Maxwell \(H\), radial Maxwell
\(B_r\), radial photons \(W_r\) and angular photons \(W_a\).
Their normalized \((p,2q)\) columns are

\[
H:(1,0),\quad B_r:(-1,2),\quad W_r:(1,0),\quad W_a:(0,1).
\]

For any fixed fraction \(0\le\eta\le1\), the substitution

\[
H'=H+\eta(W_r+W_a/2),\qquad
B_r'=B_r+\eta W_a/2,
\]
\[
W_r'=(1-\eta)W_r,\qquad W_a'=(1-\eta)W_a
\]

preserves total energy and both pressure channels exactly. It also
preserves the sum of the reversible work ports under the same macro
evolution. Individual port powers, guide schedules and current demand
change with the representation.

The audit checks \(\eta=1/2\) and \(1\). Complete substitution
raises the maximum added Maxwell energy, including the small reaction
bias, to 2.371264 in the first-fine history and 0.576795 in the
second-fine history. These energies use the inherited rail normalization.
For a common fractional loss of the resulting Maxwell populations alone,
the corresponding energy-budget ceilings are
\(7.44650\times10^{-5}\) and \(1.59084\times10^{-3}\) per
proper-time unit. They describe a different dissipation channel drawing
on the same reserve.

Realizing this family requires spatial fields whose averaged stresses add
as assumed, compatible current populations, induction work, return
surfaces and connections into the existing longitudinal and angular
supports. A superposition of coherent fields also carries cross terms;
the tensor mixture needs a compatible orientation or spatial population
construction. The previous independent added-current-host trial retains
ten rejected first-fine samples. Shared hosting and field mixtures
therefore need a fresh coupled source allocation.

The next comparison combines these holding requirements with the local
reaction-work dynamics and then recomputes the eighteen-node exchange
network. Physical acceptance depends on the combined constitutive,
current, containment, propagation and loss equations of that ensemble.

## Reproducibility

The [standing-field archive](data/standing_field_losses/summary.json)
contains four independent history audits, both bias representations,
half/full field substitutions, source snapshots and verified parent
hashes. Three tests check equal-tensor substitution, exact residence
integration with a continuous panel screen, and the zero-photon limit.
Numerical tables are computed by the audit; this report is manually
authored.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_standing_field_losses.py \
  --workers 4 --output /tmp/standing_field_losses_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_standing_field_losses.py
```
