# Finite thermal transfer budget

The passive paired emitter and its finite relay fit inside the conditional
19- and 20-unit holding allocations. The calculation includes the larger
passive emission power, retained flight photons, their reaction pressure,
and the extra radial damping induced by delayed thermal arrival. The first
fine history retains minimum spin bounds 0.325048 and 0.371577, respectively.

The [thermal interface construction](PAIRED_THERMAL_EXCHANGE_INTERFACES.md)
supplies exact source recoil and a finite frozen relay. The present history
bound assumes equal-delay, rotor-matched ports with zero additional collector
work. Moving collectors have a separately measured work and recoil
requirement, described below.

## Delayed energy and heat

Let \(q_p\) be optical power entering the absorbing rotor ports and \(Q_e\)
the passive thermal emission. At absorption \(a\) and spin floor \(j_f\),

\[
0\le Q_e\le\kappa|q_p|,\qquad
\kappa=\frac{a}{2j_f-a(1+j_f)}.
\]

For a matched route with delay \(\tau\), the arriving heat is
\(Q_a(t)=Q_e(t-\tau)\). The additional flight state satisfies

\[
W_h=\int_{t-\tau}^tQ_e(u)\,du,\qquad
\dot W_h=Q_e-Q_a,\qquad
q_r=q_p-\dot W_h.
\]

Thermal action receives \(xQ_a/(\gamma_rM)\). The cold spin rate receives
\(x(q_p-Q_e)/(\gamma_rMj)\). Their sum preserves the original equation
for \(j^2+2b\), now driven by \(q_r\). Three equal rotated relay copies
preserve total photon energy and give mean pressure \(W_h/3\) in each
spatial direction; local guide reactions remain part of their construction.

With support derivative \(c\), the added effective rotor forcing is
\(-(1+c)\dot W_h\). Positivity of \(Q_e\) gives

\[
\|\dot W_h\|_1\le2\kappa\|q_p\|_1,\qquad
\|\dot W_h\|_\infty\le\kappa\|q_p\|_\infty.
\]

Using the existing coupled gain \(G=2.85\), one obtains

\[
\|q_p\|_1\le
\frac{G\|F_0\|_1}{1-2\kappa[G(1+c_{\max})+1]}.
\]

At \(a=0.62\) ppm and \(j_f=0.3\), the denominator is 0.999989098 and
the resulting gain is 2.850031072. A simultaneous peak bootstrap gives
\(q_{p,\max}\le MU_{\max}/[R_0(1-\kappa)]\), with \(U_{\max}=0.006\).
Consequently,

\[
W_{h,\max}\le\tau\kappa q_{p,\max},\qquad
\|\dot W_h\|_2^2\le2\kappa^2q_{p,\max}\|q_p\|_1.
\]

Minkowski's inequality adds this forcing to the existing full-history
input-squared bound. The maximum thermal arrival integral is
\(\kappa\|q_p\|_1\). Reconstructed spin includes both contributions.
The combined flight and support energy allowance adds
\((1+c_{\max})W_{h,\max}\).

## Four-history results

The route delay is \(\delta/64\). For 19 units,
\(W_{h,\max}=6.93901\times10^{-8}C\); the combined extra state allowance
is \(1.04092\times10^{-7}C\). Eight source, mixer, turn and receiver
encounters per transferred thermal energy are reserved in the energy
screen. This encounter allowance concerns transfer into the thermal
population; its physical holding loss law remains a material requirement.

| History | Minimum spin, 19 units | Minimum spin, 20 units | Energy reserve, 19 units | Energy reserve, 20 units |
|---|---:|---:|---:|---:|
| First, 16 labels | 0.415779 | 0.446719 | \(2.766343\times10^{-4}\) | \(2.278997\times10^{-4}\) |
| First, 32 labels | 0.325048 | 0.371577 | \(1.226230\times10^{-4}\) | \(7.356900\times10^{-5}\) |
| Second, 16 labels | 0.442625 | 0.468398 | \(2.954043\times10^{-3}\) | \(2.944843\times10^{-3}\) |
| Second, 32 labels | 0.428792 | 0.456739 | \(2.257016\times10^{-3}\) | \(2.235281\times10^{-3}\) |

All eight variants retain the energy, forcing and spin domains used by the
nonlinear certificate. The scalar allowance for replacement of losses in
other components remains separate from their physical thermal and routing
construction.

## Moving-guide connection

For guide work \(G_h\) delivered to the thermal photons,

\[
\dot W_h=Q_e-Q_a+G_h,\qquad
q_r=q_p-\dot W_h+G_h.
\]

The guide host supplies \(-G_h\) and its recoil. A moving collector can
therefore preserve energy and momentum through an explicit mechanical
port. For an axial incoming ray and radial collector speed bounded by
0.00905, its photon-energy increment is at most
\(8.19092\times10^{-5}E_{\rm in}\). This is a small duty compared with
the already small thermal flux, while its time-dependent path, reaction
host and work exchange still require a geometric construction. The matched
history calculation above keeps that construction as a condition.

## Reproduction

Four tests verify the feedback inequality, positive delayed-photon
variation, recovery of the parent dynamics at zero absorption, and the
thermal effect of increased absorption and delay. The four-worker audit
checks the source manifests and each history's invariant and energy bounds.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_finite_thermal_budget.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_finite_thermal_budget.py -q
~~~

The [evidence directory](data/finite_thermal_budget/) retains the numerical
arrays, source snapshots, parent hashes and output manifest.
