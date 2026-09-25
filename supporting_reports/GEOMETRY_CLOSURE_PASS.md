# Geometry Closure Pass: Trimming, Speed and Path Audits

Date: 2026-09-25. Context: the [front light surface pass](FRONT_LIGHT_SURFACE_PASS.md)
and the [cone tip field pass](CONE_TIP_FIELD_PASS.md) left the geometry with
three open items. Every result so far was at a lane speed of 2.1. The demand
had two untried levers. The service audits had yet to run along the
compartment's path with the conical front. This pass closes all three on the
prescribed metric. Run: `scripts/run_geometry_closure_pass.py`, with data in
[data/geometry_closure_pass](data/geometry_closure_pass/).

## Result

- **Trimmed reference.** The reference design now has a plateau of \(e^{3}\)
  and a shift edge of width 1. Its outer lapse fall is pulled in to
  \(8.75\le r\le10.75\), from \(9.25\le r\le13.25\), and its cone base is 14,
  down from 16.
  - It passes the full gate: 2.41 million points around the pattern and 0.26
    million across the cone, all Type I, with the refinement likewise and no
    band.
  - Its peak negative-null content is 252 against 333, and its peak stress
    1.81 against 2.91.
  - The tip keeps \(\kappa=0.563\) and \(\lambda=2.70\). Swept matter leaves at
    \(\gamma\le11.5\) and light at gains up to 11.6, on both lane lengths.
- **Speed is a lapse contrast.** Raising the plateau and cone log-lapse by
  \(\ln(v/2.1)\) leaves the geometry around the shift the same up to a
  rescaling of time. The demanded tensor there at 10 matches its value at 2.1
  to \(10^{-5}\). Only the pure-lapse parts change with speed: the
  compartment's hole, the outer falls and the cone.
- **Every part of a front advances along its normal slower than light.** A
  cone of half-angle \(\theta_c\) moves its flank along the flank's normal at
  \(v\sin\theta_c\). Once that exceeds the exterior light speed, light moving
  along the normal rides the flank and blueshifts all the way to the base. The
  15° cone does this above \(1/\sin15°=3.9\), with swept gains of
  \(3.7\times10^{6}\) at 5 and \(8\times10^{11}\) at 10. Scaling the half-angle
  as \(\sin\theta_c=0.54/v\), the margin the cone has at 2.1, keeps the flank
  at 0.54 of the light speed along its normal.
- **Speed scan.** With the scaled cone, every speed from 1.5 to 20 passes the
  gate with no Type IV point.
  - Swept gains stay bounded on both lane lengths, growing roughly as \(5v\):
    12 at 2.1, 49 at 10, 96 at 20.
  - Peak stress grows as \(\ln v\), from 1.5 to 4.8.
  - Peak content grows with the cone's length, which is proportional to speed:
    211 at 1.5, 787 at 10, 1,529 at 20.
  - Passengers at clock rate 1 age 174 days per light-year of lane at 2.1, 37
    at 10 and 18 at 20.
- **Path audits.**
  - Escape: all light launched from the compartment in every direction reaches
    flat space, without blueshift. Its largest gain is 1.00 at 2.1.
  - The compartment is a lapse cavity. Light leaves it during the carry only
    within 1.05° of the normal of its boundaries at 2.1, and within 0.22° at
    10. That is about 2% of light emitted evenly inside at 2.1, and 0.4% at
    10. The rest reflects inside until the lapse relaxes at arrival, so
    passengers see out through narrow cones and a closed cabin keeps most of
    its radiated heat.
  - Reachability: light reaching the compartment comes from ahead along the
    axis and from the region around the packet at departure.
  - Bundles: fans of neighbouring rays keep their width, except a fan grazing
    the cone's tip, which the tip focuses into a caustic.
  - At 10 with the scaled cone the audits repeat this picture. The largest
    gain during the carry is 1.02, and again only the fan grazing the tip
    narrows.

## The trimming screen

The screen applies the gate at spacing 0.5 in \(\sigma\) and 0.2 along the
track around the pattern, without the cone, and records the demand and the
radius out to which the pattern's own lapse exceeds the carry speed. That
radius sets the cone's base.

| Variant | Type IV points | Peak content | Peak stress | Peak negative energy | Radius with lapse above \(v\) |
|---|---:|---:|---:|---:|---:|
| previous reference | 0 | 198 | 2.91 | 0.0013 | 12.2 |
| plateau \(e^{3}\) | 0 | 176 | 1.82 | 0.0096 | 12.1 |
| shift edge 1 | 0 | 180 | 2.91 | 0.0012 | 12.2 |
| outer fall from 8.75 | 0 | 190 | 2.91 | 0.0013 | 10.2 |
| sheath rise 4.5, outer fall from 8.25 | 0 | 179 | 2.91 | 0.0012 | 9.7 |
| sheath rise 4, outer fall from 7.75 | 242 | 168 | 2.91 | 0.0011 | 9.2 |
| sheath rise 3, outer fall from 7.25 | 262 | 155 | 2.91 | 0.0007 | 9.1 |
| plateau \(e^{3}\), outer fall from 8.75 | 0 | 168 | 1.82 | 0.0096 | 10.2 |
| **plateau \(e^{3}\), outer fall from 8.75, shift edge 1** | **0** | **149** | **1.82** | **0.0090** | **10.2** |
| the same with shift edge 0.75 | 0 | 136 | 1.84 | 0.0088 | 10.2 |
| the same with plateau \(e^{2.5}\) | 620 | 138 | 1.43 | 0.0245 | 10.1 |
| the same with sheath \(e^{0.5}\) | 3,610 | 138 | 1.82 | 0.0107 | 10.1 |

The outer fall lies where the shift vanishes, so any profile there is Type
I, and it can be pulled in freely. The sheath's rise has to continue across
the whole of the shift's radial transition, \(4.25\le r\le6.25\): compressed
to a width of 3 or 4, it levels off near \(r\approx5.5\), and Type IV points
appear there during the carry. The plateau \(e^{3}\) takes 38% off the peak
stress, because the compartment's hole is one e-fold shallower. It raises the
small negative energy of the shift's radial transition from 0.0013 to 0.009,
and the worst lapse-envelope ratio from 0.08 to 0.50, still below one. A shift
edge of 0.75 also passes, with an envelope ratio of 0.66. The reference keeps
the edge at 1 for margin.

## The trimmed reference

| Measure | Previous cone reference | Trimmed reference |
|---|---:|---:|
| gate around the pattern: Type I points (Type IV) | 3,315,848 (0) | 2,413,034 (0) |
| refined: half jet step, double nodes, every other \(\sigma\) | 3,315,829 (0) | 2,412,967 (0) |
| gate across the cone: Type I points (Type IV) | 229,150 (0) | 255,794 (0) |
| resolved banded crossings | 0 | 0 |
| worst lapse-envelope ratio | 0.08 | 0.50 |
| peak negative-null content | 333 | 252 |
| content integrated over \(\sigma\), 12.6 trip | 3,114 | 2,361 |
| of which in the cone's window | 518 | 494 |
| peak stress component | 2.91 | 1.81 |
| peak negative energy | 0.0013 | 0.009 |
| largest lapse | 1,694 | 395 |
| cone base, length ahead of the packet | 16, 66.5 | 14, 58.0 |
| tip: \(\kappa\), \(\lambda\) | 0.563, 2.70 | 0.563, 2.70 |
| swept matter, largest \(\gamma\) (12.6 / 25.2 trips) | 6.7 / 12.2 | 5.9 / 11.5 |
| swept light, largest gain | 11.6 | 11.6 |

At one unit equal to one metre, the peak content is \(0.17M_\odot\) against
\(0.22M_\odot\), and the peak stress is \(2.2\times10^{44}\) Pa against
\(3.5\times10^{44}\) Pa.

## Speed as a lapse contrast

Around the shift, the metric \(-\alpha^2d\sigma^2+(dz+\beta\,d\sigma)^2+dr^2+r^2d\phi^2\)
depends on the lapse and the shift through \(\alpha\,d\sigma\) and
\(\beta\,d\sigma\). Multiplying both by the same factor \(c\) is a
rescaling of \(\sigma\), so the local geometry is unchanged. The pattern's
position advances \(c\) times faster per unit \(\sigma\), which is a carry
speed of \(cv\). The exterior keeps a lapse of one, so the whole difference
sits where the lapse returns to one. Those regions are shift-free or
shift-uniform and therefore Type I for any profile: the hole around the
compartment, the outer falls and the cone. At mid-lane the demanded tensor
across the shift's edges and radial transition at a carry speed of 10
matches the tensor at 2.1 to \(10^{-5}\), with the plateau log-lapse raised by
\(\ln(10/2.1)\) (`tests/test_speed_scaling.py`).

## The cone at speed

A surface of the moving pattern whose normal makes angle \(\theta_c\) with
the radius moves along that normal at \(v\sin\theta_c\). Light moving along
the normal keeps pace with the surface where its local speed \(\alpha\)
equals \(v\sin\theta_c\). The cone's layer holds every lapse from one up to
its interior value, so that point exists as soon as \(v\sin\theta_c>1\). The
light then rides the flank toward the base and blueshifts all the way. The
ray traced at 10 settles at 75° to the axis, perpendicular to the 15° flank,
and gains five e-folds per unit time. At the tip itself the normal is the
axis, and there the transverse lapse curvature does the work, as the
[cone tip field pass](CONE_TIP_FIELD_PASS.md) found.

With the half-angle fixed at 15°, the scan shows the threshold.

| Speed | 1.5 | 2.1 | 3 | 5 | 10 | 20 |
|---|---:|---:|---:|---:|---:|---:|
| \(v\sin15°\) | 0.39 | 0.54 | 0.78 | 1.29 | 2.59 | 5.18 |
| swept matter, largest \(\gamma\) | 5.4 | 9.4 | 12.3 | \(3.4\times10^{4}\) | \(3.2\times10^{11}\) | \(2.6\times10^{14}\) |
| swept light, largest gain | 6.0 | 11.8 | 36 | \(3.7\times10^{6}\) | \(7.9\times10^{11}\) | \(5.1\times10^{14}\) |

With \(\sin\theta_c=0.54/v\) the flank keeps the margin it has at 2.1.

| Speed | Half-angle | Cone length ahead of the packet | Type IV points | Peak content | Content over \(\sigma\) | of which in the cone | Peak stress | Largest lapse | Tip \(\kappa\), \(\lambda\), ratio | Swept \(\gamma\) (lanes ending at \(\sigma=6\) / 9) | Swept light | Lead over light, test trip | Passenger days per light-year |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| 1.5 | 21.2° | 41.8 | 0 | 211 | 2,040 | 214 | 1.54 | 223 | 0.44, 1.64, 3.7 | 6.6 / 3.9 | 8.9 | 1.5 | 244 |
| 2.1 | 15.0° | 58.0 | 0 | 252 | 2,367 | 400 | 1.82 | 395 | 0.56, 2.70, 4.8 | 9.4 / 4.2 | 11.8 | 5.1 | 174 |
| 3 | 10.4° | 81.7 | 0 | 311 | 2,775 | 680 | 2.18 | 739 | 0.68, 4.37, 6.4 | 12.9 / 5.0 | 15.9 | 10.5 | 122 |
| 5 | 6.2° | 133.8 | 0 | 442 | 3,782 | 1,479 | 2.75 | 1,808 | 0.83, 8.31, 10.0 | 19.4 / 26.2 | 25.3 | 22.5 | 73 |
| 10 | 3.1° | 262.9 | 0 | 787 | 6,182 | 3,634 | 3.65 | 6,094 | 1.02, 18.8, 18.5 | 46.8 / 44.8 | 48.8 | 52.5 | 37 |
| 20 | 1.6° | 520.7 | 0 | 1,529 | 11,260 | 8,486 | 4.77 | 20,530 | 1.18, 41.0, 34.9 | 92.4 / 93.8 | 95.9 | 112.5 | 18 |

The swept gains follow from the exit-angle law of the
[front light surface pass](FRONT_LIGHT_SURFACE_PASS.md),
\((v-1)/(v\cos\theta_f-1)\). A faster pattern turns what it overtakes
through larger angles, and the gain grows roughly as \(5v\), bounded on both
lane lengths. Each lane's launch grid spans its own reach, so the two maxima
sample different objects; at 10 and 20 they agree to 5%. The tip grows safer with speed: its ratio of
transverse escape to blueshift rises from 3.7 to 35, because the slender
cone's lapse rises gently along the axis. The cost moves into the cone.
Above a speed of about 3, most of the demand lies in the cone, and it grows
with the cone's length, in proportion to the speed.

## Path audits

The audits trace light in three dimensions through the trimmed reference, on
a lane from \(\sigma=1.5\) to 12 so that light crossing the long cone can
leave before the pattern slows.

**Escape.** From the compartment's centre and from an off-centre point, light
is launched in 16 directions at six times: during switch-on, during
acceleration, twice in the lane, during deceleration, and at rest before
switch-off. The audit records when each ray first stands in flat space,
outside both the lapse structure and the shift.

| Launch \(\sigma\) | Rays | Leave during the carry | Reach flat space by the end | Median time to leave | Longest | Largest energy gain |
|---:|---:|---:|---:|---:|---:|---:|
| −2 (switch-on) | 32 | 32 | 32 | 0 | 0 | 1.01 |
| 0.75 (acceleration) | 32 | 7 | 32 | 12.7 | 13.1 | 1.00 |
| 3 (lane) | 32 | 7 | 32 | 10.5 | 11.3 | 1.00 |
| 7 (lane) | 32 | 7 | 32 | 6.5 | 7.8 | 1.00 |
| 12.75 (deceleration) | 32 | 0 | 32 | 0.7 | 2.1 | 1.00 |
| 14.5 (at rest) | 32 | 0 | 32 | 0 | 0 | 1.00 |

Every ray reaches flat space, and none gains energy. The rays that leave
during the carry point straight back along the axis or straight out from it,
and they leave within 2 to 5 units. Most of the others stay in the
compartment until the lapse structure relaxes at arrival.

In the pattern's frame the compartment and the hole around it are static,
since the shift there is uniform and equal to minus the carry speed. There a
lapse acts on light as a refractive index \(1/\alpha\), with the Killing energy
\(\alpha|k|\) conserved. Light leaving the compartment climbs from the clock lapse
of 1 to the plateau and sheath, which reach 55 at 2.1 both radially and along
the axis. It is totally reflected unless its direction lies within
\(\arcsin(1/55)=1.05°\) of the boundary's normal, and the traced rays reflect
exactly as that predicts. Light emitted evenly at the compartment's centre
escapes at a share of \(1/55\), about 2%, through a band within 1° of the
transverse plane. The rest reflects inside with its energy unchanged. The
forward ray along the axis passes the boundary at normal incidence. It then
crosses the cone's interior, whose lapse exceeds the carry speed, and leaves
after the lane. When the speed rises, the plateau lapse grows in proportion,
and at 10 the escape cone narrows to 0.22°, a share of 0.4%.

The cavity sets two conditions for a crewed compartment. Passengers see out
through narrow cones along the axis and across it, with the Doppler shift of
their motion. A closed cabin also keeps about 98% of the heat it radiates
for the length of the carry. It needs heat storage, or radiators beamed
along the escape directions.

**Reachability.** Light arriving at the compartment's centre from 16
directions at four times is traced back to before switch-on.

| Arrival \(\sigma\) | From ahead | From behind | From around the departure point | From the side |
|---:|---:|---:|---:|---:|
| 0.75 | 1 | 1 | 14 | 0 |
| 3 | 1 | 1 | 14 | 0 |
| 7 | 1 | 1 | 14 | 0 |
| 12.75 | 1 | 1 | 12 | 2 |

Light arriving along the axis from the front comes from ahead, so passengers
see forward along the track. The light arriving from other directions was
around the packet when the lapse structure switched on, and it has crossed
the raised lapse since. After the pattern slows, light from the side reaches
the compartment again.

**Bundles.** Fans of 15 parallel rays spaced 0.05 apart are followed for
crossings and for their narrowest width relative to the start.

| Fan | Narrowest width | Final width | Crossings |
|---|---:|---:|---:|
| overtaken along the axis | 1.00 | 1.05 | 0 |
| overtaken off the axis | 1.00 | 6.87 | 0 |
| inward from the side | 1.00 | 1.00 | 0 |
| forward from behind | 1.00 | 1.00 | 0 |
| from the compartment, forward | 1.00 | 1.02 | 0 |
| from the compartment, backward | 1.00 | 1.00 | 0 |
| from the compartment, sideways | 1.00 | 1.00 | 0 |
| grazing the cone's tip | \(9\times10^{-4}\) | 1.16 | 14 |

The one fan that narrows grazes the tip. Its rays are pushed off the axis
with different strengths, and neighbours cross in a fold caustic. The fan
then widens again. A caustic concentrates intensity along a surface while
conserving energy, and the gains of the rays through it stay bounded.

**At 10.** With the scaled cone, the audits at 10 repeat these results.

- **Escape.** Every ray launched from the compartment reaches flat space, with
  a largest gain of 1.02 during the carry. Six of the 32 rays at each carry
  time leave before the pattern slows, the directions inside the 0.22° escape
  cone. Light launched during switch-on is swept by the forming cone and
  leaves with gains up to 46, within the swept bound at that speed.
- **Reachability and bundles.** Reachability matches 2.1. Of the bundles, only
  the fan grazing the tip narrows, to \(1.0\times10^{-3}\), and it widens again.

The same audit with the 15° cone at 10 records the flank trap. There, light
launched from the compartment during switch-on and acceleration leaves with
gains up to \(7\times10^{19}\).

## Where the geometry stands

On the prescribed metric, the carry now closes at every tested speed from
1.5 to 20:
- every evaluated point is Type I;
- light and matter overtaken by the pattern leave with bounded energy on every
  lane length;
- no front horizon forms;
- light from the compartment reaches flat space in every direction, promptly
  within about 1° of the compartment's boundary normals, and at arrival for
  the rest, which the compartment's lapse contrast reflects;
- passengers see ahead, ride in a flat compartment and age at a chosen rate.

Speed costs little in the pattern itself: peak stress grows as \(\ln v\). The
front's length grows with \(v\), and above a speed of about 3 the cone carries
most of the demand.

## Open items

1. **Cone shape at speed.** A flank that curves, keeping its normal speed
   below the light speed everywhere, could shorten the cone at high speed.
2. **Cabin environment.** The compartment is a lapse cavity, with escape
   cones set by the ratio of clock lapse to plateau lapse. It needs a view
   and a heat path through those cones.
3. **Achronal null energy.** The map of the averaged null energy along
   complete light rays through the pattern, the next tier.
4. **Quantum magnitudes.** The trace anomaly, the rear horizon's flux and the
   mode mixing in the outrun exterior, also the next tier.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_geometry_closure_pass.py --workers 4
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_geometry_closure_pass.py --workers 4 --stages speed_scaled,audit_scaled
```

The first command runs the trimming screen, the reference, the fixed-cone
speed scan and the audits at 2.1 and 10, in 1.8 hours with four workers. The
second runs the scaled-cone scan and the audit at 10 with the scaled cone,
in 54 minutes. The manifest records the specifications, the stages and the
software hashes of each run.
