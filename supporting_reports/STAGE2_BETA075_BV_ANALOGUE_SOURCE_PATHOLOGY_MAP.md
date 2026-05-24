# Stage II Beta075 Barcelo--Visser Analogue Source Pathology Map

Status: concurrent Parquet boundedness ledger completed.

## Purpose

This report translates the Barcelo--Visser scalar-field lesson into the current
sealed beta075 source-family variables, then records a new boundedness ledger
run for the rail's own critical quantities. The question is where the
active-rail source story can hide the same kind of hard cost that appears in
non-minimally-coupled scalar wormhole models: a critical field amplitude, an
effective-coupling denominator, a near-null transport boundary, a singular
support layer, or a resolution-growing source concentration.

The current sealed design has moved past the original single-source question.
The lead physical target is a regulated anisotropic heat/current endpoint
medium, entrained to a radial director and coupled to a localized support
reservoir. The useful comparison is scalar amplitude/coupling pathology
against the rail's own boundedness variables.

## Barcelo--Visser Lesson

Barcelo and Visser are valuable here because their scalar model makes the
price of throat support algebraically visible. The non-minimal coupling puts a
field-dependent Einstein-tensor term in the stress tensor. Rearranging the
field equations produces an effective gravitational-coupling denominator, and
the wormhole branch drives the scalar toward a critical, Planck-scale field
range or an extreme curvature-coupling choice.

The rail analogue is the same style of question: when the demanded source is
written as a recognizable source family, do any of its own denominators,
transport speeds, support constants, or local exchange laws run to a critical
boundary? Barcelo--Visser already live in the exotic averaged-null class, so
the sharper issue is whether the exotic cost is paid by a controlled support
architecture or by an extreme hidden parameter.

## Current Source Class

The scalar route has been superseded as the lead source story for beta075. The
endpoint source-class screen keeps a single canonical or phantom scalar ruled
out:

| quantity | baseline | dense |
| --- | ---: | ---: |
| canonical scalar compatible volume fraction | `0.379515` | `0.335594` |
| phantom scalar compatible volume fraction | `0.382312` | `0.407455` |
| Type-IV source-burden fraction before regulator | `0.251505` | `0.258979` |
| minimal regulator/source burden ratio | `0.037723` | `0.039030` |

The positive source class is a regulated anisotropic heat/current medium. At
the decision safety factor `1.10`, the regulator remains small, non-live, and
finite-spread:

| quantity | baseline | dense |
| --- | ---: | ---: |
| regulator/source burden ratio | `0.041495` | `0.042933` |
| boundary-gradient/source ratio | `0.012888` | `0.007239` |
| p99 heat-flux ratio | `0.974975` | `0.975555` |
| p01 transport margin | `0.025025` | `0.024445` |
| max boost speed | `0.978182` | `0.987443` |
| live regulator rows | `0` | `0` |
| post-regulator Type-IV rows | `0` | `0` |

That changes the physics question. The current rail source family is built
around a regulated heat/current medium and support reservoir carrying the
localized endpoint/support cost while keeping transport and exchange variables
bounded.

## Code And Storage

New harness:

```text
toolkit/adm_harness_cli/adm_harness/beta075_bv_denominator_ledger.py
toolkit/adm_harness_cli/scripts/run_beta075_bv_denominator_ledger.py
```

Run command:

```text
python toolkit/adm_harness_cli/scripts/run_beta075_bv_denominator_ledger.py --max-workers 6
```

The run used `6` workers over independent source tables and wrote all tabular
outputs as zstd Parquet:

```text
toolkit/adm_harness_cli/runs/stage2_beta075_bv_denominator_ledger/
```

| output | rows | storage |
| --- | ---: | --- |
| medium denominator points | `142188` | Parquet |
| source-family point-symbol margins | `66301` | Parquet |
| energy-estimate point margins | `63906` | Parquet |
| finite-domain ANEC trace margins | `6894` | Parquet |
| metric summary | `2508` | Parquet |
| top tight rows | `3760` | Parquet |
| gate summary | `12` | Parquet |

Unit verification:

```text
python -m pytest tests/test_beta075_bv_denominator_ledger.py
```

Result: `1 passed`. The test locks in Parquet tabular outputs and active-row
symbol-failure accounting.

## Computed Analogue Map

| Barcelo--Visser pathology handle | Rail-source analogue | Current sealed beta075 read |
| --- | --- | --- |
| scalar field reaches critical amplitude | rapidity `psi`, transport boost, source-profile scale | dense max `psi = 5.064348`; max boost speed `0.987443`; source-profile scale `0.092617` is bounded but severe |
| effective Newton denominator approaches zero or changes sign | `h_reg = 1 - v_q^2`, flux cone margin, Type-I discriminant | decision-factor regulator rows retain Type-I form with zero live regulator rows, zero post-regulator Type-IV rows, and zero superluminal/undefined boost rows |
| throat support paid by a thin extreme layer | support-edge heat ratio, local regulator/source cushion, boundary-gradient/source cost | dense minimum transport margin is `7.983e-05` at reset-decompression/support-edge; maximum local regulator/source ratio is `1.052677` at release-shift-fade/support-edge |
| formally conserved source hides an exchange sink | explicit support current `J_support = P u + F s`, total support closure | active symbol rows have zero hard symbol failures and zero live support flags; support closure headroom is thin at `0.005433` on dense surfaces |
| source action has large lower-order work terms | support-work constant, local `P/F` exchange shape | dense energy work constant peaks at `2.049051 / 2.5`; local `P = 0.609031`; local exchange headroom is `0.190969` |
| scalar solution is algebraic but physically expensive | fixed-background equation skeleton and energy certificate | hard gates pass with positive symmetrizer and in-cone flux; theorem margin remains watch-bounded |
| exotic support leaks into the traveler/live region | live regulator rows, live support rows, live angular exchange | live regulator rows and live support flags remain zero in the boundedness ledger |
| radial ANEC cost survives averaging | finite-domain radial ANEC diagnostic | geometric total is radial-ANEC negative with closure-residual dominance; residual-plus-live-trim removal leaves worst branch integrals `-0.004643` and `-0.009361` |

## Ledger Results

Medium/regulator gates at the decision safety factor `1.10`:

| mesh | rows | live regulator | Type-IV after regulator | superluminal boost | near heat boundary | order-one local regulator | angular-inertia negatives | min transport margin | min `h_reg` quadratic | min Type-I margin | max heat ratio | max boost | max local regulator/source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | `7188` | `0` | `0` | `0` | `28` | `0` | `1958` | `0.000243` | `0.000486` | `1.020e-07` | `0.999757` | `0.978182` | `0.892239` |
| dense | `28359` | `0` | `0` | `0` | `107` | `1` | `7531` | `0.000080` | `0.000160` | `4.036e-09` | `0.999920` | `0.987443` | `1.052677` |

Source-family point-symbol gates:

| surface | active rows | active hard-symbol failures | live support flags | thin cone rows | min cone margin | p01 cone margin | max rapidity | max local exchange error | min local exchange headroom |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sealed baseline V5 | `7188` | `0` | `0` | `0` | `0.000241` | `0.019362` | `4.507205` | `0.327001` | `0.472999` |
| sealed dense V5 | `28359` | `0` | `0` | `1` | `0.000079` | `0.017972` | `5.064348` | `0.609031` | `0.190969` |
| lower-service dense V2 | `28359` | `0` | `0` | `1` | `0.000079` | `0.017863` | `5.064348` | `0.609031` | `0.190969` |

Energy-estimate gates:

| surface | rows | hard failures | thin flux rows | near work bound rows | support-closure near-gate rows | min flux margin | max work constant | min work headroom | max support closure | min closure headroom |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sealed baseline V5 | `7188` | `0` | `0` | `0` | `0` | `0.000241` | `1.349510` | `1.150490` | `0.302640` | `0.247360` |
| sealed dense V5 | `28359` | `0` | `1` | `7` | `28359` | `0.000079` | `2.049051` | `0.450949` | `0.544567` | `0.005433` |
| lower-service dense V2 | `28359` | `0` | `1` | `7` | `28359` | `0.000079` | `2.049050` | `0.450950` | `0.544567` | `0.005433` |

The support-closure ratio is a dense-surface support constant repeated across
the energy point table, so the near-gate row count records surface scope rather
than a new pointwise failure population.

Finite-domain radial ANEC trace gates:

| mode | branch | traces | negative traces | worst integral | p01 integral | median integral | dominant negative read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| geometric total | minus | `1701` | `1495` | `-1.796825` | `-0.239549` | `-0.067083` | closure residual dominates |
| geometric total | plus | `1751` | `1607` | `-1.143288` | `-0.231385` | `-0.067097` | closure residual dominates, with one live-trim extreme |
| residual and live trim removed | minus | `1708` | `849` | `-0.004643` | `-0.002366` | `0.000000` | small angular-capacity remainder |
| residual and live trim removed | plus | `1734` | `883` | `-0.009361` | `-0.006382` | `-2.657e-08` | small angular-capacity remainder |

## Row-Level Boundary Read

The tightest heat/current transport row is dense
reset-decompression/support-edge at `(s,l) = (2.537234, 2.00)`. It has
regulated heat ratio `0.999920`, transport margin `7.983e-05`, quadratic
`h_reg = 1.596e-04`, boost speed `0.987443`, Type-I margin `8.272e-07`, and a
negative angular-inertia read. The same row is also the tightest active
point-symbol cone row on sealed dense V5 and lower-service dense V2. This is
the rail's closest analogue to a BV-style denominator boundary: finite,
passing, and narrow.

The thinnest Type-I discriminant row is different. It lies in the dense
entry-precatch/support-edge band at `(s,l) = (-0.710106, 1.50)`, with Type-I
margin `4.036e-09`, heat ratio `0.997600`, and transport margin `0.002400`.
The next rows sit in entry-precatch and catch-rematch support-edge bands. This
separates the Type-I algebraic edge from the worst heat/current transport row
and makes the endpoint/support source law a two-boundary problem rather than a
single scalar-amplitude wall.

The maximum local regulator/source ratio is dense release-shift-fade/support
edge at `(s,l) = (1.220745, -1.20)`, with local ratio `1.052677`, heat ratio
`0.915607`, and transport margin `0.084393`. This is the strongest sign that
the support edge needs a real enthalpy/reservoir degree of freedom. It is a
localized support-source cushion inside a globally small regulator budget.

The largest local support-exchange work is dense reset-decompression/core
throat around `(s,l) = (1.659574, -1.10)`, where local `P = 0.609031`,
`F = 0.450115`, and local exchange headroom is `0.190969`. The maximum
energy-work constant `2.049051` lives on the same core-throat exchange family,
while the minimum flux/cone margin lives at reset-decompression/support-edge.
That split is useful: the rail's proof debt has a transport edge and a work
edge, not one hidden scalar knob doing everything.

## Sealed-Design Read

The sealed beta075 design has replaced the scalar trans-Planckian question with
a regulated-medium boundedness question, and the ledger makes that replacement
concrete. The support architecture is described by explicit measured boundary
variables: rapidity, enthalpy cushion, cone margin, Type-I margin, support
closure, local exchange shape, angular response, and finite-domain averaged-null
completion.

The strongest positive signal is that the source-family hard gates remain
coherent after the source class is made explicit. At decision safety factor
`1.10`, the regulator is finite, non-live, and restores the radial block to
Type-I form on the baseline and dense ledgers. The formal
director/support-reservoir equations preserve real in-cone characteristics,
total endpoint/support conservation, live exclusion, positive symmetrizer,
symmetric principal block, and bounded lower-order work on the available
complete surfaces. Lower-service dense V2 carries essentially the same watch
constants as sealed dense V5, so the support-family debt is stable across the
available adjacent service surface.

The rail-specific critical boundary is also clear. It sits at the support edge
and reset-decompression exchange rows while the live carrier corridor remains
protected. The ledger separates three rail-specific watch surfaces: the
near-null heat/current transport row at reset-decompression/support-edge, the
ultra-thin Type-I discriminant rows in entry/catch support-edge phases, and the
large local `P` work rows at reset-decompression/core-throat. These are finite
and passing. They are also narrow enough that the next matter-action derivation
has to expose its denominators and characteristic speeds directly.

The finite-domain radial ANEC result fits the same picture. The demanded
geometric total carries a radial-ANEC deficit dominated by
`sector_closure_residual`. Once that source-completion residual and the
plus-branch live-handoff trim are separated, the explicit non-live sector
package sits close to finite-domain radial-ANEC balance, with worst remaining
branch integrals about `-0.004643` and `-0.009361`. For the rail, the
averaged-null cost is presently a source-completion and endpoint/support plant
target, while the live corridor remains protected by the repaired SNEC-clean
package.

For the sealed rail, the data point to a controlled but thin regulated-medium
boundary rather than the Barcelo--Visser scalar trans-Planckian wall. A future
finite-domain radial-ANEC-clean rail would most plausibly come from
source-family completion and support-edge constitutive refinement on the same
carrier geometry, while the live packet corridor remains a protected carrier
channel.

## Confidence

The confidence read improves from "plausible source-family replacement" to
moderate confidence in a distinct rail source class with explicit boundedness
variables. The evidence is the scalar-class rejection, the finite non-live
regulator budget, zero live regulator rows, zero active hard-symbol failures,
zero live support flags, preserved energy hard gates, and stable dense V5/V2
watch pattern.

The confidence ceiling remains set by action-level closure and finite-domain
radial ANEC completion. The support-edge transport margin, Type-I discriminant,
support-closure headroom, local `P/F` exchange shape, angular-inertia rows, and
residual ANEC attribution are the rail-specific places where a hidden
denominator or large-coupling demand would show itself.

## Next Rung

The next useful rung is matter-action denominator exposure. A constructive
medium model should name and preserve the same variables measured here:

```text
h_reg = 1 - v_q^2
Type-I discriminant
cone margin
support closure headroom
local P/F exchange headroom
angular-response coefficient scale
source-profile scale
finite-domain ANEC residual attribution
```

A successful derivation should widen the support-edge proof margin, supply the
order-one local enthalpy cushion through an explicit support reservoir, and
turn the remaining finite-domain ANEC residue into a source-completion target.
The useful follow-up run is a denominator-drift ladder under support-edge
constitutive refinement, with the same Parquet ledger schema so the tight rows
can be compared directly.
