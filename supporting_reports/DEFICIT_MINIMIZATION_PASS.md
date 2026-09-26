# Deficit Minimization Pass: Shaping the Lapse Falls

Date: 2026-09-26. Context: the [geometry closure pass](GEOMETRY_CLOSURE_PASS.md)
trimmed the pattern's negative-null content, the part of its demand that
violates the null energy condition, from 333 to 252 with a screen of a dozen
variants. This pass measures how far the pattern's shape can take that number
down, and where its floor lies. Run: `scripts/run_deficit_minimization_pass.py`,
with data in [data/deficit_minimization_pass](data/deficit_minimization_pass/).

## Result

- **The deficit falls 46%, to 137 at carry speed 2.1.** The minimized design
  passes the full gate: 2.48 million points across the pattern and the cone,
  all Type I, with no band, and 2.23 million refined. Its peak stress stays at
  1.84. At 10 the deficit falls from 787 to 591.
- **The design.** The falls along the track interpolate the lapse, with their
  onset drawn toward the plateau. The radial fall keeps the log-lapse and moves
  in to \(r=8.25\), inside the sheath's rise. The shift's along-track edge
  narrows to 0.75, and the cone takes a log-lapse of 1 with a rise of width 2.
  The compartment is unchanged: passengers at the 1× clock age with exterior
  time, with tides and acceleration at zero.
- **A floor.** Where the shift vanishes, the null energy condition fails
  wherever the two smallest eigenvalues of the lapse's Hessian sum below zero.
  Across a fall this gives at least the log-lapse drop times the plateau's
  integrated mean curvature over \(4\pi\), which is half the drop times the
  plateau's mean width. The floor is about 48 for the minimized design, against
  the 137 it carries.
- **The widths were the wrong lever.** Wider falls move deficit between regions
  and lengthen the cone. The shape of each fall sets its deficit.
- **The front rule decides between shapes.** Two branches that cut the deficit
  further break it at speed. A slow cone rise leaves a flat front across the
  pattern's front fall from 3 upward, and lapse-space radial falls tilt the
  pattern's side past it above 15. Both are recorded below. The minimized
  design keeps every piece of its front below 0.77 of light speed along its
  normal at every speed from 1.5 to 20.
- **At a one-metre scale** the deficit corresponds to \(0.092M_\odot\), from
  \(0.17M_\odot\).

## The floor

Where the shift vanishes or is uniform, the slices are flat and the demanded
stress is pure stress,
\(T_{ij}=(\delta_{ij}\nabla^2\alpha-\partial_i\partial_j\alpha)/8\pi\alpha\),
with zero energy density and flux. For a null direction \(k=n+e\) this gives
\(T(k,k)=(\nabla^2\alpha-e\cdot H\cdot e)/8\pi\alpha\), with \(H\) the Hessian
of the lapse. Its minimum over \(e\) is the sum of the two smallest eigenvalues
of \(H\), over \(8\pi\alpha\), so the null energy condition fails exactly where
that sum is negative.

Across a fall, let the lapse drop along the outward normal of level surfaces
with principal curvatures \(\kappa_1,\kappa_2\). Along their principal
directions \(H\) has the diagonal values \(\alpha_n\kappa_1\) and
\(\alpha_n\kappa_2\), and the sum of its two smallest eigenvalues never exceeds
that pair's sum. The deficit density is therefore at least
\(|\alpha_n|(\kappa_1+\kappa_2)/8\pi\alpha\), which integrates across the fall to
\(\Delta(\kappa_1+\kappa_2)/8\pi\) per unit area, with \(\Delta\) the log-lapse
drop. Over the plateau's boundary,
Minkowski's formula \(\int H\,dA=2\pi\bar b\) for its mean width \(\bar b\)
gives

\[
\text{deficit}\;\ge\;\frac{\Delta}{8\pi}\oint(\kappa_1+\kappa_2)\,dA=\frac{\Delta\,\bar b}{2}.
\]

For a plateau of radius \(R\) and length \(\ell\),
\(\bar b=(\ell+\pi R)/2\): its side contributes \(\Delta\ell/4\), a quarter of
the drop per unit length, and its two rims \(\Delta\pi R/4\). The flat end
caps carry no floor, and their deficit comes entirely from the lapse's
curvature across the fall. For the minimized pattern at 2.1, with
\(\Delta=4\) including the sheath, the floor is 38. The cone adds 9.5, the
deficit that radially moving light meets across its flank.

## The screen

The screen changes one lever at a time about the trimmed reference, with the
gate at spacing 0.5 in \(\sigma\) and 0.2 along the track, over the pattern and
the cone together. Each variant's cone takes the base the closure pass used:
the radius out to which the pattern's own lapse exceeds the carry speed, plus
the cone's layer, plus 0.8. The screen's peak content for the reference is 247,
against 252 on the full gate's finer sampling.

| Variant | Peak content | Peak stress | Type IV points | Cone base |
|---|---:|---:|---:|---:|
| reference | 247 | 1.81 | 0 | 14 |
| end falls 3 / 4 / 6 wide | 245 / 242 / 254 | 1.81 | 0 | 14 |
| radial fall 3 / 4 wide | 255 / 269 | 1.81 | 0 | 14.75 / 15.5 |
| radial fall from 8.25, sheath rise compressed | 231 | 1.81 | 46 | 13.5 |
| shift edge 0.75 | 243 | 1.84 | 0 | 14 |
| hole edge 1.5 along the track | 250 | 1.16 | 0 | 14 |
| hole edge 2 in radius | 248 | 1.72 | 0 | 14 |
| flattened joins 0.25 / 0.4 | 251 / 263 | 2.04 / 2.17 | 1,068 / 1,463 | 14 |
| cone log-lapse 1 / 1.25 | 219 / 233 | 1.81 | 0 | 14 |
| cone layer 4 | 238 | 1.81 | 0 | 15 |
| cone rise 3 | 226 | 1.81 | 0 | 14 |
| cone rounding 1 | 252 | 1.81 | 0 | 14 |

A split at mid-lane shows where the reference's deficit lies: 36 in the radial
fall, 62 in the falls along the track, 73 in the rims where the two meet, 14
inside the pattern and 64 in the cone. Widening the end falls from 2 to 6 takes
their share from 62 to 35 and lengthens the rims, whose share grows from 73 to
103. Widening the radial fall pushes the pattern's lapse out, and with it the
cone's base and length. The cone's lapse and rise pay directly. A longer
compartment edge takes 36% off the peak stress, which sits at the compartment's
lapse boundary in this design.

## Shapes

A term added to the pattern's log-lapse reshapes its outer falls, which lie
where the shift vanishes, so every shape keeps the stress Type I there
(`front_surface.pattern_correction`). Inside the plateau's core the term
vanishes. The falls can interpolate the lapse \(\alpha-1\) in place of the
log-lapse, and a warp \(t\mapsto t^q\) inside the step moves the onset of each
fall toward the plateau and lengthens its landing. The corners can take the
product of the two falls or a fall across the softened distance from the core.
The cone takes the same two options for its layer.

| Variant | Peak content | Peak stress |
|---|---:|---:|
| falls in the lapse | 247 | 7.73 |
| the same, warp 0.5 | 216 | 2.53 |
| the same, warp 0.35 | 212 | 6.25 |
| rounded corners, log-lapse | 254 | 1.81 |
| falls in the lapse, rounded, warp 0.5 | 222 | 2.52 |
| the same, radial fall from 8.25 | 208 | 2.50 |
| the same, end falls 3 wide | 216 | 2.11 |
| cone in the lapse, warp 1 / 0.5 | 240 / 239 | 1.81 |

Interpolating the lapse with a symmetric step concentrates the lapse's
curvature at the foot of each fall, where \(\alpha\) nears 1, and the peak
stress rises fourfold. A warped onset moves the curvature up the fall, where
the lapse is large. The warp that suits the falls along the track, 0.35, takes
their deficit from 62 to 22, while the radial fall does best near 0.5. Rounded
corners pay nothing. With the sheath's rise left whole inside the shaped
pattern, the radial fall moves in to 8.25 and passes the gate, and the cone's
base shrinks to 13.5.

## Combinations and the front rule

Combining separate warps along the track (0.35) and in radius (0.5), the
radial fall from 8.25 and the cone's lapse of 1 with a rise of 3 brings the
peak content to 127, and a shift edge of 0.75 to 119. That design passes the
full gate at 2.1, with peak content 123. A check the gate leaves out then
separates it from the minimized design: the front rule of the closure pass,
that every piece of the front advance along its normal slower than light.
The check finds each place where the lapse falls below \(|\beta+v|\) going
forward, at radii from 0.5 to 14, and measures the surface's normal speed
\(v|n_z|\) there. The axis at the tip, the one null point, belongs to the tip
rates.

| Design | 1.5 | 2.1 | 3 | 5 | 10 | 15 | 20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| trimmed reference | 0.72 | 0.74 | 0.76 | 0.76 | 0.77 | 0.77 | 0.77 |
| lapse-space falls, cone rise 3 | 0.72 | 0.74 | 2.69 | 5.00 | 10.0 | 15.0 | 20.0 |
| lapse-space falls, cone rise 1.5 | 0.72 | 0.74 | 0.76 | 0.76 | 0.77 | 1.00 | 1.33 |
| minimized design | 0.72 | 0.74 | 0.76 | 0.76 | 0.77 | 0.77 | 0.77 |

With the cone rising over 3, its lapse fills the pattern's front fall too late
at speed. From 3 upward the lapse dips below the carry speed across a disk at
\(\zeta\approx4.8\) spanning every radius to 9, 17–19% deep at 10, and that disk
is a flat front. With the cone rising over 1.5, the lapse-space radial fall tilts
the pattern's side instead. Its gentle landing places the surface
\(\alpha=v\) far down the fall, where the plateau's rise toward its ends moves
it outward; the side leans forward by \(n_z=0.067\), which crosses the rule
above 15. A radial fall in the log-lapse holds the side upright. The minimized
design therefore interpolates the lapse along the track and the log-lapse in
radius, and it keeps the cone's rise at 2.

| Mixed design | Peak content | Peak stress |
|---|---:|---:|
| shift edge 0.75, cone log-lapse 1 | 154 | 1.84 |
| the same, radial fall from 8.25 | 145 | 1.84 |
| the same, radial warp 0.7 | 147 | 1.84 |
| the same, cone in the lapse | 142 | 1.84 |
| **the same, cone rise 2** | **133** | **1.84** |
| the same, warp 0.5 along the track | 168 | 2.10 |
| shift edge 1 | 152 | 1.81 |
| cone log-lapse 1.25 | 161 | 1.84 |

## The minimized design

| Measure | Trimmed reference | Minimized design |
|---|---:|---:|
| peak negative-null content | 252 | 137 |
| content integrated over \(\sigma\), 12.6 trip | 2,361 | 1,275 |
| of which in the cone's window | 494 | 329 |
| peak stress component | 1.81 | 1.84 |
| largest lapse | 395 | 123 |
| worst lapse-envelope ratio | 0.50 | 0.72 |
| Type IV points, bands | 0, 0 | 0, 0 |
| cone base, tip ahead of the packet | 14, 58.0 | 13.5, 55.9 |
| tip: \(\kappa\), \(\lambda\), ratio | 0.563, 2.70, 4.8 | 0.346, 2.16, 6.2 |
| swept matter, largest \(\gamma\), lanes to \(\sigma=6\) / 12 | 5.9 / 11.5 | 4.5 / 5.5 |
| swept light, largest gain | 11.6 | 6.8 |
| fastest front normal speed, 1.5–20 | 0.77 | 0.77 |
| at 10: peak content, peak stress, tip ratio | 787, 3.65, 18.5 | 591, 3.69, 23.9 |
| deficit as mass at one unit = 1 m | \(0.17M_\odot\) | \(0.092M_\odot\) |

At mid-lane the deficit lies in the radial fall (39, against a floor of 6),
the rims (38, near their floor of 29), the cone (43, against 9.5), the falls
along the track (4) and the pattern's interior (12). The rims sit close to
their geometric floor, so the room that remains lies in the radial fall and the
cone. At 10 the cone carries 438 of 593, against a floor of 137 that grows with
its length.

The tip sheds field modes 6.2 times faster than it blueshifts them at 2.1 and
24 times at 10, both above the reference. Swept matter and light leave with
smaller gains, and the gains stay bounded on both lane lengths. The packet's
path and service are unchanged: it arrives 5.1 ahead of exterior light on the
12.6 trip, and at the 1× clock passengers spend 174 days per light-year.

## Open items

1. **The radial fall.** It carries seven times its floor. A profile that keeps
   the side of the surface \(\alpha=v\) upright at speed and moves the
   curvature up the fall would take the next share.
2. **The cone at speed.** It dominates above a few times light speed. Its
   flank advances at 0.54 of light speed along its normal by construction; a
   faster flank, still below 1, shortens the cone and its floor.
3. **Audits of the minimized design.** The three-dimensional path audits and
   the escape cones of the compartment's lapse cavity run on the trimmed
   reference and remain to be repeated on this one.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_deficit_minimization_pass.py --workers 4 \
    --stages screen,shapes,combine,fronts,mixed
OPENBLAS_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_deficit_minimization_pass.py --workers 4 \
    --stages full
PYTHONPATH=toolkit/adm_harness_cli:toolkit/adm_harness_cli/scripts python -m pytest \
    toolkit/adm_harness_cli/tests/test_shaped_pattern.py
```

The screens take about an hour with four workers, and the full stage 30–40
minutes per finalist. The manifest records every variant, the cone margin,
the split time, the front radii and speeds, each finalist's full record, and
the software hashes of each stage. The tests check that the shaped pattern
equals the product form inside the plateau's core, reaches flat space beyond
its falls, and gives a demanded tensor that matches a brute-force Einstein
tensor from the metric, for every shape and for the shaped cone.
