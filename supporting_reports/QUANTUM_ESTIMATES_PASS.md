# Quantum Estimates Pass: Vacuum Stress, Rear Horizon and Exterior Mixing

Date: 2026-09-25. Context: the [ANEC map pass](ANEC_MAP_PASS.md) found
negative averaged null energy along the first light of the trimmed carry,
which places its source among classical fields. This pass sizes the response
of quantum fields to the prescribed geometry: the vacuum stress that the local
curvature fixes, the Hawking-like flux of the rear horizon, and the pair
creation in the exterior that the pattern outruns. Run:
`scripts/run_quantum_estimates_pass.py`, with data in
[data/quantum_estimates_pass](data/quantum_estimates_pass/).

## Result

- **Vacuum stress stays a factor \((\ell_P/L)^2\) below the demand.** The
  photon field's trace anomaly peaks at \(1.33\,\hbar c/L^4\) at carry speed
  2.1 and at 6.0 at speed 10. The demanded stress peaks at 1.79 and 3.67
  \(c^4/(GL^2)\). Their ratio is \((\ell_P/L)^2\) times 0.74 and 1.6, about
  \(2\times10^{-70}\) and \(4\times10^{-70}\) at \(L=1\) m, so the two meet
  only at 0.9–1.3 Planck lengths.
- **The compartment holds none of it.** The trace peaks on the axis at the
  compartment's lapse boundary, 0.375 beyond the flat interior, and inside it
  vanishes with the curvature, below \(10^{-27}\). The peaks stay the same
  from the cone's extension through the lane to the deceleration.
- **The rear horizon radiates at millikelvin temperatures on a metre scale.**
  It is a null disk out to \(r\approx9\), with surface gravity 7.55 on the
  axis at 2.1 and 57 at 10. Passengers at the 1× clock read its flux at
  \(\kappa/2\pi\): 2.8 mK and 21 mK for \(L=1\) m, falling as \(1/L\) to
  2.8 μK and 21 μK at 1 km.
- **Exterior pair creation stays within a few \(10^{-3}\) per mode.**
  Packets overtaken by the cone leave with negative-frequency shares of
  \(0.3\)–\(4\times10^{-3}\), the level that the edge of the flat-space window
  produces by itself, which bounds the mixing there. At the bound the
  emission is of order \(10^{-19}\) W per mode channel at \(L=1\) m.
- **Passengers.** At the 1× clock they age with exterior time, and the flat
  compartment keeps their tides and acceleration at zero. The quantum
  environment adds the rear flux, at a blackbody flux of
  \(3\times10^{-18}\) W/m² at 2.1 and \(1\times10^{-14}\) W/m² at 10 for
  \(L=1\) m.

## Trace anomaly

For a conformal field the trace of the renormalized stress is fixed by the
local curvature in every state,

\[
\langle T^\mu{}_\mu\rangle=\frac{c\,W^2-a\,E}{16\pi^2}\;\frac{\hbar c}{L^4},
\]

with the Weyl square \(W^2\) and the Euler density \(E\) in units of
\(1/L^4\). A finite \(R^2\) counterterm shifts the remaining \(\Box R\) term,
which the run leaves out. The coefficients \((a,c)\) are \((1/360,1/120)\)
for a conformally coupled scalar, \((11/720,1/40)\) for a two-component Weyl
fermion and \((31/180,1/10)\) for the Maxwell field. On Ricci-flat curvature
the scalar value reduces to the Kretschmann scalar over \(2880\pi^2\), the
Christensen–Fulling value on Schwarzschild. Among the fields of the real
vacuum the photon is the massless conformal one at rail scales. Neutrinos of mass 0.01–0.1 eV have Compton
wavelengths of 2–20 μm, so on a metre scale they act as massive fields, whose
vacuum stress carries a further factor of that wavelength over \(L\), squared.
The Weyl-fermion column covers a massless lightest neutrino.

The run builds \(W^2\), \(E\) and the demanded stress \(G/8\pi\) from the
metric's Riemann tensor in the normal frame. The Einstein tensor from these
contractions reproduces the design's demanded tensor to \(5\times10^{-13}\).
Samples run along the track every 0.125 across the pattern and every 0.25
along the cone to 2 past its tip, on the gate's radial nodes. They cover five
times: mid-acceleration and mid-deceleration, at half the lane speed; the
two moments the cone is half extended, at carry speed 0.8; and mid-lane. Contents
integrate the magnitudes over the pattern's volume.

| Quantity | Speed 2.1 | Speed 10 |
|---|---:|---:|
| peak Kretschmann scalar | 6,365 | 28,614 |
| peak demanded stress component | 1.79 | 3.67 |
| peak trace, conformal scalar | 0.110 | 0.501 |
| peak trace, Weyl fermion | 0.331 | 1.50 |
| peak trace, photon | 1.33 | 6.01 |
| photon peak over demanded peak | 0.74 | 1.64 |
| photon trace content | 359 | 1,325 |
| demanded content | 1,286 | 4,761 |
| share of the photon trace content in the cone | 1.8% | 17.6% |
| share of the demanded content in the cone | 16% | 60% |

Curvature is in \(1/L^4\), stress in \(c^4/(GL^2)\) and traces in
\(\hbar c/L^4\); contents are in \(\hbar c/L\) and \(c^4L/G\).

The peaks sit on the axis at the compartment's lapse boundary, where the lapse
climbs from the compartment's 1 to the plateau across one unit of track. The
shift there is uniform, so the change of speed during the acceleration leaves
that curvature untouched, and the peaks hold at every sampled time. The cone
carries 60% of the demanded content at speed 10 and 18% of the vacuum stress
content. Its slender profile keeps the curvature gentle along its length. Its
photon trace peaks where the lapse rises behind the tip: 0.0036 on the axis,
5.5 behind the tip, at 2.1, and 0.019 at \(r=2.6\), 58 behind the tip, at 10.
While the cone extends, the same peaks travel out with the tip. At the
half-extension moments the photon trace content is 346 at 2.1 and 1,069 at
10, against demanded contents of 1,047 and 2,304.

| \(L\) | Photon trace peak, 2.1 / 10 | Demanded stress peak, 2.1 / 10 | Ratio, 2.1 / 10 |
|---:|---:|---:|---:|
| 1 m | \(4.2\times10^{-26}\) / \(1.9\times10^{-25}\) J/m³ | \(2.2\times10^{44}\) / \(4.4\times10^{44}\) Pa | \(1.9\times10^{-70}\) / \(4.3\times10^{-70}\) |
| 10 m | \(4.2\times10^{-30}\) / \(1.9\times10^{-29}\) J/m³ | \(2.2\times10^{42}\) / \(4.4\times10^{42}\) Pa | \(1.9\times10^{-72}\) / \(4.3\times10^{-72}\) |
| 100 m | \(4.2\times10^{-34}\) / \(1.9\times10^{-33}\) J/m³ | \(2.2\times10^{40}\) / \(4.4\times10^{40}\) Pa | \(1.9\times10^{-74}\) / \(4.3\times10^{-74}\) |
| 1 km | \(4.2\times10^{-38}\) / \(1.9\times10^{-37}\) J/m³ | \(2.2\times10^{38}\) / \(4.4\times10^{38}\) Pa | \(1.9\times10^{-76}\) / \(4.3\times10^{-76}\) |

At \(L=1\) m the photon trace peak lies twelve orders of magnitude below the
energy density of the cosmic microwave background, \(4.2\times10^{-14}\)
J/m³.

## Rear horizon

In the pattern's frame during the lane the metric is stationary, and its
Killing time turns null on the surface \(S\) where \(\alpha=b\), with
\(b=\beta+v\). Behind the packet the shift is zero, so \(S\) sits where the
rear lapse fall passes through the carry speed. As the
[cone tip field pass](CONE_TIP_FIELD_PASS.md) showed, \(S\) is null, and a
Killing horizon, exactly where its transverse lapse gradient vanishes. There
its surface gravity is \(\kappa=|\partial_\zeta\alpha|\).

| \(r\) | 2.1: \(\zeta\) of \(S\) | 2.1: \(|\partial_r\alpha|/|\partial_\zeta\alpha|\) | 2.1: \(\kappa\) | 10: \(|\partial_r\alpha|/|\partial_\zeta\alpha|\) | 10: \(\kappa\) |
|---:|---:|---:|---:|---:|---:|
| 0 | −5.107 | 0 | 7.55 | 0 | 57.2 |
| 2 | −5.107 | 0 | 7.55 | 0 | 57.2 |
| 4 | −5.107 | \(6\times10^{-4}\) | 7.55 | \(8\times10^{-4}\) | 57.2 |
| 6 | −5.127 | 0.017 | 7.89 | 0.022 | 60.6 |
| 8 | −5.152 | 0.004 | 8.30 | 0.005 | 65.1 |
| 8.5 | −5.153 | \(5\times10^{-4}\) | 8.32 | \(6\times10^{-4}\) | 65.3 |
| 9 | −5.150 | 0.035 | 8.24 | 0.065 | 64.4 |
| 9.5 | −5.087 | 0.26 | 6.76 | 0.54 | 48.2 |
| 10 | −4.748 | 1.59 | 2.92 | — | — |

The surface is null to within 3.5% out to \(r=9\) at 2.1, and to within 6.5%
at 10. Beyond that, inside the outer lapse fall that begins at \(r=8.75\), it
turns crossable. Across the disk \(\kappa\) runs from 7.55 on the axis to 8.3, so the disk
radiates at 1.20–1.32 \(\hbar c/(k_BL)\) at 2.1. At 10 the plateau stands
higher and \(S\) crosses a steeper part of the rear fall: \(\kappa\) runs from
57 to 65 and the temperature from 9.1 to 10.4. The trim lowered the reference
value from the 9.1 of the pre-trim front.

The flux runs forward through the plateau into the compartment. There the
Killing time has norm \(N=\sqrt{\alpha^2-b^2}\), which is 1 at the 1× clock,
where \(\alpha=1\) and \(b=0\). Passengers therefore read the Tolman
temperature \(\kappa/2\pi N=\kappa/2\pi\).

| \(L\) | Passenger temperature, 2.1 / 10 | Blackbody flux, 2.1 / 10 |
|---:|---:|---:|
| 1 m | 2.75 mK / 20.8 mK | \(3.3\times10^{-18}\) / \(1.1\times10^{-14}\) W/m² |
| 10 m | 0.28 mK / 2.1 mK | \(3.3\times10^{-22}\) / \(1.1\times10^{-18}\) W/m² |
| 100 m | 28 μK / 208 μK | \(3.3\times10^{-26}\) / \(1.1\times10^{-22}\) W/m² |
| 1 km | 2.8 μK / 21 μK | \(3.3\times10^{-30}\) / \(1.1\times10^{-26}\) W/m² |

The cosmic microwave background delivers \(3.1\times10^{-6}\) W/m² at 2.725 K.

## Exterior mixing

In the pattern's frame the exterior's Killing vector is spacelike, so field
modes of both signs of Killing energy meet there. Scattering off the
stationary cone conserves the Killing frequency \(\omega-vk_z\), which is
negative for light overtaken on the axis. Outgoing waves match it either with
positive lab frequency, at the gains of the Killing-energy law, or with
negative lab frequency. The negative part is pair creation, and its share of
the Klein–Gordon norm measures the mixing \(|\beta|^2\) of a normalized
packet.

The run sends complex packets of positive normal frequency at the cone from
12 units ahead of its light surface on the axis: three on the axis, of
wavelengths 0.5, 1 and 2, and a ring of wavelength 1 at \(r=2\). They are
built from flat-space modes, which leaves \(10^{-10}\)–\(10^{-12}\) of their
norm at negative frequency. They evolve on the lane's stationary metric at
speed 2.1, on a grid of step 0.04, 48 units along the track by 14 in radius,
with absorbing layers at the edges. Once per unit time a Fourier–Hankel
transform splits the field inside a window of flat space, one unit clear of
the structure, into its two frequency parts. A control places each packet,
unevolved, astride the window's edge ahead of the tip.

| Packet | Share before contact | Share at \(t=7\) | Share at \(t=10\) | Share at \(t=15\) | Windowed norm at \(t=15\) | Control astride the edge |
|---|---:|---:|---:|---:|---:|---:|
| axis, wavelength 0.5 | \(3\)–\(7\times10^{-8}\) | \(1.7\times10^{-3}\) | \(9.5\times10^{-4}\) | \(1.6\times10^{-3}\) | 0.12 | \(1.3\times10^{-3}\) |
| axis, wavelength 1 | \(8\times10^{-10}\) | \(1.6\times10^{-3}\) | \(9.4\times10^{-4}\) | \(6.6\times10^{-4}\) | 0.47 | \(3.9\times10^{-3}\) |
| axis, wavelength 2 | \(1.3\times10^{-8}\) | \(4.0\times10^{-3}\) | \(3.0\times10^{-3}\) | \(3.9\times10^{-3}\) | 0.49 | \(5.9\times10^{-3}\) |
| ring at \(r=2\), wavelength 1 | \(3\times10^{-10}\) | \(4.6\times10^{-4}\) | \(4.9\times10^{-4}\) | \(2.1\times10^{-3}\) | 0.46 | \(4.4\times10^{-5}\) |

The control column centres each packet on the window's half contour, where
64–99% of its norm lies inside.

Before contact the shares stay at the floor set by the packet construction
and the solver's dispersion, which is largest at the shortest wavelength.
From contact at \(t\approx3\)–5 they rise to \(0.3\)–\(4\times10^{-3}\) and
hold that level through \(t=15\). By then 46–49% of each longer packet's norm
lies in the window, and 12% of the shortest. The rest still slides along the
cone's flank and crosses its layer, and the absorbing layers have taken
0.04–2%. A field that straddles the window's edge picks up a negative share
from the edge itself, and the axis controls put that share at
\(1\)–\(6\times10^{-3}\). The measured shares sit at the same level, so the
run bounds the mixing at a few \(10^{-3}\) per packet for wavelengths 0.5–2.
Finer resolution takes the scattered field into flat space far from the
structure, on a larger grid and a longer run. Emission at the bound carries a
power of order \(|\beta|^2\hbar c^2/L^2\) per mode channel, about
\(10^{-19}\) W at \(L=1\) m.

## Open items

1. **Renormalized stress in 3+1.** The full stress, by Hadamard subtraction
   on evolved modes, at the tip and across the pattern.
2. **Emission rate.** The mixing below \(10^{-3}\), read from the scattered
   field far from the structure; its spectrum over frequency and angular
   momentum; its rate; and the mixing at speed 10.
3. **Fields through the transitions.** Field evolution while the cone
   extends and the carry speed passes 1.
4. **Rays and modes off the meridian.**

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_quantum_estimates_pass.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli:toolkit/adm_harness_cli/scripts python -m pytest toolkit/adm_harness_cli/tests/test_quantum_estimates.py
```

The mixing stage takes nearly all of the run time. Its recorded run took 110
minutes with four workers while an eight-process climate model shared the
machine's eight cores; at the step rate of an unloaded machine each packet
takes about 25 minutes. The other stages take about a minute with
`--stages anomaly,rear,control,physical`. The manifest records the sampled
times, the anomaly coefficients, the packets, the grid, the control depths,
the rail scales and the software hashes of each stage. The tests check
the scalar anomaly against its Riemann and Ricci form, the contractions
against the demanded tensor, the vanishing trace in the compartment, the
compartment's unit Killing norm, the sampled times of the half-extended
cone, the radial transform against a Gaussian's, the positive frequency of
every packet, the flat-space window, and the control's floor and edge
readings.
