# Stage II Beta075 Action-Level Fixed-Background PDE Proof Obligation

## Status

Status: `action_pde_obligation_gap_temporal_regularization_required`.

The sealed beta075 package has now cleared the observed-amplitude scheduled
fixed-background evolution test, but the first action-level proof certificate
does not yet close the stronger temporal-profile-independent claim. The right
reading is narrow and important: the current package remains clean under the
observed source timing, while the proof still needs an admissible source-time
envelope that rules out an unphysical impulse collapse.

This is not a same-level component failure. It is the first point where the
testing has moved from "does this full-domain run behave" to "what class of
time-dependent source laws can the fixed-background PDE proof actually allow."

## Test Object

The certificate uses the sealed beta075 package as an input:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 support-source coupling law
- bounded rapidity as the heat/current transport variable
- active non-live support-source domain only

The harness writes structured artifacts only. The proof certificate lives in
CSV and JSON outputs under:

`toolkit/adm_harness_cli/runs/stage2_beta075_action_pde_obligation/`

No scripted Markdown/prose report is produced by the harness.

## Result

The scheduled observed-amplitude system remains clean:

- max scheduled budget fraction: `0.121201`
- live evolved rows: `0`
- packet-live evolved rows: `0`
- state/source amplification violation: `False`
- observed outward/forward, inward/forward, and outward/backward scenarios all
  pass

The stronger arbitrary impulse certificate fails:

- max impulse budget fraction: `1.158579`
- worst row: `support_edge_endpoint_junction / release_shift_fade / support_edge`
- worst coordinates: `s=1.0890957446808511`, `l=2.1`
- sampled cone margin at the worst impulse row: `1.3623908834414777e-07`
- sampled transport margin at the worst impulse row: `2.491800735748839e-07`

The transport edge certificate also shows that the normalized budget-row map is
not globally contractive under the overbroad arbitrary-timing model:

- transport edge rows checked: `167733`
- expansive edge rows: `82161`
- max normalized row-sum bound: `1.554856`
- worst row-sum receiver: row `4605`, inward radial direction

## Interpretation

The completed full-system evolution rung was a real pass, but it was a pass
for the observed scheduled source profile. This new certificate asks a stronger
question: if the same observed source budget is allowed to arrive at one time
as an arbitrary nonnegative impulse, can the fixed-background PDE proof still
guarantee the local rapidity budget everywhere?

The answer is no, not yet.

That is uncomfortable in a useful way. It means the action-level proof cannot
be based only on total source budget plus positivity. It must also include a
source-time regularity assumption or prove a temporal envelope from the
physical source law. Without that, the adversary is allowed to concentrate too
much source into the thin release/support-edge margin row.

This does not say the support-edge source law is bad. The observed scheduled
law still lands at only about `12.1%` of budget in the full-domain evolution.
The failing case is a deliberately stronger proof adversary that discards the
time profile and asks for safety under instantaneous collapse. That adversary
is broader than the current physical claim and broader than the source law
used in the completed evolution rung.

## Implications

The beta075 package should stay sealed at the current claim level. The evidence
does not point back to collar fitting, support-edge reshaping, V interpolation,
or artificial `5e-4` stress tuning.

The next proof obligation is sharper:

1. Define the admissible source-time envelope for the cap-0.95 source law.
2. Show that the envelope is not an arbitrary impulse and cannot collapse the
   observed source budget into one dangerous time step.
3. Propagate that admissible envelope through radial and service-time transport.
4. Gate the result on local rapidity budgets, cone/transport margin
   preservation, live exclusion, and no hidden component.

If that envelope proof passes, the action-level fixed-background story becomes
much stronger than the scheduled run alone: it would show that a whole class of
allowed source timings stays inside the invariant margin region.

If it fails, the failure should be interpreted carefully. A failure caused by an
unreasonably broad timing adversary is a proof-model mismatch. A failure caused
by the physical source law requiring too sharp a time profile would be the point
where source-law regularity becomes a real physics/design issue.

## Next Rung

The next rung is source-time regularity / admissible temporal-envelope proof.

Do not retune the component just because the arbitrary impulse certificate
failed. The immediate task is to identify the narrowest defensible time-regular
source class that matches the existing cap-0.95 source law and then certify that
class against the fixed-background transport budget.

The machine side of that rung should remain structured-artifact only. Narrative
reports should be written by hand after interpreting the artifacts.
