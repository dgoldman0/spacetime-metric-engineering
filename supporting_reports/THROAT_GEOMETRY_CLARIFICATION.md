# Geometry Clarification: The Throat-Supported Shift Rail

Date: 2026-09-24. Scope: the May 2026 paper *From the Warp/Wormhole
Interface to a Throat-Supported Shift Rail* (preprint,
[doi:10.13140/RG.2.2.10402.39368](https://doi.org/10.13140/RG.2.2.10402.39368)),
and the [technical disclosure](../active_rail_technical_disclosure.tex)
through its constant-radius revision. A one-page public addendum carries the
same clarification: [addenda/2026-09_Throat_Supported_Shift_Rail_Addendum.pdf](../addenda/2026-09_Throat_Supported_Shift_Rail_Addendum.pdf).

## Summary

The earlier geometry is a traversable wormhole carrying a shift service
along its throat. The May paper says so in its own terms: the wormhole side
supplies the plant and the warp side supplies the transport handle. The
technical disclosure kept the same metric, describing it as a
"Morris–Thorne-like intrinsic throat/support geometry", while presenting the
system as a rail between two endpoints. Three of its readings belong to a
rail through one space:
- its comparison with an exterior light signal;
- its throat relaxation;
- its premise that sources are available.

The one-space geometry of the current work places the rail along an axis in
ordinary space. The paper's two service rules and its service sequence
carry forward into it directly.

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
  (`source_ledger.scalars`). This is the Ellis–Morris–Thorne throat, with
  minimum radius \(R_{th}\) at \(l=0\) and \(R\to|l|\) on both sides. The
  angular capacity jacket \(c_\Omega=e^{0.2\,q_\Omega w_\Omega}\) widens the
  throat by up to 22% until \(\sigma\approx2\) and then relaxes.
- **Constant-radius track.** It holds \(R=R_b=1.75\) for \(|l|\le5\) and
  flares to \(R'=1\) beyond \(|l|=6.5\) at both ends
  (`constant_radius_track.areal_radius`). The whole track then sits at the
  minimum radius.

Either profile joins two asymptotically flat regions through a minimal
sphere, so the spatial slices have the topology \(\mathbb R\times S^2\) with
two ends. The flare-out sits in the end transitions, where both radial null
energies equal \(-R''/4\pi R\). Along the constant-radius track the radial
block is a string cloud with zero radial null energy. With the shift off,
the lapse is positive and finite everywhere. The escape and reachability
audits carried radial light across the throat both ways, so the throat is
traversable as a static geometry. The shift is the transport service riding
along it.

## Three readings that belong to one space

1. **The exterior light comparison.** The disclosure's service-time ledger
   compares the packet's service time with an exterior null signal between
   endpoints A and B. It takes the rail coordinate as their distance, through
   the "modeled tube relation \(l=\sigma\)". The two sides of the throat lie in
   separate asymptotic regions, and the reduced metric contains no exterior
   path between them. The V = 5 ratios, 2.569 on the schedule factor and 1.233
   on the packet coordinate, therefore compare throat traversal with a
   flat-space reference placed by that assumption.
2. **Throat relaxation.** The service sequence ends
   "relax throat → reset". In the code, the relaxation acts on three things:
   - the support stretch (\(C_0=100\), \(B_0=8\));
   - the support lapse (\(\lambda C_0=600\));
   - the angular capacity jacket.

   The minimal sphere of radius 1.75, and with it the two ends, persists
   through every service.
3. **Source availability.** The paper's premise supplies the stress that
   holds a throat open. Forming a two-ended space from ordinary space
   requires a change of spatial topology, which in a compact region brings
   closed timelike curves (Geroch, *J. Math. Phys.* 8, 782 (1967)).

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

\[
ds^2=-\alpha^2d\sigma^2+(dz+\beta\,d\sigma)^2+dr^2+r^2d\phi^2,
\qquad
\rho=-\frac{1}{32\pi}\left(\frac{\beta_r}{\alpha}\right)^2 .
\]

The service region \(r\le1.75\) carries the lapse and shift. A transverse
boundary layer returns them to Minkowski values by \(r=13.25\). The design
and its results are in the [lapse and staging pass](LAPSE_AND_STAGING_PASS.md):
- **Gate.** Every non-vacuum boundary-layer point is Type I, including
  under refinement.
- **Arrival and packet.** The 2.1c lane arrives 1.66 ahead of light through
  flat space, with the packet timelike throughout.
- **Standing geometry.** It is flat space.
- **Demand.** A tension without energy acts during each transit, local to
  the packet: peak stress 2.9 and peak negative energy
  \(1.9\times10^{-4}\).

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
