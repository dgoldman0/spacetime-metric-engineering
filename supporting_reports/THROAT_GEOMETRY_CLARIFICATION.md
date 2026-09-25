# Geometry Clarification: The Throat-Supported Shift Rail

Date: 2026-09-24. Scope: the May 2026 paper *From the Warp/Wormhole
Interface to a Throat-Supported Shift Rail* (preprint,
[doi:10.13140/RG.2.2.10402.39368](https://doi.org/10.13140/RG.2.2.10402.39368)),
and the technical disclosure at commit
`2146526c7a70691cd1ac1f8f4928b99d7cca0c19` (2026-09-23), its constant-radius
revision
([PDF at that commit](https://github.com/dgoldman0/spacetime-metric-engineering/blob/2146526c7a70691cd1ac1f8f4928b99d7cca0c19/active_rail_technical_disclosure.pdf)).
The disclosure will be revised after the source evaluation, and references
to it here and in the addendum name that commit. A two-page public addendum
carries the corrections: [addenda/2026-09_Throat_Supported_Shift_Rail_Addendum.pdf](../addenda/2026-09_Throat_Supported_Shift_Rail_Addendum.pdf).

## Summary

The earlier geometry is a two-ended, traversable wormhole of Morris–Thorne
type. The earlier system is an active rail laid through its throat. The May
paper describes this combination in its own terms: the wormhole side
supplies the plant and the warp side supplies the transport handle.

The technical disclosure kept the same metric, calling it a
"Morris–Thorne-like intrinsic throat/support geometry", while presenting the
system as a rail between two endpoints.

The paper has six issues, listed below with their evidence:
1. It leaves the topology unstated.
2. Its source premise is incomplete.
3. Its own relaxation step demands a Type IV stress.
4. It reads the packet's motion two ways.
5. It leaves the throat's shortcut and the shift's transport unseparated,
   which the disclosure's service-time ratios then inherit.
6. Its confidence statement overreaches.

The Garattini–Zatrimaylov obstruction concerns warp bubbles crossing a
wormhole. The rail's shift lies outside it, because the shift is the
throat's own radial field.

The one-space geometry of the current work is a track-only rail: a
packet-safe service region in ordinary space, with no throat. The paper's
two service rules and its service sequence carry forward into it directly.

## The earlier geometry

Both documents use the spherically symmetric reduced metric

\[
ds^2=-\alpha^2d\sigma^2+\gamma_{ll}\,(dl+\beta\,d\sigma)^2+\gamma_{\Omega\Omega}\,d\Omega^2 ,
\]

with the rail coordinate \(l\) as its radial direction and
\(R=\sqrt{\gamma_{\Omega\Omega}}\) the radius of the spheres around it. The
radius took two profiles:
- **beta075 service.** The service sets
  \(\gamma_{\Omega\Omega}=(l^2+R_{th}^2)\,c_\Omega^2\) with \(R_{th}=1.75\)
  (`source_ledger.scalars`). This is the Ellis throat, with minimum radius
  \(R_{th}\) at \(l=0\) and \(R\to|l|\) on both sides. The angular capacity
  jacket \(c_\Omega=e^{0.2\,q_\Omega w_\Omega}\) widens the throat by up to
  22% until \(\sigma\approx2\) and then relaxes.
- **Constant-radius track.** It holds \(R=R_b=1.75\) for \(|l|\le5\) and
  flares to \(R'=1\) beyond \(|l|=6.5\) at both ends
  (`constant_radius_track.areal_radius`). The whole track then sits at the
  minimum radius, forming a long throat.

Either profile joins two asymptotically flat regions through a minimal
sphere, so the spatial slices have the topology \(\mathbb R\times S^2\) with
two ends. The geometry is therefore a spherically symmetric, two-ended
wormhole of Morris–Thorne type: an Ellis throat in the beta075 service and a
long throat of constant radius in the later revision. Its topology is
static, while the support stretch, the lapse and the shift change during a
service. The flare-out sits in the end transitions, where both radial null
energies equal \(-R''/4\pi R\). Along the constant-radius track the radial
block is a string cloud with zero radial null energy.

The throat is traversable in the Morris–Thorne sense. The lapse is positive
and finite everywhere, so the geometry has no horizon, and light and slow
travelers cross the throat directly. The escape and reachability audits
carried radial light across it in both directions. The metric leaves open
whether the two flat regions belong to one universe; the service-time
ledger assumed they do.

The earlier system is therefore an active rail laid through a wormhole, and
its shortcut has two sources. The throat's topology joins the two regions,
and the shift carries the packet along the throat.

## Relation to the wormhole–warp correspondence

Garattini and Zatrimaylov
([arXiv:2401.15136](https://arxiv.org/abs/2401.15136), *JCAP* 2024(08), 061)
write a Morris–Thorne wormhole in warp form. They use unit lapse and a
spatial form factor \(g=e^{\Phi}/\sqrt{1-b/r}\) that carries the intrinsic
curvature. Into that background they embed a localized Natário–Alcubierre
bubble and move it through the throat. At a throat free of horizons the
form factor diverges, and the bubble's shell meets a real curvature
singularity. A warp bubble therefore crosses only a wormhole with a
horizon, and a humanly traversable wormhole admits ordinary travel through
its throat.

The rail's shift belongs to another class. It is the throat's own radial
field, with three properties:
- it is spherically symmetric;
- it is written in the proper-distance coordinate \(l\), in which the Ellis
  throat is regular;
- it is paired with a non-unit lapse.

The correspondence paper identifies spherical warp drives, and a
reparametrized radial coordinate, as regular. Both carry an extra radial
function whose physical meaning the sources supply. The May paper's move
from a bubble crossing a completed throat to a throat that carries the
transport role directly is the choice of that class.

During a carry, the shift tilted the radial light cones far enough that one
radial null branch crossed zero while \(g_{\sigma\sigma}\) changed sign in
the active support band. The disclosure records this as the GZ-like cone
signature. It is a local, horizon-like tilt of the kind the correspondence
associates with warp traversal. The escape and reachability audits carried
rays out of that band, so no persistent horizon formed.

The current metric has flat spatial slices. It is the Natário–Alcubierre
form with a non-unit lapse, on the warp side of the correspondence.

## Issues in the May paper and the disclosure

1. **Unstated topology.** The paper presents the throat as infrastructure
   that the service prepares and relaxes: "prepare support → carry packet →
   catch packet → fade shift → relax throat → reset". It also draws on the
   prepared-route picture of the Krasnikov tube, a route through ordinary
   space. The geometry is a wormhole with two asymptotic ends, and the paper
   leaves that topology and its consequences unstated. In the code, the
   relaxation acts on three things:
   - the support stretch (\(C_0=100\), \(B_0=8\));
   - the support lapse (\(\lambda C_0=600\));
   - the angular capacity jacket.

   The minimal sphere of radius 1.75, and with it the two ends, persists
   through every service.
2. **Incomplete source premise.** The paper's premise supplies the stress
   that holds a throat open. Forming a two-ended space from ordinary space
   requires a change of spatial topology, which in a compact region brings
   closed timelike curves (Geroch, *J. Math. Phys.* 8, 782 (1967)). The
   paper's conditional feasibility claim therefore rests on a geometry that
   sources alone cannot produce.
3. **Inadmissible stress.** The paper's screen tests four things:
   - packet timelikeness;
   - a stationary monitor;
   - radial light speeds;
   - bundle compression.

   The algebraic type of the demanded stress lies outside it. The
   Hawking–Ellis classification applied later found a refinement-stable
   Type IV layer in the service family's V = 5 operating geometry, with
   13,587 points on its 141,661-point certification map
   ([boundary diagnostic](LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md),
   [constant-radius track](CONSTANT_RADIUS_TRACK.md)). The attribution run
   isolates the paper's own relaxation step. Support decompression alone,
   acting on the throat's varying areal radius, produces 874 Type IV points,
   against 842 for the full geometry on the same grid. It splits the two
   radial null energies into opposite signs, leaving the stress with no
   timelike eigenvector, so no source with a rest frame supplies it.
4. **Mismatched packet readings.** In the service family behind the paper,
   the packet windows advanced at unit coordinate speed while the packet-norm
   test used the carry speed \(U/B\). The packet screen therefore combined
   two readings of the packet's motion. The
   [choreography pass](CHOREOGRAPHY_PASS.md) aligns both to one prescribed
   path.
5. **Unseparated transport.** The paper describes traversal as a timed rail
   service and leaves the throat's shortcut and the shift's transport
   unseparated. The disclosure's service-time ledger then compares the
   packet's service time with an exterior null signal between endpoints A
   and B. It takes the rail coordinate as their distance, through the
   "modeled tube relation \(l=\sigma\)". The two sides of the throat lie in
   separate asymptotic regions, and the reduced metric contains no exterior
   path between them. The V = 5 ratios, 2.569 on the schedule factor and
   1.233 on the packet coordinate, therefore compare throat traversal with a
   flat-space reference placed by that assumption. The mismatch of item 4
   enters both. They are proxies, and the geometry defines no arrival lead.
6. **Overstated confidence.** The paper concludes that its reduced results
   "increase confidence" in a conditional engineering possibility. Given
   items 1–3, that confidence applies to its two service rules alone. The
   geometry on which they were tested requires a change of topology and
   demands inadmissible stress.

## Resolution

The termination decision chose one space. The
[axial track](AXIAL_TRACK.md) embeds the service around an axis in flat
space and returns every field to Minkowski values across a transverse
boundary layer. The later passes then tuned that embedding:
- the [one-space revision](ONE_SPACE_REVISION.md);
- the [choreography pass](CHOREOGRAPHY_PASS.md);
- the [demand census](DEMAND_CENSUS.md);
- the [amplitude pass](AMPLITUDE_PASS.md);
- the [lapse and staging pass](LAPSE_AND_STAGING_PASS.md).

The choreography pass gives the first well-posed arrival comparison. Packet
and light share one flat exterior and one coordinate distance, and the
packet leads light through flat space by 1.66, a mean of 1.35c.

## What carries forward

| May paper | Current design |
|---|---|
| shift inside its support envelope, \(\mathrm{supp}(\beta)\subseteq\mathrm{supp}(A,T)\) | the shift sits inside the convex packet lapse plateau; the lapse is the support, with unit stretch |
| catch before release | the rematch sleeve catches the packet before the release fade |
| prepare → carry → catch → fade shift → relax → reset | live windows and the lapse sheath switch on around the packet, carry it, release it and switch off, leaving flat space |
| packet worldtube as the passenger object | packet safety measured across the packet body along its path |

## Current state

The current design realizes the rail as a track in one flat space, with no
throat:

\[
ds^2=-\alpha^2d\sigma^2+(dz+\beta\,d\sigma)^2+dr^2+r^2d\phi^2,
\qquad
\rho=-\frac{1}{32\pi}\left(\frac{\beta_r}{\alpha}\right)^2 .
\]

- **Packet-safe region.** The service region \(r\le1.75\) plays this role.
  The packet rides the shift there, inside the convex lapse plateau.
- **Transverse boundary layer.** It returns the lapse and shift to
  Minkowski values by \(r=13.25\). In the staged form it exists only around
  the packet as it passes, and flat space remains behind each transit.
- **Lane.** The lane forms the track. Sources placed along the route switch
  on as the packet arrives.
- **Arrival.** The lead comes entirely from the shift and the lapse,
  measured against light through the same flat space. The 2.1c lane arrives
  1.66 ahead, a mean of 1.35c, with the packet timelike throughout.
- **Gate and demand.** Every non-vacuum boundary-layer point is Type I,
  including under refinement. During each transit the demand is a tension
  without energy, local to the packet: peak stress 2.9 and peak negative
  energy \(1.9\times10^{-4}\).

The design and its results are in the
[lapse and staging pass](LAPSE_AND_STAGING_PASS.md).

## For the disclosure update

The disclosure update follows the source evaluation.
- **Sections that carry over:** the service architecture, the catch and
  release choreography, the entry gating and the chronology governance.
- **Sections to replace:**
  - the reduced metric;
  - the constant-radius track and its end transitions;
  - the rail-stretch substrate;
  - the string-cloud source family;
  - the service-time ledger, which becomes the one-space arrival comparison.

The Garattini–Zatrimaylov discussion moves to the warp side of the
correspondence.
