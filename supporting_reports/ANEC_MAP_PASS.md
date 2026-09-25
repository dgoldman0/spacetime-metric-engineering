# ANEC Map Pass: Averaged Null Energy Along Complete Light Rays

Date: 2026-09-25. Context: the [geometry closure pass](GEOMETRY_CLOSURE_PASS.md)
closed the prescribed geometry of the trimmed reference, with the cone's
half-angle scaled to the speed. This pass maps the averaged null energy
(ANEC) along complete light rays through that design. It identifies the
achronal ones, the first light to reach a point, where quantum fields obey a
lower bound of zero. Run: `scripts/run_anec_map_pass.py`, with data in
[data/anec_map_pass](data/anec_map_pass/).

## Result

- **The first light from the departure carries negative ANEC.** The first
  light to reach a plane just past the packet's arrival leaves the departure
  event along the axis. It lies on the boundary of the departure's causal
  future, so it is achronal.

  | Carry speed | Lane | Lead over exterior light | ANEC |
  |---|---|---:|---:|
  | 2.1 | 12.6 trip | 11.4 | −0.0012 |
  | 10 | test trip | 58 | −0.0007 |
  | 2.1 | ending at \(\sigma=30\) | 50.5 | −202 |
  | 10 | ending at \(\sigma=30\) | 287 | \(-2.2\times10^{4}\) |

  On the long lanes the ray reaches the cone's tip and rides it on the axis,
  blueshifting all the while.
- **The negative part lies in the cone.** There the lapse peaks on the axis,
  and for light along the axis \(T(k,k)=\alpha_{rr}/(4\pi\alpha)\), which is
  negative. The first light travels through the cone's interior, whose lapse
  of 4.48 (21 at 10) exceeds the carry speed. That is how it outruns both the
  packet and exterior light.
- **Every other ray from the departure arrives later and carries positive
  ANEC**, up to 8. Most of it comes from reflections at the compartment's lapse
  boundary, the cavity found in the closure pass.
- **Rays crossing the pattern.**
  - Backward along the axis: \(-0.3\), or \(-1.9\) at 10.
  - Overtaken on the exact axis during the long lane: \(-5\times10^{4}\), or
    \(-1.3\times10^{11}\) at 10, riding the tip.
  - Overtaken off the axis: \(+0.1\) to \(+0.2\), with bounded energy.
  - Inward from the side: about \(-0.02\).
- **What this fixes about the source.** The design needs negative ANEC along
  achronal light rays, as any lead over exterior light does. Achronal ANEC
  holds for quantum field theories in flat space (Faulkner, Leigh, Parrikar
  and Wang 2016; Hartman, Kundu and Tajdini 2017). In curved space it holds
  for free fields at small curvature (Kontou and Olum 2015), and it is the
  proposed self-consistent condition (Graham and Olum 2007). A semiclassical
  quantum sector therefore supplies none of this demand, at any size. The
  [source scaling test](SOURCE_SCALING_TEST.md) confined such sectors by
  magnitude; this result confines them in principle. The source class that
  remains is classical fields that violate ANEC, of which the
  higher-derivative scalars are the open family.

## Method

For a null geodesic the ANEC integral is \(\int T(k,k)\,d\lambda\) over its
affine parameter. The meridional tracer advances in exterior time \(\sigma\),
with \(d\lambda=\alpha\,d\sigma/|k|\). Writing \(T(k,k)=|k|^2T(e,e)\), with
\(e=n+k/|k|\) in the normal observers' frame, the integrand becomes
\(\alpha|k|\,T(e,e)\,d\sigma\). Each ray is traced both ways from its launch
point, from \(\sigma=-3\), before the structure switches on, to twelve units
after the packet comes to rest. That makes it complete, with \(k\) of unit
energy at the start. The demanded tensor is sampled every 0.004 in
\(\sigma\), and the integral is split by region: compartment, hole boundary,
the shift's extent, the rest of the pattern, the cone, and flat space.

The departure fan leaves the packet's centre at the start of the carry, at
angles from straight ahead to straight back. The first ray of the fan to
reach the plane two units past the packet's arrival generates the boundary
of the departure's causal future. It is achronal. Every later ray reaches
events that the first light already reached, so those rays are chronal, and
achronal ANEC places no bound on them. The run repeats the fan on the 12.6
trip and on a lane ending at \(\sigma=30\), long enough for the first light
to reach the cone's tip, at carry speeds 2.1 and 10.

## The departure fan

| Launch angle | ANEC, 2.1, test trip | ANEC, 2.1, long lane | ANEC, 10, test trip | ANEC, 10, long lane |
|---:|---:|---:|---:|---:|
| 0° (first light) | −0.0012 | −202 | −0.0007 | \(-2.2\times10^{4}\) |
| 0.5° | 1.06 | 4.55 | 0.002 | 0.002 |
| 2° | 0.41 | 5.54 | 0.16 | 4.96 |
| 10° | 0.75 | 1.24 | 1.03 | 3.94 |
| 45° | 2.56 | 2.69 | 3.16 | 8.13 |
| 90° | 0.021 | 0.021 | 0.028 | 0.028 |
| 180° | 0 | 0 | 0 | 0 |

The first light reaches the plane at \(\sigma=14.5\) on the long lanes. Every
other ray of the fan reaches it from \(\sigma=23.5\) on, or only after the
lapse structure relaxes. Off the axis, even at 0.5°, light lies outside the
compartment's forward escape cone. It reflects inside until the pattern
slows, which is where its positive ANEC comes from. The forward cone is the
narrowest of the compartment's escape cones, 0.36° at 2.1 and 0.023° at 10.
Just ahead of the shift the cone's lapse adds to the plateau, and the lapse
on the way forward reaches 161 at 2.1 and 2,500 at 10. Light sent straight
back or straight out crosses regions where \(T(k,k)\) nearly vanishes along
its direction, and its integral is close to zero.

## Rays crossing the pattern

| Ray, launched at mid-lane | 2.1, test trip | 2.1, long lane | 10, test trip | 10, long lane |
|---|---:|---:|---:|---:|
| backward along the axis, from ahead of the tip | −0.32 | −0.31 | −1.91 | −1.90 |
| backward at \(r=3\) | 0 | 0.13 | 0 | 0.23 |
| overtaken on the axis | — | \(-5.0\times10^{4}\) | −2.5 | \(-1.3\times10^{11}\) |
| overtaken at \(r=1\) | — | 0.12 | 0.13 | 0.17 |
| overtaken at \(r=6\) | — | 0.15 | — | 0.23 |
| inward from the side, at the packet | 0.003 | −0.016 | −0.001 | −0.019 |
| inward from the side, at the cone | — | −0.023 | — | −0.028 |

A dash marks a ray that the pattern does not reach before it slows. The
largest magnitudes belong to the exact axis. There light overtaken by the
pattern rides the tip's light surface and blueshifts, which is the one
trapped set the [cone tip field pass](CONE_TIP_FIELD_PASS.md) found. Light
overtaken off the axis slides off with bounded energy and positive ANEC.

## Open items

1. **Quantum magnitudes.** The trace anomaly, the rear horizon's flux and the
   mode mixing in the outrun exterior, the rest of this tier.
2. **Rays off the meridian.** Rays with angular momentum about the axis, and
   the first light to points off the axis.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_anec_map_pass.py --workers 4
```

The run traces 80 complete rays in about an hour with four workers. The
manifest records the sampling, the speeds, the lanes and the software hashes.
